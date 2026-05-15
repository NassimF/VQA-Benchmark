"""Unit tests for src/evaluator.py — Task Group 4.

No real models are loaded. All LLM calls are mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.evaluator import (
    build_judge_prompt,
    citation_accuracy,
    compute_krippendorff_alpha,
    hit_rate_at_k,
    iou_at_threshold,
    merge_spans,
    multihop_complete_retrieval_at_k,
    multihop_per_hop_iou,
    multihop_per_hop_recall_at_k,
    multihop_union_iou,
    predicted_span_from_chunks,
    temporal_iou,
)

# ─── Fixtures ─────────────────────────────────────────────────────────────────


def _chunk(start: float, end: float, chunk_id: str = "c000", video_id: str = "v") -> dict:
    return {"chunk_id": chunk_id, "video_id": video_id, "start_time": start, "end_time": end, "text": "t"}


def _gt(start: float, end: float, hop: int = 1) -> dict:
    return {"start": start, "end": end, "hop": hop, "description": ""}


# ─── 4.1 temporal_iou ─────────────────────────────────────────────────────────


def test_temporal_iou_perfect_overlap():
    assert temporal_iou(0, 45, 0, 45) == pytest.approx(1.0)


def test_temporal_iou_zero_overlap():
    assert temporal_iou(0, 45, 50, 95) == pytest.approx(0.0)


def test_temporal_iou_partial_overlap():
    # pred [0,45], gt [30,75]: intersection=15, union=(45+45-15)=75
    assert temporal_iou(0, 45, 30, 75) == pytest.approx(15 / 75)


def test_temporal_iou_zero_length_span():
    # pred is a point; union > 0 but intersection = 0
    assert temporal_iou(10, 10, 0, 45) == pytest.approx(0.0)


def test_temporal_iou_contained():
    # pred fully inside gt: intersection=20, union=45
    assert temporal_iou(10, 30, 0, 45) == pytest.approx(20 / 45)


def test_iou_at_threshold_true():
    assert iou_at_threshold(0.333, 0.3) is True


def test_iou_at_threshold_false():
    assert iou_at_threshold(0.2, 0.3) is False


def test_iou_at_threshold_exact():
    assert iou_at_threshold(0.3, 0.3) is True


# ─── merge_spans ──────────────────────────────────────────────────────────────


def test_merge_spans_no_overlap():
    result = merge_spans([(0, 10), (20, 30)])
    assert result == [(0, 10), (20, 30)]


def test_merge_spans_adjacent():
    result = merge_spans([(0, 10), (10, 20)])
    assert result == [(0, 20)]


def test_merge_spans_overlapping():
    result = merge_spans([(0, 15), (10, 25)])
    assert result == [(0, 25)]


def test_merge_spans_unsorted():
    result = merge_spans([(20, 30), (0, 10)])
    assert result == [(0, 10), (20, 30)]


def test_merge_spans_empty():
    assert merge_spans([]) == []


# ─── predicted_span_from_chunks ───────────────────────────────────────────────


def test_predicted_span_from_chunks_single():
    assert predicted_span_from_chunks([_chunk(10, 50)]) == (10.0, 50.0)


def test_predicted_span_from_chunks_multiple():
    chunks = [_chunk(10, 50), _chunk(100, 150)]
    assert predicted_span_from_chunks(chunks) == (10.0, 150.0)


def test_predicted_span_from_chunks_empty():
    assert predicted_span_from_chunks([]) == (0.0, 0.0)


# ─── 4.2 hit_rate_at_k ────────────────────────────────────────────────────────


def test_hit_rate_at_k_hit_at_1():
    # chunk [30, 75] vs GT [0, 45]: IoU = 15/90 ≈ 0.167 < 0.3 — NOT a hit
    chunks = [_chunk(30, 75)]
    assert hit_rate_at_k(chunks, [_gt(0, 45)], k=1, iou_threshold=0.3) is False


def test_hit_rate_at_k_strong_hit():
    # chunk [0, 45] vs GT [0, 45]: IoU = 1.0 ≥ 0.3
    chunks = [_chunk(0, 45)]
    assert hit_rate_at_k(chunks, [_gt(0, 45)], k=1, iou_threshold=0.3) is True


def test_hit_rate_at_k_miss_at_1_hit_at_3():
    chunks = [_chunk(200, 250), _chunk(300, 350), _chunk(0, 45)]
    assert hit_rate_at_k(chunks, [_gt(0, 45)], k=1, iou_threshold=0.3) is False
    assert hit_rate_at_k(chunks, [_gt(0, 45)], k=3, iou_threshold=0.3) is True


def test_hit_rate_at_k_miss_all():
    chunks = [_chunk(200, 250), _chunk(300, 350)]
    assert hit_rate_at_k(chunks, [_gt(0, 45)], k=5, iou_threshold=0.3) is False


def test_hit_rate_at_k_empty_gt():
    assert hit_rate_at_k([_chunk(0, 45)], [], k=1) is False


# ─── 4.3 multihop metrics ─────────────────────────────────────────────────────


def test_multihop_per_hop_iou_perfect():
    pred = [(0.0, 45.0), (100.0, 150.0)]
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    assert multihop_per_hop_iou(pred, gt) == pytest.approx(1.0)


def test_multihop_per_hop_iou_one_miss():
    pred = [(0.0, 45.0)]  # covers hop 1 but not hop 2
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    # hop 1: IoU = 1.0, hop 2: IoU = 0.0 → mean = 0.5
    assert multihop_per_hop_iou(pred, gt) == pytest.approx(0.5)


def test_multihop_per_hop_iou_empty_pred():
    assert multihop_per_hop_iou([], [_gt(0, 45)]) == pytest.approx(0.0)


def test_multihop_union_iou_perfect():
    pred = [(0.0, 45.0), (100.0, 150.0)]
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    assert multihop_union_iou(pred, gt) == pytest.approx(1.0)


def test_multihop_union_iou_partial():
    pred = [(0.0, 45.0)]  # covers only first hop
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    # pred_len=45, gt_len=95 (45+50), intersection=45, union=45+95-45=95
    assert multihop_union_iou(pred, gt) == pytest.approx(45 / 95)


def test_multihop_union_iou_no_overlap():
    pred = [(200.0, 250.0)]
    gt = [_gt(0, 45, 1)]
    assert multihop_union_iou(pred, gt) == pytest.approx(0.0)


# ─── 4.4 citation_accuracy ────────────────────────────────────────────────────


def test_citation_accuracy_all_correct():
    cited = [_chunk(0, 45), _chunk(100, 150)]
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    assert citation_accuracy(cited, gt) == pytest.approx(1.0)


def test_citation_accuracy_none_correct():
    cited = [_chunk(200, 250)]
    gt = [_gt(0, 45, 1)]
    assert citation_accuracy(cited, gt) == pytest.approx(0.0)


def test_citation_accuracy_partial():
    cited = [_chunk(0, 45)]  # covers hop 1 only
    gt = [_gt(0, 45, 1), _gt(100, 150, 2)]
    assert citation_accuracy(cited, gt) == pytest.approx(0.5)


def test_citation_accuracy_empty_cited():
    assert citation_accuracy([], [_gt(0, 45)]) == pytest.approx(0.0)


def test_citation_accuracy_empty_gt():
    assert citation_accuracy([_chunk(0, 45)], []) == pytest.approx(0.0)


# ─── 4.5 build_judge_prompt ───────────────────────────────────────────────────


def test_build_judge_prompt_single_hop_contains_required_fields():
    chunks = [_chunk(0, 45, "c001", "vid1")]
    prompt = build_judge_prompt(
        question="What is X?",
        reference_answer="X is Y.",
        retrieved_chunks=chunks,
        generated_answer="X is Y.",
        num_hops=1,
        answerable=True,
    )
    assert "What is X?" in prompt
    assert "X is Y." in prompt
    assert "C1" in prompt
    assert "C3" in prompt
    # Single-hop: C2 should not ask judge to independently score
    assert "single-hop" in prompt.lower() or "C2 = C1" in prompt


def test_build_judge_prompt_multi_hop_contains_c2():
    chunks = [_chunk(0, 45, "c001", "vid1")]
    prompt = build_judge_prompt(
        question="Compare X and Y?",
        reference_answer="X differs from Y in ...",
        retrieved_chunks=chunks,
        generated_answer="They differ.",
        num_hops=2,
        answerable=True,
    )
    assert "C2" in prompt
    assert "2" in prompt  # num_hops substituted


def test_build_judge_prompt_unanswerable():
    prompt = build_judge_prompt(
        question="What is the exact angle?",
        reference_answer="",
        retrieved_chunks=[],
        generated_answer="I cannot answer.",
        num_hops=1,
        answerable=False,
    )
    assert "no answer" in prompt.lower() or "unanswerable" in prompt.lower() or "no answer in the lecture" in prompt.lower()


# ─── Krippendorff's α ─────────────────────────────────────────────────────────


def test_krippendorff_alpha_perfect_agreement():
    results = [
        {"judge_1_C1": 4, "judge_2_C1": 4},
        {"judge_1_C1": 3, "judge_2_C1": 3},
        {"judge_1_C1": 5, "judge_2_C1": 5},
    ]
    assert compute_krippendorff_alpha(results, "C1") == pytest.approx(1.0)


def test_krippendorff_alpha_in_range():
    results = [
        {"judge_1_C1": 1, "judge_2_C1": 5},
        {"judge_1_C1": 3, "judge_2_C1": 2},
        {"judge_1_C1": 4, "judge_2_C1": 3},
        {"judge_1_C1": 2, "judge_2_C1": 4},
    ]
    alpha = compute_krippendorff_alpha(results, "C1")
    assert -1.0 <= alpha <= 1.0


def test_krippendorff_alpha_single_unit():
    results = [{"judge_1_C1": 3, "judge_2_C1": 4}]
    assert compute_krippendorff_alpha(results, "C1") == pytest.approx(0.0)


# ─── 4.6 Integration: evaluate_question with mocks ───────────────────────────


def _make_qa_pair() -> dict:
    return {
        "qa_id": "test_vid_q001",
        "video_id": "test_vid",
        "question": "What is the main idea?",
        "answer": "The main idea is X.",
        "num_hops": 1,
        "ground_truth_spans": [{"start": 0.0, "end": 45.0, "hop": 1, "description": "Intro"}],
        "question_type": "text",
        "difficulty": "easy",
        "answerable": True,
    }


def _make_cfg():
    from src.config import (
        Config, DataConfig, EmbeddingConfig, EvaluatorConfig, FrameCaptionerConfig,
        FrameExtractionConfig, GeneratorConfig, ChunkingConfig, QAGenerationConfig,
        QAReviewConfig, RetrievalConfig, VectorDBConfig,
    )
    from pathlib import Path
    return Config(
        data=DataConfig(
            raw_dir=Path("/tmp"), videos_dir=Path("/tmp"), transcripts_dir=Path("/tmp"),
            chunks_dir=Path("/tmp"), frame_captions_dir=Path("/tmp"),
            qa_pairs_dir=Path("/tmp"), benchmark_dir=Path("/tmp"),
            metadata_file=Path("/tmp/metadata.json"),
        ),
        embedding=EmbeddingConfig(model="stub", device="cpu"),
        retrieval=RetrievalConfig(top_k=4, k_values=[1, 3, 5], distance_metric="cosine", iou_threshold=0.3),
        vector_db=VectorDBConfig(path=Path("/tmp"), transcript_only_collection="t", transcript_frames_collection="tf"),
        chunking=ChunkingConfig(window_seconds=45.0, overlap_seconds=10.0),
        frame_extraction=FrameExtractionConfig(interval_seconds=15.0),
        frame_captioner=FrameCaptionerConfig(model="stub", device="cpu", max_new_tokens=128),
        generator=GeneratorConfig(model="gpt-4o-mini", temperature=0.1, max_tokens=512, citation_format=""),
        qa_generation=QAGenerationConfig(model="stub", questions_per_lecture=15, target_accepted=12),
        qa_review=QAReviewConfig(
            primary_model="stub", c1_crosscheck_model="stub", temperature=0.0,
            floor_accepted=10, discard_threshold=0, max_retries=1, min_span_gap_seconds=70.0,
        ),
        evaluator=EvaluatorConfig(
            judge_1_model="claude-sonnet-4-6",
            judge_2_model="gpt-4o",
            iou_hit_threshold=0.3,
            output_path=Path("/tmp/eval_results.json"),
        ),
    )


def test_evaluate_question_schema():
    """Smoke test: evaluate_question returns all required fields with mocked components."""
    from src.evaluator import evaluate_question
    from src.generator import GeneratorResult

    qa_pair = _make_qa_pair()
    cfg = _make_cfg()

    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [
        {"chunk_id": "c001", "video_id": "test_vid", "start_time": 5.0, "end_time": 45.0,
         "text": "The main idea is X.", "score": 0.9},
        {"chunk_id": "c002", "video_id": "test_vid", "start_time": 50.0, "end_time": 90.0,
         "text": "Additional content.", "score": 0.7},
        {"chunk_id": "c003", "video_id": "test_vid", "start_time": 100.0, "end_time": 140.0,
         "text": "More content.", "score": 0.5},
        {"chunk_id": "c004", "video_id": "test_vid", "start_time": 150.0, "end_time": 190.0,
         "text": "Even more.", "score": 0.4},
        {"chunk_id": "c005", "video_id": "test_vid", "start_time": 200.0, "end_time": 240.0,
         "text": "Last chunk.", "score": 0.3},
    ]

    mock_gen_result = GeneratorResult(
        question="What is the main idea?",
        answer="The main idea is X.",
        citations=["[test_vid @ 00:05 to 00:45]"],
        cited_chunks=[mock_retriever.query.return_value[0]],
        predicted_start=5.0,
        predicted_end=45.0,
        mode="transcript_only",
        raw_llm_response='{"answer": "The main idea is X.", "citations": [1]}',
    )

    judge_scores = {
        "judge_1_C1": 5, "judge_1_C2": 5, "judge_1_C3": 5, "judge_1_aggregate": 5,
        "judge_2_C1": 4, "judge_2_C2": 4, "judge_2_C3": 4, "judge_2_aggregate": 4,
        "llm_judge_C1": 4.5, "llm_judge_C2": 4.5, "llm_judge_C3": 4.5,
        "llm_judge_score": 4.5,
    }

    required_fields = [
        "qa_id", "video_id", "question_type", "config",
        "retrieved_chunks", "predicted_spans", "generated_answer", "citations",
        "temporal_iou", "iou_at_03", "iou_at_05",
        "hit_rate_at_1", "hit_rate_at_3", "hit_rate_at_5",
        "multihop_per_hop_iou", "multihop_union_iou",
        "multihop_complete_at_5", "multihop_per_hop_recall_at_5",
        "citation_accuracy",
        "judge_1_C1", "judge_1_C2", "judge_1_C3", "judge_1_aggregate",
        "judge_2_C1", "judge_2_C2", "judge_2_C3", "judge_2_aggregate",
        "llm_judge_C1", "llm_judge_C2", "llm_judge_C3", "llm_judge_score",
    ]

    with patch("src.evaluator.generate", return_value=mock_gen_result), \
         patch("src.evaluator.score_with_both_judges", return_value=judge_scores):
        result = evaluate_question(qa_pair, "transcript_only", mock_retriever, cfg)

    for field in required_fields:
        assert field in result, f"Missing field: {field}"

    # Check types
    assert isinstance(result["temporal_iou"], float)
    assert isinstance(result["iou_at_03"], bool)
    assert isinstance(result["hit_rate_at_1"], bool)
    assert isinstance(result["citation_accuracy"], float)
    # Config label correct
    assert result["config"] == "transcript_only"
    # Single-hop: temporal_iou should be > 0 (chunk [5,45] vs GT [0,45])
    assert result["temporal_iou"] > 0.0
    assert result["iou_at_03"] is True


def test_evaluate_question_unanswerable_zeros():
    """Unanswerable questions should have temporal_iou=0 and citation_accuracy=0."""
    from src.evaluator import evaluate_question
    from src.generator import GeneratorResult

    qa_pair = _make_qa_pair()
    qa_pair["answerable"] = False
    qa_pair["ground_truth_spans"] = []
    qa_pair["answer"] = ""
    cfg = _make_cfg()

    mock_retriever = MagicMock()
    mock_retriever.query.return_value = [
        {"chunk_id": "c001", "video_id": "test_vid", "start_time": 5.0, "end_time": 45.0,
         "text": "Some content.", "score": 0.9},
    ] * 5

    mock_gen_result = GeneratorResult(
        question=qa_pair["question"],
        answer="I cannot answer from the provided context.",
        citations=[],
        cited_chunks=[],
        predicted_start=0.0,
        predicted_end=0.0,
        mode="transcript_only",
        raw_llm_response='{"answer": "I cannot answer.", "citations": []}',
    )

    judge_scores = {
        "judge_1_C1": 5, "judge_1_C2": 5, "judge_1_C3": 5, "judge_1_aggregate": 5,
        "judge_2_C1": 5, "judge_2_C2": 5, "judge_2_C3": 5, "judge_2_aggregate": 5,
        "llm_judge_C1": 5.0, "llm_judge_C2": 5.0, "llm_judge_C3": 5.0,
        "llm_judge_score": 5.0,
    }

    with patch("src.evaluator.generate", return_value=mock_gen_result), \
         patch("src.evaluator.score_with_both_judges", return_value=judge_scores):
        result = evaluate_question(qa_pair, "transcript_only", mock_retriever, cfg)

    assert result["temporal_iou"] == pytest.approx(0.0)
    assert result["citation_accuracy"] == pytest.approx(0.0)
    assert result["iou_at_03"] is False
    assert result["hit_rate_at_5"] is False
