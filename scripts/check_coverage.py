"""Post-regeneration coverage check and zero-pair retry.

Two-pass safety net after regeneration completes:

Pass 1 — Zero-pair retry:
  Any lecture with 0 accepted pairs gets one fresh regeneration attempt.
  These lectures never produced a valid batch so this does not violate D8's
  1-retry rule (which applies to lectures that had at least some accepted pairs).

Pass 2 — Total count check:
  After zero-pair retries, sum accepted pairs across all 60 lectures.
  If total < MIN_TOTAL (500), print a ranked list of lowest-count lectures
  and ask the user whether to run another regeneration pass.
  Does NOT auto-retry beyond Pass 1 — policy decision stays with the user.

Usage:
    python scripts/check_coverage.py --check     # report only, no retries
    python scripts/check_coverage.py --fix        # run zero-pair retries, then report
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.qa_reviewer import QAReviewer
from scripts.regenerate_qa import regenerate_qa, run_one

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MIN_TOTAL = 500          # minimum accepted pairs for a defensible benchmark
MIN_VISUAL = 300         # minimum visual-dependent pairs for Config 1 vs Config 2 comparison
CRITICAL_THRESHOLD = 3   # lectures with ≤ this many pairs are flagged for manual inspection

_VISUAL_TYPES = {"multi-hop-visual", "visual"}


def load_lecture_counts(reviewed_dir: Path, video_ids: list[str]) -> dict[str, dict]:
    """Return per-lecture accepted counts and visual counts."""
    counts: dict[str, dict] = {}
    for vid in video_ids:
        path = reviewed_dir / f"{vid}_qa_reviewed.json"
        if not path.exists():
            counts[vid] = {"total": 0, "visual": 0, "pairs": []}
            continue
        pairs = json.loads(path.read_text())
        visual = sum(1 for p in pairs if p.get("question_type") in _VISUAL_TYPES)
        counts[vid] = {"total": len(pairs), "visual": visual, "pairs": pairs}
    return counts


def print_coverage_report(counts: dict[str, dict]) -> tuple[int, int]:
    """Print coverage report. Returns (total_accepted, total_visual)."""
    zero = [v for v, c in counts.items() if c["total"] == 0]
    critical = [v for v, c in counts.items() if 1 <= c["total"] <= CRITICAL_THRESHOLD]
    below_floor = [v for v, c in counts.items() if CRITICAL_THRESHOLD < c["total"] < 10]
    at_floor = [v for v, c in counts.items() if 10 <= c["total"] < 12]
    at_target = [v for v, c in counts.items() if c["total"] >= 12]

    total_accepted = sum(c["total"] for c in counts.values())
    total_visual = sum(c["visual"] for c in counts.values())

    print("\n" + "=" * 60)
    print("COVERAGE REPORT")
    print("=" * 60)
    print(f"Total lectures:        {len(counts)}")
    print(f"Total accepted pairs:  {total_accepted}  (minimum: {MIN_TOTAL})")
    print(f"Total visual pairs:    {total_visual}  (minimum: {MIN_VISUAL})")
    print()

    status = "✅ PASS" if total_accepted >= MIN_TOTAL else "❌ FAIL"
    vstatus = "✅ PASS" if total_visual >= MIN_VISUAL else "❌ FAIL"
    print(f"Total count check:     {status}")
    print(f"Visual count check:    {vstatus}")
    print()

    print(f"Zero pairs (must fix):          {len(zero)}")
    if zero:
        print("  " + ", ".join(zero))

    print(f"Critical (1–{CRITICAL_THRESHOLD} pairs, flag): {len(critical)}")
    if critical:
        for v in critical:
            print(f"  {v}: {counts[v]['total']} pairs")

    print(f"Below floor (4–9 pairs):        {len(below_floor)}")
    if below_floor:
        for v in below_floor:
            print(f"  {v}: {counts[v]['total']} pairs")

    print(f"At floor (10–11 pairs):         {len(at_floor)}")
    print(f"At target (≥12 pairs):          {len(at_target)}")
    print("=" * 60)

    if total_accepted < MIN_TOTAL:
        shortfall = MIN_TOTAL - total_accepted
        print(f"\n⚠️  SHORTFALL: {shortfall} pairs needed to reach {MIN_TOTAL}.")
        print("Lowest-count lectures (candidates for another regen pass):")
        ranked = sorted(counts.items(), key=lambda x: x[1]["total"])
        for v, c in ranked[:10]:
            if c["total"] < 12:
                print(f"  {v}: {c['total']} pairs")
        print("\nTo run another pass on these lectures, use:")
        print("  python scripts/regenerate_qa.py --video_id <id>")
        print("This is a policy decision — not run automatically.")

    return total_accepted, total_visual


def run_zero_pair_retries(
    zero_lectures: list[str],
    cfg,
    reviewed_dir: Path,
    raw_dir: Path,
    review_log_dir: Path,
    reviewer: QAReviewer,
) -> None:
    """Run one fresh regeneration pass for each zero-pair lecture."""
    if not zero_lectures:
        logger.info("No zero-pair lectures — skipping Pass 1.")
        return

    logger.info(f"Pass 1: {len(zero_lectures)} zero-pair lecture(s) to retry.")
    for i, video_id in enumerate(zero_lectures):
        logger.info(f"--- Zero-pair retry: {video_id} ({i + 1}/{len(zero_lectures)}) ---")

        # Build a synthetic review log that triggers all three constraint blocks
        synthetic_log = [
            {
                "overall": "REJECT",
                "criterion_1": {"result": "FAIL", "reason": "no accepted pairs"},
                "criterion_2": {"result": "FAIL", "reason": "no accepted pairs"},
                "criterion_3": {"result": "FAIL", "reason": "no accepted pairs"},
            }
        ] * 15

        run_one(
            video_id=video_id,
            cfg=cfg,
            raw_dir=raw_dir,
            reviewed_dir=reviewed_dir,
            review_log_dir=review_log_dir,
            reviewer=reviewer,
            dry_run=False,
        )

        if i < len(zero_lectures) - 1:
            time.sleep(65)


def main() -> None:
    parser = argparse.ArgumentParser(description="Post-regeneration coverage check")
    parser.add_argument("--check", action="store_true",
                        help="Report only — do not run any retries")
    parser.add_argument("--fix", action="store_true",
                        help="Run zero-pair retries, then report")
    args = parser.parse_args()

    if not args.check and not args.fix:
        parser.print_help()
        sys.exit(1)

    cfg = load_config()
    reviewed_dir = cfg.data.qa_pairs_dir / "reviewed"
    raw_dir = cfg.data.qa_pairs_dir / "raw"
    review_log_dir = cfg.data.qa_pairs_dir / "review_log"

    metadata = json.loads(cfg.data.metadata_file.read_text())
    video_ids = [e["video_id"] for e in metadata]

    counts = load_lecture_counts(reviewed_dir, video_ids)
    zero_lectures = [v for v, c in counts.items() if c["total"] == 0]

    if args.fix and zero_lectures:
        reviewer = QAReviewer(cfg.qa_review)
        run_zero_pair_retries(zero_lectures, cfg, reviewed_dir, raw_dir,
                              review_log_dir, reviewer)
        # Reload counts after retries
        counts = load_lecture_counts(reviewed_dir, video_ids)

    total, visual = print_coverage_report(counts)

    if total < MIN_TOTAL or visual < MIN_VISUAL or zero_lectures:
        sys.exit(1)  # non-zero exit so CI can catch failures


if __name__ == "__main__":
    main()
