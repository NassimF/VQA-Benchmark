"""Extract audio from all lecture videos as 16 kHz mono 16-bit PCM WAV.

Output: data/raw/audio/{video_id}.wav

Usage:
    python scripts/extract_audio.py --all
    python scripts/extract_audio.py --video_id mit_6046_lec10
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def extract_audio(video_path: Path, out_path: Path) -> None:
    """Extract audio from video_path and save as 16 kHz mono 16-bit PCM WAV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                  # drop video stream
        "-acodec", "pcm_s16le", # 16-bit PCM
        "-ar", "16000",         # 16 kHz sample rate
        "-ac", "1",             # mono
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {video_path.name}:\n{result.stderr[-500:]}")


def process(video_id: str, cfg) -> None:
    metadata = json.loads(cfg.data.metadata_file.read_text())
    entry = next((e for e in metadata if e["video_id"] == video_id), None)
    if entry is None:
        logger.error(f"video_id '{video_id}' not found in metadata.json")
        sys.exit(1)

    video_path = Path(entry["video_file"])
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        sys.exit(1)

    out_path = cfg.data.raw_dir / "audio" / f"{video_id}.wav"
    if out_path.exists():
        logger.info(f"Skipping {video_id} — already exists at {out_path}")
        return

    logger.info(f"Extracting audio: {video_path.name} → {out_path.name}")
    extract_audio(video_path, out_path)
    size_mb = out_path.stat().st_size / 1_048_576
    logger.info(f"  Done: {out_path} ({size_mb:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract 16 kHz mono WAV audio from lecture videos")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Single video ID to process")
    group.add_argument("--all", action="store_true", help="Process all videos in metadata.json")
    args = parser.parse_args()

    cfg = load_config()

    if args.all:
        metadata = json.loads(cfg.data.metadata_file.read_text())
        total = len(metadata)
        for i, entry in enumerate(metadata, 1):
            vid = entry["video_id"]
            out_path = cfg.data.raw_dir / "audio" / f"{vid}.wav"
            if out_path.exists():
                logger.info(f"[{i}/{total}] Skipping {vid} — already exists")
                continue
            video_path = Path(entry["video_file"])
            if not video_path.exists():
                logger.warning(f"[{i}/{total}] Video not found, skipping: {video_path}")
                continue
            logger.info(f"[{i}/{total}] {vid}")
            extract_audio(video_path, out_path)
            size_mb = out_path.stat().st_size / 1_048_576
            logger.info(f"  → {out_path} ({size_mb:.1f} MB)")
    else:
        process(args.video_id, cfg)


if __name__ == "__main__":
    main()
