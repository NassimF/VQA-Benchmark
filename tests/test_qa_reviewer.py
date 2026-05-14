"""Unit tests for src/qa_reviewer.py.

No real API calls — both anthropic.Anthropic and openai.OpenAI clients are mocked.
No real model or API key required.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.qa_reviewer import QAReviewer, ReviewResult, CriterionResult
from src.config import QAReviewConfig

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CFG = QAReviewConfig(
    primary_model="claude-sonnet-4-6",
    c1_crosscheck_model="gpt-4o",
    temperature=0.0,
    floor_accepted=10,
    discard_threshold=8,
    max_retries=1,
    min_span_gap_seconds=70.0,
)

CHUNK_WITH_FRAME = (
    "The professor explains gradient descent. "
    "[frame caption: Slide shows loss curve descending over 100 epochs.]"
)
CHUNK_NO_FRAME = "The professor explains gradient descent step by step."

QA_MULTI_HOP_VISUAL = {
    "qa_id": "test_lec01_q001",
    "question": "What does the slide show about gradient descent?",
    "answer": "The slide shows a loss curve descending over 100 epochs.",
    "question_type": "multi-hop-visual",
    "answerable": True,
    "ground_truth_spans": [
        {"start": 0.0, "end": 45.0, "hop": 1, "description": "hop 1"},
        {"start": 140.0, "end": 185.0, "hop": 2, "description": "hop 2"},
    ],
    "source_chunk_ids": ["chunk_000", "chunk_004"],
}

QA_UNANSWERABLE = {
    "qa_id": "test_lec01_q002",
    "question": "Does the lecture discuss quantum computing?",
    "answer": "This question cannot be answered from the lecture content.",
    "question_type": "unanswerable",
    "answerable": False,
    "ground_truth_spans": [{"start": 0.0, "end": 45.0, "hop": 1, "description": "n/a"}],
    "source_chunk_ids": ["chunk_000"],
}

CHUNKS_WITH_FRAME = {"chunk_000": CHUNK_WITH_FRAME, "chunk_004": CHUNK_WITH_FRAME}
CHUNKS_NO_FRAME = {"chunk_000": CHUNK_NO_FRAME, "chunk_004": CHUNK_NO_FRAME}


def _claude_response(**overrides) -> str:
    base = {
        "criterion_1": {"result": "PASS", "reason": "All claims supported."},
        "criterion_2": {"result": "PASS", "reason": "Spans are plausible."},
        "criterion_3": {"result": "PASS", "reason": "Type is correct."},
        "overall": "ACCEPT",
        "rejection_reason": "",
    }
    base.update(overrides)
    return json.dumps(base)


def _gpt_c1_response(result: str = "PASS", reason: str = "All claims verified.") -> str:
    return json.dumps({"criterion_1": {"result": result, "reason": reason}})


def _make_reviewer(claude_text: str, gpt_text: str | None = None) -> QAReviewer:
    """Build a QAReviewer with mocked API clients."""
    reviewer = QAReviewer.__new__(QAReviewer)
    reviewer._cfg = CFG

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value.content = [MagicMock(text=claude_text)]
    reviewer._anthropic = mock_anthropic

    mock_openai = MagicMock()
    gpt_reply = gpt_text or _gpt_c1_response()
    mock_openai.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=gpt_reply))
    ]
    reviewer._openai = mock_openai

    return reviewer


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_accept_all_pass():
    """All criteria pass; GPT-4o C1 cross-check also passes → ACCEPT."""
    reviewer = _make_reviewer(
        claude_text=_claude_response(),
        gpt_text=_gpt_c1_response("PASS"),
    )
    result = reviewer.review_qa_pair(QA_MULTI_HOP_VISUAL, CHUNKS_WITH_FRAME)
    assert result.overall == "ACCEPT"
    assert result.criterion_1.result == "PASS"
    assert result.criterion_2.result == "PASS"
    assert result.criterion_3.result == "PASS"
    assert result.c1_cross_check_result == "PASS"
    assert result.rejection_reason == ""


def test_c1_fail_claude():
    """Claude returns FAIL for C1 → REJECT; GPT-4o not called."""
    claude_resp = _claude_response(
        **{
            "criterion_1": {"result": "FAIL", "reason": "Claim not in chunk."},
            "overall": "REJECT",
            "rejection_reason": "criterion_1",
        }
    )
    reviewer = _make_reviewer(claude_text=claude_resp)
    result = reviewer.review_qa_pair(QA_MULTI_HOP_VISUAL, CHUNKS_WITH_FRAME)
    assert result.overall == "REJECT"
    assert result.criterion_1.result == "FAIL"
    assert result.c1_cross_check_result == "SKIPPED"
    reviewer._openai.chat.completions.create.assert_not_called()


def test_c2_fail_span_gap():
    """Claude returns FAIL for C2 (span gap < 70s) → REJECT."""
    claude_resp = _claude_response(
        **{
            "criterion_2": {"result": "FAIL", "reason": "Span gap is only 25s, less than 70s."},
            "overall": "REJECT",
            "rejection_reason": "criterion_2",
        }
    )
    reviewer = _make_reviewer(claude_text=claude_resp)
    result = reviewer.review_qa_pair(QA_MULTI_HOP_VISUAL, CHUNKS_WITH_FRAME)
    assert result.overall == "REJECT"
    assert result.criterion_2.result == "FAIL"
    assert "25s" in result.criterion_2.reason or "gap" in result.criterion_2.reason.lower()


def test_c3_fail_no_frame_caption():
    """Claude returns FAIL for C3 (multi-hop-visual but no frame caption) → REJECT."""
    claude_resp = _claude_response(
        **{
            "criterion_3": {"result": "FAIL", "reason": "No [frame caption:] marker found."},
            "overall": "REJECT",
            "rejection_reason": "criterion_3",
        }
    )
    reviewer = _make_reviewer(claude_text=claude_resp)
    result = reviewer.review_qa_pair(QA_MULTI_HOP_VISUAL, CHUNKS_NO_FRAME)
    assert result.overall == "REJECT"
    assert result.criterion_3.result == "FAIL"


def test_knowledge_conflict_discard():
    """Claude passes C1; GPT-4o disagrees → REJECT with c1_knowledge_conflict."""
    reviewer = _make_reviewer(
        claude_text=_claude_response(),
        gpt_text=_gpt_c1_response("FAIL", "Claim contradicts source text."),
    )
    result = reviewer.review_qa_pair(QA_MULTI_HOP_VISUAL, CHUNKS_WITH_FRAME)
    assert result.overall == "REJECT"
    assert result.rejection_reason == "c1_knowledge_conflict"
    assert result.c1_cross_check_result == "FAIL"
    reviewer._openai.chat.completions.create.assert_called_once()


def test_unanswerable_pass():
    """Unanswerable question: no evidence in chunks → ACCEPT; GPT-4o skipped."""
    claude_resp = _claude_response(
        **{
            "criterion_2": {"result": "PASS", "reason": "Not applicable for unanswerable questions."},
            "criterion_3": {"result": "PASS", "reason": "Not applicable for unanswerable questions."},
        }
    )
    reviewer = _make_reviewer(claude_text=claude_resp)
    result = reviewer.review_qa_pair(QA_UNANSWERABLE, CHUNKS_NO_FRAME)
    assert result.overall == "ACCEPT"
    assert result.c1_cross_check_result == "SKIPPED"
    reviewer._openai.chat.completions.create.assert_not_called()


def test_unanswerable_fail():
    """Unanswerable question: evidence found in chunk → REJECT."""
    claude_resp = _claude_response(
        **{
            "criterion_1": {"result": "FAIL", "reason": "Chunk contains supporting evidence."},
            "overall": "REJECT",
            "rejection_reason": "criterion_1",
        }
    )
    reviewer = _make_reviewer(claude_text=claude_resp)
    result = reviewer.review_qa_pair(QA_UNANSWERABLE, CHUNKS_WITH_FRAME)
    assert result.overall == "REJECT"
    assert result.criterion_1.result == "FAIL"
    assert result.c1_cross_check_result == "SKIPPED"


def test_unanswerable_skips_gpt4o():
    """GPT-4o C1 cross-check is never called for unanswerable questions."""
    reviewer = _make_reviewer(claude_text=_claude_response())
    reviewer.review_qa_pair(QA_UNANSWERABLE, CHUNKS_NO_FRAME)
    reviewer._openai.chat.completions.create.assert_not_called()
