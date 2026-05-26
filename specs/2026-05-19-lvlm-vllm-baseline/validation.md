# Validation: LVLM / Video LLM Baseline

## Automated Checks

- [ ] `pytest tests/` passes with no regressions (existing tests must not break)
- [ ] `scripts/run_lvlm_baseline.py --model video-llava-7b --dry-run` completes without error
- [ ] Each `data/benchmark/lvlm_results_{model}.json` contains exactly 810 entries (one per QA pair)
- [ ] `scripts/compute_text_metrics.py --results data/benchmark/lvlm_results_{model}.json` runs without error for all 4 models
- [ ] `python scripts/reproduce_tables.py` runs end-to-end without error and prints the LVLM comparison table

## Output Artifacts

| File | Required? | Description |
|---|---|---|
| `data/benchmark/lvlm_results_video_llava_7b.json` | Yes | Inference outputs for Video-LLaVA-7B |
| `data/benchmark/lvlm_results_mplug_owl3_8b.json` | Yes | Inference outputs for mPLUG-Owl3-8B |
| `data/benchmark/lvlm_results_qwen_vl_7b.json` | Yes | Inference outputs for Qwen-VL-7B |
| `data/benchmark/lvlm_results_llava_13b.json` | Yes | Inference outputs for LLaVA-13B |
| `data/benchmark/lvlm_text_metrics.json` | Yes | BLEU/ROUGE-L/METEOR/Entailment for all models |
| `data/benchmark/lvlm_factqa.json` | If FactQA in scope | FQA-P and FQA-R for all models |
| `scripts/run_lvlm_baseline.py` | Yes | Inference script committed to repo |
| `scripts/compute_factqa.py` | If FactQA in scope | FactQA scorer script |
| `results.md` updated | Yes | Full LVLM comparison table added |

## Manual Checks

- [ ] RAG Config 2 outperforms all 4 Video LLMs on ROUGE-L and METEOR for visual questions — this is the paper's central claim; if any Video LLM exceeds Config 2, investigate before reporting
- [ ] Entailment-R values are plausible (0.6–0.9 range expected for coherent answers)
- [ ] Spot-check 3 Video LLM answers against ground truth for a visual question, a multi-hop question, and an unanswerable question — confirm model behavior is as expected
- [ ] Frame sampling strategy documented in paper: exact N, uniform spacing, no oracle timestamp
- [ ] `push_to_overleaf.sh` run after any changes to `overleaf/assets/`

## Merge Criteria

All of the following must be true before merging `feature/lvlm-vllm-baseline` into `main`:

1. All 4 model result files present and validated (810 entries each)
2. `reproduce_tables.py` regenerates the LVLM comparison table cleanly
3. `results.md` updated with Config 1 | Config 2 | LVLM comparison
4. Frame sampling strategy and transcript-access decision documented in `requirements.md`
5. FactQA decision documented (in scope or explicitly deferred with cost rationale)
6. All existing pytest tests still pass
7. `/changelog` run and CHANGELOG.md updated
