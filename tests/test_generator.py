"""Unit tests for src/generator.py.

No real LLM calls — _call_llm is monkeypatched throughout.
No real model or API key required.
"""

from __future__ import annotations

import json
import pytest

from src.generator import (
    GeneratorResult,
    _build_prompt,
    _format_citation,
    _parse_llm_output,
    _seconds_to_mmss,
    _union_span,
    generate,
)


# ---------------------------------------------------------------------------
# Synthetic fixtures
# ---------------------------------------------------------------------------

CHUNKS = [
    {
        "chunk_id": "mit_6046_lec10_chunk_009",
        "video_id": "mit_6046_lec10",
        "start_time": 315.0,
        "end_time": 360.0,
        "text": "Dynamic programming relies on optimal substructure.",
    },
    {
        "chunk_id": "mit_6046_lec10_chunk_010",
        "video_id": "mit_6046_lec10",
        "start_time": 350.0,
        "end_time": 395.0,
        "text": "Memoization caches overlapping subproblems.",
    },
    {
        "chunk_id": "mit_6046_lec10_chunk_082",
        "video_id": "mit_6046_lec10",
        "start_time": 2870.0,
        "end_time": 2940.0,
        "text": "The complexity claim relies on the subproblem property.",
    },
]

METADATA = {
    "mit_6046_lec10": {
        "video_id": "mit_6046_lec10",
        "youtube_id": "Tw1k46ywN6E",
        "title": "MIT 6.046 Lecture 10",
    }
}


# ---------------------------------------------------------------------------
# _seconds_to_mmss
# ---------------------------------------------------------------------------

def test_seconds_to_mmss_zero() -> None:
    assert _seconds_to_mmss(0.0) == "00:00"


def test_seconds_to_mmss_exact_minute() -> None:
    assert _seconds_to_mmss(60.0) == "01:00"


def test_seconds_to_mmss_mixed() -> None:
    assert _seconds_to_mmss(315.0) == "05:15"


def test_seconds_to_mmss_truncates_not_rounds() -> None:
    assert _seconds_to_mmss(319.9) == "05:19"


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

def test_build_prompt_excerpt_count() -> None:
    prompt = _build_prompt("What is DP?", CHUNKS)
    assert "[1]" in prompt
    assert "[2]" in prompt
    assert "[3]" in prompt
    assert "[4]" not in prompt


def test_build_prompt_mmss_format() -> None:
    prompt = _build_prompt("What is DP?", CHUNKS[:1])
    assert "05:15 to 06:00" in prompt


def test_build_prompt_includes_question() -> None:
    prompt = _build_prompt("What is optimal substructure?", CHUNKS[:1])
    assert "What is optimal substructure?" in prompt


def test_build_prompt_includes_video_id() -> None:
    prompt = _build_prompt("?", CHUNKS[:1])
    assert "mit_6046_lec10" in prompt


# ---------------------------------------------------------------------------
# _parse_llm_output
# ---------------------------------------------------------------------------

def test_parse_valid_output() -> None:
    raw = json.dumps({"answer": "DP uses optimal substructure.", "citations": [1]})
    answer, cited = _parse_llm_output(raw, CHUNKS)
    assert answer == "DP uses optimal substructure."
    assert len(cited) == 1
    assert cited[0]["chunk_id"] == "mit_6046_lec10_chunk_009"


def test_parse_multi_citation() -> None:
    raw = json.dumps({"answer": "Both chunks matter.", "citations": [1, 3]})
    _, cited = _parse_llm_output(raw, CHUNKS)
    assert cited[0]["chunk_id"] == "mit_6046_lec10_chunk_009"
    assert cited[1]["chunk_id"] == "mit_6046_lec10_chunk_082"


def test_parse_empty_citations() -> None:
    raw = json.dumps({"answer": "Not enough info.", "citations": []})
    answer, cited = _parse_llm_output(raw, CHUNKS)
    assert cited == []


def test_parse_strips_markdown_fences() -> None:
    raw = "```json\n" + json.dumps({"answer": "Yes.", "citations": [2]}) + "\n```"
    answer, cited = _parse_llm_output(raw, CHUNKS)
    assert answer == "Yes."
    assert cited[0]["chunk_id"] == "mit_6046_lec10_chunk_010"


def test_parse_raises_on_invalid_json() -> None:
    with pytest.raises(ValueError, match="not valid JSON"):
        _parse_llm_output("not json at all", CHUNKS)


def test_parse_raises_on_missing_answer() -> None:
    raw = json.dumps({"citations": [1]})
    with pytest.raises(ValueError, match="missing 'answer'"):
        _parse_llm_output(raw, CHUNKS)


