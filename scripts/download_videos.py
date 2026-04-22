"""Download full video and .en.vtt caption files for all 60 corpus lectures."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("download_videos")

_PROJECT_ROOT = Path(__file__).parent.parent
_METADATA_FILE = _PROJECT_ROOT / "data" / "raw" / "metadata.json"
_VIDEOS_DIR = _PROJECT_ROOT / "data" / "raw" / "videos"


def _video_on_disk(video_id: str) -> Path | None:
    for ext in ("mp4", "mkv"):
        p = _VIDEOS_DIR / f"{video_id}.{ext}"
        if p.exists():
            return p
    return None


def _vtt_on_disk(video_id: str) -> Path | None:
    p = _VIDEOS_DIR / f"{video_id}.en.vtt"
    return p if p.exists() else None


def _already_downloaded(video_id: str) -> bool:
    return _video_on_disk(video_id) is not None and _vtt_on_disk(video_id) is not None


def _download(entry: dict) -> bool:
    video_id = entry["video_id"]
    url = entry["url"]
    output_template = str(_VIDEOS_DIR / f"{video_id}.%(ext)s")
    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-playlist",
        "-o", output_template,
        url,
    ]
    logger.info(f"Downloading {video_id} from {url}")
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"yt-dlp failed for {video_id}: {result.stderr.strip()}")
        return False
    if _video_on_disk(video_id) is None or _vtt_on_disk(video_id) is None:
        logger.error(f"yt-dlp exited 0 but expected files missing for {video_id}")
        return False
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Download lecture videos and VTT captions.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Download all 60 lectures.")
    group.add_argument("--video_id", metavar="ID", help="Download a single lecture by video_id.")
    args = parser.parse_args()

    metadata: list[dict] = json.loads(_METADATA_FILE.read_text())
    index = {entry["video_id"]: i for i, entry in enumerate(metadata)}

    if args.video_id:
        if args.video_id not in index:
            parser.error(f"video_id '{args.video_id}' not found in metadata.json")
        targets = [args.video_id]
    else:
        targets = [entry["video_id"] for entry in metadata]

    _VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    n_downloaded = n_skipped = n_failed = 0
    failed_ids: list[str] = []

    for video_id in targets:
        entry = metadata[index[video_id]]
        if _already_downloaded(video_id):
            logger.info(f"Skipping {video_id} (already on disk)")
            entry["downloaded"] = True
            n_skipped += 1
            continue
        success = _download(entry)
        if success:
            entry["downloaded"] = True
            n_downloaded += 1
        else:
            entry["downloaded"] = False
            n_failed += 1
            failed_ids.append(video_id)

    _METADATA_FILE.write_text(json.dumps(metadata, indent=2))

    print(f"Done. Downloaded: {n_downloaded}  Skipped: {n_skipped}  Failed: {n_failed}")
    if failed_ids:
        print("Failed video_ids:")
        for vid in failed_ids:
            print(f"  {vid}")


if __name__ == "__main__":
    main()
