"""Merge all reviewed QA JSON files into data/benchmark/benchmark_v1.json."""

import json
import logging
import argparse
from pathlib import Path
from datetime import date

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

VISUAL_TYPES = {"multi-hop-visual", "visual"}


def load_reviewed_pairs(reviewed_dir: Path) -> list[dict]:
    pairs: list[dict] = []
    missing_fields: list[str] = []

    for f in sorted(reviewed_dir.glob("*_qa_reviewed.json")):
        raw = json.loads(f.read_text())
        lecture_pairs = raw if isinstance(raw, list) else raw.get("qa_pairs", [])

        for p in lecture_pairs:
            missing = REQUIRED_FIELDS - set(p.keys())
            if missing:
                missing_fields.append(f"{p.get('qa_id', f.stem)}: missing {missing}")
                continue
            pairs.append(p)

    if missing_fields:
        for msg in missing_fields:
            logger.warning("Skipped — %s", msg)

    return pairs


def build_manifest(pairs: list[dict]) -> dict:
    video_ids = sorted({p["video_id"] for p in pairs})
    visual = [p for p in pairs if p["question_type"] in VISUAL_TYPES]
    multi_hop = [p for p in pairs if p["num_hops"] >= 2]
    unanswerable = [p for p in pairs if not p.get("answerable", True)]

    by_type: dict[str, int] = {}
    for p in pairs:
        by_type[p["question_type"]] = by_type.get(p["question_type"], 0) + 1

    return {
        "version": "1.0",
        "build_date": date.today().isoformat(),
        "total_pairs": len(pairs),
        "total_lectures": len(video_ids),
        "visual_pairs": len(visual),
        "visual_pct": round(100 * len(visual) / len(pairs), 1) if pairs else 0,
        "multi_hop_pairs": len(multi_hop),
        "unanswerable_pairs": len(unanswerable),
        "by_question_type": by_type,
        "lectures": video_ids,
    }


def main(cfg_path: str = "config.yaml", dry_run: bool = False) -> None:
    cfg = load_config(Path(cfg_path))
    reviewed_dir = cfg.data.qa_pairs_dir / "reviewed"
    benchmark_dir = cfg.data.benchmark_dir
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    out_path = benchmark_dir / "benchmark_v1.json"

    logger.info("Loading reviewed pairs from %s", reviewed_dir)
    pairs = load_reviewed_pairs(reviewed_dir)
    manifest = build_manifest(pairs)

    logger.info("Total pairs:    %d", manifest["total_pairs"])
    logger.info("Total lectures: %d", manifest["total_lectures"])
    logger.info("Visual pairs:   %d (%.1f%%)", manifest["visual_pairs"], manifest["visual_pct"])
    logger.info("Multi-hop:      %d", manifest["multi_hop_pairs"])
    logger.info("Unanswerable:   %d", manifest["unanswerable_pairs"])
    logger.info("By type:        %s", manifest["by_question_type"])

    if dry_run:
        logger.info("Dry run — not writing output.")
        return

    output = {"manifest": manifest, "qa_pairs": pairs}
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info("Written → %s", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build benchmark_v1.json from reviewed QA files.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry_run", action="store_true", help="Report stats without writing output.")
    args = parser.parse_args()
    main(cfg_path=args.config, dry_run=args.dry_run)
