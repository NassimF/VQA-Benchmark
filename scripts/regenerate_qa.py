"""Phase 7.3 regeneration pass — re-draft QA pairs for lectures below floor.

D8 protocol (requirements.md): one retry per lecture that scored < floor after first review.
Regenerates all 15 pairs fresh with failure-aware constraints injected into the prompt.

Usage:
    python scripts/regenerate_qa.py --video_id mit_18065_lec06
    python scripts/regenerate_qa.py --all           # all lectures below floor
    python scripts/regenerate_qa.py --all --dry_run # list targets without running

Output files:
    data/qa_pairs/raw/{video_id}_qa_regen.json       -- 15 freshly generated pairs
    data/qa_pairs/reviewed/{video_id}_qa_reviewed.json -- updated with newly accepted pairs
    data/qa_pairs/review_log/{video_id}_regen_log.json -- review log for regenerated pairs
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

import anthropic

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config, load_config
from src.qa_generator import (
    _SYSTEM_PROMPT,
    _extract_json_array,
    load_augmented_chunks,
    _seconds_to_mmss,
)
from src.qa_reviewer import QAReviewer
from scripts.review_qa import review_lecture, _compute_lecture_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# qa_id index base for regenerated pairs — avoids collision with first-run q001–q015
_REGEN_ID_OFFSET = 15

# Temperature for regeneration — higher than default (0.0) to produce diverse pairs
_REGEN_TEMPERATURE = 0.9

_REGEN_SYSTEM_PREFIX = """\
REGENERATION PASS — this is a second attempt for a lecture where the first batch had a
high rejection rate. Do NOT reuse questions, phrasings, or chunk combinations from any
previous batch. Every pair must be genuinely new.

"""

# Failure-aware constraint blocks injected when a criterion dominated rejections
_C1_CONSTRAINT = """\
CORRECTNESS CONSTRAINT (C1 failures were high in the previous batch):
Before writing each answer, decompose it into individual atomic claims. For each claim,
locate the exact sentence or [frame caption] text that supports it. If you cannot point
to specific chunk text, remove that claim from the answer. Do not add any claim based on
general knowledge about the topic.

"""

_C2_CONSTRAINT = """\
SPAN GAP CONSTRAINT (C2 failures were high in the previous batch):
For every multi-hop or multi-hop-visual pair, compute |span_A.start - span_B.start| for
all pairs of hops before finalising the pair. The gap must be ≥ 70 seconds for every pair.
Pairs where any two hops start within 70 seconds of each other will be rejected — do not
generate such pairs.

"""

_C3_CONSTRAINT = """\
TYPE ACCURACY CONSTRAINT (C3 failures were high in the previous batch):
Before assigning question_type, check the following in the chunk text provided:
- "multi-hop-visual" or "visual": the literal string "[frame caption:" must appear in
  the text of every cited chunk that is claimed to provide visual evidence. If the marker
  is absent, use "multi-hop" or "text" instead.
- "multi-hop" or "multi-hop-visual": hops must be genuinely non-adjacent (≥ 70s apart).
  If they are adjacent, use "text" or "visual" instead.

