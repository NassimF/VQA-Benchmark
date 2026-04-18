# PROJECT_PLAN.md — Long-Lecture Video RAG Benchmark

**Course:** CS 6263 LLM and Agentic Systems, UTSA  
**Track:** C — Long-Lecture Video RAG and Benchmark Construction  
**GitHub:** https://github.com/NassimF/VQA-Benchmark  
**Instructor:** Dr. Peyman Najafirad | **TA:** Mohammad Bahrami  

---

## What We Are Building

A Visual Question Answering (VQA) benchmark for **long lecture videos**, paired with a full
Retrieval-Augmented Generation (RAG) pipeline that can answer questions about lecture content
and cite the exact video timestamp where the answer was spoken (or shown on slides).

> **RAG in plain terms:** Instead of asking an LLM to answer from memory, we first *retrieve*
> relevant transcript chunks from a vector database (like searching a library), then feed those
> chunks as context to the LLM. The LLM answers using only the retrieved text and cites its sources.
> For this project, sources are timestamp ranges in lecture videos.

---

## Project File Structure

```
VQA_Benchmark/
├── CLAUDE.md
├── PROJECT_PLAN.md                    # Living progress tracker (this file)
├── README.md                          # Track declaration, setup, usage
├── requirements.txt
├── config.yaml
├── .gitignore                         # chroma_db/, *.mp4, *.m4a, .env, __pycache__/
│
├── data/
│   ├── raw/
│   │   ├── videos/                    # git-ignored
│   │   └── metadata.json              # video_id, title, URL, duration, license
│   ├── transcripts/                   # Whisper JSON (word-level timestamps)
│   ├── chunks/                        # 45s windows, 10s overlap
│   ├── frame_captions/                # CLIP/LLaVA captions per keyframe
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
│   ├── transcriber.py                 # Whisper-large-v3 transcription
│   ├── chunker.py                     # 45s windows, 10s overlap (prescribed)
│   ├── frame_extractor.py             # Extract keyframes from video
│   ├── frame_captioner.py             # CLIP or LLaVA captions
│   ├── retriever.py                   # Two modes: transcript-only / +frames (CRITICAL)
│   ├── generator.py                   # Grounded prompt + [video_id @ mm:ss] citations
│   ├── qa_generator.py                # 15 draft QA per lecture via LLM
│   └── evaluator.py                   # Temporal IoU, hit rate@k, LLM-judge
│
├── run_part1.py                       # Deliverable: end-to-end RAG demo
├── run_part2.py                       # Deliverable: benchmark eval (both configs)
│
├── scripts/
│   ├── download_videos.py             # yt-dlp wrapper
│   ├── build_benchmark.py             # Merge reviewed QA → benchmark_v1.json
│   ├── validate_benchmark.py          # Schema + quality checks
│   └── cross_validate.py             # IAA metrics for cross-student annotation
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
└── report/
    ├── main.tex
    └── figures/
```

---

## Phase Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Setup: CLAUDE.md, PROJECT_PLAN.md, git/GitHub, literature review | 🔄 In Progress |
| 1 | Video selection (licensing confirmed) + download | ⏳ Pending |
| 2 | Transcription with whisper-large-v3 | ⏳ Pending |
| 3 | Chunking (45s windows, 10s overlap) | ⏳ Pending |
| 4 | Frame extraction + caption generation | ⏳ Pending |
| 5 | RAG ingestion — two ChromaDB collections | ⏳ Pending |
| 6 | Generator module (grounded prompt + citations) | ⏳ Pending |
| 7 | QA generation + human review (12–15 per lecture) | ⏳ Pending |
| 8 | Cross-student validation (5 annotations + IAA) | ⏳ Pending |
| 9 | Evaluation (both configs: temporal IoU, hit rate@k, LLM-judge) | ⏳ Pending |
| 10 | run_part1.py + run_part2.py | ⏳ Pending |
| 11 | Report (4–6 pages LaTeX) + README | ⏳ Pending |

---

## Phase Step Details

### Phase 0 — Setup
- Create `CLAUDE.md`, `PROJECT_PLAN.md`, `README.md`, `.gitignore`
- Initialize git, link remote, push skeleton
- Run `/literature-review` skill on topics listed below
- Confirm lecture selection with TA before downloading

### Phase 1 — Video Collection
- Download audio-only `.m4a` with `yt-dlp` (saves space vs `.mp4`)
- Write `data/raw/metadata.json`: `video_id`, `title`, `url`, `duration_seconds`, `license`
- Verify CC license for each video before proceeding

### Phase 2 — Transcription
- `whisper-large-v3`, `word_timestamps=True`, `language="en"`
- ~15–25 min per 90-min lecture on GPU; ~3–5 hrs on CPU
- Fallback: `whisper-medium` for iteration, large-v3 for finals
- Output: `data/transcripts/{video_id}.json` (full Whisper dict with word-level start/end)

### Phase 3 — Chunking (prescribed: 45s / 10s)
- Slide a 45s window every 35s (stride = window − overlap)
- Force new chunk at silence gaps > 5s (topic breaks)
- Output: `data/chunks/{video_id}_chunks.json`
- Report justification: 45s captures one concept; 10s overlap prevents answers at boundaries

