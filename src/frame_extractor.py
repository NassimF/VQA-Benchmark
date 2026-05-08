"""Extract keyframes from a lecture video at fixed intervals.

Uses ffmpeg for extraction (handles all codecs including AV1/VP9/H.264).
Falls back to a temp-directory approach: ffmpeg writes JPEG files, we read them
with PIL, then clean up. This avoids cv2 codec compatibility issues entirely.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class Frame:
    frame_id: str
    video_id: str
    time: float        # seconds
    image: np.ndarray  # BGR, HxWx3


def _video_duration(video_path: Path) -> float:
    """Return video duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def extract_frames(video_path: Path, video_id: str, interval_seconds: float) -> list[Frame]:
    """Extract one frame every interval_seconds using ffmpeg."""
    duration = _video_duration(video_path)
    timestamps = [round(t, 2) for t in
                  [i * interval_seconds for i in range(int(duration / interval_seconds) + 1)]
                  if t < duration]

    frames: list[Frame] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        for index, t in enumerate(timestamps):
            out_path = tmp / f"frame_{index:04d}.jpg"
            subprocess.run(
                ["ffmpeg", "-threads", "1", "-ss", str(t), "-i", str(video_path),
                 "-frames:v", "1", "-threads", "1", "-q:v", "2", str(out_path)],
                capture_output=True,
            )
            if not out_path.exists():
                logger.warning(f"ffmpeg produced no frame at t={t}s for {video_id}")
                continue
            img_rgb = np.array(Image.open(out_path).convert("RGB"))
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            frames.append(Frame(
                frame_id=f"{video_id}_frame_{index:03d}",
                video_id=video_id,
                time=t,
                image=img_bgr,
            ))

    logger.info(f"{video_id}: extracted {len(frames)} frames at {interval_seconds}s intervals")
    return frames
