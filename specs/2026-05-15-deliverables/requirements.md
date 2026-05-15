# Phase 9 — Deliverable Scripts: Requirements

## Scope

Three remaining deliverables from the assignment spec (mission.md):

| Task | File | Current state |
|------|------|---------------|
| 9.1 | `run_part1.py` | Exists — stale API, needs rewrite |
| 9.3 | `scripts/reproduce_tables.py` | Does not exist |
| 9.4 | `results.md` | Exists — correct structure, all cells TBD |

9.2 (`run_part2.py`) is complete (✅, 1620 pairs evaluated, results in `evaluation_results.json`).

---

## run_part1.py

### What exists
A placeholder with the right skeleton (argparse, 3 demo questions, per-config loop) but
using a stale API surface that was never aligned with the implemented modules.

### Stale vs correct API

| Placeholder (wrong) | Actual API |
|---------------------|------------|
| `Retriever(cfg)` | `Retriever(mode, cfg=cfg)` |
| `retriever.retrieve(query, video_id, use_frames)` | `retriever.query(question, video_id=None)` |
| `Generator(cfg)` | no class — module-level `generate()` function |
| `generator.generate(question, chunks, video_id)` | `generate(question, chunks, mode, cfg)` |
| prints raw answer string | must use `GeneratorResult.answer` and `.citations` |

### Decisions
- Keep `--question` and `--video_id` argparse args unchanged.
- Keep 3 hardcoded demo questions (good representative coverage: visual, multi-hop, text).
- Instantiate both retrievers up front; reuse across demo questions to avoid reloading embedder.
- Print retrieved chunk summaries: `[video_id @ mm:ss–mm:ss] <first 80 chars of text>`.
- Print `result.answer` then `result.citations` (one citation per line).
- Use `print` throughout — no `logging` per CLAUDE.md.
- All paths and model config from `load_config()` — no hardcoded values.

---

## scripts/reproduce_tables.py

### Purpose
Audit tool and paper reproducibility artifact. Single `python scripts/reproduce_tables.py`
regenerates all three tables from results.md.

### Decisions
- Three functions matching results.md table structure: `reproduce_table_1` (overall),
  `reproduce_table_2` (tIoU by type), `reproduce_table_3` (Hit Rate@k by type).
- Question type filter for "all-visual" row in Table 2: `{multi-hop-visual, visual}`.
- No LaTeX output. Plain-text stdout only.
- No new API calls — reads only `evaluation_results.json` and `benchmark_v1.json`.
- Default paths from `load_config()`. Optional `--results` and `--benchmark` CLI args.

### Metrics
- Table 1: mean tIoU, IoU@0.3, IoU@0.5, HR@1/3/5, LLM-judge, citation accuracy — per config.
- Table 2: mean tIoU per question type — per config, with Δ column.
- Table 3: HR@1, HR@3, HR@5 per question type — per config.

---

## results.md

### What exists
The file has the correct 3-table structure with "Paper-Reported" columns. All cells are TBD.
The "Reproduction Status" section at the bottom tracks which tables have been filled.

### Decisions
- Fill all TBD cells from `evaluation_results.json`. Numbers must match `reproduce_tables.py` output exactly.
- "Paper-Reported" columns = same as reproduced numbers (single canonical evaluation run).
  These columns exist to catch drift if the evaluation is re-run in the future.
- Bold Config 2 values where they exceed Config 1 (already implied by the structure).
- Multi-hop IoU@0.5 anomaly must be disclosed in Table 1 narrative: Config 2 (0.072) is
  marginally below Config 1 (0.076) — frame augmentation slightly inflates predicted spans
  on multi-hop pairs, reducing precision at the stricter 0.5 threshold.
- Update "Last updated" date and flip Reproduction Status rows to ✅.

### Table 2 — question type rows
| Row | Filter |
|-----|--------|
| multi-hop-visual | `question_type == "multi-hop-visual"` |
| visual | `question_type == "visual"` |
| multi-hop | `question_type == "multi-hop"` |
| text | `question_type == "text"` |
| **all visual** | `question_type in {multi-hop-visual, visual}` — 455 pairs, primary claim |

---

## Out of scope
- Plots / figures (deferred to Phase 10 paper work)
- LaTeX table output
- Third judge / re-evaluation
- Any changes to `src/evaluator.py`, `src/generator.py`, or `src/retriever.py`
