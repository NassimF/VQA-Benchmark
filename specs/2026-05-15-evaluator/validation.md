# Phase 8.1 — Validation Criteria
**Date:** 2026-05-15
**Branch:** `phase-8-evaluator`

Implementation is complete and ready to merge when ALL of the following pass.

---

## V1 — Unit Tests

```bash
conda activate vqa-benchmark
pytest tests/test_evaluator.py -v
```

**Must pass:** All tests green. No real models loaded — fixtures use synthetic data only.

Spot-check specific cases:
- `temporal_iou(0, 45, 30, 75)` → `0.2` (15s intersection / 75s union: pred[0,45]+gt[30,75]−overlap=75)
- `temporal_iou(0, 45, 50, 95)` → `0.0` (no overlap)
- `hit_rate_at_k` with a chunk covering [30, 75] against GT [0, 45] at k=1, threshold=0.3 → `False` (IoU = 0.2 < 0.3)

---

## V2 — Schema Conformance

Run evaluation on a single lecture (manually call `evaluate_question` in a test script):

- Every result dict contains all required fields from `requirements.md` output schema
- `judge_1_C1`, `judge_1_C2`, `judge_1_C3`, `judge_2_C1`, `judge_2_C2`, `judge_2_C3` all present and integers 1–5
- `llm_judge_score` is a float in [1.0, 5.0]
- `config` field is either `"transcript_only"` or `"transcript_plus_frames"`
- Each QA pair appears exactly twice in results (once per config)

---

## V3 — Mathematical Metric Sanity Checks

After a full or partial evaluation run, verify:

- `temporal_iou` values are all in [0.0, 1.0]
- `hit_rate_at_5 >= hit_rate_at_3 >= hit_rate_at_1` for every question (monotonicity)
- `multihop_complete_at_5` is never `True` when `multihop_per_hop_recall_at_5 < 1.0`
- Unanswerable questions (`answerable: false`) have `temporal_iou = 0.0` and `citation_accuracy = 0.0`
- Single-hop questions have `multihop_per_hop_iou = temporal_iou` (they are equivalent for 1 hop)

---

## V4 — LLM Judge Sanity Checks

- All C1/C2/C3 scores are integers in {1, 2, 3, 4, 5}
- `judge_1_aggregate` and `judge_2_aggregate` equal round(mean(C1, C2, C3)) for each judge
- `llm_judge_score` = mean of `judge_1_aggregate` and `judge_2_aggregate`
- Krippendorff's α is reported for C1, C2, C3, and aggregate in `metadata`
- α values are floats in [-1.0, 1.0]
- No API call failures silently produce 0 scores — failed calls must raise or be logged as errors

---

## V5 — Config Isolation

- Running with `config="transcript_only"` uses collection `lecture_transcript_only`
- Running with `config="transcript_plus_frames"` uses collection `lecture_transcript_plus_frames`
- Results for the same `qa_id` differ between configs (they should, given different retrievals)
- Both configs produce results for all 810 QA pairs (total rows = 1620)

---

## V6 — Output File

```bash
python -c "
import json
results = json.load(open('data/benchmark/evaluation_results.json'))
assert 'metadata' in results
assert 'results' in results
assert len(results['results']) == 1620  # 810 questions × 2 configs
print('Output schema OK')
"
```

---

## V7 — Existing Tests Unaffected

```bash
pytest tests/ -v
```

All pre-existing tests (chunker, retriever) must remain green. `src/evaluator.py` must not import or depend on real models at module load time.

---

## Merge Checklist

- [ ] V1 unit tests all pass
- [ ] V2 schema conformance verified on at least one lecture
- [ ] V3 mathematical sanity checks pass
- [ ] V4 LLM judge sanity checks pass
- [ ] V5 config isolation confirmed
- [ ] V6 output file structure valid
- [ ] V7 no regression in existing tests
- [ ] `config.yaml` updated with `evaluator` section
- [ ] `specs/roadmap.md` Phase 8.1 marked ✅
- [ ] `/changelog` run and committed
