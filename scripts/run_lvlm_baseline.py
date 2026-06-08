"""Run Video LLM / LVLM inference on LectureBench (Phase 11).

Evaluates one model on the 698 answerable QA pairs using oracle-windowed frames
(±120s centered on each hop's GT span start) and transcript text from that window.
Matches the EduVidQA Section 5.3 experimental setup exactly.

Unanswerable pairs (112) are excluded — oracle windowing requires non-empty
ground_truth_spans to define the window center.

Usage:
    python scripts/run_lvlm_baseline.py --model qwen2-vl-7b
    python scripts/run_lvlm_baseline.py --model video-llava-7b
    python scripts/run_lvlm_baseline.py --model mplug-owl3-8b
    python scripts/run_lvlm_baseline.py --model llava-13b
    python scripts/run_lvlm_baseline.py --model qwen2-vl-7b --no-resume
    python scripts/run_lvlm_baseline.py --model qwen2-vl-7b --dry-run

Output: data/benchmark/lvlm_results_{model}.json  (schema-compatible with evaluation_results.json)
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path

import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# EduVidQA Appendix E.1 prompts (verbatim, adapted for multi-hop)
_SYSTEM_SINGLE = (
    "You are an expert computer science educator. You have to answer a question that a "
    "student has asked from a video. For context, we have provided you with the transcript "
    "around the relevant timestamp, and the frame from the video corresponding to the "
    "relevant timestamp."
)
_SYSTEM_MULTI = (
    "You are an expert computer science educator. You have to answer a question that a "
    "student has asked from a video. For context, we have provided you with the transcript "
    "around the relevant timestamp, and the frames from the video corresponding to the "
    "relevant timestamp."
)
_QUESTION_PROMPT = (
    "Make sure the answer has good clarity, uses pedagogical techniques and encourages "
    "critical thinking. Use the context from the transcript to answer the following "
    "question in a single paragraph."
)

MODEL_CHOICES = ["qwen2-vl-7b", "video-llava-7b", "mplug-owl3-8b", "llava-13b"]


# ---------------------------------------------------------------------------
# Oracle frame extraction
# ---------------------------------------------------------------------------

def _video_duration(video_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def extract_oracle_frames(
    video_path: Path,
    hop_start: float,
    window_secs: float,
    n_frames: int,
    video_duration: float,
) -> list[Image.Image]:
    """Extract n_frames uniformly from [hop_start-window_secs, hop_start+window_secs]."""
    t_start = max(0.0, hop_start - window_secs)
    t_end = min(video_duration, hop_start + window_secs)

    images: list[Image.Image] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        suffix = video_path.suffix.lower()
        if suffix == ".mp4":
            # Fast per-frame seek: .mp4 keyframe index makes -ss before -i instant.
            if n_frames <= 1:
                timestamps = [(t_start + t_end) / 2.0]
            else:
                step = (t_end - t_start) / (n_frames - 1)
                timestamps = [t_start + i * step for i in range(n_frames)]
            for i, t in enumerate(timestamps):
                out_path = tmp / f"frame_{i:03d}.jpg"
                subprocess.run(
                    ["ffmpeg", "-threads", "1", "-ss", str(t), "-i", str(video_path),
                     "-frames:v", "1", "-q:v", "2", str(out_path)],
                    capture_output=True,
                )
                if out_path.exists():
                    images.append(Image.open(out_path).convert("RGB").copy())
        else:
            # Single-pass window extraction for AV1/VP9 .webm and .mkv: seek once to
            # window start, decode through to window end, then sample n_frames uniformly.
            window_dur = t_end - t_start
            subprocess.run(
                ["ffmpeg", "-threads", "1",
                 "-ss", str(t_start), "-to", str(t_end), "-i", str(video_path),
                 "-vf", f"fps={n_frames}/{window_dur:.3f}",
                 "-frames:v", str(n_frames), "-q:v", "2",
                 str(tmp / "frame_%03d.jpg")],
                capture_output=True,
            )
            for f in sorted(tmp.glob("frame_*.jpg")):
                images.append(Image.open(f).convert("RGB").copy())
    return images


# ---------------------------------------------------------------------------
# Transcript extraction
# ---------------------------------------------------------------------------

def get_window_transcript(chunks: list[dict], hop_start: float, window_secs: float) -> str:
    """Return transcript text for all chunks whose start_time falls in the oracle window."""
    t_start = max(0.0, hop_start - window_secs)
    t_end = hop_start + window_secs
    window = sorted(
        [c for c in chunks if t_start <= c["start_time"] <= t_end],
        key=lambda c: c["start_time"],
    )
    return " ".join(c["text"] for c in window).strip()


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(question: str, hop_transcripts: list[str], use_multi_frame_prompt: bool) -> str:
    """Build the EduVidQA Appendix E.1 prompt, with segment labels for multi-hop."""
    system = _SYSTEM_MULTI if use_multi_frame_prompt else _SYSTEM_SINGLE
    if len(hop_transcripts) > 1:
        transcript_block = "\n\n".join(
            f"--- Segment {i + 1} ---\n{t}" for i, t in enumerate(hop_transcripts)
        )
    else:
        transcript_block = hop_transcripts[0]
    return (
        f"System Prompt: {system}"
        f" Relevant transcript: {transcript_block}"
        f" Question Prompt: {_QUESTION_PROMPT}"
        f" Question: {question}"
    )


# ---------------------------------------------------------------------------
# Model backends
# ---------------------------------------------------------------------------

class _ModelBackend(ABC):
    @abstractmethod
    def generate(self, images: list[Image.Image], prompt: str) -> str: ...


class Qwen2VLBackend(_ModelBackend):
    def __init__(self, hub_id: str, max_new_tokens: int) -> None:
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        from qwen_vl_utils import process_vision_info

        logger.info(f"Loading Qwen2-VL from {hub_id}...")
        self._model = Qwen2VLForConditionalGeneration.from_pretrained(
            hub_id, torch_dtype=torch.bfloat16, device_map="cuda"
        ).eval()
        # Cap image resolution to ~256 tokens/image so 60 frames (30/window × 2-hop)
        # fits within the 32,768 token context limit. Default is ~2,700 tokens/image
        # which causes CUDNN_STATUS_NOT_INITIALIZED from context overflow.
        # 256*28*28 = 200,704 pixels ≈ 448×448 — adequate for lecture slide OCR.
        _max_px = 256 * 28 * 28
        processor = AutoProcessor.from_pretrained(hub_id)
        processor.image_processor.max_pixels = _max_px
        processor.image_processor.min_pixels = _max_px
        self._processor = processor
        self._process_vision_info = process_vision_info
        self._max_new_tokens = max_new_tokens

    def generate(self, images: list[Image.Image], prompt: str) -> str:
        content: list[dict] = [{"type": "image", "image": img} for img in images]
        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]

        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = self._process_vision_info(messages)
        inputs = self._processor(
            text=[text], images=image_inputs, videos=video_inputs, return_tensors="pt"
        ).to("cuda")

        with torch.no_grad():
            out_ids = self._model.generate(
                **inputs, max_new_tokens=self._max_new_tokens, do_sample=False
            )
        return self._processor.batch_decode(
            out_ids[:, inputs.input_ids.shape[1]:], skip_special_tokens=True
        )[0].strip()


class VideoLlavaBackend(_ModelBackend):
    """LanguageBind/Video-LLaVA-7B-hf — native transformers VideoLlavaForConditionalGeneration."""

    def __init__(self, hub_id: str, max_new_tokens: int) -> None:
        from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration

        logger.info(f"Loading Video-LLaVA from {hub_id}...")
        self._model = VideoLlavaForConditionalGeneration.from_pretrained(
            hub_id, torch_dtype=torch.bfloat16, device_map="cuda"
        ).eval()
        self._processor = VideoLlavaProcessor.from_pretrained(hub_id)
        self._max_new_tokens = max_new_tokens

    def generate(self, images: list[Image.Image], prompt: str) -> str:
        # VideoLlava treats a list of frames as a video clip via <video> token
        formatted = f"USER: <video>\n{prompt}\nASSISTANT:"
        import numpy as np
        frames_array = np.stack([np.array(img) for img in images])  # (T, H, W, C)
        inputs = self._processor(
            text=formatted, videos=[frames_array], return_tensors="pt"
        ).to("cuda")

        with torch.no_grad():
            out_ids = self._model.generate(
                **inputs, max_new_tokens=self._max_new_tokens, do_sample=False
            )
        return self._processor.batch_decode(
            out_ids[:, inputs.input_ids.shape[1]:], skip_special_tokens=True
        )[0].strip()


class MPlugOwl3Backend(_ModelBackend):
    """mPLUG/mPLUG-Owl3-7B-241101 — uses trust_remote_code."""

    def __init__(self, hub_id: str, max_new_tokens: int) -> None:
        from transformers import AutoModel, AutoTokenizer

        logger.info(f"Loading mPLUG-Owl3 from {hub_id}...")
        self._model = AutoModel.from_pretrained(
            hub_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",  # split across available GPUs when VRAM is constrained
            trust_remote_code=True,
        ).eval()
        tokenizer = AutoTokenizer.from_pretrained(hub_id, trust_remote_code=True)
        self._processor = self._model.init_processor(tokenizer)
        self._max_new_tokens = max_new_tokens
        # Primary device = device of the embedding layer (first layer)
        self._device = self._model.language_model.model.embed_tokens.weight.device

    def generate(self, images: list[Image.Image], prompt: str) -> str:
        image_placeholders = "<|image|>" * len(images)
        messages = [
            {"role": "user", "content": f"{image_placeholders}{prompt}"},
            {"role": "assistant", "content": ""},
        ]
        inputs = self._processor(messages, images=images, videos=None)
        inputs = {k: v.to(self._device) if hasattr(v, "to") else v for k, v in inputs.items()}

        with torch.no_grad():
            # mPLUG-Owl3's custom generate() requires tokenizer= and returns decoded text
            # when decode_text=True (already slices off the input prefix).
            result = self._model.generate(
                **inputs,
                tokenizer=self._processor.tokenizer,
                max_new_tokens=self._max_new_tokens,
                do_sample=False,
                decode_text=True,
            )
        return result[0].strip() if result else ""


class LlavaBackend(_ModelBackend):
    """llava-hf/llava-1.5-13b-hf — native transformers LlavaForConditionalGeneration."""

    def __init__(self, hub_id: str, max_new_tokens: int) -> None:
        from transformers import LlavaForConditionalGeneration, AutoProcessor

        logger.info(f"Loading LLaVA from {hub_id}...")
        self._model = LlavaForConditionalGeneration.from_pretrained(
            hub_id, torch_dtype=torch.bfloat16, device_map="cuda"
        ).eval()
        self._processor = AutoProcessor.from_pretrained(hub_id)
        self._max_new_tokens = max_new_tokens

    def generate(self, images: list[Image.Image], prompt: str) -> str:
        # LLaVA-v1.5 uses one <image> token per image in the prompt
        image_tokens = "<image>" * len(images)
        formatted = f"USER: {image_tokens}\n{prompt}\nASSISTANT:"
        inputs = self._processor(
            text=formatted, images=images, return_tensors="pt"
        ).to("cuda")

        with torch.no_grad():
            out_ids = self._model.generate(
                **inputs, max_new_tokens=self._max_new_tokens, do_sample=False
            )
        return self._processor.decode(
            out_ids[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True
        ).strip()


def _load_backend(model_name: str, hub_id: str, max_new_tokens: int) -> _ModelBackend:
    backends: dict[str, type] = {
        "qwen2-vl-7b":   Qwen2VLBackend,
        "video-llava-7b": VideoLlavaBackend,
        "mplug-owl3-8b":  MPlugOwl3Backend,
        "llava-13b":      LlavaBackend,
    }
    return backends[model_name](hub_id, max_new_tokens)


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _checkpoint_path(model_name: str, benchmark_dir: Path) -> Path:
    return benchmark_dir / f"lvlm_checkpoint_{model_name.replace('-', '_')}.jsonl"


def _load_checkpoint(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    done = {}
    for line in path.read_text().splitlines():
        if line.strip():
            entry = json.loads(line)
            done[entry["qa_id"]] = entry
    return done


def _append_checkpoint(path: Path, entry: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _build_video_index(metadata_path: Path) -> dict[str, Path]:
    entries = json.loads(metadata_path.read_text())
    return {e["video_id"]: Path(e["video_file"]) for e in entries if "video_file" in e}


def _load_chunks(chunks_dir: Path, video_id: str) -> list[dict]:
    path = chunks_dir / f"{video_id}_chunks.json"
    if not path.exists():
        logger.warning(f"No chunk file for {video_id}: {path}")
        return []
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Main inference loop
# ---------------------------------------------------------------------------

def run_inference(
    model_name: str,
    benchmark_path: Path,
    metadata_path: Path,
    chunks_dir: Path,
    benchmark_dir: Path,
    window_secs: float,
    frames_per_window: int,
    hub_id: str,
    max_new_tokens: int,
    resume: bool,
    dry_run: bool,
    max_frames_total: int | None = None,
) -> None:
    # cuDNN 9.1.x fails on bfloat16 Conv operations in all four visual encoders.
    # Disable globally before any model loads; native CUDA kernels are used instead.
    torch.backends.cudnn.enabled = False

    output_path = benchmark_dir / f"lvlm_results_{model_name.replace('-', '_')}.json"
    ckpt_path = _checkpoint_path(model_name, benchmark_dir)

    bm: dict = json.loads(benchmark_path.read_text())
    all_pairs: list[dict] = bm["qa_pairs"]
    # Exclude unanswerable: oracle window requires non-empty ground_truth_spans
    pairs = [
        qa for qa in all_pairs
        if qa.get("answerable", True) and qa.get("ground_truth_spans")
    ]
    logger.info(f"Loaded {len(pairs)} answerable pairs ({len(all_pairs) - len(pairs)} excluded).")

    video_index = _build_video_index(metadata_path)
    checkpoint = _load_checkpoint(ckpt_path) if resume else {}
    if not resume and ckpt_path.exists():
        ckpt_path.unlink()

    # Determine prompt type: models with >1 frame use the multi-frame system prompt
    use_multi_frame_prompt = frames_per_window > 1

    if not dry_run:
        backend = _load_backend(model_name, hub_id, max_new_tokens)

    results: list[dict] = []
    n_total = len(pairs)

    for i, qa in enumerate(pairs):
        qa_id = qa["qa_id"]
        video_id = qa["video_id"]
        question = qa["question"]
        spans = qa["ground_truth_spans"]
        n_hops = len(spans)

        # Resume from checkpoint
        if qa_id in checkpoint:
            results.append(checkpoint[qa_id])
            continue

        logger.info(f"[{i + 1}/{n_total}] {qa_id} ({n_hops}-hop)")

        video_path = video_index.get(video_id)
        if not video_path or not Path(video_path).exists():
            logger.warning(f"  Video not found for {video_id}, skipping.")
            continue

        if dry_run:
            entry = {
                "qa_id": qa_id,
                "config": model_name,
                "video_id": video_id,
                "question": question,
                "generated_answer": "[DRY RUN]",
                "question_type": qa.get("question_type", "unknown"),
                "num_hops": n_hops,
                "num_frames": frames_per_window * n_hops,
            }
            results.append(entry)
            _append_checkpoint(ckpt_path, entry)
            continue

        video_duration = _video_duration(video_path)
        chunks = _load_chunks(chunks_dir, video_id)

        all_images: list[Image.Image] = []
        hop_transcripts: list[str] = []

        # Distribute frames evenly across hops, capped by max_frames_total if set.
        frames_this_hop = (
            max(1, max_frames_total // n_hops) if max_frames_total else frames_per_window
        )
        for span in sorted(spans, key=lambda s: s["hop"]):
            hop_start = float(span["start"])
            hop_frames = extract_oracle_frames(
                video_path, hop_start, window_secs, frames_this_hop, video_duration
            )
            all_images.extend(hop_frames)
            hop_transcripts.append(get_window_transcript(chunks, hop_start, window_secs))

        prompt = build_prompt(question, hop_transcripts, use_multi_frame_prompt)

        t0 = time.time()
        try:
            answer = backend.generate(all_images, prompt)
        except Exception as exc:
            logger.error(f"  Inference error for {qa_id}: {exc}")
            answer = ""

        elapsed = time.time() - t0
        logger.info(f"  -> {elapsed:.1f}s | {len(answer)} chars")

        entry = {
            "qa_id": qa_id,
            "config": model_name,
            "video_id": video_id,
            "question": question,
            "generated_answer": answer,
            "question_type": qa.get("question_type", "unknown"),
            "num_hops": n_hops,
            "num_frames": len(all_images),
        }
        results.append(entry)
        _append_checkpoint(ckpt_path, entry)

    output = {"model": model_name, "hub_id": hub_id, "n_pairs": len(results), "results": results}
    output_path.write_text(json.dumps(output, indent=2))
    logger.info(f"Saved {len(results)} results to {output_path}")

    if dry_run:
        logger.info("Dry run complete — no actual inference was performed.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", required=True, choices=MODEL_CHOICES,
        help="Which Video LLM to run.",
    )
    parser.add_argument(
        "--benchmark", type=Path,
        default=PROJECT_ROOT / "data" / "benchmark" / "benchmark_v1.json",
    )
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Restart from scratch, ignoring any existing checkpoint.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Extract frames and build prompts but skip model inference.")
    args = parser.parse_args()

    if args.model not in cfg.lvlm.models:
        print(f"ERROR: {args.model} not in config.yaml lvlm.models")
        sys.exit(1)

    model_cfg = cfg.lvlm.models[args.model]

    run_inference(
        model_name=args.model,
        benchmark_path=args.benchmark,
        metadata_path=cfg.data.metadata_file,
        chunks_dir=cfg.data.chunks_dir,
        benchmark_dir=cfg.data.benchmark_dir,
        window_secs=cfg.lvlm.oracle_window_seconds,
        frames_per_window=model_cfg.frames_per_window,
        hub_id=model_cfg.hub_id,
        max_new_tokens=model_cfg.max_new_tokens,
        resume=args.resume,
        dry_run=args.dry_run,
        max_frames_total=getattr(model_cfg, "max_frames_total", None),
    )


if __name__ == "__main__":
    main()
