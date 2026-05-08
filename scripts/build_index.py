"""Ingest chunk files into ChromaDB collections.

CLI:
  python scripts/build_index.py --all [--mode both] [--rebuild]
  python scripts/build_index.py --video_id mit_6046_lec10 [--mode both] [--rebuild]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODES = ("transcript_only", "transcript_plus_frames")


def load_all_video_ids(cfg) -> list[str]:
    metadata = json.loads(cfg.data.metadata_file.read_text())
    return [entry["video_id"] for entry in metadata]


def ingest(video_ids: list[str], mode: str, rebuild: bool) -> tuple[int, int]:
    """Ingest video_ids into one collection. Returns (videos_added, chunks_added)."""
    retriever = Retriever(mode=mode)  # type: ignore[arg-type]
    videos_added = 0
    chunks_added = 0
    for video_id in video_ids:
        added = retriever.build([video_id], rebuild=rebuild)
        if added > 0:
            videos_added += 1
            chunks_added += added
    return videos_added, chunks_added


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ChromaDB index from chunk files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Ingest all 60 lectures.")
    group.add_argument("--video_id", metavar="ID", help="Ingest a single lecture by video_id.")
    parser.add_argument(
        "--mode",
        choices=["transcript_only", "transcript_plus_frames", "both"],
        default="both",
        help="Which collection(s) to populate (default: both).",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force re-ingestion even if chunks already exist in the collection.",
    )
    args = parser.parse_args()

    cfg = load_config()

    if args.all:
        video_ids = load_all_video_ids(cfg)
        logger.info(f"Targeting all {len(video_ids)} lectures.")
    else:
        video_ids = [args.video_id]
        logger.info(f"Targeting single lecture: {args.video_id}")

    modes = MODES if args.mode == "both" else (args.mode,)

    total_videos = 0
    total_chunks = 0
    for mode in modes:
        logger.info(f"--- Collection: {mode} ---")
        videos_added, chunks_added = ingest(video_ids, mode, args.rebuild)
        total_videos += videos_added
        total_chunks += chunks_added
        print(f"[{mode}] {videos_added} video(s) ingested, {chunks_added} chunks added.")

    print(f"\nDone. {total_videos} video-collection pair(s) ingested, {total_chunks} total chunks.")


if __name__ == "__main__":
    main()
