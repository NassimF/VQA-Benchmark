# Phase 10 — Report & README: Plan

## Task Group 1 — Fix factual errors in existing paper sections

Files: `overleaf/assets/sections/pipeline.tex`, `overleaf/assets/sections/conclusion.tex`, `overleaf/assets/sections/results.tex`

1. `pipeline.tex`: "720 questions × 2 configurations = 1,440 calls" → "810 × 2 = 1,620"
2. `conclusion.tex`: "~720 LLM-reviewed question--answer pairs" → "810"
3. `results.tex`: remove stale comment `% Fill in all TBD placeholders after Phase 9 (evaluation).`

**Done when:** No stale counts (720, 1440) remain in any section.

---

## Task Group 2 — Generate figures with matplotlib

File: `scripts/generate_figures.py` (new)

1. **Figure A — QA type distribution** (`overleaf/assets/images/fig_qa_dist.pdf` + `.png`):
   Horizontal bar chart of accepted pair counts by question type.
   Data source: `data/benchmark/benchmark_v1.json`.
   Types: multi-hop-visual (320), visual (135), multi-hop (140), text (103), unanswerable (112).

2. **Figure B — tIoU by question type** (`overleaf/assets/images/fig_iou_by_type.pdf` + `.png`):
   Grouped bar chart, Config 1 vs Config 2, one group per question type (exclude unanswerable).
   Data source: `data/benchmark/evaluation_results.json` + `benchmark_v1.json`.
   Add horizontal dotted line at tIoU=0.3 (primary IoU threshold).

3. Academic style: no chartjunk, spine on left/bottom only, 9pt font, bar value annotations.
4. Save as PDF (vector for LaTeX) and PNG (preview).

**Done when:** Both figures exist in `overleaf/assets/images/` and render correctly.

---

## Task Group 3 — Wire figures into paper sections

Files: `overleaf/assets/sections/benchmark.tex`, `overleaf/assets/sections/results.tex`

1. `benchmark.tex`: replace `\fbox{\rule{0pt}{3cm}\rule{8cm}{0pt}}` with
   `\includegraphics[width=\columnwidth]{images/fig_qa_dist}`. Update caption with actual counts.
2. `results.tex`: replace `\fbox{\rule{0pt}{3.5cm}\rule{8cm}{0pt}}` with
   `\includegraphics[width=\columnwidth]{images/fig_iou_by_type}`. Update caption.

**Done when:** No `\fbox{\rule...}` figure placeholders remain in any section.

---

## Task Group 4 — README: fill results table and fix stale note

File: `README.md`

1. Fill the 4-metric key results table with real numbers (tIoU, IoU@0.3, HR@5, LLM-judge).
2. Remove the `*(Filled in after Phase 8 evaluation)*` line above the table.

**Done when:** No dashes or stale notes remain in the results section.

---

## Task Group 5 — Remove blue line numbers (review ruler)

File: `overleaf/assets/vqa_benchmark.tex`

The `\bmvcreviewcopy{??}` command on line 4 activates BMVC review mode, which renders
a blue line-number ruler on every page. For clean reading (course submission), comment it out.

1. Comment out `\bmvcreviewcopy{??}` → `%\bmvcreviewcopy{??}  % remove for clean read; restore for BMVC submission`

**Done when:** Overleaf PDF no longer shows blue line numbers.

---

## Task Group 6 — Fix text overflow (overfull hbox)

Files: all `overleaf/assets/sections/*.tex`

The user identified `\texttt{gpt-4o-mini}` in pipeline.tex §3.5 (Answer Generation, first paragraph)
as overflowing the column margin. Scan all sections for similar issues.

1. Fix `\texttt{gpt-4o-mini}` overflow: wrap as `\mbox{\texttt{gpt-4o-mini}}` or restructure sentence.
2. Scan all sections for other long `\texttt{...}` tokens, long URLs, and compound model names
   that may cause overfull hbox warnings. Fix each with `\allowbreak`, `\mbox{}`, or rephrasing.
3. Verify: no visible margin overflow in Overleaf PDF preview.

**Done when:** No text visibly extends beyond the column border in any section.

---

## Task Group 7 — BMVC format compliance check

Reference: `overleaf/assets/bmvc_review.tex` (official BMVC author guidelines)

Compare `vqa_benchmark.tex` and all section files against BMVC requirements:

1. **Page limit** — count paper pages (excl. bibliography); must be ≤14.
2. **Anonymization** — author list suppressed via `\bmvcreviewcopy` (currently active). Verify no author name or institution appears in the body text.
3. **Citation style** — numbered natbib (`\cite{key}`). Check all citations use this form; no `\citep`, no manual `[N]`.
4. **Figure formatting** — captions below figures, centered, using `\caption{}`. No caption above.
5. **Table formatting** — captions below tables (BMVC convention); `\hline\hline` for double rule after header.
6. **Section numbering** — all sections and subsections numbered (no `\section*`).
7. **Running head** — `\runninghead` set correctly.
8. **`\eg`, `\etal` macros** — used consistently instead of manual `e.g.`, `et al.`.
9. **References** — bibliography compiles without errors; all `\cite{}` keys resolve.

Document findings; fix any violations.

**Done when:** All 9 checklist items pass.

---

## Task Group 8 — Writing style audit against top-venue papers

Reference papers (from `literature-review/literature_review_report.md`):
Fetch and read the introduction and related work of each paper listed below, then compare
writing style against each of our paper sections.

Papers to analyze (fetch from arXiv):
- EgoSchema (arXiv:2308.09126) — NeurIPS 2024
- LongVidSearch (arXiv:2603.14468) — closest structural match
- EduVidQA (arXiv:2509.24120) — closest domain match
- RAG original (arXiv:2005.11401) — NeurIPS 2020
- VideoRAG (arXiv:2501.05874) — ICLR 2025

For each paper, note:
1. **Claim precision** — are contributions stated as concrete, falsifiable claims or vague assertions?
2. **Active vs passive voice** — top venues prefer active ("We show", "We introduce") for contributions.
3. **Hedging language** — inappropriate hedges ("seems to", "might", "could potentially") vs appropriate ones.
4. **Sentence length and rhythm** — vary sentence length; avoid back-to-back long sentences.
5. **Terminology consistency** — same term used every time (no mixing "temporal IoU" / "tIoU" / "temporal overlap").
6. **Transition quality** — each paragraph ends with a bridge to the next idea.

Apply findings as targeted edits to our sections (abstract, introduction, pipeline, benchmark, results, conclusion).

**Done when:** Each paper has been read and any identified improvements applied to our sections.

---

## Task Group 9 — Overleaf sync, roadmap, changelog, merge

1. Run `cd overleaf && ./push_to_overleaf.sh` after all edits to `overleaf/assets/`.
2. Update `specs/roadmap.md`: 10.1 ✅, 10.2 ✅, Phase 10 header ✅.
3. Add Phase 10 entry to `CHANGELOG.md`.
4. Commit, push, merge `phase-10-paper` into `main`, delete branch.
