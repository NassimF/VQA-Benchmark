"""CLI: parse VTT captions for one or all lectures → data/transcripts/{video_id}.json

Usage:
    python scripts/parse_vtt.py --video_id mit_6046_lec10
    python scripts/parse_vtt.py --all
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.transcriber import vtt_to_transcript_json

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def process(video_id: str, cfg) -> None:
    vtt_path = cfg.data.videos_dir / f"{video_id}.en.vtt"
    if not vtt_path.exists():
        logging.error(f"VTT not found: {vtt_path}")
        sys.exit(1)

    out_path = cfg.data.transcripts_dir / f"{video_id}.json"
    transcript = vtt_to_transcript_json(video_id, vtt_path, out_path)

    total_duration = transcript["segments"][-1]["end"] if transcript["segments"] else 0
    print(f"{video_id}: {len(transcript['segments'])} segments, "
          f"duration {total_duration / 60:.1f} min → {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse VTT captions to transcript JSON")
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
