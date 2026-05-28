# Plan: LVLM / Video LLM Baseline

Phase 11 — run Video LLM baselines on LectureBench and compare against Config 1 & 2 RAG results.

---

## 1. Frame extraction and windowing ✅

- [x] Implement oracle-windowed frame extractor: for each QA pair, extract frames from a ±120s window centered on each hop's `ground_truth_spans[i].start` using ffmpeg
- [x] Use per-model frame counts: mPLUG-Owl3-8B and Qwen2-VL-7B → 30 frames/window; Video-LLaVA-7B → 8 frames/window; LLaVA-13B → 3 frames/window + max_frames_total=6
- [x] For multi-hop pairs, concatenate frames from all hop windows into a single ordered input
- [x] Add frame extraction helper to `scripts/run_lvlm_baseline.py` (reuse ffmpeg logic from `scripts/build_frame_captions.py`)
- [x] Update `config.yaml` with per-model frame counts (`lvlm.models` section)
- [x] Fix `extract_oracle_frames` for AV1/VP9 `.webm`/`.mkv`: single-pass window extraction (seek once to window start, decode through); `.mp4` keeps fast per-frame seek
- [x] Add `max_frames_total` param to `run_inference` — distributes frames evenly across hops to prevent context overflow (critical for Video-LLaVA-7B `max_frames_total=8` and LLaVA-13B `max_frames_total=6`)

## 2. FactQA cost analysis and decision ✅

- [x] Compute exact token cost estimate for FactQA over 1,620 result pairs using GPT-4o-mini pricing ($0.15/1M input, $0.60/1M output)
- [x] Compute same estimate for GPT-4o pricing ($2.50/1M input, $10/1M output)
- [x] Document both scenarios in `requirements.md` and decide which model to use (GPT-4o-mini, ~$0.54)
- [x] Add `scripts/compute_factqa.py` standalone script

## 3. Video LLM inference script ✅

- [x] Implement `scripts/run_lvlm_baseline.py` — oracle-windowed frame extraction, model loading, answer generation for 696 answerable QA pairs (698 − 2 removed after benchmark quality fix)
- [x] Support `--model` flag: `video-llava-7b`, `mplug-owl3-8b`, `qwen2-vl-7b`, `llava-13b`
- [x] Save outputs to `data/benchmark/lvlm_results_{model}.json` with schema compatible with `compute_text_metrics.py`
- [x] Add progress checkpoint/resume so inference can be interrupted and continued
- [x] `--dry-run` flag verified: 698 pairs processed correctly (696 after benchmark quality fix)

## 3b. Benchmark data quality fix (discovered 2026-05-28) ⚠️

Root cause: `_parse_and_validate()` never checks that GT span timestamps fall within video duration. LLM occasionally copies a timestamp slightly beyond the last chunk boundary.

**Resolution (completed 2026-05-28):** 10 pairs had correct source chunks but wrong timestamps — fixed by replacing each hop's span with the source chunk's actual start/end. 2 pairs removed: `nyu_dl_week3_q027` (adjacent source chunks, 35s gap) and `mit_18650_lec03_q006` (discovered during sanity check — adjacent source chunks, 15s gap after fix). **Final benchmark: 696 answerable pairs (808 total, 112 unanswerable).**

- [x] **Fix 10 QA pairs** in `benchmark_v1.json` — `timestamp_corrected: true` + `original_ground_truth_spans` preserved. IDs: `mit_18650_lec07_q012`, `mit_6006f11_lec04_q007`, `mit_6006f11_lec14_q016`, `mit_6006sp20_lec04_q009`, `mit_6006sp20_lec04_q029`, `mit_6006sp20_lec09_q027`, `mit_6006sp20_lec11_q001`, `mit_6006sp20_lec11_q008`, `mit_6006sp20_lec11_q011`, `mit_6006sp20_lec17_q012`
- [x] **Remove 2 QA pairs** (`nyu_dl_week3_q027`, `mit_18650_lec03_q006`) — adjacent source chunks make multi-hop structure unrepaireable
- [x] Remove both qa_ids from all 3 existing LVLM result files and checkpoints; `n_pairs` updated
- [x] Clean Video-LLaVA checkpoint of 22 empty-answer entries (ready for re-run with `--resume`)
- [x] Add post-generation VTT bounds check to `src/qa_generator.py` `_parse_and_validate()`
- [ ] **Start LLaVA-13B re-run** (config already fixed): `python scripts/run_lvlm_baseline.py --model llava-13b --no-resume >> logs/llava_rerun.log 2>&1 &` (~6 hrs)

