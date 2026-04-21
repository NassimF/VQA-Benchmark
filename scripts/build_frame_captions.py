"""CLI: extract frames + generate Qwen2-VL captions → data/frame_captions/{video_id}_frame_captions.json
Also writes augmented chunks (transcript + nearest caption) to data/chunks/{video_id}_chunks_augmented.json

Usage:
    python scripts/build_frame_captions.py --video_id mit_6046_lec10
    python scripts/build_frame_captions.py --all
    python scripts/build_frame_captions.py --all --device cuda
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.frame_extractor import extract_frames
from src.frame_captioner import caption_frames

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _get_video_path(video_id: str, cfg) -> Path:
    """Look up video file path from metadata.json (supports .mp4 and .mkv)."""
    metadata = json.loads(cfg.data.metadata_file.read_text())
    for entry in metadata:
        if entry["video_id"] == video_id:
            return Path(entry["video_file"])
    return cfg.data.videos_dir / f"{video_id}.mp4"


def assign_captions_to_chunks(chunks: list[dict], captions: list[dict]) -> list[dict]:
    """Append the nearest frame caption to each chunk's text."""
    augmented = []
    for chunk in chunks:
        chunk_mid = (chunk["start_time"] + chunk["end_time"]) / 2
        nearest = min(captions, key=lambda c: abs(c["time"] - chunk_mid))
        augmented.append({
            **chunk,
            "text": f"{chunk['text']} [frame caption: {nearest['caption']}]",
            "frame_caption": nearest["caption"],
            "frame_time": nearest["time"],
        })
    return augmented


def process(video_id: str, cfg, device: str) -> None:
    video_path = _get_video_path(video_id, cfg)
    if not video_path.exists():
        logging.error(f"Video not found: {video_path}")
        sys.exit(1)

    # --- Frame extraction ---
    logging.info(f"Extracting frames from {video_id} ({video_path.name})...")
    frames = extract_frames(video_path, video_id, cfg.frame_extraction.interval_seconds)

    # --- Captioning ---
    logging.info(f"Captioning {len(frames)} frames on {device}...")
    captions = caption_frames(frames, device=device,
                              model_name=cfg.frame_captioner.model,
                              max_new_tokens=cfg.frame_captioner.max_new_tokens)

    # --- Save frame captions ---
    caption_records = [
        {"frame_id": fc.frame_id, "video_id": fc.video_id,
         "time": fc.time, "caption": fc.caption}
        for fc in captions
    ]
    out_captions = cfg.data.frame_captions_dir / f"{video_id}_frame_captions.json"
    out_captions.parent.mkdir(parents=True, exist_ok=True)
    out_captions.write_text(json.dumps(caption_records, indent=2, ensure_ascii=False))
    print(f"{video_id}: saved {len(caption_records)} frame captions → {out_captions}")

    # --- Build augmented chunks (transcript + nearest caption) ---
    chunks_path = cfg.data.chunks_dir / f"{video_id}_chunks.json"
    if not chunks_path.exists():
        logging.warning(f"Chunks not found: {chunks_path} — skipping augmented chunks")
        return

    chunks = json.loads(chunks_path.read_text())
    augmented = assign_captions_to_chunks(chunks, caption_records)
    out_augmented = cfg.data.chunks_dir / f"{video_id}_chunks_augmented.json"
    out_augmented.write_text(json.dumps(augmented, indent=2, ensure_ascii=False))
    print(f"{video_id}: saved augmented chunks → {out_augmented}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract frames and generate Qwen2-VL captions")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video_id", help="Single video ID to process")
    group.add_argument("--all", action="store_true", help="Process all videos in metadata.json")
    parser.add_argument("--device", default="cpu", help="Torch device: cpu or cuda (default: cpu)")
    args = parser.parse_args()

    cfg = load_config()

    if args.all:
        metadata = json.loads(cfg.data.metadata_file.read_text())
        for entry in metadata:
            process(entry["video_id"], cfg, args.device)
    else:
        process(args.video_id, cfg, args.device)


if __name__ == "__main__":
    main()