### Phase 4 — Frame Captions
- Extract 1 frame every 30s with `ffmpeg` or `cv2`
- Caption with CLIP zero-shot OR BLIP-2/LLaVA (decision pending)
- Store: `{"frame_id": ..., "time": 120.0, "caption": "Slide showing merge sort diagram"}`
- Append captions to nearest chunk for Collection 2

### Phase 5 — RAG Ingestion
- Embed with `all-MiniLM-L6-v2`; store in two ChromaDB collections
- Metadata per chunk: `video_id`, `start_time`, `end_time`, `chunk_id`
- Add `--rebuild` CLI flag to force re-ingestion without silently overwriting

### Phase 6 — Generator
- Numbered excerpts prompt with timestamps; structured JSON output for citations
- Parse cited chunk indices → predicted span = union of cited chunk time ranges
- Citation string: `[mit_6046_lec01 @ 30:23 to 31:41](https://youtu.be/ID?t=1823)`

### Phase 7 — QA Generation & Review
- Generate 15 drafts per lecture with Claude/GPT-4 given transcript + keyframe captions
- Human review: watch cited span, tighten spans, rewrite awkward questions
- Add 2–4 visual-dependent questions the LLM missed
- Mark exactly 1 question per lecture `"answerable": false`
- Filter: reject if answer < 10 words or if answer is verbatim in the question

### Phase 8 — Cross-Student Validation
- Receive 5 QA pairs from a classmate; annotate in same schema
- Run `scripts/cross_validate.py` → Cohen's Kappa on `answerable`, mean IoU on spans

### Phase 9 — Evaluation
- Both configs × all verified questions
- Save per-question results to `results/evaluation_results.json`
- Generate summary tables and plots for the report

### Phase 10 — run_part1.py / run_part2.py
- `run_part1.py`: demo pipeline, accepts question via `argparse` or uses 3 hardcoded examples
- `run_part2.py`: full eval loop → both configs → summary table → save JSON + plots

### Phase 11 — Report & README
- LaTeX, 4–6 pages; every parameter choice explained and justified (not just stated)
- README declares Track C; includes setup and usage instructions

---

## Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Chunking strategy | Whisper segment grouping, 45s/10s | Prescribed; respects speech boundaries |
| Overlapping chunks | Yes, 10s overlap | Prevents answers falling at chunk edges |
| Embedding model | all-MiniLM-L6-v2 | Prescribed; fast, lightweight, strong retrieval |
| Vector DB | ChromaDB persistent | Prescribed |
| Citation format | `[video_id @ mm:ss to mm:ss]` | Prescribed; YouTube deep-linkable |
| Structured output | JSON from LLM | More reliable than regex-parsing `[1]` |
| Span aggregation | Union of cited chunk spans | Standard for multi-chunk answers |
| Frame interval | 30s | Balances coverage vs. storage |

---

## Report Structure (4–6 pages)

| Section | Length | Content |
|---------|--------|---------|
| Abstract | ~150 words | What was built, key metrics |
| Introduction | ~0.5 page | Motivation, gap in long-video QA benchmarks |
| Related Work | ~0.75 page | Video QA, temporal grounding, RAG, Whisper |
| Pipeline | ~1 page | Transcription, chunking, frame captions, retrieval, generation |
| Benchmark Contribution | ~1 page | Lecture selection, QA generation method, IAA, QA breakdown |
| Results | ~1 page | Both configs side-by-side, failure mode analysis |
| Conclusion | ~0.25 page | Limitations, future work |

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Track C selected | Research exposure + co-authorship eligibility |
| 2026-04-18 | Chunking: 45s window, 10s overlap | Prescribed by assignment |
| 2026-04-18 | Embedding: all-MiniLM-L6-v2 | Prescribed by assignment |
| — | Lectures: TBD | Need TA assignment or user choice |
| — | Generator model: TBD | UTSA Llama / Claude / GPT-4o-mini |
| — | Frame captioner: TBD | CLIP vs BLIP-2/LLaVA |

---

## Required Deliverables

- [ ] `config.yaml`
- [ ] `src/retriever.py` (transcript-only and transcript+frames modes)
- [ ] `src/generator.py`
- [ ] `run_part1.py` — end-to-end RAG demo
- [ ] `run_part2.py` — full benchmark evaluation (both retrieval configs)
- [ ] `requirements.txt`
- [ ] `data/benchmark/benchmark_v1.json` (12–15 QA × 2–4 lectures)
- [ ] Cross-validation annotations (5 questions from a classmate)
- [ ] 4–6 page report (`report/main.tex`)
- [ ] `README.md` (declares Track C)
- [ ] `.gitignore`

---

## Key Metrics to Report

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|--------------------------|------------------------------|
| Mean Temporal IoU | | |
| IoU@0.3 | | |
| IoU@0.5 | | |
| Hit Rate@1 | | |
| Hit Rate@3 | | |
| Hit Rate@5 | | |
| LLM-Judge Score (1–5) | | |
| Citation Accuracy | | |

