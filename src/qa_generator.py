"""QA Generator — draft QA pair generation for the VQA benchmark.

Reads augmented chunks (transcript + frame captions) for a lecture and calls
Claude to produce 15 draft QA pairs spanning five question types.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date
from pathlib import Path

import anthropic

from src.config import Config, load_config

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent

_VALID_QUESTION_TYPES = {"multi-hop-visual", "multi-hop", "visual", "text", "unanswerable"}
_MULTIHOP_TYPES = {"multi-hop", "multi-hop-visual"}
_REQUIRED_FIELDS = {
    "qa_id", "question", "answer", "num_hops",
    "ground_truth_spans", "source_chunk_ids", "question_type",
    "difficulty", "answerable", "key_concepts",
}

_SYSTEM_PROMPT = """\
You are an expert question designer for a video lecture RAG benchmark.
Your task is to generate exactly 15 draft QA pairs for a given lecture.
You will be given numbered chunks from the lecture transcript, each optionally
followed by frame captions describing visual content at that moment.

QUESTION SLOT ASSIGNMENTS — each slot has a fixed type; do not deviate:
  Slots 1–7:   question_type = "multi-hop-visual"  (≥2 non-adjacent spans, ≥1 visual hop)
  Slots 8–9:   question_type = "visual"            (single-hop; answer from frame caption)
  Slots 10–12: question_type = "multi-hop"         (≥2 non-adjacent spans; transcript-only)
  Slots 13–14: question_type = "text"              (single-hop; lecture-specific fact, not
                                                    answerable from general LLM knowledge)
  Slot 15:     question_type = "unanswerable"      (answerable=false, empty spans/chunks,
                                                    answer = "This question cannot be answered
                                                    from the provided lecture content.")

The qa_id index must match the slot number: slot 1 → q001, slot 7 → q007, slot 15 → q015.
The final array MUST have exactly 15 items in slot order.

SCHEMA — each item must be a JSON object with EXACTLY these fields:
{
  "qa_id": "{video_id}_q{index:03d}",   // e.g. "mit_6046_lec10_q001"
  "video_id": "{video_id}",
  "question": "...",
  "answer": "...",
  "num_hops": 1,                         // 1 for visual/text/unanswerable; ≥2 for multi-hop types
  "ground_truth_spans": [                // empty list [] for unanswerable
    {"start": 320.0, "end": 398.0, "hop": 1, "description": "..."},
    {"start": 2870.0, "end": 2940.0, "hop": 2, "description": "..."}
  ],
  "source_chunk_ids": ["chunk_id_1"],    // empty list [] for unanswerable
  "question_type": "multi-hop-visual",
  "difficulty": "hard",                  // "easy" | "medium" | "hard"
  "answerable": true,                    // false for "unanswerable"
  "key_concepts": ["concept1", "concept2"]
}

FIELD RULES:
- "multi-hop-visual": num_hops ≥ 2, ≥2 ground_truth_spans from non-adjacent chunks
  (span[1].start - span[0].end > 60s), ≥1 span's answer relies on a [frame caption]
- "visual": num_hops = 1, answer must come from [frame caption] content, not transcript text
- "multi-hop": num_hops ≥ 2, ≥2 spans from non-adjacent chunks, transcript-only
- "text": num_hops = 1, lecture-specific fact (reject if answerable without retrieval)
- "unanswerable": num_hops = 1, answerable = false, ground_truth_spans = [], source_chunk_ids = []
- difficulty: multi-hop-visual → "hard"; multi-hop → "medium" or "hard"; others → "easy" or "medium"
- ground_truth_spans: use chunk start/end times as float seconds

REJECTION CRITERIA (generate questions that pass all of these):
- Answer must be ≥ 10 words
- Answer must NOT appear verbatim inside the question
- "text" questions must be lecture-specific — cannot be answered by general knowledge

OUTPUT: Respond with ONLY a valid JSON array of exactly 15 objects. No markdown fences,
no explanation, no preamble. Start your response with '[' and end with ']'.
"""


def _seconds_to_mmss(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def load_augmented_chunks(video_id: str, cfg: Config | None = None) -> list[dict]:
    """Load augmented chunks for a lecture from disk."""
    _cfg = cfg or load_config()
    path = _cfg.data.chunks_dir / f"{video_id}_chunks_augmented.json"
    if not path.exists():
        raise FileNotFoundError(f"Augmented chunks not found: {path}")
    chunks = json.loads(path.read_text())
    logger.info(f"{video_id}: loaded {len(chunks)} augmented chunks from {path}")
    return chunks


def build_prompt(video_id: str, chunks: list[dict]) -> str:
    """Format augmented chunks into the user prompt for QA generation."""
    lines: list[str] = [
        f"Lecture: {video_id}",
        f"Total chunks: {len(chunks)}",
        "",
        "CHUNKS:",
        "",
    ]
    for i, chunk in enumerate(chunks, start=1):
        start = _seconds_to_mmss(chunk["start_time"])
        end = _seconds_to_mmss(chunk["end_time"])
        lines.append(f"[{i}] {chunk['chunk_id']} ({start}–{end})")
        lines.append(chunk["text"])
        lines.append("")

    lines.append(
        f"Generate exactly 15 QA pairs for lecture '{video_id}' following the schema and "
        "distribution specified in the system prompt. Use the chunk_ids above for "
        "source_chunk_ids and ground_truth_spans timestamps."
    )
    return "\n".join(lines)


def _extract_json_array(raw: str) -> str:
    """Extract the first JSON array from raw text, stripping markdown fences."""
    stripped = raw.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        stripped = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        stripped = stripped.strip()
    # Find array boundaries in case there's leading prose
    start = stripped.find("[")
    end = stripped.rfind("]")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_qa_response(video_id: str, raw_json: str) -> list[dict]:
    """Parse and validate the LLM's JSON response into a list of QA dicts.

    Raises:
        ValueError: If the response cannot be parsed or any item fails validation.
    """
    candidate = _extract_json_array(raw_json)

    try:
        items = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Response is not valid JSON: {exc}\n---\n{raw_json[:500]}") from exc

    if not isinstance(items, list):
        raise ValueError(f"Expected JSON array, got {type(items).__name__}")

    validated: list[dict] = []
    for i, item in enumerate(items):
        missing = _REQUIRED_FIELDS - set(item)
        if missing:
            raise ValueError(f"Item {i} missing fields: {missing}")

        qt = item["question_type"]
        if qt not in _VALID_QUESTION_TYPES:
            raise ValueError(f"Item {i} has invalid question_type: {qt!r}")

        hops = item["num_hops"]
        if qt in _MULTIHOP_TYPES and hops < 2:
            raise ValueError(f"Item {i}: {qt} requires num_hops ≥ 2, got {hops}")
        if qt not in _MULTIHOP_TYPES and hops != 1:
            raise ValueError(f"Item {i}: {qt} requires num_hops = 1, got {hops}")

        if qt == "unanswerable":
            if item.get("answerable", True):
                raise ValueError(f"Item {i}: unanswerable question must have answerable=false")
            if item.get("ground_truth_spans"):
                raise ValueError(f"Item {i}: unanswerable question must have empty ground_truth_spans")

        # Normalise video_id in case LLM got it wrong
        item["video_id"] = video_id
        validated.append(item)

    # Validate exact question type distribution
    from collections import Counter
    counts = Counter(item["question_type"] for item in validated)
    expected = {"multi-hop-visual": 7, "visual": 2, "multi-hop": 3, "text": 2, "unanswerable": 1}
    wrong = {k: (counts[k], v) for k, v in expected.items() if counts[k] != v}
    if wrong:
        detail = ", ".join(f"{k}: got {got} expected {exp}" for k, (got, exp) in wrong.items())
        raise ValueError(f"Wrong question type distribution — {detail}")

    logger.info(f"{video_id}: parsed {len(validated)} QA items")
    return validated


def generate_qa(video_id: str, cfg: Config | None = None) -> list[dict]:
    """Generate 15 draft QA pairs for a lecture by calling Claude.

    Args:
        video_id: Lecture identifier, e.g. "mit_6046_lec10".
        cfg: Loaded Config; if None, loaded from default config.yaml.

    Returns:
        List of validated QA dicts with reviewed_by and review_date stamped.

    Raises:
        FileNotFoundError: If augmented chunks are missing.
        ValueError: If the LLM response fails schema validation.
    """
    _cfg = cfg or load_config()
    chunks = load_augmented_chunks(video_id, _cfg)
    user_prompt = build_prompt(video_id, chunks)

    client = anthropic.Anthropic()
    logger.info(f"{video_id}: calling {_cfg.qa_generation.model} for QA generation")

    last_exc: Exception | None = None
    for attempt in range(1, 4):  # up to 3 attempts
        response = client.messages.create(
            model=_cfg.qa_generation.model,
            max_tokens=8192,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text
        logger.debug(f"{video_id}: attempt {attempt} response length={len(raw)}")
        try:
            items = parse_qa_response(video_id, raw)
            break
        except ValueError as exc:
            logger.warning(f"{video_id}: attempt {attempt} failed validation — {exc}")
            last_exc = exc
            if attempt < 3:
                time.sleep(65)  # wait out the 1-minute rate limit window before retry
    else:
        raise ValueError(f"{video_id}: all 3 attempts failed") from last_exc

    today = date.today().isoformat()
    for item in items:
        item["reviewed_by"] = "llm_draft"
        item["review_date"] = today

    logger.info(f"{video_id}: generated {len(items)} QA pairs")
    return items
