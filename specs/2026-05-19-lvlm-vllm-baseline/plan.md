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
- [x] **LLaVA-13B re-run complete** — `max_frames_total=2` fix applied; 696/696, 0 empty (see §4c)

## 4. Metric computation for Video LLM outputs

- [x] **Video-LLaVA-7B re-run complete** — 690/696 scored (99.1% coverage). 6 persistent empty answers documented below.
- [x] **LLaVA-13B inference complete** — 696 processed, but 259 empty (37%) due to positional overflow; re-run needed (see §4c)
- [ ] Investigate mPLUG-Owl3 1 remaining empty pair (`mit_1806_lec10_q007`) — tensor size mismatch on that video
- [x] Run `scripts/compute_text_metrics.py` against Qwen2, Video-LLaVA, mPLUG-Owl3
- [x] Run `scripts/compute_text_metrics.py` against LLaVA-13B — BLEU=0.1254, ROUGE-L=0.3181, METEOR=0.3616, n=696
- [x] Run `scripts/compute_text_metrics.py` (with entailment) against all 4 LVLM models and Config 1 & 2 ✅

**Entailment-R (gen→ref) — All Questions (primary metric for paper):**

| Model | Entailment-R (all) | Entailment-R (visual) | Entailment-R (non-visual) | n |
|---|---|---|---|---|
| Config 1 (RAG, text only) | 0.8172 | 0.8118 | 0.8273 | 696 |
| Config 2 (RAG, +frames)   | 0.8509 | 0.8498 | 0.8530 | 696 |
| Qwen2-VL-7B               | 0.8079 | 0.8085 | 0.8068 | 696 |
| mPLUG-Owl3-8B             | 0.8156 | 0.7988 | 0.8470 | 695 |
| Video-LLaVA-7B            | 0.8149 | 0.8039 | 0.8352 | 690 |
| LLaVA-13B                 | 0.8450 | 0.8385 | 0.8573 | 696 |
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

### mPLUG-Owl3-8B — 4 empty answers

- **3 pairs** (`mit_6006sp20_lec04_q009`, `mit_6006sp20_lec11_q008`, `mit_6006sp20_lec17_q012`): **0 frames extracted** — inference ran before the 2026-05-28 benchmark fix; oracle window used the old invalid timestamps (beyond video duration) → ffmpeg returned 0 frames → empty output. Fixable by re-running just these 3 pairs.
- **1 pair** (`mit_1806_lec10_q007`): **tensor size mismatch** in mPLUG-Owl3's vision encoder for that video's resolution. Not fixable without methodology change.

### LLaVA-13B — 259 empty answers (37%)

**Root cause — positional embedding overflow:**
6 frames × 576 tokens/frame = 3456 image tokens + 2-hop transcript ≈ 1200–1600 tokens = **4600–5050 total**, well beyond the 4096-token position limit. At this range, RoPE extrapolation is unstable — 37% of pairs generate EOS immediately. Not a truncation issue (tokenizer has no length cap); the model receives the full sequence but position embeddings are out-of-distribution.

**Fix:** reduce `max_frames_total` to 2 for llava-13b → 2 × 576 = 1152 image tokens; 2-hop pairs fit within ~2800 tokens total. Requires full re-run (~2 hrs).

### Note on n_scored in metrics table

`compute_text_metrics.py` currently includes empty answers as zero-scores in the mean, inflating n but depressing scores. Fix: filter empties before averaging. Impact by model:
- Qwen2-VL-7B: 0 empty → unchanged
- mPLUG-Owl3-8B: 4 empty → n=692 (negligible score change)
- Video-LLaVA-7B: 6 empty → n=690 (minor score bump)
- LLaVA-13B: 259 empty → n=437 (major change; current scores are meaningless)

## 4c. Inference corrections before final metric computation ⚠️

**Step 1 (fast, ~minutes) — Fix mPLUG-Owl3 3 stale-timestamp empties:** ✅
- [x] Re-run inference for `mit_6006sp20_lec04_q009`, `mit_6006sp20_lec11_q008`, `mit_6006sp20_lec17_q012` with corrected benchmark timestamps
- [x] Patch the 3 results into `lvlm_results_mplug_owl3_8b.json` — all 3 non-empty (89/207/473 chars); 1 unfixable empty remains (`mit_1806_lec10_q007`)

**Step 2 (long, ~2 hrs) — Fix LLaVA-13B positional overflow:** ✅
- [x] Set `max_frames_total: 2` for `llava-13b` in `config.yaml` (2 × 576 = 1152 img tokens; 2-hop total ≤ ~2800)
- [x] Re-run full LLaVA-13B inference — 696/696, 0 empty answers

**Step 3 (fast, ~20s, depends on steps 1+2) — Fix metric script and recompute all models:** ✅
- [x] Update `scripts/compute_text_metrics.py`: filter empty `generated_answer` before computing mean
- [x] Re-run metrics for all 4 LVLM models
- [x] Updated results table with final corrected scores

### Final text metrics — all models complete, empties filtered (2026-05-29)

