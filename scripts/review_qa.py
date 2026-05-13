"""Phase 7.3 QA review script.

Usage:
    python scripts/review_qa.py --video_id mit_18065_lec06
    python scripts/review_qa.py --all
    python scripts/review_qa.py --all --stats_only   # print summary of existing logs
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.qa_reviewer import QAReviewer, ReviewResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_chunks(chunks_dir: Path, video_id: str) -> dict[str, str]:
    """Load augmented chunk text for a lecture."""
    path = chunks_dir / f"{video_id}_chunks_augmented.json"
    if not path.exists():
        logger.warning(f"Augmented chunks not found for {video_id}, falling back to base chunks")
        path = chunks_dir / f"{video_id}_chunks.json"
    with path.open() as f:
        chunks = json.load(f)
    return {c["chunk_id"]: c["text"] for c in chunks}


def review_lecture(
    video_id: str,
    raw_dir: Path,
    chunks_dir: Path,
    reviewed_dir: Path,
    review_log_dir: Path,
    reviewer: QAReviewer,
) -> dict:
    """Review all QA pairs for one lecture. Returns per-lecture stats dict."""
    raw_path = raw_dir / f"{video_id}_qa_raw.json"
    if not raw_path.exists():
        logger.error(f"Raw QA file not found: {raw_path}")
        return {}

    with raw_path.open() as f:
        qa_pairs = json.load(f)

    chunks = load_chunks(chunks_dir, video_id)
    accepted, all_log = [], []

    for qa in qa_pairs:
        result = reviewer.review_qa_pair(qa, chunks)
        log_entry = _result_to_log(qa, result)
        all_log.append(log_entry)

        if result.overall == "ACCEPT":
            accepted.append(qa)
        else:
            logger.info(f"  REJECT {qa['qa_id']}: {result.rejection_reason}")

    # Write outputs
    reviewed_dir.mkdir(parents=True, exist_ok=True)
    review_log_dir.mkdir(parents=True, exist_ok=True)

    with (reviewed_dir / f"{video_id}_qa_reviewed.json").open("w") as f:
        json.dump(accepted, f, indent=2)

    with (review_log_dir / f"{video_id}_review_log.json").open("w") as f:
        json.dump(all_log, f, indent=2)

    stats = _compute_lecture_stats(video_id, qa_pairs, accepted, all_log)
    _print_lecture_summary(stats)
    return stats


def _result_to_log(qa: dict, result: ReviewResult) -> dict:
    return {
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


def _compute_lecture_stats(
    video_id: str, all_qa: list[dict], accepted: list[dict], log: list[dict]
) -> dict:
    rejected = [e for e in log if e["overall"] == "REJECT"]
    breakdown: dict[str, int] = defaultdict(int)
    type_breakdown: dict[str, dict] = defaultdict(lambda: {"total": 0, "accepted": 0})

    for entry in log:
        qt = entry.get("question_type", "unknown")
        type_breakdown[qt]["total"] += 1
        if entry["overall"] == "ACCEPT":
            type_breakdown[qt]["accepted"] += 1
        else:
            reason = entry.get("rejection_reason", "unknown")
            breakdown[reason] += 1

    visual_count = sum(
        1 for qa in accepted
        if qa.get("question_type") in ("multi-hop-visual", "visual")
    )
    visual_pct = visual_count / max(len(accepted), 1) * 100

    return {
        "video_id": video_id,
        "total_drafted": len(all_qa),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "visual_accepted": visual_count,
        "visual_pct": round(visual_pct, 1),
        "rejection_breakdown": dict(breakdown),
        "type_breakdown": {k: dict(v) for k, v in type_breakdown.items()},
    }


def _print_lecture_summary(stats: dict) -> None:
    vid = stats.get("video_id", "?")
    acc = stats.get("accepted", 0)
    rej = stats.get("rejected", 0)
    vpct = stats.get("visual_pct", 0)
    bd = stats.get("rejection_breakdown", {})
    logger.info(
        f"{vid}: accepted={acc}, rejected={rej}, visual={vpct}% | "
        f"rejections: {bd}"
    )


def print_corpus_summary(all_stats: list[dict], cfg_floor: int, cfg_discard: int) -> dict:
    """Print and return corpus-wide statistics report."""
    total_accepted = sum(s["accepted"] for s in all_stats)
    total_rejected = sum(s["rejected"] for s in all_stats)
    at_floor = [s for s in all_stats if cfg_floor <= s["accepted"] < 12]
    at_risk = [s for s in all_stats if s["accepted"] < cfg_floor]
    discard_risk = [s for s in all_stats if s["accepted"] < cfg_discard]

    corpus_breakdown: dict[str, int] = defaultdict(int)
    for s in all_stats:
        for reason, count in s.get("rejection_breakdown", {}).items():
            corpus_breakdown[reason] += count

    print("\n" + "=" * 60)
    print("CORPUS REVIEW SUMMARY")
    print("=" * 60)
    print(f"Lectures reviewed:     {len(all_stats)}")
    print(f"Total accepted:        {total_accepted}")
    print(f"Total rejected:        {total_rejected}")
    print(f"Overall rejection rate:{total_rejected / max(total_accepted + total_rejected, 1) * 100:.1f}%")
    print()
    print("Rejection reasons (corpus-wide):")
    for reason, count in sorted(corpus_breakdown.items(), key=lambda x: -x[1]):
        print(f"  {reason}: {count}")
    print()
    print(f"Lectures at floor ({cfg_floor}–11 accepted): {len(at_floor)}")
    if at_floor:
        print("  " + ", ".join(s["video_id"] for s in at_floor))
    print(f"Lectures below floor (<{cfg_floor} accepted): {len(at_risk)}")
    if at_risk:
        print("  " + ", ".join(f"{s['video_id']}({s['accepted']})" for s in at_risk))
    print(f"Discard risk (<{cfg_discard} accepted):        {len(discard_risk)}")
    if discard_risk:
        print("  " + ", ".join(f"{s['video_id']}({s['accepted']})" for s in discard_risk))
    print()
    kc = corpus_breakdown.get("c1_knowledge_conflict", 0)
    print(f"Knowledge-conflict discards (C1 GPT-4o disagreement): {kc}")
    print("=" * 60)

    summary = {
        "lectures_reviewed": len(all_stats),
        "total_accepted": total_accepted,
        "total_rejected": total_rejected,
        "rejection_breakdown": dict(corpus_breakdown),
        "lectures_at_floor": [s["video_id"] for s in at_floor],
        "lectures_below_floor": [s["video_id"] for s in at_risk],
        "lectures_discard_risk": [s["video_id"] for s in discard_risk],
        "c1_knowledge_conflict_count": kc,
        "per_lecture": all_stats,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 7.3 QA review pass")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Review a single lecture")
    group.add_argument("--all", action="store_true", help="Review all lectures")
    parser.add_argument("--stats_only", action="store_true",
                        help="Print summary from existing review logs without re-running")
    args = parser.parse_args()

    cfg = load_config()
    raw_dir = cfg.data.qa_pairs_dir / "raw"
    reviewed_dir = cfg.data.qa_pairs_dir / "reviewed"
    review_log_dir = cfg.data.qa_pairs_dir / "review_log"

    if args.stats_only:
        _print_stats_from_logs(review_log_dir, cfg)
        return

    reviewer = QAReviewer(cfg.qa_review)

    if args.video_id:
        stats = review_lecture(
            args.video_id, raw_dir, cfg.data.chunks_dir,
            reviewed_dir, review_log_dir, reviewer,
        )
        all_stats = [stats] if stats else []
    else:
        raw_files = sorted(raw_dir.glob("*_qa_raw.json"))
        video_ids = [f.stem.replace("_qa_raw", "") for f in raw_files]
        logger.info(f"Reviewing {len(video_ids)} lectures...")
        all_stats = []
        for vid in video_ids:
            logger.info(f"--- {vid} ---")
            s = review_lecture(vid, raw_dir, cfg.data.chunks_dir, reviewed_dir, review_log_dir, reviewer)
            if s:
                all_stats.append(s)

    if all_stats:
        summary = print_corpus_summary(all_stats, cfg.qa_review.floor_accepted, cfg.qa_review.discard_threshold)
        review_log_dir.mkdir(parents=True, exist_ok=True)
        with (review_log_dir / "review_summary.json").open("w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {review_log_dir / 'review_summary.json'}")


def _print_stats_from_logs(review_log_dir: Path, cfg) -> None:
    log_files = sorted(review_log_dir.glob("*_review_log.json"))
    if not log_files:
        print("No review logs found.")
        return
    all_stats = []
    for lf in log_files:
        video_id = lf.stem.replace("_review_log", "")
        with lf.open() as f:
            log = json.load(f)
        accepted = [e for e in log if e["overall"] == "ACCEPT"]
        all_stats.append(_compute_lecture_stats(video_id, log, accepted, log))
    print_corpus_summary(all_stats, cfg.qa_review.floor_accepted, cfg.qa_review.discard_threshold)


if __name__ == "__main__":
    main()
