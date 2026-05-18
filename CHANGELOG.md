# Changelog

## 2026-05-18

- chore: sync §2 related work fixes to Overleaf (8baeb9b)

## 2026-05-18

- review: add 4 new §2 citations (LLM-judge, video RAG, aligned captions, negative queries) (769a73a)

## 2026-05-18

- review: fix §2 related work factual errors (610b2f9)

## 2026-05-18

- chore: ignore REVIEW_CHECKLIST.md (30b59c2)
- checkpoint: BMVC compliance + figure layout polish complete (86e6943)

## 2026-05-17

- fix: fig1 arrow video→caps, neutral phase label colors (bd7af82)
- fix: move fig4 back to top of §5 with [t] and intro sentence (35ee05e)
- fix: remove line numbers, restore URL, fix float spacing (d3a0d20)
- fix: BMVC compliance — blind review, URL, hatch, intextsep (bfda9af)
- fix: add enumitem, replace unicode geq with \$\geq\$ (1b0e501)
- fix: add amssymb for checkmark, replace invalid texttimes (2e549f5)
- fix: update fig3 caption to reflect visual-dependent/control grouping (f422c50)
- fix: move fig4 legend to upper left to clear bars (64d2c1a)
- fix: update fig4 caption to new question type names (5f60a3a)
- fix: rename question types in benchmark.tex to match new taxonomy (7e237ee)
- fix: restore y-axis, add group spacer in fig_qa_dist (323686f)
- feat: two-level grouped QA dist chart, rename question types (48ea11d)
- feat: TikZ pipeline fig, author name/email fix (e6ce319)
- feat: replace fig1 PNG with TikZ pipeline diagram (7542b9a)
- fix: correct +183% -> +283% in fig4, add multi-hop regression note (2ee98b8)

## 2026-05-15

- fix: §4.5 Schema overflow — split long texttt, footnotesize+sloppy (535eb8f)
- fix: reduce intextsep to close gap above [H] tables (791fedd)
- fix: shrink fig4, raggedbottom to remove stretched whitespace (0e87042)
- fix: fig3 smaller+pinned, §4.5 gap removed, Schema overflow fixed (6abcb4b)
- fix: table overflow, §2 overflow, tab:qa_dist position, §4.5 gap (bc57a53)
- fix: pin fig_qa_dist and fig_iou_by_type with [H] to correct sections (a9928b9)
- fix: pin figures 4 and 5 with [H] to correct sections (40330ce)
- fix: force tables 4+5 to exact position with [H] and float package (db094f7)
- chore: sync Overleaf submodule after results table fix (1c0b6f6)
- fix: results tables [t] -> [ht] to keep them in their subsections (c91d3bd)
- fix: reposition all figures and tables to correct paper locations (ed00aba)
- fix: change all tables [h] -> [t] for correct column placement (1a95703)
- fix: scale figures to 0.82col, use [t] placement to fix refs bleed (aca2d76)
- docs: Phase 10 complete — paper polish, figures, README (048867f)
- docs: update Phase 10 spec — add TG5-8 (line numbers, overflow, BMVC format, style audit) (c674a0b)
- docs: Phase 10 spec — paper figures, factual fixes, README (f6c97c8)
- docs: Phase 9 complete — roadmap ✅, changelog updated (1fc68ad)
- feat: add --output flag to run_part1 and reproduce_tables (8308032)
- feat: Phase 9 complete — run_part1, reproduce_tables, results.md (36694d1)
- docs: revise Phase 9 spec — reflect existing files and stale API (78fa01a)
- docs: Phase 9 spec — deliverables plan, requirements, validation (79430dd)
- docs: update roadmap Phase 9.2 complete, add Phase 8 changelog (3d786fe)
- feat: Phase 8.2 complete — full eval results + paper updates (883de61)
- feat: rewrite run_part2.py to use evaluate_all API (d8a3bad)
- feat: Phase 8.1 complete — evaluator, tests, specs (fa222ec)

## 2026-05-15 (Phase 10)

### Report & README

