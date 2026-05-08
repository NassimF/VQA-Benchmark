a# Tech Stack

## Runtime Requirements

| Requirement | Value |
|-------------|-------|
| Python | 3.10+ |
| GPU | NVIDIA A100 80 GB (×1 minimum) — required for Qwen2-VL-7B in bfloat16 (~14 GB VRAM) |
| System tools | `ffmpeg`, `yt-dlp` — must be installed and on PATH |

---

## Core Infrastructure

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Config management | PyYAML | `≥6.0` | Single `config.yaml` drives all paths, model names, and hyperparameters — nothing hardcoded |
| Path handling | pathlib (stdlib) | — | All file I/O uses `Path`; no `os.path` |
| Logging | logging (stdlib) | — | Structured logs across all modules; `print` only in `run_part1.py` / `run_part2.py` |
| Testing | pytest | `≥8.0` | Fixtures use synthetic data — real models never loaded in unit tests |

---

## Data Acquisition

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Video download | yt-dlp | system | Handles YouTube; downloads `.mp4` / `.mkv` and auto-generates `.en.vtt` captions in one pass |
| VTT parsing | custom (`src/transcriber.py`) | — | Rolling-caption VTT format requires deduplication of word-timing cues; off-the-shelf parsers produce duplicate text |

---

## Frame Pipeline

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Frame extraction | ffmpeg (subprocess) | system | Handles all codecs including AV1 (NYU `.mkv` files); `cv2.VideoCapture` cannot decode AV1 on this platform |
| Frame I/O | opencv-python | `≥4.9` | BGR array handling between ffmpeg JPEG output and PIL conversion |
| Image conversion | Pillow | `≥10.0` | PIL `Image` objects required by the Qwen2-VL processor |
| Frame captioner | Qwen2-VL-7B-Instruct | transformers `≥4.45` | Strongest OCR and math comprehension on lecture slides and whiteboards among evaluated models; Apache 2.0 license; fits on one A100 in bfloat16 |
| VL preprocessing | qwen-vl-utils | `≥0.0.8` | `process_vision_info()` required to format PIL images for the Qwen2-VL chat template |
| Tensor backend | PyTorch (via transformers) | — | bfloat16 inference on A100; pulled in automatically by sentence-transformers |

**Captioning approach:** Approach A (text augmentation) — captions are appended as `[frame caption: ...]` to the nearest chunk's text before embedding. Both ChromaDB collections use the identical embedding model; the only difference is document content.

---

## Retrieval

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | `≥2.7.0` | Prescribed by assignment; 384-dim, fast CPU/GPU inference, strong semantic retrieval |
| Vector database | ChromaDB (persistent) | `≥0.5` | Prescribed by assignment; local persistent store, no server required; supports metadata filtering for `video_id` |
| Distance metric | cosine | — | Standard for sentence embeddings; ChromaDB default |
| Collections | `lecture_transcript_only`, `lecture_transcript_plus_frames` | — | Two collections required to enable side-by-side evaluation of both retrieval configs |

---

## Generation

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Primary LLM | gpt-4o-mini (OpenAI) | openai `≥1.30` | Cost-effective; reliable structured JSON output for citations; fast |
| Alternative LLMs | `claude-haiku-4-5`, `gpt-4o-mini` | anthropic `≥0.28` | Haiku / GPT-4o-mini as cost-effective fallbacks |
| Output format | Structured JSON | — | More reliable than regex-parsing bracket citations `[1]`; allows strict schema validation |
| Citation format | `[video_id @ mm:ss to mm:ss](youtube_deep_link)` | — | Prescribed by assignment; human-readable and directly verifiable |

---

## QA Generation & Evaluation

| Component | Tool | Version Pin | Reason |
|-----------|------|-------------|--------|
| Draft QA generation | Claude / GPT-4 (strong model) | — | 15 drafts per lecture; stronger model produces better question diversity than gpt-4o-mini |
| LLM judge | Claude / GPT-4 | — | Scores generated answers 1–5 for accuracy and grounding; more reliable than ROUGE for long-form answers |
| Numeric evaluation | NumPy | `≥1.26` | Temporal IoU, hit rate@k computations |

