# Phase 10 — Report & README: Plan

## Task Group 1 — Fix factual errors in existing paper sections

Files: `overleaf/assets/sections/pipeline.tex`, `overleaf/assets/sections/conclusion.tex`

1. `pipeline.tex` line ~97: "720 questions × 2 configurations = 1,440 calls" → "810 × 2 = 1,620"
2. `conclusion.tex` line ~3: "~720 LLM-reviewed question--answer pairs" → "810"
3. Remove stale comment in `results.tex` line 6: `% Fill in all TBD placeholders after Phase 9`

**Done when:** No stale numbers remain in any section.

---

## Task Group 2 — Generate figures with matplotlib

File: `scripts/generate_figures.py` (new)

1. **Figure A — QA type distribution** (`overleaf/assets/images/fig_qa_dist.pdf`):
   Bar chart of accepted pair counts by question type across 60 lectures.
   Data source: `data/benchmark/benchmark_v1.json`.
   Types: multi-hop-visual (320), visual (135), multi-hop (140), text (103), unanswerable (112).

2. **Figure B — tIoU by question type** (`overleaf/assets/images/fig_iou_by_type.pdf`):
   Grouped bar chart, Config 1 vs Config 2, one group per question type.
   Data source: `data/benchmark/evaluation_results.json` + `benchmark_v1.json`.
   Types: multi-hop-visual, visual, multi-hop, text (exclude unanswerable — tIoU=0 by definition).

3. Save both as PDF (vector, scales cleanly in LaTeX) and PNG (for preview).
4. Use a clean academic style (no chartjunk; label values on bars).

**Done when:** Both files exist in `overleaf/assets/images/` and compile without error in LaTeX.

---

## Task Group 3 — Wire figures into paper sections

Files: `overleaf/assets/sections/benchmark.tex`, `overleaf/assets/sections/results.tex`

1. `benchmark.tex`: replace `\fbox{\rule{0pt}{3cm}\rule{8cm}{0pt}}` with
   `\includegraphics[width=\columnwidth]{images/fig_qa_dist}`.
   Update caption to include actual counts.
2. `results.tex`: replace `\fbox{\rule{0pt}{3.5cm}\rule{8cm}{0pt}}` with
   `\includegraphics[width=\columnwidth]{images/fig_iou_by_type}`.
   Update caption.

**Done when:** Both sections reference real figures; no fbox figure placeholders remain.

---

## Task Group 4 — README: fill results table and fix stale note

File: `README.md`

1. Fill the 4-metric key results table with real numbers from `evaluation_results.json`.
2. Remove the `*(Filled in after Phase 8 evaluation)*` note.

**Done when:** `grep -c "\-\-\-" README.md` returns 0 in the results table rows.

---

## Task Group 5 — Overleaf sync and commit

1. Run `cd overleaf && ./push_to_overleaf.sh` after all edits to `overleaf/assets/`.
2. Update `specs/roadmap.md`: 10.1 ✅, 10.2 ✅, Phase 10 header ✅.
3. Add Phase 10 entry to `CHANGELOG.md`.
4. Commit, push, merge into `main`, delete branch.