- `overleaf/assets/vqa_benchmark.tex` — removed `\bmvcreviewcopy{??}` to eliminate blue review line numbers.
- `overleaf/assets/sections/pipeline.tex` — fixed stale count (720→810 × 2=1,620 calls), fixed `\texttt{gpt-4o-mini}` overfull hbox in §3.5, added line break between long ChromaDB collection name tokens.
- `overleaf/assets/sections/benchmark.tex` — replaced figure placeholder with `\includegraphics{fig_qa_dist}`, fixed `\shortcite` → `\cite` with `\etal`, fixed bare `e.g.,` → `\eg`, fixed schema line overflow.
- `overleaf/assets/sections/results.tex` — replaced figure placeholder with `\includegraphics{fig_iou_by_type}`, updated caption with real percentages (+183%, +26%), removed stale TBD comment, rewrote failure mode prose to active voice (active-sentence leads, removed italics from failure mode names, split run-on sentences).
- `overleaf/assets/sections/conclusion.tex` — rewrote opening paragraph: "We introduce LectureBench..." (active voice, concrete pair count), replaced vague gains sentence with specific percentages (65% visual, 13% text).
- `overleaf/assets/sections/abstract.tex` — applied 2 style edits: concrete numbers upfront, cleaner visual-split framing.
- `overleaf/assets/sections/introduction.tex` — applied 7 style edits: active voice ("we anchor", "we evaluate"), concrete multi-hop percentage (56.8%), split compound sentences, tightened visual-contribution framing.
- `scripts/generate_figures.py` — new script: generates `fig_qa_dist` (horizontal bar chart) and `fig_iou_by_type` (grouped bar chart, Config 1 vs 2) as both PDF and PNG.
- `overleaf/assets/images/fig_qa_dist.{pdf,png}` — QA type distribution figure.
- `overleaf/assets/images/fig_iou_by_type.{pdf,png}` — tIoU by question type figure.
- `README.md` — filled key results table, removed stale Phase 8 placeholder note.
- `requirements.txt` — added `matplotlib>=3.8.0`.

## 2026-05-15 (Phase 9)

### Deliverable Scripts

- `run_part1.py` — rewrote stale placeholder to use correct API: `Retriever(mode, cfg=cfg)`, `retriever.query()`, module-level `generate()` function, `GeneratorResult.answer`/`.citations`. Verified end-to-end with real ChromaDB + OpenAI calls across 3 demo questions.
- `scripts/reproduce_tables.py` — rewrote stale placeholder (wrong aggregated-dict format) to read flat `results` array from `evaluation_results.json`, joined with `benchmark_v1.json` for question types. Three functions: `reproduce_table_1` (overall, n=810), `reproduce_table_2` (tIoU by type), `reproduce_table_3` (HR@k by type).
- `results.md` — filled all TBD cells from `evaluation_results.json`. Added narrative per table. Discovered Config 2 is marginally lower on multi-hop tIoU (0.223 vs 0.236) and HR@3 for text — disclosed and explained.
- Both scripts gained `--output <path>` flag to tee stdout to a file; default is stdout only.
- `tests/test_run_part1.py` — 7 new tests; full suite 111/111 passing.

## 2026-05-15 (Phase 8)

### Evaluation (Phase 8)

- `src/evaluator.py` — full evaluation module: temporal IoU, IoU@0.3/0.5, Hit Rate@k (k=1,3,5), multi-hop per-hop IoU, union IoU, complete retrieval rate, LLM-judge (G-Eval, 2 judges: Claude Sonnet 4.6 + GPT-4o), Krippendorff's α, citation accuracy. JSONL checkpointing with resume.
- `run_part2.py` — rewritten to use `evaluate_all()` / `evaluate_question()` API; `--limit` and `--video_id` flags for smoke tests; partial results saved to separate file to protect canonical output.
- Fixed `src/generator.py` `_parse_llm_output`: LaTeX escape sanitization now uses `(?<!\\)` lookbehind to avoid corrupting already-valid `\\(` sequences; tries `json.loads` first, sanitizes only on failure.
- Fixed `src/evaluator.py` `_parse_judge_response`: 3-stage fallback — (1) standard JSON parse, (2) fix unquoted keys `{C1: 4}` → `{"C1": 4}`, (3) regex extraction without braces.
- `tests/test_evaluator.py` — 40 new tests; full suite 104/104 passing.
- Full evaluation run: 810 pairs × 2 configs = 1,620 evaluations. Results saved to `data/benchmark/evaluation_results.json`.
- Paper (Overleaf): filled all TBD result cells, fixed factual errors (720→810 pairs, 67%→56.8% multi-hop, 455/819→455/810 visual), added GitHub URL to abstract.

### Key results

| Metric | Config 1 (Transcript-Only) | Config 2 (+Frames) |
|---|---|---|
| Mean tIoU | 0.154 | 0.198 (+29%) |
| IoU@0.3 | 0.228 | 0.279 |
| IoU@0.5 | 0.091 | 0.126 |
| Hit Rate@5 | 0.515 | 0.565 |
| LLM-Judge (1–5) | 3.03 | 3.56 |
| Citation Accuracy | 23.4% | 31.6% |

