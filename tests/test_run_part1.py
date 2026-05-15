"""Smoke tests for run_part1.py — no real API calls, no GPU."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import run_part1
from run_part1 import _fmt_time, run_demo


def _make_chunk(video_id: str = "mit_18065_lec06", start: float = 0.0, end: float = 45.0) -> dict:
    return {
        "chunk_id": f"{video_id}_chunk_000",
        "video_id": video_id,
        "start_time": start,
        "end_time": end,
        "text": "Sample chunk text for testing purposes.",
        "score": 0.9,
    }


def _make_result():
    return SimpleNamespace(
        answer="This is a test answer.",
        citations=["[mit_18065_lec06 @ 00:00 to 00:45](https://youtu.be/abc?t=0)"],
        cited_chunks=[_make_chunk()],
        predicted_start=0.0,
        predicted_end=45.0,
        mode="transcript_only",
        raw_llm_response='{"answer": "This is a test answer.", "citations": [1]}',
        question="What is SVD?",
    )


def test_fmt_time_zero():
    assert _fmt_time(0.0) == "00:00"


def test_fmt_time_mixed():
    assert _fmt_time(125.9) == "02:05"


def test_run_demo_calls_both_configs(capsys):
    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [_make_chunk()]

    with patch("run_part1.generate", return_value=_make_result()) as mock_gen:
        run_demo(
            question="What is SVD?",
            video_id=None,
            retrievers={
                "transcript_only": mock_retriever,
                "transcript_plus_frames": mock_retriever,
            },
            cfg=MagicMock(),
        )

    assert mock_retriever.query.call_count == 2
    assert mock_gen.call_count == 2


def test_run_demo_video_id_passed_to_retriever(capsys):
    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [_make_chunk()]

    with patch("run_part1.generate", return_value=_make_result()):
        run_demo(
            question="What is SVD?",
            video_id="mit_18065_lec06",
            retrievers={
                "transcript_only": mock_retriever,
                "transcript_plus_frames": mock_retriever,
            },
            cfg=MagicMock(),
        )

    for call in mock_retriever.query.call_args_list:
        assert call.kwargs.get("video_id") == "mit_18065_lec06"


def test_run_demo_output_contains_answer(capsys):
    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [_make_chunk()]

    with patch("run_part1.generate", return_value=_make_result()):
        run_demo(
            question="What is SVD?",
            video_id=None,
            retrievers={
                "transcript_only": mock_retriever,
                "transcript_plus_frames": mock_retriever,
            },
            cfg=MagicMock(),
        )

    captured = capsys.readouterr()
    assert "This is a test answer." in captured.out
    assert "youtu.be" in captured.out


def test_main_uses_question_arg(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["run_part1.py", "--question", "What is SVD?"])

    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [_make_chunk()]
    mock_cfg = MagicMock()
    mock_cfg.retrieval.top_k = 4

    with (
        patch("run_part1.load_config", return_value=mock_cfg),
        patch("run_part1.Retriever", return_value=mock_retriever),
        patch("run_part1.generate", return_value=_make_result()),
    ):
        run_part1.main()

    captured = capsys.readouterr()
    assert "What is SVD?" in captured.out


def test_main_runs_demo_questions_when_no_arg(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["run_part1.py"])

    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [_make_chunk()]
    mock_cfg = MagicMock()

    with (
        patch("run_part1.load_config", return_value=mock_cfg),
        patch("run_part1.Retriever", return_value=mock_retriever),
        patch("run_part1.generate", return_value=_make_result()),
    ):
        run_part1.main()

    captured = capsys.readouterr()
    assert "running 3 demo questions" in captured.out
