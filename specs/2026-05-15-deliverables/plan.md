# Phase 9 — Deliverable Scripts: Plan

## Task Group 1 — run_part1.py (rewrite to correct API)

**File:** `run_part1.py`

The file exists but uses a stale API that does not match the implemented modules:
- `Retriever(cfg)` → must be `Retriever(mode, cfg=cfg)` where mode is `"transcript_only"` or `"transcript_plus_frames"`
- `retriever.retrieve(query, video_id, use_frames)` → must be `retriever.query(question, video_id=video_id)`
- `Generator(cfg)` / `generator.generate(...)` → no `Generator` class exists; must use the module-level function `generate(question, chunks, mode, cfg)` from `src.generator`
- Answer output does not use `GeneratorResult` fields (`.answer`, `.citations`)

Steps:
1. Remove stale `Retriever(cfg)` and `Generator` class usage.
2. Instantiate `Retriever("transcript_only", cfg=cfg)` and `Retriever("transcript_plus_frames", cfg=cfg)`.
3. Call `retriever.query(question, video_id=video_id)` → returns list of chunk dicts.
4. Call `generate(question, chunks, mode=config_name, cfg=cfg)` → returns `GeneratorResult`.
5. Print retrieved chunk summaries (video_id, mm:ss–mm:ss, first 80 chars).
6. Print `result.answer` and `result.citations` (already formatted with YouTube deep links).
7. Keep `--question` and `--video_id` argparse args; keep 3 hardcoded demo questions.

**Done when:** `python run_part1.py` runs end-to-end without error and shows answer + citations for both configs.

---

## Task Group 2 — results.md (fill TBD values)

**File:** `results.md` (repo root)

The file exists with the correct 3-table structure. All cells are TBD. Fill them from
`data/benchmark/evaluation_results.json` and `data/benchmark/benchmark_v1.json`.

Table 1 — Overall (n=810): tIoU, IoU@0.3/0.5, HR@1/3/5, LLM-judge, citation accuracy.
Table 2 — Mean tIoU by question type: per type (multi-hop-visual, visual, multi-hop, text, all-visual).
Table 3 — Hit Rate@k by question type: HR@1/3/5 per type.

The "Paper-Reported" columns equal the reproduced numbers (single evaluation run).
Mark reproduction status at bottom: all three tables ⏳ → ✅.

**Done when:** No TBD cells remain in results.md and all numbers match evaluation_results.json.

---

## Task Group 3 — scripts/reproduce_tables.py

**File:** `scripts/reproduce_tables.py`

Does not yet exist. Create it to match the 3-table structure in results.md:

1. `reproduce_table_1(results_path, benchmark_path) -> None` — overall (n=810), all configs, all metrics.
2. `reproduce_table_2(results_path, benchmark_path) -> None` — mean tIoU per question type.
3. `reproduce_table_3(results_path, benchmark_path) -> None` — Hit Rate@1/3/5 per question type.
4. Top-level block calls all three with default paths from `load_config()`. Optional `--results` CLI arg.
5. Plain-text stdout. No API calls. No LaTeX output.

**Done when:** `python scripts/reproduce_tables.py` prints three tables matching results.md numbers.

---

## Task Group 4 — Tests

**File:** `tests/test_run_part1.py`

1. Smoke-test that `run_part1.py` imports cleanly and `main()` can be called with mocked retriever + generator (no API calls, no GPU).
2. Verify `--question` arg is parsed correctly.

**Done when:** `pytest tests/test_run_part1.py` passes.

---

## Task Group 5 — Specs, changelog, merge

1. Update `specs/roadmap.md`: mark 9.1 ✅, 9.3 ✅, 9.4 ✅, Phase 9 header ✅.
2. Add Phase 9 entry to `CHANGELOG.md`.
3. Run `/changelog` before committing.
4. Merge `phase-9-deliverables` into `main` and delete branch.
