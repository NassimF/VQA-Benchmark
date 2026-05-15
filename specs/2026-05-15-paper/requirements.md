# Phase 10 — Report & README: Requirements

## Scope

| Task | File(s) | Current state |
|------|---------|---------------|
| TG1 | pipeline.tex, conclusion.tex, results.tex | Stale counts: 720→810, 1440→1620 |
| TG2 | scripts/generate_figures.py (new) | Does not exist |
| TG3 | benchmark.tex, results.tex | Two `\fbox{\rule...}` figure placeholders |
| TG4 | README.md | Results table has dashes; stale note |
| TG5 | vqa_benchmark.tex | `\bmvcreviewcopy{??}` active → blue ruler |
| TG6 | All sections/*.tex | `gpt-4o-mini` overflow in pipeline §3.5 + scan |
| TG7 | All sections/*.tex vs bmvc_review.tex | Format compliance audit |
| TG8 | All sections/*.tex vs top-venue papers | Writing style audit |
| TG9 | Overleaf, roadmap, changelog | Sync and merge |

The pipeline figure already exists at `overleaf/assets/images/fig1_pipeline.png` and
`pipeline.tex` already references it correctly. No change needed there.

---

## TG5 — Line numbers

The BMVC `bmvc2k.cls` activates a blue review ruler (line numbers in the left margin)
whenever `\bmvcreviewcopy{<number>}` is called. This is intended for peer reviewers
to cite line numbers in their comments.

**File:** `overleaf/assets/vqa_benchmark.tex` line 4:
```latex
\bmvcreviewcopy{??}
```

**Fix:** Comment it out with a note:
```latex
%\bmvcreviewcopy{??}  % restore for BMVC submission; comment out for clean reading
```

Note: if actually submitting to BMVC, this must be restored with the assigned paper number.

---

## TG6 — Overflow

The user identified `\texttt{gpt-4o-mini}` in the Answer Generation subsection (pipeline.tex)
as visibly extending past the right column border. This is an "overfull hbox" — LaTeX cannot
find a valid line break inside `\texttt{...}` tokens.

**Known instance:**
- `pipeline.tex` §3.5 (Answer Generation), first paragraph: `\texttt{gpt-4o-mini}` or
  `\texttt{gpt-4o-mini} by default` in a tight line.

**Fix strategy (in order of preference):**
1. Restructure the sentence so the token falls at a natural line break.
2. Wrap: `\mbox{\texttt{gpt-4o-mini}}` — prevents internal break but may push word to next line.
3. Allow break: `\texttt{gpt\allowbreak-\allowbreak4o\allowbreak-\allowbreak mini}` — ugly but effective.

**Scan scope:** All section files. Check for other long `\texttt{...}`, URLs (`\url{...}`),
and compound model names (`all-MiniLM-L6-v2`, `Qwen2-VL-7B-Instruct`) that may also overflow.

---

## TG7 — BMVC Format Compliance

Reference: `overleaf/assets/bmvc_review.tex` (official guidelines).

| Requirement | Source in bmvc_review.tex | Check |
|-------------|--------------------------|-------|
| ≤14 pages (excl. refs) | §1.1 "Paper length" | Count in Overleaf PDF |
| Double-blind: no author names in body | §1.3 "Anonymity" | grep for "Faridnia", "UTSA" in sections/ |
| natbib numbered citations `\cite{}` | §1.5 "Citations" | grep for `\citep`, manual `[N]` |
| Figure captions below, centered | §1.6 implied | Check all `\begin{figure}` |
| Table captions below | BMVC convention | Check all `\begin{table}` |
| All sections numbered | Standard | grep `\section*` |
| `\runninghead` set | vqa_benchmark.tex | Already set: "Faridnia / Long-Lecture Video RAG Benchmark" |
| `\eg`, `\etal` macros | §1.5 "Citations" | grep for `e\.g\.`, `et al\.` in sections/ |
| Bibliography compiles | — | Check for undefined references |

---

## TG8 — Writing Style Audit

**Papers to fetch and read** (arXiv — intro + related work sections only):

| Paper | arXiv ID | Venue | Relevance |
|-------|----------|-------|-----------|
| EgoSchema | 2308.09126 | NeurIPS 2024 | Benchmark paper — compare benchmark construction writing |
| LongVidSearch | 2603.14468 | arXiv 2026 | Closest structural match — compare framing and gap statement |
| EduVidQA | 2509.24120 | arXiv 2025 | Closest domain match — compare QA generation section |
| RAG original (Lewis et al.) | 2005.11401 | NeurIPS 2020 | RAG framing — compare pipeline section |
| VideoRAG (Jeong et al.) | 2501.05874 | arXiv 2025 | Video RAG — compare results section |

**For each paper, evaluate our sections against:**
1. Contribution claims — are ours as concrete and falsifiable?
2. Active voice in contribution statements — "We introduce", "We show", "We measure"
3. No inappropriate hedging in results ("seems to improve" → "improves")
4. Sentence length variation — no 3+ consecutive long sentences
5. Terminology locked — pick one form per term and use it everywhere
6. Paragraph transitions — last sentence of each ¶ bridges to the next

**Output:** A set of targeted edits to our sections. Not a report — applied changes only.

---

## TG2 — Figure Design Decisions

### Figure A: QA Type Distribution

- Horizontal bar chart (type labels readable without rotation)
- Single accent color (no Config split — corpus stat, not eval result)
- Sorted descending by count
- Bar annotations: count + percentage of 810
- Output size: `\columnwidth` wide (~8.5cm for BMVC two-column)

### Figure B: tIoU by Question Type

- Grouped bar chart: 4 question-type groups × 2 bars
- Config 1 = `#4C72B0` (BMVC blue), Config 2 = `#DD8452` (orange) — colorblind-safe pair
- Horizontal dotted reference line at tIoU=0.3 (labeled "IoU@0.3 threshold")
- Bar value annotations (2 decimal places)
- Legend: "Config 1: Transcript-Only" / "Config 2: +Frames"
- Exclude `unanswerable` type (tIoU=0 by definition, not a retrieval failure)
- Output size: `\columnwidth` wide

Both figures: `matplotlib`, `tight_layout()`, saved as PDF + PNG at 300 dpi.

---

## Out of scope

- Rewriting entire sections from scratch (targeted edits only)
- Generating the pipeline figure (already exists)
- Changing evaluation results
- Full README audit (TG4 is targeted fix only)
