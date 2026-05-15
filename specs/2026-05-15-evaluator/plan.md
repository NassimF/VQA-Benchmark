# Phase 8.1 — Evaluator Implementation Plan
**Date:** 2026-05-15
**Branch:** `phase-8-evaluator`

---

## Task Group 1 — Mathematical Metrics Core (`src/evaluator.py`)

1.1 Implement `temporal_iou(pred_start, pred_end, gt_start, gt_end) -> float`
1.2 Implement `iou_at_threshold(iou, threshold) -> bool`
1.3 Implement `merge_spans(spans: list[tuple]) -> list[tuple]` — merge overlapping predicted spans into union
1.4 Implement `predicted_span_from_chunks(chunks: list[dict]) -> tuple[float, float]` — union of cited chunk time ranges
1.5 Implement `hit_rate_at_k(retrieved_chunks, gt_spans, k, iou_threshold=0.3) -> bool` — single-hop
1.6 Implement `multihop_per_hop_iou(pred_spans, gt_spans) -> float`
1.7 Implement `multihop_union_iou(pred_spans, gt_spans) -> float`
1.8 Implement `multihop_per_hop_recall_at_k(retrieved_chunks, gt_spans, k, iou_threshold=0.3) -> float`
1.9 Implement `multihop_complete_retrieval_at_k(retrieved_chunks, gt_spans, k, iou_threshold=0.3) -> bool`
1.10 Implement `citation_accuracy(cited_chunks, gt_spans, iou_threshold=0.3) -> float`

---

## Task Group 2 — LLM Judge (`src/evaluator.py`)

2.1 Implement `build_judge_prompt(question, reference_answer, retrieved_chunks, generated_answer, num_hops) -> str`
    — G-Eval form-filling format, chain-of-thought before scoring, JSON output `{C1, C2, C3, aggregate}`
2.2 Implement `call_judge(prompt, model) -> dict` — calls Claude Sonnet 4.6 or GPT-4o; parses JSON response; handles retries on parse failure (max 2 retries)
2.3 Implement `score_with_both_judges(prompt) -> dict` — calls judge 1 and judge 2, returns per-judge scores and averaged scores
2.4 Implement `compute_krippendorff_alpha(results: list[dict], criterion: str) -> float` — computes α across all questions for a given criterion (C1/C2/C3/aggregate)

---

## Task Group 3 — Evaluation Loop (`src/evaluator.py`)

3.1 Implement `evaluate_question(qa_pair, config, retriever, generator) -> dict` — runs one QA pair through retrieval → generation → all metrics; returns result dict matching output schema
3.2 Implement `evaluate_all(benchmark_path, output_path) -> None` — iterates all 810 QA pairs × 2 configs; calls `evaluate_question`; accumulates results; computes aggregate metrics and Krippendorff's α; saves `evaluation_results.json`
3.3 Add aggregate summary block to output JSON — mean per metric, broken down by: question_type, config, single-hop vs. multi-hop

---

## Task Group 4 — Tests (`tests/test_evaluator.py`)

4.1 Unit test `temporal_iou` — perfect overlap, zero overlap, partial overlap, zero-length span edge case
4.2 Unit test `hit_rate_at_k` — hit at k=1, miss at k=1 hit at k=3, miss all k
4.3 Unit test `multihop_per_hop_iou` and `multihop_union_iou` — 2-hop cases, misaligned predictions
4.4 Unit test `citation_accuracy` — all cited correct, none correct, partial
4.5 Unit test `build_judge_prompt` — verify required fields present, num_hops substituted correctly
4.6 Integration test `evaluate_question` — synthetic QA pair with mocked retriever/generator/judge; verify all fields in result dict match schema
4.7 Verify all tests pass: `pytest tests/test_evaluator.py -v`

---

## Task Group 5 — Config & Tech Stack Updates

5.1 Add `evaluator` section to `config.yaml`:
    ```yaml
    evaluator:
      judge_1_model: "claude-sonnet-4-6"
      judge_2_model: "gpt-4o"
      iou_hit_threshold: 0.3
      output_path: "data/benchmark/evaluation_results.json"
    ```
5.2 Update `src/config.py` to expose evaluator config fields
5.3 Update `specs/tech-stack.md` — add evaluator row with judge models and krippendorff dependency

---

## Task Group 6 — Spec & Changelog

6.1 Update `specs/roadmap.md` Phase 8.1 status to ✅
6.2 Run `/changelog` and commit
