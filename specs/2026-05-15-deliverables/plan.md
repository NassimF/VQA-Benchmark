# Phase 9 — Deliverable Scripts: Plan

## Task Group 1 — run_part1.py (demo script)

**File:** `run_part1.py`

1. Parse `--question` CLI arg (argparse). If omitted, use 3 hardcoded example questions drawn from `benchmark_v1.json`.
2. Load both retriever configs (`transcript_only`, `transcript_plus_frames`) using `src/retriever.py`.
3. For each question, run retrieval + generation for both configs using `src/generator.py`.
4. Print results side-by-side: retrieved chunk summaries (video_id, mm:ss–mm:ss, first 80 chars of text), then generated answer + formatted citations for each config.
5. Use `print` throughout — no `logging`. No evaluation metrics.

**Done when:** `python run_part1.py` runs without error and `python run_part1.py --question "..."` shows retrieval + answer output for both configs.

---

## Task Group 2 — scripts/reproduce_tables.py

**File:** `scripts/reproduce_tables.py`

1. Define `reproduce_table_1(results_path) -> None` — single-hop results table (n=238). Reads `evaluation_results.json`, filters to `question_type in {visual, text}`, aggregates per config, prints formatted table.
2. Define `reproduce_table_2(results_path) -> None` — multi-hop results table (n=460). Filters to `question_type in {multi-hop-visual, multi-hop}`, aggregates per config, prints formatted table.
3. Define `reproduce_table_3(results_path) -> None` — overall results table (n=810, all question types). Full dataset aggregation per config.
4. Top-level `if __name__ == "__main__"` block calls all three in sequence with default paths from `config.yaml`.
5. Each function prints a plain-text table to stdout (matching the format of `run_part2.py` output). No LaTeX output.

**Done when:** `python scripts/reproduce_tables.py` runs cleanly and prints three tables matching the numbers in `evaluation_results.json`.

---

## Task Group 3 — results.md

**File:** `results.md` (repo root)

1. Overall table: all 810 pairs, Config 1 vs Config 2, every metric (tIoU, IoU@0.3, IoU@0.5, HR@1/3/5, LLM-judge, citation accuracy).
2. Single-hop table: n=238, same metrics.
3. Multi-hop table: n=460, same metrics.
4. Visual-dependent table: n=455 (`multi-hop-visual` + `visual`), same metrics — this is the key Config 2 improvement claim.
5. Short narrative (3–5 sentences) after each table noting the direction of improvement and any anomalies (e.g. multi-hop IoU@0.5 is the one metric where Config 2 is marginally lower).

**Done when:** `results.md` contains all four tables with correct numbers from `evaluation_results.json` and the visual-dependent table clearly shows the +65% tIoU improvement.

---

## Task Group 4 — Tests

**File:** `tests/test_run_part1.py`

1. Smoke-test that `run_part1.py` is importable and `main()` can be called with a mocked retriever + generator without hitting any API.
2. Verify that `--question` arg is parsed correctly.

**Done when:** `pytest tests/test_run_part1.py` passes with mocked dependencies.

---

## Task Group 5 — Specs, changelog, merge

1. Update `specs/roadmap.md`: mark 9.1, 9.3, 9.4 ✅.
2. Add Phase 9 entry to `CHANGELOG.md`.
3. Run `/changelog` before committing.
4. Merge `phase-9-deliverables` into `main`.
