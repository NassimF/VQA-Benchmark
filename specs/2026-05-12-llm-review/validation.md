# Phase 7.3 — LLM Review: Validation

Phase 7.3 is complete and ready to merge when ALL of the following pass.

---

## Output File Checks

- [ ] `data/qa_pairs/reviewed/` contains exactly 60 `{video_id}_qa_reviewed.json` files
- [ ] `data/qa_pairs/review_log/` contains exactly 60 `{video_id}_review_log.json` files
- [ ] No lecture is marked as discarded (discard flag absent or count = 0)

## Count Checks

- [ ] Total accepted QA pairs across all lectures = **720** (12 accepted × 60 lectures)
- [ ] Every lecture has ≥ 10 accepted pairs
- [ ] Every lecture has ≥ 1 accepted `unanswerable` pair
- [ ] Every lecture has ≥ 60% visual-type accepted pairs (`multi-hop-visual` + `visual`)

## Quality Checks (automated via `validate_benchmark.py`)

- [ ] No accepted pair has `answer` length < 10 words
- [ ] No accepted pair has `answer` text verbatim contained in `question` text
- [ ] All accepted `multi-hop*` pairs have `|start_A - start_B| ≥ 70s` across `ground_truth_spans`
- [ ] All accepted `multi-hop-visual` pairs have ≥ 1 `source_chunk_id` whose chunk text
      contains a `[frame caption: ...]` marker
- [ ] All `qa_id` values follow the schema `{video_id}_q{index:03d}` and are unique

## Test Suite

- [ ] `pytest tests/test_qa_reviewer.py` — all tests pass
- [ ] No real model loaded in any test fixture (mock client only)

## Rejection Log Integrity

- [ ] Every rejected pair has a `rejection_reason` string (non-empty)
- [ ] Every rejected pair specifies which criterion failed (`criterion_1`, `criterion_2`,
      or `criterion_3`)

## Merge Condition

All checkboxes above must be checked before merging `feat/phase-7-llm-review` into `main`.
If any lecture ends up with 10–11 accepted pairs (at floor but not discarded), add a
footnote in `overleaf/assets/sections/results.tex` disclosing the actual per-lecture
distribution before merging.
