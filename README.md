# LectureBench — Temporally Grounded QA for Long Lecture Videos

**CS 6263: LLM and Agentic Systems — Assignment 4**
**Track C: Long-Lecture Video RAG and Benchmark Construction**
**UTSA | Dr. Peyman Najafirad | TA: Mohammad Bahrami**

---

## What This Is

**LectureBench** is a temporally grounded QA benchmark over 60 long-form academic lecture
videos (~62.6 hours), paired with a Retrieval-Augmented Generation (RAG) pipeline.
Every QA pair is anchored to precise video timestamps and evaluated by temporal
intersection-over-union (tIoU) rather than token matching.

Two retrieval configurations are evaluated under identical infrastructure:
1. **Config 1 — Transcript-only:** dense retrieval over 45-second transcript chunks
2. **Config 2 — Transcript + Frames:** same chunks augmented with Qwen2-VL-7B frame captions

The benchmark's central question: does adding visual frame captions improve temporally
grounded retrieval, and for which question types?

---

## Corpus

60 CC-licensed lectures from three sources:

| Source | Courses | License |
|--------|---------|---------|
| MIT OpenCourseWare | 18.065, 18.06, 18.404, 18.650, 6.004, 6.006, 6.034, 6.041, 6.042, 6.046, 6.851, 6.858 | CC BY-NC-SA 4.0 |
| NYU Deep Learning | Deep Learning (weeks 1–13) | CC BY 4.0 |
| Stanford Engineering Everywhere | CS229 Machine Learning | CC BY-NC-SA 3.0 |

Full metadata: `data/raw/metadata.json`

---

## Setup

```bash
git clone https://github.com/NassimF/VQA-Benchmark.git
cd VQA-Benchmark
conda create -n vqa-benchmark python=3.10
conda activate vqa-benchmark
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY and OPENAI_API_KEY
```

System requirements: NVIDIA A100 80 GB (for Qwen2-VL-7B frame captioning), `ffmpeg`, `yt-dlp`.

---

## Usage

### Part 1 — End-to-end RAG demo

```bash
python run_part1.py --question "What is the geometric interpretation of SVD?"
python run_part1.py --question "..." --video_id mit_18065_lec06
python run_part1.py   # runs 3 hardcoded demo questions
```

### Part 2 — Full benchmark evaluation (both configs)

```bash
python run_part2.py
python run_part2.py --limit 20   # smoke test
```

Results saved to `data/benchmark/evaluation_results.json`.

### Reproduce paper tables

```bash
python scripts/reproduce_tables.py          # all tables
python scripts/reproduce_tables.py --table 1
```

---

## Pipeline Overview

```
YouTube VTT captions
        ↓
scripts/parse_vtt.py        → data/transcripts/{video_id}_transcript.json
        ↓
scripts/build_chunks.py     → data/chunks/{video_id}_chunks.json          (45s/35s stride)
        ↓
scripts/build_frame_captions.py → data/chunks/{video_id}_chunks_augmented.json
        ↓
scripts/build_index.py      → chroma_db/   (two collections)
        ↓
scripts/generate_qa.py      → data/qa_pairs/raw/
        ↓
scripts/review_qa.py        → data/qa_pairs/reviewed/
        ↓
scripts/build_benchmark.py  → data/benchmark/benchmark_v1.json
        ↓
run_part2.py                → data/benchmark/evaluation_results.json
```

---

## Question Type Distribution (per lecture)

| Type | Drafted | Target accepted | Role |
|------|:-------:|:---------------:|------|
| multi-hop-visual (≥2 spans, ≥1 visual hop) | 7 | 4 | Primary |
| visual (single-hop, frame caption required) | 2 | 1 | Primary |
| multi-hop (transcript-only, ≥2 spans)       | 3 | 2 | Control |
| text (single-hop, lecture-specific fact)    | 2 | 1 | Control |
| unanswerable                                | 1 | 1 | Required |
| **Total** | **15** | **≥10** | |

Visual-dependent types (multi-hop-visual + visual) ≥ 60% of accepted pairs.

---

## Key Results

*(Filled in after Phase 8 evaluation)*

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|:---:|:---:|
| Mean Temporal IoU | — | — |
| IoU@0.3 | — | — |
| Hit Rate@5 | — | — |
| LLM-Judge Score (1–5) | — | — |

See `results.md` for full side-by-side table and `data/benchmark/evaluation_results.json`
for raw numbers.

---

## Evaluation Metrics

- **Temporal IoU** — overlap between predicted and ground-truth time span
- **IoU@0.3 / IoU@0.5** — fraction of pairs with tIoU above threshold
- **Hit Rate@k** — fraction where ground-truth span is covered by top-k retrieved chunks
- **LLM-Judge Score (1–5)** — answer quality judged by a second LLM against reference
- **Citation Accuracy** — fraction of cited spans that are temporally correct

---

## Dataset License

CC BY-NC-SA 4.0 — required by the ShareAlike clause of the MIT OCW and Stanford SEE source material.

---

## Citation

```bibtex
@dataset{lecturebench2026,
  title  = {LectureBench: Temporally Grounded QA for Long Lecture Videos},
  author = {Faridnia, Seyedehnasim},
  year   = {2026},
  note   = {CS 6263 Assignment 4, UTSA}
}
```
