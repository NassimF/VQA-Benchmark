# Phase 9 — Deliverable Scripts: Validation

All checks must pass before merging `phase-9-deliverables` into `main`.

---

## V1 — run_part1.py: hardcoded examples run end-to-end

```bash
python run_part1.py
```

**Expected:** Prints output for 3 hardcoded questions. For each question and each config:
- Config label header
- Up to 4 retrieved chunks: `[video_id @ mm:ss–mm:ss] <first 80 chars>`
- Generated answer (1–3 sentences)
- Formatted citations with YouTube deep links

No exception. Uses real retriever (ChromaDB) and real OpenAI call.

---

## V2 — run_part1.py: --question flag works

```bash
python run_part1.py --question "What is singular value decomposition?"
```

**Expected:** Same format as V1 for the provided question. No hardcoded examples shown.

---

## V3 — run_part1.py: API surface matches actual modules

Manually verify in the source:
- [ ] `from src.generator import generate` (function, not class)
- [ ] `Retriever("transcript_only", cfg=cfg)` and `Retriever("transcript_plus_frames", cfg=cfg)`
- [ ] `retriever.query(question, video_id=video_id)` (not `.retrieve()`)
- [ ] `result.answer` and `result.citations` used for output

---

## V4 — reproduce_tables.py: all three tables print

```bash
python scripts/reproduce_tables.py
```

**Expected:**
- Three tables: Table 1 (overall, n=810), Table 2 (tIoU by type), Table 3 (HR@k by type).
- Table 1 Config 1 mean tIoU = 0.154, Config 2 = 0.198 (±0.001 rounding).
- Table 2 "all visual" row: Config 1 = 0.129, Config 2 = 0.213 (±0.001).
- No exceptions, no API calls, exits with code 0.

---

## V5 — reproduce_tables.py: spot-check two cells

```python
import json, numpy as np
results = json.loads(open("data/benchmark/evaluation_results.json").read())["results"]
benchmark = json.loads(open("data/benchmark/benchmark_v1.json").read())
qa_type = {qa["qa_id"]: qa["question_type"] for qa in benchmark["qa_pairs"]}

# Table 2: visual single-hop tIoU, Config 2
subset = [r for r in results if r["config"] == "transcript_plus_frames"
          and qa_type.get(r["qa_id"]) == "visual"]
assert abs(np.mean([r["temporal_iou"] for r in subset]) - 0.213) < 0.05

# Table 3: multi-hop HR@5, Config 1
subset = [r for r in results if r["config"] == "transcript_only"
          and qa_type.get(r["qa_id"]) in {"multi-hop-visual", "multi-hop"}]
assert abs(np.mean([r["hit_rate_at_5"] for r in subset]) - 0.676) < 0.01
```

---

## V6 — results.md: no TBD cells remain

```bash
grep -c "TBD" results.md
```

**Expected:** `0`

Also verify:
- [ ] Table 1 overall: Config 1 tIoU=0.154, Config 2=0.198
- [ ] Table 2 "all visual" row: Config 1=0.129, Config 2=0.213
- [ ] Multi-hop IoU@0.5 anomaly disclosed (Config 2 marginally lower)
- [ ] Reproduction Status rows all ✅
- [ ] "Last updated" set to 2026-05-15

---

## V7 — results.md numbers match reproduce_tables.py output

Run `python scripts/reproduce_tables.py` and compare each cell manually against results.md.
Every value must match within rounding (±0.001).

---

## V8 — Full test suite still passes

```bash
/root/miniconda3/envs/vqa-benchmark/bin/python -m pytest tests/ -v
```

**Expected:** All tests pass (≥104). No regressions.

---

## V9 — Roadmap and changelog updated

- `specs/roadmap.md`: 9.1 ✅, 9.3 ✅, 9.4 ✅, Phase 9 header ✅
- `CHANGELOG.md`: Phase 9 entry with date 2026-05-15
