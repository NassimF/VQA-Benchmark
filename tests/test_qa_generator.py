"""Unit tests for src/qa_generator.py.

No real API calls — the Anthropic client is monkeypatched throughout.
No real model or API key required.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock, patch

from src.qa_generator import (
    build_prompt,
    load_augmented_chunks,
    parse_qa_response,
    generate_qa,
)

# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------

VIDEO_ID = "test_lec01"

CHUNKS = [
    {
        "chunk_id": "test_lec01_chunk_000",
        "video_id": VIDEO_ID,
        "start_time": 0.0,
        "end_time": 45.0,
        "text": "Introduction to dynamic programming. [frame caption: slide title 'Divide and Conquer']",
        "frame_captions": ["slide title 'Divide and Conquer'"],
    },
    {
        "chunk_id": "test_lec01_chunk_001",
        "video_id": VIDEO_ID,
        "start_time": 35.0,
        "end_time": 80.0,
        "text": "Optimal substructure is the key property. [frame caption: diagram of subproblem tree]",
        "frame_captions": ["diagram of subproblem tree"],
    },
    {
        "chunk_id": "test_lec01_chunk_010",
        "video_id": VIDEO_ID,
        "start_time": 350.0,
        "end_time": 395.0,
        "text": "The complexity is O(n^2) because each subproblem is solved once.",
        "frame_captions": [],
    },
]


def _make_qa_item(index: int, question_type: str, num_hops: int, answerable: bool = True) -> dict:
    spans = [] if not answerable else [
        {"start": 0.0, "end": 45.0, "hop": 1, "description": "intro"},
    ]
    if num_hops >= 2:
        spans.append({"start": 350.0, "end": 395.0, "hop": 2, "description": "complexity claim"})
    return {
        "qa_id": f"{VIDEO_ID}_q{index:03d}",
        "video_id": VIDEO_ID,
        "question": "What property is required and what is the resulting complexity?",
        "answer": "Optimal substructure is required, and the complexity is O(n^2) per subproblem.",
        "num_hops": num_hops,
        "ground_truth_spans": spans if answerable else [],
        "source_chunk_ids": [CHUNKS[0]["chunk_id"], CHUNKS[2]["chunk_id"]] if num_hops >= 2 else [CHUNKS[0]["chunk_id"]],
        "question_type": question_type,
        "difficulty": "hard" if question_type in ("multi-hop-visual", "multi-hop") else "medium",
        "answerable": answerable,
        "key_concepts": ["dynamic programming", "optimal substructure"],
    }


def _make_valid_15_items() -> list[dict]:
    items: list[dict] = []
    idx = 1
    for _ in range(7):
        items.append(_make_qa_item(idx, "multi-hop-visual", 2))
        idx += 1
    for _ in range(2):
        items.append(_make_qa_item(idx, "visual", 1))
        idx += 1
    for _ in range(3):
        items.append(_make_qa_item(idx, "multi-hop", 2))
        idx += 1
    for _ in range(2):
        items.append(_make_qa_item(idx, "text", 1))
        idx += 1
    items.append({
        "qa_id": f"{VIDEO_ID}_q{idx:03d}",
        "video_id": VIDEO_ID,
        "question": "Does this lecture discuss quantum computing?",
        "answer": "This lecture does not cover quantum computing at all.",
        "num_hops": 1,
        "ground_truth_spans": [],
        "source_chunk_ids": [],
        "question_type": "unanswerable",
        "difficulty": "medium",
        "answerable": False,
        "key_concepts": ["quantum computing"],
    })
    return items


# ---------------------------------------------------------------------------
# Tests for build_prompt
# ---------------------------------------------------------------------------

def test_build_prompt_contains_chunk_ids():
    prompt = build_prompt(VIDEO_ID, CHUNKS)
    for chunk in CHUNKS:
        assert chunk["chunk_id"] in prompt


def test_build_prompt_contains_video_id():
    prompt = build_prompt(VIDEO_ID, CHUNKS)
    assert VIDEO_ID in prompt


def test_build_prompt_contains_timestamps():
    prompt = build_prompt(VIDEO_ID, CHUNKS)
    assert "00:00" in prompt  # chunk_000 start


# ---------------------------------------------------------------------------
# Tests for parse_qa_response
# ---------------------------------------------------------------------------

def test_parse_qa_response_valid():
    items = _make_valid_15_items()
    raw = json.dumps(items)
    result = parse_qa_response(VIDEO_ID, raw)
    assert len(result) == 15
    for item in result:
        assert item["video_id"] == VIDEO_ID


def test_parse_qa_response_strips_markdown_fences():
    items = _make_valid_15_items()
    raw = f"```json\n{json.dumps(items)}\n```"
    result = parse_qa_response(VIDEO_ID, raw)
    assert len(result) == 15


def test_parse_qa_response_raises_on_invalid_json():
    with pytest.raises(ValueError, match="not valid JSON"):
        parse_qa_response(VIDEO_ID, "not json at all")


def test_parse_qa_response_raises_on_missing_field():
    items = _make_valid_15_items()
    del items[0]["question"]
    with pytest.raises(ValueError, match="missing fields"):
        parse_qa_response(VIDEO_ID, json.dumps(items))


def test_parse_qa_response_raises_on_invalid_question_type():
    items = _make_valid_15_items()
    items[0]["question_type"] = "unknown_type"
    with pytest.raises(ValueError, match="invalid question_type"):
        parse_qa_response(VIDEO_ID, json.dumps(items))


def test_parse_qa_response_raises_on_multihop_with_one_hop():
    items = _make_valid_15_items()
    items[0]["num_hops"] = 1  # multi-hop-visual must be ≥2
    with pytest.raises(ValueError, match="num_hops"):
        parse_qa_response(VIDEO_ID, json.dumps(items))


def test_parse_qa_response_raises_on_non_multihop_with_two_hops():
    items = _make_valid_15_items()
    # visual item should have num_hops=1
    items[7]["num_hops"] = 2
    with pytest.raises(ValueError, match="num_hops"):
        parse_qa_response(VIDEO_ID, json.dumps(items))


def test_parse_qa_response_reviewed_by_not_set_by_parser():
    items = _make_valid_15_items()
    result = parse_qa_response(VIDEO_ID, json.dumps(items))
    # reviewed_by is stamped by generate_qa, not parse_qa_response
    for item in result:
        assert "reviewed_by" not in item


# ---------------------------------------------------------------------------
# Tests for generate_qa
# ---------------------------------------------------------------------------

def test_generate_qa_stamps_reviewed_by(tmp_path):
    items = _make_valid_15_items()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(items))]

    chunk_file = tmp_path / "test_lec01_chunks_augmented.json"
    chunk_file.write_text(json.dumps(CHUNKS))

    mock_cfg = MagicMock()
    mock_cfg.data.chunks_dir = tmp_path
    mock_cfg.qa_generation.model = "claude-sonnet-4-6"

    with patch("src.qa_generator.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        result = generate_qa(VIDEO_ID, mock_cfg)

    assert len(result) == 15
    for item in result:
        assert item["reviewed_by"] == "llm_draft"


def test_generate_qa_stamps_review_date(tmp_path):
    items = _make_valid_15_items()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(items))]

    chunk_file = tmp_path / "test_lec01_chunks_augmented.json"
    chunk_file.write_text(json.dumps(CHUNKS))

    mock_cfg = MagicMock()
    mock_cfg.data.chunks_dir = tmp_path
    mock_cfg.qa_generation.model = "claude-sonnet-4-6"

    with patch("src.qa_generator.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        result = generate_qa(VIDEO_ID, mock_cfg)

    import re
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for item in result:
        assert date_pattern.match(item["review_date"]), f"Bad review_date: {item['review_date']}"


def test_generate_qa_no_real_api_call(tmp_path):
    """Confirm no real Anthropic API call is made when client is mocked."""
    items = _make_valid_15_items()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(items))]

    chunk_file = tmp_path / "test_lec01_chunks_augmented.json"
    chunk_file.write_text(json.dumps(CHUNKS))

    mock_cfg = MagicMock()
    mock_cfg.data.chunks_dir = tmp_path
    mock_cfg.qa_generation.model = "claude-sonnet-4-6"

    with patch("src.qa_generator.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        generate_qa(VIDEO_ID, mock_cfg)

        mock_client.messages.create.assert_called_once()


def test_generate_qa_raises_on_missing_chunks(tmp_path):
    mock_cfg = MagicMock()
    mock_cfg.data.chunks_dir = tmp_path
    mock_cfg.qa_generation.model = "claude-sonnet-4-6"

    with pytest.raises(FileNotFoundError):
        generate_qa("nonexistent_lec", mock_cfg)
