# Phase 7.1–7.2 — QA Generation: Task Plan

## Task Groups

### Group 1 — Config & Schema
1.1 Verify `config.yaml` has `qa_generation.model: "claude-sonnet-4-6"`,
    `questions_per_lecture: 15`, and `target_accepted: 12`.  
1.2 Verify `src/config.py` exposes `cfg.qa_generation` with the above fields.  
1.3 Confirm `data/qa_pairs/raw/` directory exists (create if missing).

### Group 2 — `src/qa_generator.py`
2.1 Implement `load_augmented_chunks(video_id) -> list[dict]` — reads
    `data/chunks/{video_id}_chunks_augmented.json`.  
2.2 Implement `build_prompt(video_id, chunks) -> str` — formats chunks as
    numbered excerpts including frame captions; embeds question-type mix
    instructions and rejection criteria.  
2.3 Implement `parse_qa_response(video_id, raw_json) -> list[dict]` — validates
    each item against the standard schema; raises on malformed output.  
2.4 Implement `generate_qa(video_id) -> list[dict]` — orchestrates 2.1–2.3;
    calls the Anthropic SDK with `cfg.qa_generation.model`; returns the list.  
2.5 Add `reviewed_by: "llm_draft"` and `review_date` (today's date) to each
    item before returning.

### Group 3 — `scripts/generate_qa.py`
3.1 Implement CLI with `argparse`:
    - `--video_id <id>` — generate for one lecture
    - `--all` — generate for all 60 (reads `data/raw/metadata.json`)
    - `--overwrite` — re-generate even if raw file already exists (default: skip)
3.2 Save output to `data/qa_pairs/raw/{video_id}_qa_raw.json` (2-space indent).
3.3 Log progress: `INFO` per lecture (chunks loaded, questions generated, path saved).

### Group 4 — Unit Tests
4.1 Write `tests/test_qa_generator.py`:
    - Mock the Anthropic SDK call; supply a synthetic 3-chunk augmented fixture.
    - Test that `generate_qa()` returns a list of dicts matching the schema.
    - Test that `parse_qa_response()` raises on missing required fields.
    - Test `reviewed_by == "llm_draft"` on all items.
    - No real API calls or model loading in tests.

### Group 5 — Pilot Run
5.1 Run `python scripts/generate_qa.py --video_id mit_6046_lec10`.  
5.2 Run `python scripts/generate_qa.py --video_id mit_18065_lec06`.  
5.3 Run `python scripts/generate_qa.py --video_id nyu_dl_week6`.  
5.4 Inspect each raw file:
    - Confirm 15 QA items per lecture.
    - Confirm question type distribution (5–6 multi-hop, 2+ visual, 1 unanswerable).
    - Read 3–4 multi-hop questions; verify they reference 2+ non-adjacent chunk IDs.
    - Verify `ground_truth_spans` have plausible `start`/`end` values (float seconds).
5.5 If prompt quality is poor, revise `build_prompt()` and re-run pilot.

### Group 6 — Full Run (after pilot passes)
6.1 Run `python scripts/generate_qa.py --all`.  
6.2 Confirm 60 raw files exist in `data/qa_pairs/raw/`.  
6.3 Spot-check 2 additional lectures (different course from pilot).

### Group 7 — Git Checkpoint
7.1 Stage and commit:
    - `src/qa_generator.py`
    - `scripts/generate_qa.py`
    - `tests/test_qa_generator.py`
    - `data/qa_pairs/raw/` (all 60 raw files)
    - `specs/2026-05-10-qa-generation/`
7.2 Commit message: `feat: QA generation pipeline (Phase 7.1–7.2)`
7.3 Push branch; open PR against `main`.

---

## Dependencies

- `data/chunks/{video_id}_chunks_augmented.json` must exist for all 60 lectures (Phase 4.2 ✅)
- `ANTHROPIC_API_KEY` must be set in environment
- `vqa-benchmark` conda env must be active
