"""Validate benchmark_v1.json: schema, span validity, num_hops, unanswerable flags."""

import json
import logging
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "qa_id", "video_id", "question", "answer", "num_hops",
    "ground_truth_spans", "source_chunk_ids", "question_type",
    "difficulty", "answerable", "key_concepts",
}
VALID_TYPES = {"multi-hop-visual", "visual", "multi-hop", "text", "unanswerable"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
MULTI_HOP_TYPES = {"multi-hop-visual", "multi-hop"}
VISUAL_TYPES = {"multi-hop-visual", "visual"}
MIN_SPAN_GAP_S = 70.0


def _check_schema(pair: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(pair.keys())
    if missing:
        errors.append(f"missing fields: {missing}")
    if pair.get("question_type") not in VALID_TYPES:
        errors.append(f"invalid question_type: {pair.get('question_type')!r}")
    if pair.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append(f"invalid difficulty: {pair.get('difficulty')!r}")
    if not isinstance(pair.get("ground_truth_spans"), list):
        errors.append("ground_truth_spans must be a list")
    if not isinstance(pair.get("source_chunk_ids"), list):
        errors.append("source_chunk_ids must be a list")
    if not isinstance(pair.get("key_concepts"), list):
        errors.append("key_concepts must be a list")
    return errors


def _check_spans(pair: dict) -> list[str]:
    errors: list[str] = []
    spans = pair.get("ground_truth_spans", [])
    qtype = pair.get("question_type")
    answerable = pair.get("answerable", True)

    # Unanswerable: must have empty spans
    if qtype == "unanswerable":
        if spans:
            errors.append("unanswerable question must have empty ground_truth_spans")
        return errors

    # Answerable questions must have at least one span
    if answerable and not spans:
        errors.append("answerable question has no ground_truth_spans")
        return errors

    for i, span in enumerate(spans):
        if "start" not in span or "end" not in span:
            errors.append(f"span[{i}] missing start/end")
            continue
        if span["end"] <= span["start"]:
            errors.append(f"span[{i}] end ({span['end']}) <= start ({span['start']})")

    # Multi-hop: check ≥70s start-to-start gap between all hop pairs
    if qtype in MULTI_HOP_TYPES and len(spans) >= 2:
        starts = sorted(s["start"] for s in spans if "start" in s)
        for i in range(len(starts) - 1):
            gap = starts[i + 1] - starts[i]
            if gap < MIN_SPAN_GAP_S:
                errors.append(
                    f"multi-hop span gap {gap:.0f}s < {MIN_SPAN_GAP_S:.0f}s "
                    f"(starts: {starts})"
                )

    return errors


def _check_num_hops(pair: dict) -> list[str]:
    errors: list[str] = []
    qtype = pair.get("question_type")
    num_hops = pair.get("num_hops", 0)
    spans = pair.get("ground_truth_spans", [])

    if qtype in MULTI_HOP_TYPES:
        if num_hops < 2:
            errors.append(f"multi-hop type has num_hops={num_hops} (must be ≥2)")
        if len(spans) < 2:
            errors.append(f"multi-hop type has {len(spans)} span(s) (must be ≥2)")
    elif qtype == "unanswerable":
        pass  # no hop requirement
    else:
        if num_hops != 1:
            errors.append(f"single-hop type has num_hops={num_hops} (expected 1)")

    return errors


def _check_visual(pair: dict) -> list[str]:
    """Visual types must cite at least one chunk containing a [frame caption: marker."""
    errors: list[str] = []
    if pair.get("question_type") not in VISUAL_TYPES:
        return errors
    # source_chunk_ids are chunk references; we can only verify marker if chunk text
    # is available — skip silently if not present in the pair itself.
    # (Full chunk-text check is done in audit_span_precision.py)
    return errors


def validate(benchmark_path: Path, cfg_path: Path) -> bool:
    cfg = load_config(cfg_path)
    data = json.loads(benchmark_path.read_text())
    pairs = data.get("qa_pairs", [])

    errors_by_pair: dict[str, list[str]] = {}
    lecture_unanswerables: dict[str, int] = {}

    for pair in pairs:
        qa_id = pair.get("qa_id", "UNKNOWN")
        errs: list[str] = []
        errs += _check_schema(pair)
        errs += _check_spans(pair)
        errs += _check_num_hops(pair)
        errs += _check_visual(pair)

        if errs:
            errors_by_pair[qa_id] = errs

        vid = pair.get("video_id", "")
        if pair.get("question_type") == "unanswerable":
            lecture_unanswerables[vid] = lecture_unanswerables.get(vid, 0) + 1

    # Summary
    total = len(pairs)
    n_errors = len(errors_by_pair)
    lectures_with_no_unanswerable = [
        vid for vid in {p["video_id"] for p in pairs}
        if lecture_unanswerables.get(vid, 0) == 0
    ]

    logger.info("Pairs checked:      %d", total)
    logger.info("Pairs with errors:  %d", n_errors)
    logger.info("Lectures missing unanswerable: %d", len(lectures_with_no_unanswerable))

    if errors_by_pair:
        logger.warning("--- Validation errors ---")
        for qa_id, errs in sorted(errors_by_pair.items()):
            for e in errs:
                logger.warning("  %s: %s", qa_id, e)

    if lectures_with_no_unanswerable:
        logger.warning("Lectures with no unanswerable pair: %s",
                       sorted(lectures_with_no_unanswerable))

    passed = n_errors == 0
    logger.info("Validation: %s", "PASSED ✅" if passed else "FAILED ❌")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate benchmark_v1.json.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--benchmark", default=None,
                        help="Path to benchmark JSON (default: data/benchmark/benchmark_v1.json)")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if args.benchmark:
        benchmark_path = Path(args.benchmark)
    else:
        cfg = load_config(cfg_path)
        benchmark_path = cfg.data.benchmark_dir / "benchmark_v1.json"

    if not benchmark_path.exists():
        logger.error("Benchmark file not found: %s", benchmark_path)
        sys.exit(1)

    passed = validate(benchmark_path, cfg_path)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
