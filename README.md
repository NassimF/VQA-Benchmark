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

## Reproducing the Results from a Clean Checkout

Run these steps in order. Each step saves output that the next step reads.
Estimated total time: ~10–15 GPU-hours (dominated by frame captioning).

```bash
# 1. Download all 60 videos and VTT captions (~20–40 GB, several hours)
python scripts/download_videos.py --all

# 2. Parse VTT captions into segment JSON
python scripts/parse_vtt.py --all

# 3. Chunk transcripts into 45-second windows (10-second overlap)
python scripts/build_chunks.py --all

# 4. Extract frames (every 15s) and caption with Qwen2-VL-7B  [A100 required]
python scripts/build_frame_captions.py --all --device cuda

# 5. Ingest all chunks into both ChromaDB collections
python scripts/build_index.py --all

# 6. Build the benchmark  (requires data/qa_pairs/reviewed/ — see below)
python scripts/build_benchmark.py
python scripts/validate_benchmark.py

# 7. Run full evaluation — both configs, all QA pairs
python run_part2.py

# 8. Reproduce paper tables from evaluation output
python scripts/reproduce_tables.py
```

> **Note on the benchmark file:** `data/benchmark/benchmark_v1.json` is committed to the
> repo. Steps 6–8 only need to be re-run if you regenerate the QA pairs. To use the
> pre-built benchmark directly, skip to step 7.

**The improvement being measured:** Config 2 (transcript + Qwen2-VL-7B frame captions)
vs Config 1 (transcript-only) on visual-dependent questions (multi-hop-visual and visual
types). `run_part2.py` prints a side-by-side table; the Δ column isolates the visual
contribution under identical embedding infrastructure.

---

## Quick Demo (no GPU required)

```bash
# Runs 3 hardcoded questions against pre-built ChromaDB index
python run_part1.py

# Or ask your own question
python run_part1.py --question "What is the SVD geometric interpretation?" \
                    --video_id mit_18065_lec06
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
 [benchmark already in repo: data/benchmark/benchmark_v1.json]
        ↓
run_part2.py                → data/benchmark/evaluation_results.json
        ↓
scripts/reproduce_tables.py → paper tables (Tables 1, 2, 3)
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

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|:---:|:---:|
| Mean Temporal IoU | 0.154 | **0.198** |
| IoU@0.3 | 0.228 | **0.279** |
| Hit Rate@5 | 0.515 | **0.565** |
| LLM-Judge Score (1–5) | 3.03 | **3.56** |

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