---

## Git Checkpoints

| Checkpoint | Commit Message | Date |
|------------|---------------|------|
| Phase 0 complete | `feat: project skeleton and docs` | — |
| Phase 2 complete | `feat: transcription pipeline` | — |
| Phase 3 complete | `feat: chunking pipeline` | — |
| Phase 4 complete | `feat: frame caption pipeline` | — |
| Phase 5 complete | `feat: RAG ingestion (both configs)` | — |
| Phase 6 complete | `feat: generator module` | — |
| Phase 7 complete | `data: reviewed QA pairs` | — |
| Phase 8 complete | `data: cross-validation annotations` | — |
| Phase 9 complete | `feat: evaluation pipeline` | — |
| Phase 10 complete | `feat: run_part1 and run_part2` | — |
| Phase 11 complete | `docs: final report and README` | — |

---

## Video Licensing Notes

- **MIT OpenCourseWare**: CC BY-NC-SA 4.0 — academic/non-commercial use with attribution is allowed. No permission request needed.
- **Stanford Online**: License varies per course — must verify before using.
- Assignment states: *"each student is assigned 2–4 specific lectures"* — confirm with TA whether lectures are pre-assigned.

---

## config.yaml (Reference)

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

generator:
  model: "utsa-llama"         # or "claude-3-haiku-20240307" / "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 512
  citation_format: "[{video_id} @ {start_mm}:{start_ss} to {end_mm}:{end_ss}]"

qa_generation:
  questions_per_lecture: 15
  target_accepted: 12
```

---

## Evaluation Metric Formulas

### Temporal IoU
```python
def temporal_iou(pred_start, pred_end, gt_start, gt_end):
    intersection = max(0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0 else 0.0
```
Thresholds: IoU@0.3 and IoU@0.5. Predicted span = union of cited chunk spans.

### Hit Rate @ k (k = 1, 3, 5)
Fraction of questions where at least 1 of the top-k retrieved chunks has IoU > 0.3 with the ground truth span.

### LLM-Judge Score
Feed `question + generated_answer + reference_answer` to an LLM; ask it to score 1–5 for accuracy and grounding. More reliable than ROUGE for long-form answers.

### Citation Accuracy
Of the chunks the LLM cited `[1]`, `[2]` etc., what fraction actually contained the answer.

### Cross-Validation IAA
Cohen's Kappa on the `answerable` field between your annotation and the original author's.
Temporal IoU between your annotated span and the original span.

---

## QA Pair Standard Schema

```json
{
  "qa_id": "mit_6046_lec01_q007",
  "video_id": "mit_6046_lec01",
  "question": "...",
  "answer": "...",
  "ground_truth_start": 1823.4,
  "ground_truth_end": 1901.2,
  "source_chunk_id": "mit_6046_lec01_chunk_042",
  "question_type": "conceptual|procedural|factual|visual",
  "difficulty": "easy|medium|hard",
  "answerable": true,
  "key_concepts": ["concept1"],
  "reviewed_by": "human",
  "review_date": "2026-04-20"
}
```

Target mix per lecture: 6 conceptual, 4 procedural, 3 factual, 2+ visual (slide/whiteboard), 1 unanswerable.

---

## Literature Review Topics

| Topic | Key Papers |
|-------|-----------|
| Video QA Benchmarks | ActivityNet-QA, NExT-QA, EgoSchema, MSVD-QA |
| Temporal Grounding | Gao et al. 2017 (defines temporal IoU), 2D-TAN, Moment-DETR |
| RAG Systems | Lewis et al. 2020 (original RAG), REALM, REPLUG |
| Whisper ASR | Radford et al. 2023 |
| Educational Video QA | LectureSQA and similar |
| Chunking & Retrieval | RAPTOR, HyDE |
| Multimodal Retrieval | CLIP (Radford 2021), BLIP-2 |

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Whisper OOM on long video | Use `faster-whisper` or split audio into 30-min segments |
| ChromaDB collection already exists on rerun | Check before creating; add `--rebuild` CLI flag |
| LLM doesn't reliably output `[1]` citations | Use structured JSON output instead of regex parsing |
| Trivial QA pairs | Filter in `validate_benchmark.py`: reject if answer < 10 words or verbatim in question |
| Predicted span too wide | For factual Qs use intersection; for multi-chunk use union of cited spans |

---

## Candidate Lectures (pending confirmation)

| ID | Course | Topic | Why Good |
|----|--------|-------|----------|
| `mit_6046_lec01` | MIT 6.046J | Dynamic Programming | Dense slides, clear concept moments |
| `mit_6046_lec02` | MIT 6.046J | Graph Algorithms | Multiple steps = good temporal QA |
| `mit_18065_lec01` | MIT 18.065 | SVD | Whiteboard-heavy = good frame-caption test |
| `mit_6006_lec01` | MIT 6.006 | Peak Finding | Classic, YouTube available |

**Action required:** Confirm with TA if lectures are pre-assigned, or choose 2–4 from above.

---

## Notes & Observations

*(Updated as the project progresses)*

---

*Last updated: 2026-04-18*
