# Plan: LVLM / Video LLM Baseline

Phase 11 — run Video LLM baselines on LectureBench and compare against Config 1 & 2 RAG results.

---

## 1. Frame extraction and windowing

- [ ] Implement oracle-windowed frame extractor: for each QA pair, extract frames from a ±120s window centered on each hop's `ground_truth_spans[i].start` using ffmpeg
- [ ] Use per-model frame counts: mPLUG-Owl3-8B and Qwen-VL-7B → 30 frames/window; Video-LLaVA-7B and LLaVA-13B → 8 frames/window
- [ ] For multi-hop pairs, concatenate frames from all hop windows into a single ordered input
- [ ] Add frame extraction helper to `scripts/run_lvlm_baseline.py` (reuse ffmpeg logic from `scripts/build_frame_captions.py`)
- [ ] Update `config.yaml` with per-model frame counts

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
