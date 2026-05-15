# Phase 9 — Deliverable Scripts: Validation

All checks must pass before merging `phase-9-deliverables` into `main`.

---

## V1 — run_part1.py: hardcoded examples run end-to-end

```bash
python run_part1.py
```

**Expected:** Prints output for 3 hardcoded questions. Each question shows:
- A header line: `=== Question: <text> ===`
- For each config (`transcript_only`, `transcript_plus_frames`):
  - Config label
  - Up to 4 retrieved chunks: `[video_id @ mm:ss to mm:ss] <first 80 chars of text>`
  - Generated answer (1–3 sentences)
  - Formatted citations with YouTube deep links

No exception, no API mock needed — uses real retriever and real OpenAI/Anthropic calls.

---

## V2 — run_part1.py: --question flag works

```bash
python run_part1.py --question "What is singular value decomposition?"
```

**Expected:** Same output format as V1 but for the provided question. No hardcoded examples shown.

---

## V3 — reproduce_tables.py: all three tables print

```bash
python scripts/reproduce_tables.py
```

**Expected:**
- Three tables printed in sequence: single-hop (n=238), multi-hop (n=460), overall (n=810).
- Config 1 mean tIoU = 0.175 (single-hop), 0.180 (multi-hop), 0.154 (overall) ± 0.001 rounding.
- Config 2 mean tIoU = 0.281 (single-hop), 0.204 (multi-hop), 0.198 (overall) ± 0.001 rounding.
- No exceptions, no API calls, exits with code 0.

---

## V4 — reproduce_tables.py: spot-check values

Manually verify two cells against `evaluation_results.json`:

```python
import json, numpy as np
results = json.loads(open("data/benchmark/evaluation_results.json").read())["results"]
benchmark = json.loads(open("data/benchmark/benchmark_v1.json").read())
qa_type = {qa["qa_id"]: qa["question_type"] for qa in benchmark["qa_pairs"]}

# Single-hop Config 2 LLM-judge
subset = [r for r in results if r["config"] == "transcript_plus_frames"
          and qa_type.get(r["qa_id"]) in {"visual", "text"}]
assert abs(np.mean([r["llm_judge_score"] for r in subset]) - 3.525) < 0.01

# Multi-hop Config 1 Hit Rate@5
subset = [r for r in results if r["config"] == "transcript_only"
          and qa_type.get(r["qa_id"]) in {"multi-hop-visual", "multi-hop"}]
assert abs(np.mean([r["hit_rate_at_5"] for r in subset]) - 0.676) < 0.01
```

---

## V5 — results.md: all four tables present and correct

Open `results.md` and verify:
- [ ] Four markdown tables: Overall, Single-hop, Multi-hop, Visual-dependent
- [ ] Overall Config 1 tIoU = 0.154, Config 2 = 0.198
- [ ] Visual-dependent Config 1 tIoU = 0.129, Config 2 = 0.213 (+65%)
- [ ] Multi-hop IoU@0.5 anomaly disclosed: Config 2 (0.072) < Config 1 (0.076)
- [ ] Config 2 values bolded where they exceed Config 1

---

## V6 — Full test suite still passes

```bash
/root/miniconda3/envs/vqa-benchmark/bin/python -m pytest tests/ -v
```

**Expected:** All tests pass (≥104). No regressions from Phase 8.

---

## V7 — Roadmap and changelog updated

- `specs/roadmap.md`: 9.1 ✅, 9.3 ✅, 9.4 ✅, Phase 9 header ✅
- `CHANGELOG.md`: Phase 9 entry present with date 2026-05-15
