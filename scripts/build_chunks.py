"""CLI: chunk transcripts for one or all lectures → data/chunks/{video_id}_chunks.json

Usage:
    python scripts/build_chunks.py --video_id mit_6046_lec10
    python scripts/build_chunks.py --all
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.chunker import chunk_transcript

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def process(video_id: str, cfg) -> None:
    transcript_path = cfg.data.transcripts_dir / f"{video_id}.json"
    if not transcript_path.exists():
        logging.error(f"Transcript not found: {transcript_path}")
        sys.exit(1)

    out_path = cfg.data.chunks_dir / f"{video_id}_chunks.json"
    records = chunk_transcript(transcript_path, out_path, cfg.chunking)

    first, last = records[0], records[-1]
    print(
        f"{video_id}: {len(records)} chunks  "
        f"| window={cfg.chunking.window_seconds}s  "
        f"| stride={cfg.chunking.stride_seconds}s  "
        f"| first=[{first['start_time']:.0f}s–{first['end_time']:.0f}s]  "
        f"| last=[{last['start_time']:.0f}s–{last['end_time']:.0f}s]"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build overlapping transcript chunks")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Single video ID to process")
    group.add_argument("--all", action="store_true", help="Process all videos in metadata.json")
    args = parser.parse_args()

    cfg = load_config()

    if args.all:
        metadata = json.loads(cfg.data.metadata_file.read_text())
        for entry in metadata:
            process(entry["video_id"], cfg)
    else:
        process(args.video_id, cfg)


if __name__ == "__main__":
    main()
