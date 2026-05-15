# Phase 10 — Report & README: Validation

All checks must pass before merging `phase-10-paper` into `main`.

---

## V1 — No stale counts in paper sections

```bash
grep -n "1,440\|1440\|~720\| 720 " overleaf/assets/sections/*.tex
```
**Expected:** No matches.

---

## V2 — Figures generated and present

```bash
ls overleaf/assets/images/fig_qa_dist.pdf \
      overleaf/assets/images/fig_qa_dist.png \
      overleaf/assets/images/fig_iou_by_type.pdf \
      overleaf/assets/images/fig_iou_by_type.png
```
**Expected:** All four files exist.

---

## V3 — No fbox figure placeholders remain

```bash
grep -n "fbox{\\\\rule" overleaf/assets/sections/benchmark.tex \
                        overleaf/assets/sections/results.tex
```
**Expected:** No matches. (Content fboxes in the QA example and failure case are fine.)

---

## V4 — Figure values match evaluation_results.json

Visual inspection: Figure B "visual" bar for Config 2 should read ~0.25; "multi-hop-visual"
Config 1 bar should read ~0.16. Cross-check against `python scripts/reproduce_tables.py`.

---

## V5 — README results table filled, stale note removed

```bash
grep -c " — " README.md     # table dashes
grep -c "Filled in after" README.md
```
**Expected:** Both return `0`.

---

## V6 — Blue line numbers removed

Open `overleaf/assets/vqa_benchmark.tex` and confirm:
```
%\bmvcreviewcopy{??}
```
is commented out. Verify in Overleaf PDF: no blue ruler on left margin.

---

## V7 — No visible text overflow

Open the Overleaf PDF. Scan all pages: no text, `\texttt{}` token, or URL visibly extends
beyond the right column border. Specifically check pipeline.tex §3.5 first paragraph.

---

## V8 — BMVC format compliance (all 9 items)

- [ ] Page count ≤14 (excluding bibliography)
- [ ] No author names/institutions in body text: `grep -r "Faridnia\|UTSA\|University of Texas" overleaf/assets/sections/`
- [ ] No `\citep` or manual `[N]` citations: `grep -r "\\\\citep\|\[1\]\|\[2\]" overleaf/assets/sections/`
- [ ] All figures: caption below, `\caption{}` used
- [ ] All tables: caption below
- [ ] No `\section*` (unnumbered sections): `grep -r "section\*" overleaf/assets/sections/`
- [ ] `\runninghead` set in vqa_benchmark.tex
- [ ] No bare `e.g.` or `et al.`: `grep -r "e\.g\.\|et al\." overleaf/assets/sections/`
- [ ] Bibliography compiles without undefined-reference warnings

---

## V9 — Writing style: no inappropriate hedging in contribution claims

Read the abstract and introduction. Verify:
- [ ] All contribution bullets use active constructions
- [ ] No "seems to", "might", "could potentially" in results claims
- [ ] "temporal IoU" / "tIoU" used consistently (one form per context)

---

## V10 — Full test suite still passes

```bash
/root/miniconda3/envs/vqa-benchmark/bin/python -m pytest tests/ -q
```
**Expected:** 111 passed.

---

## V11 — Overleaf sync pushed

```bash
cd overleaf && git log --oneline -1
```
**Expected:** Most recent commit is today's date and covers all Phase 10 edits.

---

## V12 — Roadmap and changelog updated

- `specs/roadmap.md`: 10.1 ✅, 10.2 ✅, Phase 10 header ✅
- `CHANGELOG.md`: Phase 10 entry present with date 2026-05-15
