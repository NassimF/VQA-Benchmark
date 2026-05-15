# Phase 10 — Report & README: Validation

All checks must pass before merging `phase-10-paper` into `main`.

---

## V1 — No stale numbers in paper sections

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

## V3 — No fbox figure placeholders remain in paper

```bash
grep -n "fbox{\\\\rule" overleaf/assets/sections/benchmark.tex \
                        overleaf/assets/sections/results.tex
```
**Expected:** No matches. (Content fboxes in the QA example and failure case are fine —
those use `\fbox{\begin{minipage}...}`, not `\fbox{\rule...}`.)

---

## V4 — Figure values match evaluation_results.json

Run `python scripts/reproduce_tables.py` and verify Table 2 values match Figure B bars:
- visual Config 2 tIoU = 0.253 ✓
- multi-hop-visual Config 1 tIoU = 0.156 ✓

---

## V5 — README has real results, no stale note

```bash
grep -c "\-\-$\| — $" README.md   # table dashes
grep -c "Filled in after" README.md
```
**Expected:** Both return `0`.

---

## V6 — Overleaf sync pushed

```bash
cd overleaf && git log --oneline -1
```
**Expected:** Most recent commit includes today's date and mentions figures/paper updates.

---

## V7 — Full test suite still passes

```bash
/root/miniconda3/envs/vqa-benchmark/bin/python -m pytest tests/ -q
```
**Expected:** 111 passed (no regressions).

---

## V8 — Roadmap and changelog updated

- `specs/roadmap.md`: 10.1 ✅, 10.2 ✅, Phase 10 header ✅
- `CHANGELOG.md`: Phase 10 entry with date 2026-05-15
