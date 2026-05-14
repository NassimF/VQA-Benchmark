"""Empirically audit ground-truth span precision in benchmark_v1.json.

Stratified sample: 2 pairs per lecture (1 visual-type, 1 non-visual).
For each pair, checks whether key_concepts from the answer appear in the
cited chunk text and estimates how much of the span window is "wasted".

Decision gate (printed at end):
  mean span error ≤ 20s  → tIoU@0.3 well-justified
  mean span error > 30s  → reconsider tIoU@0.3; consider dropping to @0.2
"""

import json
import logging
import random
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

VISUAL_TYPES = {"multi-hop-visual", "visual"}
RANDOM_SEED = 42


@dataclass
class SpanAuditResult:
    qa_id: str
    question_type: str
    span_duration: float          # end - start of the cited span
    concepts_found: int           # key_concepts matched in chunk text
    concepts_total: int
    coverage_ratio: float         # concepts_found / concepts_total
    # Fraction of span where evidence is present (1.0 = full span covered,
    # 0.3 = evidence only in ~30% of the window → ~70% wasted)
    evidence_coverage: float
    estimated_error_s: float      # (1 - evidence_coverage) * span_duration / 2
    notes: str = ""


def _load_chunks(chunks_dir: Path, video_id: str) -> dict[str, dict]:
    """Load plain chunks for a video, keyed by chunk_id."""
    plain = chunks_dir / f"{video_id}_chunks.json"
    augmented = chunks_dir / f"{video_id}_chunks_augmented.json"
    src = augmented if augmented.exists() else plain
    if not src.exists():
        return {}
    chunks = json.loads(src.read_text())
    return {c["chunk_id"]: c for c in chunks}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def _concept_hits(concepts: list[str], chunk_text: str) -> int:
    norm = _normalize(chunk_text)
    return sum(1 for c in concepts if _normalize(c) in norm)


def _estimate_evidence_coverage(concepts: list[str], chunk_text: str) -> float:
    """Rough proxy: fraction of concept words found in the chunk text.

    A chunk always covers its full declared window; the question is whether
    the *answer evidence* occupies the full window or just part of it.
    We use concept hit rate as a proxy — if all concepts are present the
    evidence likely spans most of the window; if only some are present the
    evidence is sparser.
    """
    if not concepts:
        return 1.0
    hits = _concept_hits(concepts, chunk_text)
    return hits / len(concepts)


def audit_pair(pair: dict, chunks: dict[str, dict]) -> SpanAuditResult | None:
    spans = pair.get("ground_truth_spans", [])
    if not spans:
        return None

    concepts: list[str] = pair.get("key_concepts", [])
    qa_id = pair["qa_id"]
    qtype = pair["question_type"]

    # Audit each span independently, report the worst (lowest coverage)
    worst: SpanAuditResult | None = None

    for span in spans:
        start = span.get("start", 0.0)
        end = span.get("end", start)
        duration = end - start

        # Find the chunk that covers this span
        matching_chunk: dict | None = None
        for chunk in chunks.values():
            if chunk["start_time"] <= start and chunk["end_time"] >= end:
                matching_chunk = chunk
                break
        # Fallback: closest chunk by start time
        if matching_chunk is None:
            candidates = [
                c for c in chunks.values()
                if abs(c["start_time"] - start) < 50
            ]
            if candidates:
                matching_chunk = min(candidates,
                                     key=lambda c: abs(c["start_time"] - start))

        if matching_chunk is None:
            result = SpanAuditResult(
                qa_id=qa_id, question_type=qtype,
                span_duration=duration,
                concepts_found=0, concepts_total=len(concepts),
                coverage_ratio=0.0, evidence_coverage=0.0,
                estimated_error_s=duration / 2,
                notes="no matching chunk found",
            )
        else:
            chunk_text = matching_chunk.get("text", "")
            hits = _concept_hits(concepts, chunk_text)
            coverage = _estimate_evidence_coverage(concepts, chunk_text)
            error_s = (1.0 - coverage) * duration / 2.0

            result = SpanAuditResult(
                qa_id=qa_id, question_type=qtype,
                span_duration=duration,
                concepts_found=hits, concepts_total=len(concepts),
                coverage_ratio=coverage,
                evidence_coverage=coverage,
                estimated_error_s=error_s,
                notes=f"chunk {matching_chunk['chunk_id']}",
            )

        if worst is None or result.estimated_error_s > worst.estimated_error_s:
            worst = result

    return worst


