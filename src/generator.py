"""Generator — grounded answer generation with temporal citations.

Accepts a question and retrieved chunks, calls an LLM, and returns a structured
result with a formatted answer and [video_id @ mm:ss to mm:ss] citations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import openai

from src.config import Config, load_config

logger = logging.getLogger(__name__)

Mode = Literal["transcript_only", "transcript_plus_frames"]

_PROJECT_ROOT = Path(__file__).parent.parent

_SYSTEM_PROMPT = """\
You are a precise academic assistant answering questions about lecture videos.
You will be given numbered excerpts from lecture transcripts.
Rules:
- Answer ONLY using information from the provided excerpts.
- Cite the excerpt number(s) that support your answer.
- Keep the answer concise (1-3 sentences).
- Respond with ONLY valid JSON in this exact format:
  {"answer": "...", "citations": [1, 3]}
- If the excerpts do not contain enough information, respond:
  {"answer": "The provided excerpts do not contain enough information to answer this question.", "citations": []}
"""


@dataclass
class GeneratorResult:
    question: str
    answer: str
    citations: list[str]
    cited_chunks: list[dict]
    predicted_start: float
    predicted_end: float
    mode: str
    raw_llm_response: str


def _seconds_to_mmss(seconds: float) -> str:
    total = int(seconds)
    mm = total // 60
    ss = total % 60
    return f"{mm:02d}:{ss:02d}"


def _build_prompt(question: str, chunks: list[dict]) -> str:
    lines: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        start = _seconds_to_mmss(chunk["start_time"])
        end = _seconds_to_mmss(chunk["end_time"])
        lines.append(f"[{i}] {chunk['video_id']} @ {start} to {end}")
        lines.append(chunk["text"])
        lines.append("")
    lines.append(f"Question: {question}")
    return "\n".join(lines)


def _load_metadata(metadata_path: Path) -> dict[str, dict]:
    """Return a mapping from video_id to its metadata entry."""
    entries = json.loads(metadata_path.read_text())
    return {e["video_id"]: e for e in entries}


def _format_citation(chunk: dict, video_meta: dict) -> str:
    start_str = _seconds_to_mmss(chunk["start_time"])
    end_str = _seconds_to_mmss(chunk["end_time"])
    youtube_id = video_meta.get("youtube_id", video_meta.get("url", "").split("v=")[-1].split("&")[0])
    t = int(chunk["start_time"])
    return f"[{chunk['video_id']} @ {start_str} to {end_str}](https://youtu.be/{youtube_id}?t={t})"


def _union_span(chunks: list[dict]) -> tuple[float, float]:
    return min(c["start_time"] for c in chunks), max(c["end_time"] for c in chunks)


def _call_llm(system_prompt: str, user_prompt: str, cfg: Config) -> str:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=cfg.generator.model,
        temperature=cfg.generator.temperature,
        max_tokens=cfg.generator.max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _parse_llm_output(raw: str, chunks: list[dict]) -> tuple[str, list[dict]]:
    """Parse LLM JSON output into (answer, cited_chunks).

    Citation indices in the LLM response are 1-based and map to the chunks list.
    Raises ValueError for any output that cannot be used for evaluation.
    """
    raw_stripped = raw.strip()
    # Strip markdown code fences if present
    if raw_stripped.startswith("```"):
        lines = raw_stripped.split("\n")
        raw_stripped = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed = json.loads(raw_stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed LLM output (not valid JSON): {raw!r}") from exc

    if "answer" not in parsed:
        raise ValueError(f"Malformed LLM output (missing 'answer'): {raw!r}")
    if "citations" not in parsed:
        raise ValueError(f"Malformed LLM output (missing 'citations'): {raw!r}")
    if not isinstance(parsed["citations"], list):
        raise ValueError(f"Malformed LLM output ('citations' must be a list): {raw!r}")

    cited: list[dict] = []
    for idx in parsed["citations"]:
        if not isinstance(idx, int) or idx < 1 or idx > len(chunks):
            raise ValueError(
                f"Malformed LLM output (citation index {idx!r} out of range 1–{len(chunks)}): {raw!r}"
            )
        cited.append(chunks[idx - 1])

    return parsed["answer"], cited


def generate(
    question: str,
    chunks: list[dict],
    mode: Mode,
    cfg: Config | None = None,
) -> GeneratorResult:
    """Generate a grounded answer with temporal citations for a question.

    Args:
        question: Natural-language question.
        chunks: Retrieved chunks from Retriever.query() — each must have
                chunk_id, video_id, start_time, end_time, text.
        mode: Retrieval mode label, passed through to GeneratorResult.
        cfg: Loaded Config; if None, loaded from default config.yaml.

    Returns:
        GeneratorResult with answer, formatted citations, and predicted span.

    Raises:
        ValueError: If the LLM returns malformed or unusable output.
    """
    _cfg = cfg or load_config()
    metadata = _load_metadata(_cfg.data.metadata_file)

    user_prompt = _build_prompt(question, chunks)
    raw = _call_llm(_SYSTEM_PROMPT, user_prompt, _cfg)
    logger.debug(f"Raw LLM response: {raw!r}")

    answer, cited_chunks = _parse_llm_output(raw, chunks)

    if cited_chunks:
        pred_start, pred_end = _union_span(cited_chunks)
        citations = [_format_citation(c, metadata.get(c["video_id"], {})) for c in cited_chunks]
    else:
        pred_start = 0.0
        pred_end = 0.0
        citations = []

    return GeneratorResult(
        question=question,
        answer=answer,
        citations=citations,
        cited_chunks=cited_chunks,
        predicted_start=pred_start,
        predicted_end=pred_end,
        mode=mode,
        raw_llm_response=raw,
    )
