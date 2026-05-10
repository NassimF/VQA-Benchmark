# Mission

## Project

**Long-Lecture Video RAG Benchmark** — a retrieval-augmented generation benchmark built on CC-licensed academic lecture videos, evaluating a system's ability to retrieve temporally grounded answers from long-form educational content.

## Publication Goal

Build a benchmark at full venue quality for submission to EMNLP, ACL, or NeurIPS (datasets track):

- **60 lectures** across 15 courses (MIT OCW, NYU DL, Stanford SEE) — all CC-licensed
- **~720 QA pairs** (12 accepted × 60 lectures), LLM-reviewed
- **Dataset license:** CC BY-NC-SA 4.0 — required by the ShareAlike clause of the MIT OCW and Stanford SEE source material; compatible with the NYU CC BY 4.0 content

## Design Principles

### 1. CC-licensed content only
Every video must carry a confirmed Creative Commons license before being added to the corpus. The license, version, and verification source (OCW terms page, GitHub LICENSE file, SEE FAQ) are recorded in `data/raw/metadata.json` and `specs/roadmap.md`. No Standard YouTube License content.

### 2. Multi-hop questions are the core contribution
Questions that can be answered from a single 45-second chunk are weak single-hop questions and make a poor benchmark. The target is questions requiring synthesis across two or more non-adjacent segments — e.g. "How does the property introduced at minute 12 justify the claim made at minute 58?" These are harder, more realistic, and more valuable for evaluating RAG systems.

### 3. Two retrieval configurations, one embedding model
The benchmark evaluates two RAG pipelines side-by-side to isolate the contribution of visual context:

| Config | Document content | Embedding |
|--------|-----------------|-----------|
| Transcript-only | Chunk text | all-MiniLM-L6-v2 |
| Transcript + frames | Chunk text + Qwen2-VL-7B frame caption | all-MiniLM-L6-v2 |

Both collections use the identical embedding model and ChromaDB infrastructure. The only variable is document content, making the comparison clean and reproducible.

### 4. LLM-reviewed QA
All questions are LLM-drafted (15 per lecture) and LLM-reviewed by a second Claude pass
that evaluates answer correctness, span plausibility, and question type accuracy.
Ground-truth spans are LLM-estimated from chunk boundaries (~±15–30s precision) — disclosed
as a limitation in the paper. Target: 12 accepted QA pairs per lecture after review.

### 5. Temporal citation is the unit of evaluation
Every generated answer cites `[video_id @ mm:ss to mm:ss]` with a YouTube deep link. Evaluation is grounded in **temporal IoU** between predicted and ground-truth spans — not just semantic similarity. This makes the benchmark measurably harder than text-only QA and directly evaluates the retrieval system's precision.

---

## Required Deliverables

| Deliverable | Status |
|-------------|--------|
| `config.yaml` | ✅ |
| `requirements.txt` | ✅ |
| `CLAUDE.md` | ✅ |
| `.gitignore` | ✅ |
| `src/retriever.py` (transcript-only and transcript+frames modes) | ⏳ |
| `src/generator.py` | ⏳ |
| `run_part1.py` — end-to-end RAG demo | ⏳ |
| `run_part2.py` — full benchmark evaluation (both retrieval configs) | ⏳ |
| `data/benchmark/benchmark_v1.json` (12–15 QA × 60 lectures) | ⏳ |
| Conference paper (`report/main.tex`) | ⏳ |
| `README.md` (setup and usage instructions, dataset description) | ⏳ |
