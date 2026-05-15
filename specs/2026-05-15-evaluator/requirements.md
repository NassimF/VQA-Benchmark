# Phase 8.1 — Evaluator Requirements
**Date:** 2026-05-15
**Branch:** `phase-8-evaluator`
**Deliverable:** `src/evaluator.py`

---

## Scope

Implement all evaluation metrics for the LectureBench benchmark. The evaluator runs both
retrieval configs (transcript-only, transcript+frames) against all 810 QA pairs in
`data/benchmark/benchmark_v1.json` and saves results to
`data/benchmark/evaluation_results.json`.

**In scope:**
- Temporal IoU (mean), IoU@0.3, IoU@0.5
- Hit Rate @ k=1,3,5 — single-hop and multi-hop variants
- LLM-judge score (C1 correctness, C2 completeness, C3 groundedness, 1–5 each)
- Citation accuracy — single-hop and per-hop multi-hop
- Krippendorff's α between the two LLM judges

**Out of scope:**
- No `--video_id` filter or `--limit` flag — always runs all 810 questions
- No span tightening
- No human adjudication of low-α pairs (deferred decision post-run)

---

## Metric Definitions

### Temporal IoU
```python
def temporal_iou(pred_start, pred_end, gt_start, gt_end) -> float:
    intersection = max(0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0 else 0.0
```
- **Predicted span:** union of time ranges of all chunks cited by the generator
- **Ground truth span:** `ground_truth_spans` from benchmark (single entry for single-hop,
  union of all hops for multi-hop union IoU)
- **IoU@0.3 / IoU@0.5:** fraction of questions where temporal IoU exceeds threshold
- **Primary metric:** IoU@0.3 (tIoU@0.5 reported as secondary — see Phase 7.5 audit)

### Multi-hop IoU variants
- **Per-hop IoU:** mean IoU between each GT hop and its best-matching predicted span
- **Union IoU:** IoU between union of all predicted spans and union of all GT spans

### Hit Rate @ k
- A question is a "hit" at k if ≥1 of the top-k retrieved chunks has IoU > 0.3 with
  any GT span
- **Single-hop:** standard hit rate
- **Multi-hop per-hop recall:** fraction of GT hops covered by ≥1 top-k chunk
- **Multi-hop complete retrieval:** fraction of questions where ALL hops covered by top-k

### LLM-Judge Score (1–5)
- **Judges:** Claude Sonnet 4.6 + GPT-4o (cross-family)
- **Paradigm:** G-Eval form-filling with chain-of-thought (Liu et al., EMNLP 2023)
- **Criteria:**
  - C1 (Correctness): generated answer vs. gold reference answer
  - C2 (Completeness): for multi-hop, all hops addressed (single-hop: C2 = C1 score)
  - C3 (Groundedness): claims supported by retrieved chunks only, reference-free
- **Aggregation:** mean of C1+C2+C3 per judge, then mean across both judges
- **Per-judge scores saved separately** — required for Krippendorff's α computation
- **Low-α handling:** deferred — run evaluation first, decide post-hoc if α < 0.6
  (options: flag as limitation, or run PRD-style debate on disagreement pairs)

### Citation Accuracy
- **Single-hop:** fraction of cited chunks that contain content supporting the answer
- **Multi-hop:** fraction of GT hops covered by ≥1 cited chunk (IoU > 0.3)

---

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Generator model | gpt-4o-mini | Asymmetry by design: weaker generator stresses retrieval pipeline; avoids circularity with Claude-generated ground truth |
| Judge 1 | Claude Sonnet 4.6 | Strong structured reasoning; consistent with Phase 7.3 lineage |
| Judge 2 | GPT-4o | Cross-family coverage; stronger than mini — no literature precedent for weak fallback on hard disagreements |
| Judge aggregation | Average C1+C2+C3, then average across judges | G-Eval standard (Liu et al., EMNLP 2023) |
| Fallback/escalation | None pre-planned | No paper in Phase 8 lit review uses third-model escalation; deferred post-run |
| IoU primary threshold | 0.3 | Validated by Phase 7.5 span audit (mean error 25.8s); tIoU@0.3 robust to ±15–30s span precision |
| Circularity (same judge as Phase 7.3) | Acceptable | Judge scores GPT-4o-mini outputs, not its own; structured rubric reduces SPB (Ho et al., 2025; Yang et al., 2026) |
| Output path | `data/benchmark/evaluation_results.json` | Single canonical results file consumed by reproduce_tables.py |
| Run mode | Full run only (all 810 × 2 configs) | No subset filtering needed; run_part2.py is the CLI entry point |

---

## Context

- Benchmark: `data/benchmark/benchmark_v1.json` — 810 QA pairs, 60 lectures, 455 visual (56.2%)
- Both ChromaDB collections already built (Phase 5)
- Generator (`src/generator.py`) already implemented (Phase 6)
- Retriever (`src/retriever.py`) already implemented (Phase 5)
- Literature backing: `literature-review/phase8/literature_review_report.md`
- Config access: all model names, k values, IoU thresholds via `src/config.py`

---

## Output Schema

`data/benchmark/evaluation_results.json`:
```json
{
  "metadata": {
    "benchmark_version": "v1",
    "evaluation_date": "YYYY-MM-DD",
    "generator_model": "gpt-4o-mini",
    "judge_1": "claude-sonnet-4-6",
    "judge_2": "gpt-4o",
    "krippendorff_alpha": {
      "C1": 0.0, "C2": 0.0, "C3": 0.0, "aggregate": 0.0
    }
  },
  "results": [
    {
      "qa_id": "mit_6046_lec10_q007",
      "video_id": "mit_6046_lec10",
      "question_type": "multi-hop-visual",
      "config": "transcript_only",
      "retrieved_chunks": ["chunk_id_1", "chunk_id_2"],
      "predicted_spans": [[320.0, 398.0], [2870.0, 2940.0]],
      "generated_answer": "...",
      "citations": ["mit_6046_lec10_chunk_009"],
      "temporal_iou": 0.0,
      "iou_at_03": false,
      "iou_at_05": false,
      "hit_rate_at_1": false,
      "hit_rate_at_3": false,
      "hit_rate_at_5": false,
      "multihop_per_hop_iou": 0.0,
      "multihop_union_iou": 0.0,
      "multihop_complete_at_5": false,
      "multihop_per_hop_recall_at_5": 0.0,
      "citation_accuracy": 0.0,
      "judge_1_C1": 0, "judge_1_C2": 0, "judge_1_C3": 0, "judge_1_aggregate": 0,
      "judge_2_C1": 0, "judge_2_C2": 0, "judge_2_C3": 0, "judge_2_aggregate": 0,
      "llm_judge_C1": 0.0, "llm_judge_C2": 0.0, "llm_judge_C3": 0.0,
      "llm_judge_score": 0.0
    }
  ]
}
```
Each QA pair appears twice — once per config (`transcript_only`, `transcript_plus_frames`).