def stratified_sample(pairs: list[dict], seed: int = RANDOM_SEED) -> list[dict]:
    """2 per lecture: 1 visual-type, 1 non-visual (unanswerable excluded)."""
    rng = random.Random(seed)
    by_lecture: dict[str, dict[str, list[dict]]] = {}

    for p in pairs:
        vid = p["video_id"]
        qtype_class = "visual" if p["question_type"] in VISUAL_TYPES else "non-visual"
        if p["question_type"] == "unanswerable":
            continue
        by_lecture.setdefault(vid, {"visual": [], "non-visual": []})
        by_lecture[vid][qtype_class].append(p)

    sample: list[dict] = []
    for vid, buckets in sorted(by_lecture.items()):
        for bucket in ("visual", "non-visual"):
            if buckets[bucket]:
                sample.append(rng.choice(buckets[bucket]))

    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit ground-truth span precision.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--all", action="store_true",
                        help="Audit all pairs instead of stratified sample.")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    benchmark_path = cfg.data.benchmark_dir / "benchmark_v1.json"
    chunks_dir = cfg.data.chunks_dir

    data = json.loads(benchmark_path.read_text())
    all_pairs = data["qa_pairs"]

    pairs = all_pairs if args.all else stratified_sample(all_pairs, seed=args.seed)
    logger.info("Auditing %d pairs (seed=%d)", len(pairs), args.seed)

    # Cache chunks per video
    chunk_cache: dict[str, dict[str, dict]] = {}

    results: list[SpanAuditResult] = []
    no_chunk: list[str] = []

    for pair in pairs:
        vid = pair["video_id"]
        if vid not in chunk_cache:
            chunk_cache[vid] = _load_chunks(chunks_dir, vid)
        chunks = chunk_cache[vid]
        if not chunks:
            no_chunk.append(pair["qa_id"])
            continue
        result = audit_pair(pair, chunks)
        if result:
            results.append(result)

    if not results:
        logger.error("No results — check chunk paths.")
        sys.exit(1)

    errors = [r.estimated_error_s for r in results]
    coverages = [r.coverage_ratio for r in results]
    mean_error = sum(errors) / len(errors)
    max_error = max(errors)
    mean_coverage = sum(coverages) / len(coverages)
    pct_inner_50 = sum(1 for r in results if r.evidence_coverage >= 0.5) / len(results)

    print("\n" + "=" * 60)
    print("SPAN PRECISION AUDIT REPORT")
    print("=" * 60)
    print(f"Pairs audited:        {len(results)}")
    print(f"Mean span error:      {mean_error:.1f}s")
    print(f"Worst span error:     {max_error:.1f}s")
    print(f"Mean concept coverage:{mean_coverage:.2f}")
    print(f"Evidence in ≥50% of span: {100*pct_inner_50:.1f}%")

    # By question type
    for qtype in ("multi-hop-visual", "visual", "multi-hop", "text"):
        subset = [r for r in results if r.question_type == qtype]
        if subset:
            me = sum(r.estimated_error_s for r in subset) / len(subset)
            print(f"  {qtype:<26} n={len(subset):3d}  mean_error={me:.1f}s")

    if no_chunk:
        print(f"\nWARNING: {len(no_chunk)} pairs had no matching chunk file:")
        for qa_id in no_chunk[:10]:
            print(f"  {qa_id}")

    print("\n--- DECISION GATE ---")
    if mean_error <= 20.0:
        print(f"✅ mean error {mean_error:.1f}s ≤ 20s → tIoU@0.3 is well-justified.")
        print("   Update benchmark.tex: replace '±15–30s estimate' with measured value.")
    elif mean_error <= 30.0:
        print(f"⚠️  mean error {mean_error:.1f}s in 20–30s range → tIoU@0.3 acceptable;")
        print("   note as a limitation in the paper.")
    else:
        print(f"❌ mean error {mean_error:.1f}s > 30s → reconsider tIoU@0.3.")
        print("   Consider reporting only Hit Rate@k, or drop to tIoU@0.2.")
    print("=" * 60)

    # Save results JSON
    out_path = cfg.data.benchmark_dir / "span_audit_results.json"
    out_path.write_text(json.dumps({
        "summary": {
            "pairs_audited": len(results),
            "mean_error_s": round(mean_error, 2),
            "max_error_s": round(max_error, 2),
            "mean_coverage": round(mean_coverage, 3),
            "pct_evidence_inner_50pct": round(pct_inner_50, 3),
        },
        "pairs": [
            {
                "qa_id": r.qa_id,
                "question_type": r.question_type,
                "span_duration_s": r.span_duration,
                "concepts_found": r.concepts_found,
                "concepts_total": r.concepts_total,
                "coverage_ratio": round(r.coverage_ratio, 3),
                "estimated_error_s": round(r.estimated_error_s, 1),
                "notes": r.notes,
            }
            for r in results
        ],
    }, indent=2))
    logger.info("Saved → %s", out_path)


if __name__ == "__main__":
    main()
