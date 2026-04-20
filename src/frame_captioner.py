"""Generate text captions for video keyframes using BLIP base.

BLIP base (Salesforce/blip-image-captioning-base) is chosen over BLIP-2 because:
- No GPU required — runs on CPU in ~5-15s per frame
- Produces full natural-language captions (not zero-shot label matching)
- Small enough to load in a student environment (~400MB)
For GPU environments, swap model_name to 'Salesforce/blip-image-captioning-large'
or 'Salesforce/blip2-opt-2.7b' for richer captions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_processor = None
_model = None


def _load_model(device: str = "cpu"):
    global _processor, _model
    if _model is not None:
        return _processor, _model

    from transformers import BlipProcessor, BlipForConditionalGeneration

    model_name = "Salesforce/blip-image-captioning-base"
    logger.info(f"Loading {model_name} on {device}...")
    _processor = BlipProcessor.from_pretrained(model_name)
    _model = BlipForConditionalGeneration.from_pretrained(model_name).to(device)
    _model.eval()
    logger.info("Model loaded.")
    return _processor, _model


@dataclass
class FrameCaption:
    frame_id: str
    video_id: str
    time: float
    caption: str


def caption_frame(image_bgr: np.ndarray, frame_id: str, video_id: str,
                  time: float, device: str = "cpu") -> FrameCaption:
    """Generate a caption for a single BGR frame."""
    import torch

    processor, model = _load_model(device)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)

    inputs = processor(pil_image, return_tensors="pt").to(device)
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=64)
    caption = processor.decode(output_ids[0], skip_special_tokens=True)

    return FrameCaption(frame_id=frame_id, video_id=video_id, time=time, caption=caption)


def caption_frames(frames: list, device: str = "cpu") -> list[FrameCaption]:
    """Caption a list of Frame objects, logging progress."""
    results: list[FrameCaption] = []
    total = len(frames)
    for i, frame in enumerate(frames):
        fc = caption_frame(frame.image, frame.frame_id, frame.video_id, frame.time, device)
        results.append(fc)
        if (i + 1) % 10 == 0 or (i + 1) == total:
            mm, ss = divmod(int(frame.time), 60)
            logger.info(f"  [{i+1}/{total}] {frame.frame_id} @ {mm:02d}:{ss:02d} → {fc.caption[:60]}")
    return results