| Model | BLEU | ROUGE-L | METEOR | n scored |
|---|---|---|---|---|
| Config 1 (RAG, text only) | 0.0689 | 0.2662 | 0.2010 | 696 |
| Config 2 (RAG, +frames) | 0.1086 | 0.3615 | 0.2736 | 696 |
| Qwen2-VL-7B | 0.1522 | 0.3534 | 0.4072 | 696 |
| mPLUG-Owl3-8B | 0.1424 | 0.3550 | 0.3584 | 695 |
| Video-LLaVA-7B | 0.0432 | 0.1279 | 0.1312 | 690 |
| LLaVA-13B | 0.1254 | 0.3181 | 0.3616 | 696 |

### Key findings — n-gram metrics (2026-05-29)

**Overall:** No single system wins all three metrics. Config 2 leads ROUGE-L; Qwen2 leads BLEU and METEOR. 3 of 4 VLLMs beat Config 2 on BLEU and METEOR; Config 2 beats all VLLMs on ROUGE-L. Video-LLaVA is the clear outlier — worst on all metrics, below Config 1.

**Why Config 2 leads ROUGE-L but not BLEU/METEOR:** Config 2 retrieves verbatim transcript text and injects it into answers. The reference answers are also derived from transcripts → long word-for-word matches → high ROUGE-L (LCS). But verbatim retrieval also includes filler words → lower precision → lower BLEU. Qwen2 generates concise paraphrases: high precision (high BLEU), synonym-rich (high METEOR), but shorter sequences (lower ROUGE-L).

**Config 2 vs Config 1:** +58% BLEU, +36% ROUGE-L, +36% METEOR — frame captions consistently improve answer generation across all metrics.

**Important caveat:** VLLMs receive oracle frame windows centered on GT timestamps — an advantage RAG doesn't have. The fair comparison is tIoU, LLM-judge, and citation accuracy where RAG must retrieve on its own.

### Key findings — Entailment-R (2026-05-29)

**Config 2 leads overall (0.8509)** — the only system above 0.85. Generated answers are the most factually grounded in the reference.

**Strongest result: visual questions.** Config 2 (0.8498) leads all VLLMs on Entailment-R for visual questions (Qwen2: 0.8085, mPLUG: 0.7988). This is the clearest signal: frame-augmented RAG produces more factually correct answers on visual questions than Video LLMs given oracle frames.

**Combined takeaway:** VLLMs score high on BLEU/METEOR (fluent paraphrases that sound right). Config 2 leads on ROUGE-L and Entailment-R (retrieves the right content in the right words, and answers are factually grounded). N-gram metrics measure phrasing quality; entailment measures factual correctness. Config 2 winning on both ROUGE-L and Entailment-R — especially on visual questions — is the paper's strongest result.

## 4b. Recompute all RAG metrics after benchmark fix (n=698 → n=696) ⚠️ partially done

**No re-inference needed — all generated answers already stored.**

- Single-hop table (n=238) unaffected — all defect pairs are multi-hop
- Multi-hop count changes: 460 → 458 (2 removed)
- Text metrics (BLEU/ROUGE-L/METEOR): ✅ recomputed — Config 1 and 2 essentially unchanged (removed pairs had empty answers)
- tIoU / IoU / Hit Rate / citation accuracy: must recompute — GT spans changed for 10 corrected pairs

- [x] Recompute Config 1 & Config 2 text metrics (BLEU/ROUGE-L/METEOR) on 696 pairs — C1: 0.0689/0.2662/0.2010, C2: 0.1086/0.3615/0.2736
- [x] Re-run `scripts/reproduce_tables.py` (tIoU/Hit Rate tables regenerated from `evaluation_results.json`)
- [x] Recompute LLM-judge scores and citation accuracy on 696 pairs — filtered 4 stale entries (2 removed pairs × 2 configs)

| | Config 1 | Config 2 |
|---|---|---|
| LLM-judge (all) | 3.027 | 3.564 |
| LLM-judge (visual) | 2.574 | 3.520 |
| LLM-judge (text) | 3.609 | 3.620 |
| Citation acc (all) | 0.235 | 0.317 |
| Citation acc (visual) | 0.198 | 0.340 |
| Citation acc (text) | 0.281 | 0.287 |
- [ ] **Full paper consistency pass** — search every `.tex` file for hardcoded numbers that changed: 810→808 (total), 698→696 (answerable), 460→458 (multi-hop), 698→698 unanswerable (unchanged). Check narrative claims ("+32% LLM-judge", "+72% citation accuracy", etc.) against recomputed values and correct any that shifted.
- [ ] Update multi-hop counts in `overleaf/assets/sections/results.tex` (460 → 458) and any narrative percentages that shift
- [ ] Update `results.md` side-by-side with corrected numbers

## 5. Results recording and paper update

- [ ] Update `results.md` with the full LVLM comparison table
- [ ] Update `overleaf/assets/sections/results.tex` with new Video LLM comparison table and analysis paragraph
- [ ] Run `./push_to_overleaf.sh` after any Overleaf edit
- [ ] Commit all new scripts, results JSON files, and paper changes