Visual-dependent questions: tIoU +65% (0.129 → 0.213). Config 2 wins on all metrics.

## 2026-05-14

- chore: ignore literature-review/, untrack Excel and MD files (da7777c)
- docs: update roadmap Phase 7.4/7.5 complete, add regen raw + review logs (0350d12)

## 2026-05-14

- feat: Phase 7.5 span precision audit, update paper limitation (fcd93d5)

## 2026-05-14

- feat: Phase 7.4 build/validate benchmark, 810 final QA pairs (41e9c7a)

## 2026-05-14

- docs: update visual QA percentage from 60% target to 55.6% actual (9da02c4)

## 2026-05-14

- docs: add post-evaluation reminder notes to Phase 9 and 10 (4083589)
- docs: mark Phase 7.3 complete, update roadmap with final QA counts (2f06abe)

## 2026-05-14

- docs: add paper figures/tables and failure case example (451708d)

## 2026-05-14

- docs: update roadmap for no-discard policy and check_coverage step (2d5cde8)

## 2026-05-14

- feat: add coverage check script, remove lecture discard threshold (1c7c8ae)

## 2026-05-14

- docs: add paper reminder for low QA count fallback defense (a9a2b35)
- docs: add cross-benchmark density defense to benchmark section (f954e10)

## 2026-05-14

- docs: add end-to-end reproduction steps to README (034db40)

## 2026-05-14

- docs: rewrite README for LectureBench submission (2f5e959)

## 2026-05-14

- feat: Phase 10 paper sections complete with placeholders (a63d353)

## 2026-05-14

- feat: Phase 9 placeholder scripts and results tracker (11c157b)

## 2026-05-14

- docs: update changelog through Phase 7.3 pre-regen fixes (097babb)

## 2026-05-14

- fix: pre-regeneration fixes for Phase 7.3 QA review (20ff7b3)

## 2026-05-14

- docs: add question descriptions to all Q sections in phase 7.3 lit review (7b52d68)

## 2026-05-14

- docs: downgrade D8b human spot-check to optional note in all specs (6e62c34)

## 2026-05-14

- docs: sync specs with Phase 7.3 run results and lit review updates (91537dd)

## 2026-05-14

- docs: remove duplicate CALCE entry from main Paper Dictionary (896d25c)

## 2026-05-14

- docs: add missing URLs and fix venues in main Paper Dictionary (ee6b9ff)

## 2026-05-14

- docs: add Venue/Peer-Reviewed column to main Paper Dictionary (f7bc72f)

## 2026-05-14

- docs: correct RAGAS venue to EACL 2024 System Demonstrations track (318e1a3)

## 2026-05-14

- docs: add Venue/Peer-Reviewed column to phase 7.3 Paper Dictionary (e9b1589)

## 2026-05-14

- docs: fix 8 discrepancies in phase 7.3 lit review report (8e1ebce)

## 2026-05-14

- docs: rewrite abstract following top-venue benchmark paper conventions (03a2893)

## 2026-05-14

- docs: update benchmark.tex LLM Review section for Phase 7.3 (da18882)

## 2026-05-14

- docs: merge chunk-as-ground-truth argument into curation support section (60ab5d7)

## 2026-05-14

- docs: add 'What Supports LLM-Only Curation' subsection (aaa4829)

## 2026-05-14

- docs: clarify RAGAS and Ho et al. as partial support in curation table (09ff92a)

## 2026-05-14

- docs: add LLM-only curation gap section to lit review (f5f00b6)

## 2026-05-14

- docs: update lit review Q1-Q6 with peer-reviewed citations (c257293)

## 2026-05-13

- feat: add Phase 7.3 reviewer tests, 8/8 passing (Group 4) (f19f047)

## 2026-05-13

- feat: implement Phase 7.3 core reviewer and review script (Group 3) (838e7d5)

## 2026-05-13

- feat: add reviewer prompt templates for Phase 7.3 (Group 2) (b24d775)

## 2026-05-13

- docs: sync all specs with D1 two-call reviewer design (830329e)

## 2026-05-13

- docs: adopt simplified Option C (cross-family C1 check) for Phase 7.3 (67e055d)

## 2026-05-13

- fix: convert Figure 1 PNG to RGB, set 300 DPI (3720b7d)

## 2026-05-13

- feat: add Figure 1 pipeline diagram to paper (31dcd04)

## 2026-05-13

- docs: clarify tIoU@0.3 source in Q6 answer (04c4406)

## 2026-05-12

- docs: add Option C criterion-targeted reliability to lit review (c561800)

