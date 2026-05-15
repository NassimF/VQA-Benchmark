# Phase 10 — Report & README: Requirements

## Scope

| Task | File | Current state |
|------|------|---------------|
| 10.1a | Fix stale numbers in paper | pipeline.tex (1440→1620), conclusion.tex (720→810) |
| 10.1b | Generate figures | scripts/generate_figures.py (new) |
| 10.1c | Wire figures into sections | benchmark.tex, results.tex fbox → includegraphics |
| 10.2  | README key results table | Dashes → real numbers; stale note removed |

The paper's `\includegraphics{images/fig1_pipeline}` already exists — no change needed.

---

## Figure A — QA Type Distribution (benchmark.tex)

**Purpose:** Show the question type breakdown across the 810 accepted pairs.

**Data:** `data/benchmark/benchmark_v1.json` → count per `question_type`.

| Type | Count |
|------|-------|
| multi-hop-visual | 320 |
| visual | 135 |
| multi-hop | 140 |
| text | 103 |
| unanswerable | 112 |

**Design decisions:**
- Horizontal bar chart (type labels fit better horizontally)
- Single color per bar (no Config split — this is a corpus stat, not an eval result)
- Annotate each bar with its count
- Academic style: no grid, spine on left/bottom only, 9pt font
- Output: `fig_qa_dist.pdf` + `fig_qa_dist.png` in `overleaf/assets/images/`

---

## Figure B — tIoU by Question Type (results.tex)

**Purpose:** Show Config 1 vs Config 2 mean tIoU per question type — the visual contribution
claim in one glance.

**Data:** `data/benchmark/evaluation_results.json` + `benchmark_v1.json` for type mapping.

| Type | Config 1 tIoU | Config 2 tIoU |
|------|:---:|:---:|
| multi-hop-visual | 0.156 | 0.196 |
| visual | 0.066 | 0.253 |
| multi-hop | 0.236 | 0.223 |
| text | 0.319 | 0.317 |

**Design decisions:**
- Grouped bar chart: 4 question-type groups × 2 bars (Config 1 = blue, Config 2 = orange)
- Exclude unanswerable (tIoU=0 by definition, not informative)
- Annotate bars with values
- Add horizontal dotted line at tIoU=0.3 (the primary IoU threshold)
- Academic style matching Figure A
- Output: `fig_iou_by_type.pdf` + `fig_iou_by_type.png` in `overleaf/assets/images/`

---

## Paper section edits

### pipeline.tex
- Line ~97: "720 questions × 2 configurations = 1,440 calls" → "810 × 2 = 1,620"

### conclusion.tex
- Line ~3: "~720 LLM-reviewed" → "810"

### results.tex
- Remove stale comment `% Fill in all TBD placeholders after Phase 9 (evaluation).`
- Replace fbox with `\includegraphics[width=\columnwidth]{images/fig_iou_by_type}`

### benchmark.tex
- Replace fbox with `\includegraphics[width=\columnwidth]{images/fig_qa_dist}`

---

## README

Fill this table with real numbers (from `evaluation_results.json`):

| Metric | Config 1 | Config 2 |
|---|---|---|
| Mean Temporal IoU | 0.154 | 0.198 |
| IoU@0.3 | 0.228 | 0.279 |
| Hit Rate@5 | 0.515 | 0.565 |
| LLM-Judge Score (1–5) | 3.03 | 3.56 |

Remove the `*(Filled in after Phase 8 evaluation)*` line above the table.

---

## Out of scope
- Writing new paper text (all sections already written end-to-end)
- Changing any evaluation results
- README full audit (separate task if needed)
