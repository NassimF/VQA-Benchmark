"""Generate text captions for video keyframes using Qwen2-VL-7B-Instruct."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)

_PROMPT = (
    "Describe this lecture slide or whiteboard frame in detail. "
    "Include all visible text, equations, diagrams, and labels. "
    "Be specific — this caption will be used for academic retrieval."
)

_processor = None
_model = None
_loaded_model_name: str | None = None


def _load_model(model_name: str, device: str):
    global _processor, _model, _loaded_model_name
    if _model is not None and _loaded_model_name == model_name:
        return _processor, _model

    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

    logger.info(f"Loading {model_name} on {device}...")
    _model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
    ).to(device)
    _processor = AutoProcessor.from_pretrained(model_name)
    _model.eval()
    _loaded_model_name = model_name
    logger.info("Model loaded.")
    return _processor, _model


@dataclass
class FrameCaption:
    frame_id: str
    video_id: str
    time: float
    caption: str


def caption_frame(image_bgr: np.ndarray, frame_id: str, video_id: str,
                  time: float, device: str = "cuda",
                  model_name: str = "Qwen/Qwen2-VL-7B-Instruct",
                  max_new_tokens: int = 128) -> FrameCaption:
    """Generate a caption for a single BGR frame."""
    from qwen_vl_utils import process_vision_info

    processor, model = _load_model(model_name, device)

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)

    messages = [{"role": "user", "content": [
        {"type": "image", "image": pil_image},
        {"type": "text", "text": _PROMPT},
    ]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)

    generated = output_ids[:, inputs["input_ids"].shape[1]:]
    caption = processor.batch_decode(generated, skip_special_tokens=True)[0].strip()

    return FrameCaption(frame_id=frame_id, video_id=video_id, time=time, caption=caption)


def caption_frames(frames: list, device: str = "cuda",
                   model_name: str = "Qwen/Qwen2-VL-7B-Instruct",
                   max_new_tokens: int = 128) -> list[FrameCaption]:
    """Caption a list of Frame objects, logging progress."""
    results: list[FrameCaption] = []
    total = len(frames)
    for i, frame in enumerate(frames):
        fc = caption_frame(frame.image, frame.frame_id, frame.video_id, frame.time,
                           device, model_name, max_new_tokens)
        results.append(fc)
        if (i + 1) % 10 == 0 or (i + 1) == total:
            mm, ss = divmod(int(frame.time), 60)
            logger.info(f"  [{i+1}/{total}] {frame.frame_id} @ {mm:02d}:{ss:02d} → {fc.caption[:60]}")
    return results
