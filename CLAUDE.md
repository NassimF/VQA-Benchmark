# CLAUDE.md

## Project
**Long-Lecture Video RAG Benchmark** — a conference paper project.
GitHub: https://github.com/NassimF/VQA-Benchmark

The user is new to RAG systems. When introducing RAG-related concepts for the first time,
include a brief plain-English explanation before diving into implementation details.

## Specs & Roadmap
The `specs/` directory is the project constitution — read it before starting any task:
- `specs/roadmap.md` — phase-by-phase plan with statuses (✅/⚠️/⏳); always check for the current phase
- `specs/tech-stack.md` — tools, dependencies, project directory structure, config reference
- `specs/corpus.md` — full 60-video library with licensing and metadata
- `specs/mission.md` — project goals and required deliverables
- `specs/YYYY-MM-DD-<feature>/` — per-feature plan, requirements, and validation docs

Keep specs in sync with any implementation changes. Run `/changelog` before merging.

## Language & Style
- Python 3.10+
- Type hints on all function signatures
- Google-style docstrings (one short line for simple functions; skip if the name is self-explanatory)
- Line length: 100 characters
- f-strings only (no `.format()` or `%`)
- No comments unless the WHY is non-obvious to a reader unfamiliar with the codebase

## Architecture
- All configuration accessed via `src/config.py` — never hardcode paths, model names, or hyperparameters
- All file I/O uses `pathlib.Path`, never `os.path`
- Logging via Python `logging` module everywhere except `run_part1.py` and `run_part2.py` (which use `print` for demo output)
- All timestamps stored in **seconds (float)** — never frames, never milliseconds

## Citation Format (prescribed by assignment)
`[{video_id} @ mm:ss to mm:ss]` with YouTube deep link
Example: `[mit_6046_lec01 @ 30:23 to 31:41](https://youtu.be/VIDEO_ID?t=1823)`

## Data Conventions
- `chunk_id`: `{video_id}_chunk_{index:03d}`
- `qa_id`: `{video_id}_q{index:03d}`
- All JSON files: 2-space indentation

## Chunking (prescribed by assignment)
- Window: 45 seconds
- Overlap: 10 seconds (stride = 35 seconds)
- Do not change these values without explicit user approval

## Retrieval Configurations
Two ChromaDB collections must always be maintained:
1. `transcript_only` — chunk text only
2. `transcript_plus_frames` — chunk text + appended frame captions

## Evaluation Metrics (required)
- Temporal IoU (and IoU@0.3, IoU@0.5)
- Hit Rate @ k=1, 3, 5
- LLM-judge score (1–5 scale)
- Citation accuracy

## Git & GitHub
- Remote: https://github.com/NassimF/VQA-Benchmark
- Push at each major phase checkpoint
- Never commit: `chroma_db/`, `*.mp4`, `*.m4a`, `.env`, `__pycache__/`, `data/raw/videos/`
- Commit messages: imperative mood, ≤50 characters subject line

## Testing
- All tests in `tests/` using pytest
- Fixtures use small synthetic data — never load real models in unit tests
- Use `pytest.approx` for float comparisons in evaluator tests

## Report
Every parameter choice (window size, overlap, k, embedding model, frame interval, etc.)
must be **explained and justified** in the report — not just stated.