## 2026-05-12

- docs: add Lee et al. 2026 to multi-judge lit review (145773a)

## 2026-05-12

- docs: add multi-judge lit review to Phase 7.3 report (331177e)

## 2026-05-12

- feat: add Phase 7.3 LLM review spec (fcbcd2b)

## 2026-05-11

- docs: define Phase 8 LLM judge criteria, add lit review TODO (0524d15)

## 2026-05-11

- docs: add Phase 7.5 span precision audit to roadmap (0cfbaf3)

## 2026-05-11

- docs: Phase 7.3 lit review, paper formatting rules, sync fixes (08edc0d)

## 2026-05-11

- docs: add Phase 7.3 context for post-context-clear pickup (46fb5c4)
- docs: strengthen EduVidQA contrast in related work (79b15f1)

## 2026-05-10

- docs: fix frame interval and fill corpus duration in paper (4bc3877)
- docs: update changelog through Phase 7.2 (fa4c9d3)

## 2026-05-10

- chore: sync specs to current project state (b7b22ef)
- feat: complete QA generation for all 60 lectures (c915f7f)
- feat: QA generation pipeline (Phase 7.1-7.2) (b5f8fd4)
- chore: commit config.py qa model field and overleaf submodule pointer (4bb9b64)
- docs: update qa_generation model to claude-sonnet-4-6 (a362de8)
- Update Overleaf submodule - 2026-05-10 02:53 (ccd1c2e)
- docs: mark Phase 6 validation complete, update changelog (eabf86a)
- Update Overleaf submodule - 2026-05-10 02:33 (78c3d97)
- docs: update changelog and roadmap for Phase 6 and benchmark note (58b86ec)

## 2026-05-08

- docs: sync tech-stack versions and frame interval (c14814f)

## 2026-05-10

- feat: generator module (Phase 6) (d92ccef)
- docs: add model asymmetry justification to benchmark.tex and roadmap (a8a7f04)
- docs: add generator model choice justification to pipeline.tex (725bce5)
- test: smoke test passed — gpt-4o-mini, mit_6046_lec10, span 105.0s–185.0s

## 2026-05-08

- feat: RAG ingestion, both configs (Phase 5) (635af03)

## 2026-05-08

- docs: update CHANGELOG.md (22d6993)

## 2026-05-08

- docs: record open decision on Phase 7.3 QA review method (255a97d)
- docs: update CHANGELOG.md — fix (latest) tag, add phase 4.2 notes (4ff36dd)

## 2026-05-08

- docs: mark pipeline run spec complete (phases 2.2–4.2) (8df7e4c)
- feat: run full data pipeline (phases 2.2–4.2) (8a811bb)

## 2026-04-26

- docs: add Overleaf sync rule to CLAUDE.md and roadmap (453903b)
- docs: reframe as conference paper; remove Phase 8 cross-validation (06fe49a)
- docs: add per-phase paper writing reminders to roadmap (c567527)
- docs: sync Overleaf fixes, update roadmap and changelog (206ce17)
- docs: update CHANGELOG.md for Overleaf submodule (a770067)

## 2026-04-26

- fix: BMVC compliance (ack, tables) + bib missing entries (a95ebc8)
- docs: sync Overleaf submodule — paper skeleton (83f724c)
- docs: add Specs & Roadmap section to CLAUDE.md (7b6d14c)

## 2026-04-26

- docs: reflect Overleaf submodule in specs (e469714)
- docs: update CHANGELOG.md (2b08e1a)
- Add Overleaf submodule under overleaf/ (e12f6e8)

## 2026-04-23

- docs: fix roadmap discrepancies in phases 1-4 (75ef8f4)
- docs: add frame interval and overlap rationale to Phase 4.2 (a2faf93)

## 2026-04-22

- docs: update CHANGELOG.md for Phase 1 completion (3f7ae76)
- docs: mark Phase 1 complete in roadmap (e0e3213)

## 2026-04-22

- data: all 60 VTTs + metadata downloaded (Phase 1.2 ✅) (6e7492b)
- fix: add webm support and initialize downloaded field for all entries (f021580)
- docs: mark Phase 1.1 complete in roadmap (d4fd51a)
- feat: download_videos.py + Phase 1.1 feature spec (Phase 1.1) (969d75d)
- docs: remove log.md (migrated to CHANGELOG.md), fix tech-stack header (aa1825c)

## 2026-04-21

- docs: add CHANGELOG.md with git history, decisions, and observations (8d2fdba)

## 2026-04-21