def test_parse_raises_on_missing_citations() -> None:
    raw = json.dumps({"answer": "Something."})
    with pytest.raises(ValueError, match="missing 'citations'"):
        _parse_llm_output(raw, CHUNKS)


def test_parse_raises_on_out_of_range_index() -> None:
    raw = json.dumps({"answer": "X.", "citations": [5]})
    with pytest.raises(ValueError, match="out of range"):
        _parse_llm_output(raw, CHUNKS)


def test_parse_raises_on_zero_index() -> None:
    raw = json.dumps({"answer": "X.", "citations": [0]})
    with pytest.raises(ValueError, match="out of range"):
        _parse_llm_output(raw, CHUNKS)


# ---------------------------------------------------------------------------
# _union_span
# ---------------------------------------------------------------------------

def test_union_span_single_chunk() -> None:
    start, end = _union_span(CHUNKS[:1])
    assert start == pytest.approx(315.0)
    assert end == pytest.approx(360.0)


def test_union_span_multiple_chunks() -> None:
    start, end = _union_span([CHUNKS[0], CHUNKS[2]])
    assert start == pytest.approx(315.0)
    assert end == pytest.approx(2940.0)


def test_union_span_unsorted_order() -> None:
    reversed_chunks = [CHUNKS[2], CHUNKS[0]]
    start, end = _union_span(reversed_chunks)
    assert start == pytest.approx(315.0)
    assert end == pytest.approx(2940.0)


# ---------------------------------------------------------------------------
# _format_citation
# ---------------------------------------------------------------------------

def test_format_citation_structure() -> None:
    citation = _format_citation(CHUNKS[0], METADATA["mit_6046_lec10"])
    assert citation.startswith("[mit_6046_lec10 @ 05:15 to 06:00]")
    assert "https://youtu.be/Tw1k46ywN6E?t=315" in citation


def test_format_citation_t_param_is_int_of_start() -> None:
    chunk = {**CHUNKS[0], "start_time": 315.9}
    citation = _format_citation(chunk, METADATA["mit_6046_lec10"])
    assert "?t=315" in citation


# ---------------------------------------------------------------------------
# generate() — end-to-end with mocked _call_llm
# ---------------------------------------------------------------------------

def test_generate_returns_result(monkeypatch, tmp_path) -> None:
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps([
        {"video_id": "mit_6046_lec10", "youtube_id": "Tw1k46ywN6E", "title": "MIT 6.046 Lecture 10"}
    ]))

    import src.generator as gen_module
    from src.config import load_config

    cfg = load_config()
    cfg.data.metadata_file = meta_file

    llm_response = json.dumps({"answer": "DP uses optimal substructure.", "citations": [1]})
    monkeypatch.setattr(gen_module, "_call_llm", lambda sys, usr, c: llm_response)

    result = generate("What is DP?", CHUNKS, mode="transcript_only", cfg=cfg)

    assert isinstance(result, GeneratorResult)
    assert result.answer == "DP uses optimal substructure."
    assert len(result.citations) == 1
    assert "mit_6046_lec10 @ 05:15 to 06:00" in result.citations[0]
    assert result.predicted_start == pytest.approx(315.0)
    assert result.predicted_end == pytest.approx(360.0)
    assert result.mode == "transcript_only"


def test_generate_no_citations_gives_zero_span(monkeypatch, tmp_path) -> None:
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps([
        {"video_id": "mit_6046_lec10", "youtube_id": "Tw1k46ywN6E"}
    ]))

    import src.generator as gen_module
    from src.config import load_config

    cfg = load_config()
    cfg.data.metadata_file = meta_file

    llm_response = json.dumps({"answer": "Not enough info.", "citations": []})
    monkeypatch.setattr(gen_module, "_call_llm", lambda sys, usr, c: llm_response)

    result = generate("Unknown question?", CHUNKS, mode="transcript_only", cfg=cfg)

    assert result.citations == []
    assert result.predicted_start == pytest.approx(0.0)
    assert result.predicted_end == pytest.approx(0.0)


def test_generate_raises_on_malformed_llm_output(monkeypatch, tmp_path) -> None:
    meta_file = tmp_path / "metadata.json"
    meta_file.write_text(json.dumps([{"video_id": "mit_6046_lec10", "youtube_id": "X"}]))

    import src.generator as gen_module
    from src.config import load_config

    cfg = load_config()
    cfg.data.metadata_file = meta_file

    monkeypatch.setattr(gen_module, "_call_llm", lambda sys, usr, c: "bad output")

    with pytest.raises(ValueError):
        generate("Any question?", CHUNKS, mode="transcript_only", cfg=cfg)
