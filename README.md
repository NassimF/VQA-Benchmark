# VQA Benchmark — Long-Lecture Video RAG

**CS 6263: LLM and Agentic Systems — Assignment 4**  
**Track C: Long-Lecture Video RAG and Benchmark Construction**  
**UTSA | Dr. Peyman Najafirad | TA: Mohammad Bahrami**

---

## What This Is

A Visual Question Answering (VQA) benchmark for long lecture videos, paired with a
Retrieval-Augmented Generation (RAG) pipeline that retrieves relevant transcript segments
and answers questions with timestamp citations.

The pipeline transcribes lectures using Whisper, chunks transcripts into 45-second windows,
indexes them into ChromaDB, and evaluates two retrieval configurations:
1. **Transcript-only** dense retrieval
2. **Transcript + frame captions** multimodal retrieval

---

## Setup

```bash
git clone https://github.com/NassimF/VQA-Benchmark.git
cd VQA-Benchmark
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### Part 1 — End-to-end RAG demo
```bash
python run_part1.py --question "What is the key property of dynamic programming?"
```

### Part 2 — Benchmark evaluation (both retrieval configs)
```bash
python run_part2.py
```

Results are saved to `results/evaluation_results.json`.

---

## Project Structure

See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the full file tree, phase-by-phase plan,
and all technical decisions.

---

## Lectures Used

| Video ID | Course | Topic | License |
|----------|--------|-------|---------|
| TBD | TBD | TBD | CC BY-NC-SA 4.0 |

---

## Key Results

*(Filled in after evaluation — Phase 9)*

| Metric | Transcript-Only | Transcript+Frames |
|--------|----------------|-------------------|
| Mean Temporal IoU | — | — |
| Hit Rate@5 | — | — |
| LLM-Judge Score | — | — |

---

## Citation

If you use this benchmark, please cite:

```
@dataset{vqa_benchmark_2026,
  title  = {Long-Lecture Video RAG Benchmark},
  author = {Faridnia, Seyedehnasim},
  year   = {2026},
  note   = {CS 6263 Assignment 4, UTSA}
}
```