- docs: add deliverables, lit review, decisions log, and observations (cad5a5c)
- docs: add config.yaml reference and directory structure to tech-stack (979887c)
- docs: add multihop metric formulas and report tables to roadmap (571c065)
- docs: add specs/corpus.md with 60-video library and licensing (dc2a000)
- docs: add specs constitution (mission, tech-stack, roadmap) (3227be4)
- feat: expand to 60 lectures, replace BLIP with Qwen2-VL (52b1a4c)

## 2026-04-20

- docs: update plan for Phase 4 completion and NYU lectures (de77578)
- feat: frame caption pipeline complete (Phase 4) (1703106)
- feat: add NYU lectures + frame caption pipeline (Phase 4) (695e069)
- docs: add scale context note to PROJECT_PLAN.md (776d637)
- docs: sync PROJECT_PLAN.md with phases 2 and 3 (26806f4)
- feat: chunking pipeline (Phase 3) (6185799)
- feat: transcription pipeline (Phase 2) (7d805a2)
- docs: update literature review and project plan (9af7363)

## 2026-04-19

- feat: Phase 0+1 complete — literature review and video collection (eacb15d)

## 2026-04-18

- feat: project skeleton and documentation (31571fc)

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Track C selected | Research exposure + co-authorship eligibility |
| 2026-04-18 | Chunking: 45s window, 10s overlap | Prescribed by assignment |
| 2026-04-18 | Embedding: all-MiniLM-L6-v2 | Prescribed by assignment |
| 2026-04-20 | Transcription: YouTube auto-captions (Option A) | Quality spot-checked at 20-min mark; 0 errors on technical terms (eigenvectors, memoization, hash table verified). Saves ~1–2 GPU-hours per lecture vs. Whisper |
| 2026-04-20 | Generator model: gpt-4o-mini | Cost-effective; reliable structured JSON output |
| 2026-04-21 | Frame captioner: Qwen2-VL-7B-Instruct, Approach A (text augmentation) | Strongest OCR/math on lecture slides; Apache 2.0; fits on one A100 (14 GB); Approach A keeps both ChromaDB collections under the same embedding model as prescribed |
| 2026-04-21 | Expanded to 60 lectures | Advisor requires 60+ videos for full venue publication |
| 2026-04-21 | Benchmark license: CC BY-NC-SA 4.0 | Required by ShareAlike clause — derived transcript/frame-caption content from MIT OCW and Stanford SEE videos must carry same license |

---

## Notes & Observations

### Transcription (Phase 2)

- YouTube auto-captions chosen over Whisper — pre-downloaded VTTs were clean on technical terms. Saves ~1–2 GPU-hours per lecture.
- VTT "rolling caption" format alternates word-timing cues (~2s) with display cues (~10ms). The display cues carry one clean subtitle phrase each — these are the source of transcript segments.
- Segment granularity: ~3s per phrase → 1,569 segments for an 80-min lecture.
- Results: `mit_6046_lec10`: 1,569 segments | `mit_18065_lec06`: 909 segments | `nyu_dl_week6`: 1,761 segments | `nyu_dl_week7`: 1,966 segments
- Quality check: MIT lectures spot-checked at 20-min mark; 0 errors on technical terms. NYU lectures: quality not yet verified (`caption_quality_check.decision: "pending"` in metadata).

### Chunking (Phase 3)

- Pure time-based windowing: segment belongs to chunk if `segment.start ∈ [win_start, win_start+45s)`. No silence-gap detection needed.
- Overlap confirmed by unit test: segment at 40s appears in both chunk [0–45s) and chunk [35–80s).
- Chunk counts: `mit_6046_lec10` 138 | `mit_18065_lec06` 92 | `nyu_dl_week6` 153 | `nyu_dl_week7` 167 (~97 min actual; metadata says 75 min — verify with `yt-dlp --get-duration`)
- 8/8 unit tests passing.

### NYU Lectures

- Downloaded as MKV (AV1 codec) — cv2 cannot decode AV1; frame extractor uses ffmpeg instead.
- `nyu_dl_week7` duration discrepancy: metadata lists 75 min, chunk count implies ~97 min actual. Verify before Phase 4.

### Frame Captioning (Phase 4)

- Qwen2-VL-7B-Instruct (Apache 2.0) replaces BLIP base — reads slide text, equations, whiteboard diagrams.
- Frame extraction via ffmpeg at 15s intervals (changed from 30s); all-in-window assignment gives ~3 captions per 45s chunk.
- 60/60 videos captioned; 17,180 total captions. Approach A: captions appended as `[frame caption: ...]` to chunk text, embedded with all-MiniLM-L6-v2 into Collection 2.