"""


def _build_failure_constraints(review_log: list[dict]) -> str:
    """Analyse per-lecture rejection log and return constraint blocks for dominant failures."""
    rejected = [e for e in review_log if e["overall"] == "REJECT"]
    if not rejected:
        return ""

    c1_fails = sum(1 for e in rejected if e["criterion_1"]["result"] == "FAIL"
                   and e["criterion_1"]["reason"] != "parse error")
    c2_fails = sum(1 for e in rejected if e["criterion_2"]["result"] == "FAIL"
                   and e["criterion_2"]["reason"] != "parse error")
    c3_fails = sum(1 for e in rejected if e["criterion_3"]["result"] == "FAIL"
                   and e["criterion_3"]["reason"] != "parse error")

    total = len(rejected)
    constraints = ""
    # Inject constraint if criterion was the primary failure in ≥30% of rejections
    if total and c1_fails / total >= 0.30:
        constraints += _C1_CONSTRAINT
    if total and c2_fails / total >= 0.30:
        constraints += _C2_CONSTRAINT
    if total and c3_fails / total >= 0.30:
        constraints += _C3_CONSTRAINT

    return constraints


def _build_regen_prompt(video_id: str, chunks: list[dict]) -> str:
    """Format chunks into a user prompt for regeneration (same as base but with offset IDs)."""
    lines: list[str] = [
        f"Lecture: {video_id}",
        f"Total chunks: {len(chunks)}",
        "",
        "CHUNKS:",
        "",
    ]
    for i, chunk in enumerate(chunks, start=1):
        start = _seconds_to_mmss(chunk["start_time"])
        end = _seconds_to_mmss(chunk["end_time"])
        lines.append(f"[{i}] {chunk['chunk_id']} ({start}–{end})")
        lines.append(chunk["text"])
        lines.append("")

    lines.append(
        f"Generate exactly 15 QA pairs for lecture '{video_id}' following the schema and "
        "distribution specified in the system prompt. Use the chunk_ids above for "
        f"source_chunk_ids and ground_truth_spans timestamps. "
        f"qa_id indices must run from q{_REGEN_ID_OFFSET + 1:03d} to "
        f"q{_REGEN_ID_OFFSET + 15:03d} (e.g. '{video_id}_q{_REGEN_ID_OFFSET + 1:03d}')."
    )
    return "\n".join(lines)


def _parse_regen_response(video_id: str, raw_json: str) -> list[dict]:
    """Parse and validate regenerated QA batch; enforce offset qa_id range."""
    from src.qa_generator import _VALID_QUESTION_TYPES, _MULTIHOP_TYPES, _REQUIRED_FIELDS

    candidate = _extract_json_array(raw_json)
    try:
        items = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Response is not valid JSON: {exc}\n---\n{raw_json[:500]}") from exc

    if not isinstance(items, list):
        raise ValueError(f"Expected JSON array, got {type(items).__name__}")

    validated: list[dict] = []
    for i, item in enumerate(items):
        missing = _REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"Item {i} missing fields: {missing}")

        qt = item["question_type"]
        if qt not in _VALID_QUESTION_TYPES:
            raise ValueError(f"Item {i} has invalid question_type: {qt!r}")

        hops = item["num_hops"]
        if qt in _MULTIHOP_TYPES and hops < 2:
            raise ValueError(f"Item {i}: {qt} requires num_hops ≥ 2, got {hops}")
        if qt not in _MULTIHOP_TYPES and hops != 1:
            raise ValueError(f"Item {i}: {qt} requires num_hops = 1, got {hops}")

        if qt == "unanswerable":
            if item.get("answerable", True):
                raise ValueError(f"Item {i}: unanswerable must have answerable=false")
            if item.get("ground_truth_spans"):
                raise ValueError(f"Item {i}: unanswerable must have empty ground_truth_spans")

        # Enforce offset qa_id range
        expected_id = f"{video_id}_q{_REGEN_ID_OFFSET + i + 1:03d}"
        item["qa_id"] = expected_id  # overwrite in case model used wrong index
        item["video_id"] = video_id
        validated.append(item)

    counts = Counter(item["question_type"] for item in validated)
    expected = {"multi-hop-visual": 7, "visual": 2, "multi-hop": 3, "text": 2, "unanswerable": 1}
    wrong = {k: (counts[k], v) for k, v in expected.items() if counts[k] != v}
    if wrong:
        detail = ", ".join(f"{k}: got {got} expected {exp}" for k, (got, exp) in wrong.items())
        raise ValueError(f"Wrong question type distribution — {detail}")

    logger.info(f"{video_id}: parsed {len(validated)} regenerated QA items")
    return validated


def regenerate_qa(
    video_id: str,
    review_log: list[dict],
    cfg: Config,
) -> list[dict]:
    """Generate a fresh batch of 15 QA pairs with failure-aware constraints.

    Args:
        video_id: Lecture identifier.
        review_log: Per-lecture review log from the first run (used to build constraints).
        cfg: Loaded Config.

    Returns:
        List of 15 validated QA dicts with qa_ids q016–q030.
    """
    chunks = load_augmented_chunks(video_id, cfg)
    failure_constraints = _build_failure_constraints(review_log)
    system_prompt = _REGEN_SYSTEM_PREFIX + failure_constraints + _SYSTEM_PROMPT
    user_prompt = _build_regen_prompt(video_id, chunks)

    client = anthropic.Anthropic()
    logger.info(f"{video_id}: calling {cfg.qa_generation.model} for regeneration "
                f"(temp={_REGEN_TEMPERATURE})")

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        response = client.messages.create(
            model=cfg.qa_generation.model,
            max_tokens=8192,
            temperature=_REGEN_TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text
        logger.debug(f"{video_id}: regen attempt {attempt}, response length={len(raw)}")
        try:
            items = _parse_regen_response(video_id, raw)
            break
        except ValueError as exc:
            logger.warning(f"{video_id}: regen attempt {attempt} failed validation — {exc}")
            last_exc = exc
            if attempt < 3:
                time.sleep(65)
    else:
        raise ValueError(f"{video_id}: all 3 regeneration attempts failed") from last_exc

    today = date.today().isoformat()
    for item in items:
        item["reviewed_by"] = "llm_draft_regen"
        item["review_date"] = today

    return items


def run_one(
    video_id: str,
    cfg: Config,
    raw_dir: Path,
    reviewed_dir: Path,
    review_log_dir: Path,
    reviewer: QAReviewer,
    dry_run: bool,
) -> dict:
    """Regenerate and review one lecture. Returns stats dict."""
    existing_reviewed = reviewed_dir / f"{video_id}_qa_reviewed.json"
    existing_log = review_log_dir / f"{video_id}_review_log.json"

    if not existing_log.exists():
        logger.error(f"{video_id}: no review log found, skipping")
        return {}

    with existing_log.open() as f:
        review_log = json.load(f)

    already_accepted = [e for e in review_log if e["overall"] == "ACCEPT"]
    n_accepted = len(already_accepted)

    if n_accepted >= cfg.qa_review.floor_accepted:
        logger.info(f"{video_id}: already at/above floor ({n_accepted}), skipping")
        return {}

    if dry_run:
        constraints = _build_failure_constraints(review_log)
        has_c1 = "CORRECTNESS" in constraints
        has_c2 = "SPAN GAP" in constraints
        has_c3 = "TYPE ACCURACY" in constraints
        print(f"  {video_id}: accepted={n_accepted} → needs regen "
              f"[C1={'Y' if has_c1 else 'N'} C2={'Y' if has_c2 else 'N'} "
              f"C3={'Y' if has_c3 else 'N'}]")
        return {}

    # Generate fresh batch
    try:
        regen_items = regenerate_qa(video_id, review_log, cfg)
    except ValueError as exc:
        logger.error(f"{video_id}: regeneration failed — {exc}")
        return {}

    # Save raw regenerated pairs
    regen_raw_path = raw_dir / f"{video_id}_qa_regen.json"
    regen_raw_path.write_text(json.dumps(regen_items, indent=2))
    logger.info(f"{video_id}: saved {len(regen_items)} regenerated pairs → {regen_raw_path}")

    # Rate limit before review calls
    time.sleep(5)

    # Review the regenerated pairs
    regen_log_path = review_log_dir / f"{video_id}_regen_log.json"
    regen_reviewed: list[dict] = []
    regen_log_entries: list[dict] = []

    for qa in regen_items:
        # Build chunk text map
        aug_path = cfg.data.chunks_dir / f"{video_id}_chunks_augmented.json"
        with aug_path.open() as f:
            chunks_raw = json.load(f)
        chunks_map = {c["chunk_id"]: c["text"] for c in chunks_raw}

        result = reviewer.review_qa_pair(qa, chunks_map)
        log_entry = {
            "qa_id": qa["qa_id"],
            "question_type": qa.get("question_type"),
            "overall": result.overall,
            "criterion_1": {"result": result.criterion_1.result, "reason": result.criterion_1.reason},
            "criterion_2": {"result": result.criterion_2.result, "reason": result.criterion_2.reason},
            "criterion_3": {"result": result.criterion_3.result, "reason": result.criterion_3.reason},
            "rejection_reason": result.rejection_reason,
            "c1_cross_check_result": result.c1_cross_check_result,
            "c1_cross_check_reason": result.c1_cross_check_reason,
        }
        regen_log_entries.append(log_entry)
        if result.overall == "ACCEPT":
            regen_reviewed.append(qa)
        else:
            logger.info(f"  REJECT {qa['qa_id']}: {result.rejection_reason}")

    regen_log_path.write_text(json.dumps(regen_log_entries, indent=2))

    # Merge: existing accepted + newly accepted regenerated pairs
    existing_accepted: list[dict] = []
    if existing_reviewed.exists():
        with existing_reviewed.open() as f:
            existing_accepted = json.load(f)

    merged = existing_accepted + regen_reviewed
    total_accepted = len(merged)

    reviewed_dir.mkdir(parents=True, exist_ok=True)
    existing_reviewed.write_text(json.dumps(merged, indent=2))

    logger.info(
        f"{video_id}: regen accepted {len(regen_reviewed)}/15 → "
        f"total accepted {total_accepted} "
        f"(was {n_accepted})"
    )

    if total_accepted < cfg.qa_review.discard_threshold:
        logger.warning(
            f"{video_id}: still below discard threshold ({total_accepted} < "
            f"{cfg.qa_review.discard_threshold}) after regeneration — will be discarded"
        )

    return {
        "video_id": video_id,
        "accepted_before": n_accepted,
        "regen_accepted": len(regen_reviewed),
        "total_accepted": total_accepted,
        "discarded": total_accepted < cfg.qa_review.discard_threshold,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 7.3 regeneration pass for lectures below floor"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Regenerate a single lecture")
    group.add_argument("--all", action="store_true", help="Regenerate all below-floor lectures")
    parser.add_argument("--dry_run", action="store_true",
                        help="List target lectures and constraint flags without calling APIs")
    args = parser.parse_args()

    cfg = load_config()
    raw_dir = cfg.data.qa_pairs_dir / "raw"
    reviewed_dir = cfg.data.qa_pairs_dir / "reviewed"
    review_log_dir = cfg.data.qa_pairs_dir / "review_log"

    summary_path = review_log_dir / "review_summary.json"
    if not summary_path.exists():
        logger.error("review_summary.json not found — run scripts/review_qa.py --all first")
        sys.exit(1)

    with summary_path.open() as f:
        summary = json.load(f)

    below_floor = summary.get("lectures_below_floor", [])

    if args.video_id:
        video_ids = [args.video_id]
    else:
        video_ids = below_floor
        logger.info(f"Found {len(video_ids)} lectures below floor (< {cfg.qa_review.floor_accepted})")

    if args.dry_run:
        print(f"\nDry run — {len(video_ids)} lectures would be regenerated:")
        for vid in video_ids:
            review_log_dir_path = review_log_dir / f"{vid}_review_log.json"
            if review_log_dir_path.exists():
                log = json.loads(review_log_dir_path.read_text())
                run_one(vid, cfg, raw_dir, reviewed_dir, review_log_dir,
                        reviewer=None, dry_run=True)  # type: ignore[arg-type]
        return

    reviewer = QAReviewer(cfg.qa_review)
    results = []
    for i, video_id in enumerate(video_ids):
        logger.info(f"--- Regenerating {video_id} ({i + 1}/{len(video_ids)}) ---")
        stats = run_one(video_id, cfg, raw_dir, reviewed_dir, review_log_dir, reviewer,
                        dry_run=False)
        if stats:
            results.append(stats)
        if i < len(video_ids) - 1:
            time.sleep(65)

    if results:
        total_before = sum(r["accepted_before"] for r in results)
        total_regen = sum(r["regen_accepted"] for r in results)
        total_after = sum(r["total_accepted"] for r in results)
        discarded = [r["video_id"] for r in results if r["discarded"]]
        print("\n" + "=" * 60)
        print("REGENERATION SUMMARY")
        print("=" * 60)
        print(f"Lectures regenerated:  {len(results)}")
        print(f"Pairs accepted before: {total_before}")
        print(f"Regen pairs accepted:  {total_regen}")
        print(f"Total pairs now:       {total_after}")
        if discarded:
            print(f"Discarded (<{cfg.qa_review.discard_threshold}): {discarded}")
        print("=" * 60)

        regen_summary_path = review_log_dir / "regen_summary.json"
        regen_summary_path.write_text(json.dumps({
            "lectures_regenerated": len(results),
            "discarded_lectures": discarded,
            "per_lecture": results,
        }, indent=2))
        logger.info(f"Regen summary saved → {regen_summary_path}")


if __name__ == "__main__":
    main()
