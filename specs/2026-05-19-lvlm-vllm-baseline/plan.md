# Plan: LVLM / Video LLM Baseline

Phase 11 — run Video LLM baselines on LectureBench and compare against Config 1 & 2 RAG results.

---

## 1. Frame sampling design decision

- [ ] Decide N frames to sample uniformly per video (candidate: 32 frames; balances A100 VRAM vs coverage on 60-80 min videos)
- [ ] Decide whether Video LLMs receive frames-only or frames + transcript text alongside (document tradeoffs)
- [ ] Document the chosen setup in `requirements.md` under Key Decisions and update `config.yaml`
- [ ] Confirm that tIoU is dropped for Video LLMs; document the rationale (models do not reliably output timestamps off-the-shelf)
- [ ] Decide whether to add a timestamp prompt and report tIoU as an optional secondary metric in an appendix

## 2. FactQA cost analysis and decision

- [ ] Compute exact token cost estimate for FactQA over 1,620 result pairs using GPT-4o-mini pricing ($0.15/1M input, $0.60/1M output)
- [ ] Compute same estimate for GPT-4o pricing ($2.50/1M input, $10/1M output)
- [ ] Document both scenarios in `requirements.md` and decide which model to use
- [ ] Clone EduVidQA repo (`github.com/sourjyadip/eduvidqa-emnlp25`) and confirm FactQA scorer runs end-to-end on a sample pair
- [ ] Add `scripts/compute_factqa.py` standalone script (mirrors pattern of `scripts/compute_text_metrics.py`)

## 3. Video LLM inference script

- [ ] Implement `scripts/run_lvlm_baseline.py` — uniform frame extraction, model loading, answer generation for all 810 QA pairs
- [ ] Support `--model` flag: `video-llava-7b`, `mplug-owl3-8b`, `qwen-vl-7b`, `llava-13b`
- [ ] Support `--frames` flag (default: 32) for frame count
- [ ] Save outputs to `data/benchmark/lvlm_results_{model}.json` with same schema as `evaluation_results.json` (minus tIoU fields)
- [ ] Add progress checkpoint/resume so inference can be interrupted and continued

## 4. Metric computation for Video LLM outputs

- [ ] Run `scripts/compute_text_metrics.py` against each `lvlm_results_{model}.json`
- [ ] Run `scripts/compute_factqa.py` against each model (if FactQA decision is yes)
- [ ] Collect all scores into a unified comparison table (Config 1, Config 2, + 4 Video LLMs)
- [ ] Add `reproduce_table_lvlm` function to `scripts/reproduce_tables.py`

## 5. Results recording and paper update

- [ ] Update `results.md` with the full LVLM comparison table
- [ ] Update `overleaf/assets/sections/results.tex` with new Video LLM comparison table and analysis paragraph
- [ ] Run `./push_to_overleaf.sh` after any Overleaf edit
- [ ] Commit all new scripts, results JSON files, and paper changes