## 4. Metric computation for Video LLM outputs

- [x] **Video-LLaVA-7B re-run complete** — 690/696 scored (99.1% coverage). 6 persistent empty answers documented below.
- [ ] Investigate mPLUG-Owl3 1 remaining empty pair (`mit_1806_lec10_q007`) — tensor size mismatch on that video
- [x] Run `scripts/compute_text_metrics.py` against Qwen2, Video-LLaVA, mPLUG-Owl3
- [ ] Run `scripts/compute_text_metrics.py` against LLaVA-13B once inference done
- [ ] Run `scripts/compute_factqa.py` against each model (if FactQA decision is yes)
- [ ] Collect all scores into a unified comparison table (Config 1, Config 2, + 4 Video LLMs)
- [ ] Add `reproduce_table_lvlm` function to `scripts/reproduce_tables.py`

### Video-LLaVA-7B — 6 persistent empty answers (not fixable without methodology change)

**Root cause A — context overflow (1 pair):**
`mit_6006f11_lec09_q017`: long transcript context (±120s × 2 hops ≈ 14 chunks) pushes total tokens to 5823 > 4096 even with `max_frames_total=8`. Visual tokens are only ~2048; the transcript text fills the remaining budget. Would require truncating transcript context to fix.

**Root cause B — oracle window mismatch (5 nyu_dl_week11 pairs):**
- `nyu_dl_week11_q016`: hop1 GT span is 2s–185s (unusually wide); oracle window (center=2s, ±120s = 0–122s) misses content past 122s. Model gets no useful visual signal. Frames are valid (avg brightness ~150) but don't cover the relevant slide.
- `nyu_dl_week11_q017/q018/q021/q027`: hop windows overlap heavily (hops only 80s apart); both hops receive nearly identical frames — model produces no output.

**Fix cost vs benefit:** Recovering 5/696 pairs (0.7%) would require extending oracle window or deduplicating overlapping hop frames — non-trivial changes to oracle strategy. Not worth altering for paper.

**Paper note:** Report Video-LLaVA as n=690 scored; footnote the 6 failures as context-overflow/oracle-window edge cases.

### Preliminary text metrics (n=696, LLaVA-13B TBD)

| Model | BLEU | ROUGE-L | METEOR | n scored |
|---|---|---|---|---|
| Config 1 (RAG, text only) | 0.0689 | 0.2662 | 0.2010 | 696 |
| Config 2 (RAG, +frames) | 0.1086 | 0.3615 | 0.2736 | 696 |
| Qwen2-VL-7B | 0.1522 | 0.3534 | 0.4072 | 696 |
| mPLUG-Owl3-8B | 0.1420 | 0.3533 | 0.3569 | 696 |
| Video-LLaVA-7B | 0.0428 | 0.1268 | 0.1300 | 690 |
| LLaVA-13B | TBD | TBD | TBD | — |

## 4b. Recompute all RAG metrics after benchmark fix (n=698 → n=696) ⚠️ partially done

**No re-inference needed — all generated answers already stored.**

- Single-hop table (n=238) unaffected — all defect pairs are multi-hop
- Multi-hop count changes: 460 → 458 (2 removed)
- Text metrics (BLEU/ROUGE-L/METEOR): ✅ recomputed — Config 1 and 2 essentially unchanged (removed pairs had empty answers)
- tIoU / IoU / Hit Rate / citation accuracy: must recompute — GT spans changed for 10 corrected pairs

- [x] Recompute Config 1 & Config 2 text metrics (BLEU/ROUGE-L/METEOR) on 696 pairs — C1: 0.0689/0.2662/0.2010, C2: 0.1086/0.3615/0.2736
- [x] Re-run `scripts/reproduce_tables.py` (tIoU/Hit Rate tables regenerated from `evaluation_results.json`)
- [ ] Recompute LLM-judge scores and citation accuracy on 696 pairs (need to filter `evaluation_results.json`)
- [ ] Update multi-hop counts in `overleaf/assets/sections/results.tex` (460 → 458) and any narrative percentages that shift
- [ ] Update `results.md` side-by-side with corrected numbers

## 5. Results recording and paper update

- [ ] Update `results.md` with the full LVLM comparison table
- [ ] Update `overleaf/assets/sections/results.tex` with new Video LLM comparison table and analysis paragraph
- [ ] Run `./push_to_overleaf.sh` after any Overleaf edit
- [ ] Commit all new scripts, results JSON files, and paper changes