### ⚠️ Open Decision — Phase 7.3 QA Review Method

**Status:** Undecided. Do not implement Phase 7.3 until resolved.

**Proposed change:** Replace human review (original plan) with a strong LLM (GPT-4o / Claude Opus) given access to source chunks + augmented captions to evaluate and filter the raw QA pairs automatically.

**Why this is appealing:**
- Scales to 900 pairs (60 videos × 15) without manual effort
- Consistent scoring — no inter-annotator variability
- LLM can verify factual accuracy against the chunk text it generated from

**Problems and concerns:**

1. **Ground truth span tightening (critical):** Phase 7.3 is not just quality scoring — it also tightens `ground_truth_spans` to exact `start_time`/`end_time` timestamps. An LLM reading text chunks cannot reliably produce precise video timestamps. If spans remain as LLM estimates, temporal IoU scores in Phase 8 measure noise, not retrieval quality.

2. **Circularity risk:** The same model family that generated the QA pairs evaluates them. Systematic blind spots are shared — both models may miss the same errors or favor the same phrasing. Using a *different* model (e.g. GPT-4o evaluating Claude-generated pairs) reduces but does not eliminate this.

3. **Multi-hop verification:** Confirming a question genuinely requires 2+ non-adjacent spans is subtle. LLMs often fail to detect cases where a "multi-hop" question is actually answerable from a single span, inflating the multi-hop count.

4. **Visual-dependent questions:** An LLM evaluating text-only chunks cannot verify whether a question truly requires a frame caption. Must use augmented chunks (`transcript_plus_frames`) as context for this to work at all.

5. **Unanswerable question verification:** Confirming exactly 1 unanswerable question per lecture requires careful cross-checking against all chunk content — an LLM may miss partial answers scattered across chunks.

6. **Academic validity:** LLM-judged benchmarks are increasingly accepted in NLP (MT-Bench, AlpacaEval) but may be questioned by reviewers for a benchmark contribution paper. The claim "human-verified ground truth" is stronger than "LLM-verified."

**Recommendation:**
Use LLM evaluation for answer quality scoring (replacing the 1–5 human quality judgment), but retain human review specifically for:
- Tightening `ground_truth_spans` timestamps (cannot be reliably automated)
- Multi-hop span verification (confirm each hop is genuinely necessary)
- Spot-checking unanswerable questions

This hybrid approach keeps the benchmark credible for the paper while reducing manual effort from ~900 full reviews to targeted span corrections only.

---

## Prescribed Hyperparameters

These values are set by the assignment and must not be changed without explicit justification in the report.

| Parameter | Value | Source |
|-----------|-------|--------|
| Chunk window | 45 seconds | Assignment spec |
| Chunk overlap | 10 seconds (stride = 35s) | Assignment spec |
| Embedding model | all-MiniLM-L6-v2 | Assignment spec |
| Vector DB | ChromaDB | Assignment spec |
| Hit rate k values | 1, 3, 5 | Assignment spec |
| IoU thresholds | 0.3, 0.5 | Assignment spec |
| Frame interval | 15 seconds | Changed from 30s: 3 frames/chunk covers slide transitions and whiteboard build-up; all-in-window assignment replaces nearest-midpoint |
| Frame captioner max tokens | 128 | Design choice — sufficient for slide descriptions |

---

## config.yaml Reference

