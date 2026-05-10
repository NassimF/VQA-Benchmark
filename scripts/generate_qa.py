"""Generate draft QA pairs for benchmark lectures.

CLI:
  python scripts/generate_qa.py --video_id mit_6046_lec10
  python scripts/generate_qa.py --all
  python scripts/generate_qa.py --all --overwrite
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
from src.qa_generator import generate_qa

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_all_video_ids(cfg) -> list[str]:
    metadata = json.loads(cfg.data.metadata_file.read_text())
    return [entry["video_id"] for entry in metadata]


def run_one(video_id: str, out_dir: Path, overwrite: bool, cfg) -> bool:
    """Generate QA for one lecture. Returns True if generated, False if skipped."""
    out_path = out_dir / f"{video_id}_qa_raw.json"
    if out_path.exists() and not overwrite:
        logger.info(f"Skipping {video_id} (already exists)")
        return False

    items = generate_qa(video_id, cfg)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info(f"{video_id}: saved {len(items)} QA pairs → {out_path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate draft QA pairs for benchmark lectures.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Generate for a single lecture")
    group.add_argument("--all", action="store_true", help="Generate for all 60 lectures")
    parser.add_argument("--overwrite", action="store_true", help="Re-generate even if file exists")
    args = parser.parse_args()

    cfg = load_config()
    out_dir = cfg.data.qa_pairs_dir / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.video_id:
        video_ids = [args.video_id]
    else:
        video_ids = load_all_video_ids(cfg)
        logger.info(f"Loaded {len(video_ids)} video IDs from metadata")

    generated = skipped = errors = 0
    for i, video_id in enumerate(video_ids):
        made_api_call = False
        try:
            ok = run_one(video_id, out_dir, args.overwrite, cfg)
            if ok:
                generated += 1
                made_api_call = True
            else:
                skipped += 1
        except Exception as exc:
            logger.error(f"{video_id}: FAILED — {exc}")
            errors += 1
            made_api_call = True
        # Wait after any real API call to respect the 30k token/min rate limit.
        if made_api_call and i < len(video_ids) - 1:
            time.sleep(65)

    logger.info(f"Done: {generated} generated, {skipped} skipped, {errors} errors")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