```yaml
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cuda"  # or "cpu"

retrieval:
  top_k: 4
  k_values: [1, 3, 5]        # for hit rate evaluation
  distance_metric: "cosine"
  iou_threshold: 0.3

vector_db:
  path: "./chroma_db"
  transcript_only_collection: "lecture_transcript_only"
  transcript_frames_collection: "lecture_transcript_plus_frames"

chunking:
  window_seconds: 45
  overlap_seconds: 10         # stride = 35s

frame_extraction:
  interval_seconds: 30

frame_captioner:
  model: "Qwen/Qwen2-VL-7B-Instruct"
  device: "cuda"
  max_new_tokens: 128

generator:
  model: "gpt-4o-mini"        # or "utsa-llama" / "claude-haiku-4-5"
  temperature: 0.1
  max_tokens: 512
  citation_format: "[{video_id} @ {start_mm}:{start_ss} to {end_mm}:{end_ss}]"

qa_generation:
  questions_per_lecture: 15
  target_accepted: 12
```

---

## Project Directory Structure

```
VQA_Benchmark/
├── CLAUDE.md
├── PROJECT_PLAN.md                    # Living progress tracker
├── README.md                          # Track declaration, setup, usage
├── requirements.txt
├── config.yaml
├── .gitignore                         # chroma_db/, *.mp4, *.m4a, .env, __pycache__/
│
├── specs/                             # Project constitution
│   ├── mission.md
│   ├── tech-stack.md
│   ├── roadmap.md
│   └── corpus.md
│
├── data/
│   ├── raw/
│   │   ├── videos/                    # git-ignored
│   │   └── metadata.json              # 60 entries — video_id, title, URL, duration, license
│   ├── transcripts/                   # Segment JSON from YouTube VTT captions
│   ├── chunks/                        # 45s windows, 10s overlap
│   ├── frame_captions/                # Qwen2-VL-7B captions per keyframe
│   ├── qa_pairs/
│   │   ├── raw/                       # LLM-generated before human review
│   │   └── reviewed/                  # Human-approved, standard schema
│   └── benchmark/
│       └── benchmark_v1.json          # Merged final benchmark
│
├── chroma_db/                         # git-ignored
│   ├── transcript_only/               # Collection 1
│   └── transcript_plus_frames/        # Collection 2
│
├── src/
│   ├── config.py                      # Loads config.yaml, validates all settings
│   ├── transcriber.py                 # YouTube VTT parser → segment JSON
│   ├── chunker.py                     # 45s windows, 10s overlap (prescribed)
│   ├── frame_extractor.py             # Extract keyframes from video
│   ├── frame_captioner.py             # Qwen2-VL-7B captions for keyframes
│   ├── retriever.py                   # Two modes: transcript-only / +frames
│   ├── generator.py                   # Grounded prompt + [video_id @ mm:ss] citations
│   ├── qa_generator.py                # 15 draft QA per lecture via LLM
│   └── evaluator.py                   # Temporal IoU, hit rate@k, LLM-judge
│
├── run_part1.py                       # Deliverable: end-to-end RAG demo
├── run_part2.py                       # Deliverable: benchmark eval (both configs)
│
├── scripts/
│   ├── parse_vtt.py                   # ✅ VTT → transcript JSON
│   ├── build_chunks.py                # ✅ transcript JSON → chunk JSON
│   ├── download_videos.py             # yt-dlp wrapper for all 60 videos
│   ├── build_frame_captions.py        # frame extraction + Qwen2-VL captioning
│   ├── build_index.py                 # ingest chunks into both ChromaDB collections
│   ├── generate_qa.py                 # CLI for LLM draft QA generation
│   ├── build_benchmark.py             # merge reviewed QA → benchmark_v1.json
│   ├── validate_benchmark.py          # schema + quality checks
│
├── notebooks/
│   ├── 01_transcription_exploration.ipynb
│   ├── 02_chunking_analysis.ipynb
│   ├── 03_qa_generation_review.ipynb
│   └── 04_evaluation_analysis.ipynb
│
├── tests/
│   ├── test_chunker.py
│   ├── test_retriever.py
│   └── test_evaluator.py
│
├── report/
│   ├── main.tex
│   └── figures/
│
└── overleaf/                          # Overleaf integration
    ├── assets/                        # git submodule → git.overleaf.com
    ├── sync_overleaf.sh               # pull from Overleaf
    ├── push_to_overleaf.sh            # push to Overleaf
    └── check_status.sh                # diff status
```
