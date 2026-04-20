# PROJECT_PLAN.md — Long-Lecture Video RAG Benchmark

**Course:** CS 6263 LLM and Agentic Systems, UTSA  
**Track:** C — Long-Lecture Video RAG and Benchmark Construction  
**GitHub:** https://github.com/NassimF/VQA-Benchmark  
**Instructor:** Dr. Peyman Najafirad | **TA:** Mohammad Bahrami  

---

## What We Are Building

A **multi-hop** Visual Question Answering (VQA) benchmark for **long lecture videos**, paired with a full Retrieval-Augmented Generation (RAG) pipeline. Questions are designed so the answer requires connecting information from **two or more non-adjacent segments** of the video — not just finding a single relevant clip.

> **Multi-hop in plain terms:** A single-hop question ("What is memoization?") has one answer location. A multi-hop question ("How does the subproblem property introduced at the start of the lecture justify the complexity claim made at the end?") requires the model to retrieve chunks from two different parts of the video and synthesize them. This is harder, more realistic, and more useful as a benchmark.

> **RAG in plain terms:** Instead of asking an LLM to answer from memory, we first *retrieve* relevant transcript chunks from a vector database (like searching a library), then feed those chunks as context to the LLM. The LLM answers using only the retrieved text and cites its sources — here, timestamp ranges in the video.

---

## Selected Lectures

### Selected Lectures

| Video ID | Course | Topic | Multi-hop value | Frame-caption value | License | URL |
|----------|--------|-------|----------------|---------------------|---------|-----|
| `mit_6046_lec10` | MIT 6.046J Algorithms | Dynamic Programming: Advanced DP | ✅ High — DP fundamentals reused, builds recurrence → memoization → complexity | Medium (slides) | CC BY-NC-SA 4.0 ✓ | https://www.youtube.com/watch?v=Tw1k46ywN6E (80 min) |
| `mit_18065_lec06` | MIT 18.065 Matrix Methods | Singular Value Decomposition (SVD) | ✅ Very high — eigenvalues → factorization → geometry → low-rank approx | High (whiteboard) | CC BY-NC-SA 4.0 ✓ | https://www.youtube.com/watch?v=rYz83XPxiZo (54 min) |
| `nyu_dl_week6` | NYU Deep Learning (LeCun/Canziani) | CNN + RNN + Attention | ✅ Very high — CNN → RNN → attention built incrementally | Medium (diagrams) | **CC BY ✓** | https://www.youtube.com/watch?v=ycbMGyCPzvE |
| `nyu_dl_week7` | NYU Deep Learning (LeCun/Canziani) | Energy-Based Models + Self-Supervised Learning | ✅ High — EBM framing reused throughout | Low–Medium | **CC BY ✓** | https://www.youtube.com/watch?v=PHxKk5Y5ayc |

**Start with:** `mit_6046_lec10` + `mit_18065_lec06` (Phase 1). Add NYU lectures in a later phase once the pipeline is validated.

All four lectures were selected because concepts introduced early are explicitly reused and extended later — the structural requirement for meaningful multi-hop questions. NYU Week 6 is particularly strong: attention is derived from CNN and RNN concepts introduced earlier in the same 89-minute lecture.

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
│   ├── transcripts/                   # Segment JSON from YouTube VTT captions
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
│   ├── transcriber.py                 # YouTube VTT parser → segment JSON
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
│   ├── parse_vtt.py                   # ✅ VTT → transcript JSON
│   ├── build_chunks.py                # ✅ transcript JSON → chunk JSON
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
| 0 | Setup: CLAUDE.md, PROJECT_PLAN.md, git/GitHub, literature review | ✅ Complete |
| 1 | Video selection (licensing confirmed) + download | ✅ Complete |
| 2 | Transcription (YouTube VTT → segment JSON) | ✅ Complete |
| 3 | Chunking (45s windows, 10s overlap) | ✅ Complete |
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
- Download full video `.mp4` with `yt-dlp` — required for frame extraction in Phase 4
  - Audio-only `.m4a` is NOT sufficient; frames are needed for the transcript+frames retrieval config
  - `ffmpeg` will extract the audio track from `.mp4` for Whisper; no separate audio download needed
- Write `data/raw/metadata.json`: `video_id`, `title`, `url`, `youtube_id`, `duration_seconds`, `license`
- Verify CC license for each video before proceeding

### Phase 2 — Transcription ✅
**Option A used — YouTube auto-captions:**
- VTT files pre-downloaded to `data/raw/videos/{video_id}.en.vtt`
- `src/transcriber.py` parses rolling-caption VTT: collects ~10ms "display" cues (one clean phrase each), strips inline timing tags, de-duplicates consecutive identical lines
- Output: `data/transcripts/{video_id}.json` — 1,569 segments (mit_6046_lec10), 909 (mit_18065_lec06)
- Quality spot-checked at 20-min mark of both lectures; 0 errors on technical terms
- Run: `python scripts/parse_vtt.py --all`

**Option B — Whisper-large-v3 (fallback, not needed):**
- Would be used if captions were missing or had significant technical errors
- Extract audio: `ffmpeg -i video.mp4 -ar 16000 -ac 1 audio.wav`
- Run: `whisper-large-v3`, `word_timestamps=True`, `language="en"`

**Report note:** Used Option A; quality verified; VTT phrase-level timestamps (~3s per segment) are sufficient for 45s chunking windows.

### Phase 3 — Chunking (prescribed: 45s / 10s) ✅
- Slide a 45s window every 35s (stride = window − overlap)
- Segments assigned to chunk if `start` falls in `[win_start, win_start+45s)` — half-open interval
- Empty windows (no segments) are skipped automatically
- Output: `data/chunks/{video_id}_chunks.json`
- Result: 138 chunks (mit_6046_lec10, 80 min), 92 chunks (mit_18065_lec06, 54 min)
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
| Chunking strategy | YouTube VTT phrase segments, 45s/10s time window | Prescribed; phrase boundaries from VTT naturally align with speech |
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
| 2026-04-20 | Lectures: mit_6046_lec10 + mit_18065_lec06 | CC BY-NC-SA 4.0; strong multi-hop potential; VTTs pre-downloaded |
| 2026-04-20 | Transcription: YouTube auto-captions (Option A) | Quality spot-checked at 20-min mark; 0 errors on technical terms |
| 2026-04-20 | Generator model: gpt-4o-mini | Cost-effective; reliable structured JSON output |
| — | Frame captioner: TBD | CLIP vs BLIP-2/LLaVA |

---

## Required Deliverables

- [x] `config.yaml`
- [ ] `src/retriever.py` (transcript-only and transcript+frames modes)
- [ ] `src/generator.py`
- [ ] `run_part1.py` — end-to-end RAG demo
- [ ] `run_part2.py` — full benchmark evaluation (both retrieval configs)
- [x] `requirements.txt`
- [ ] `data/benchmark/benchmark_v1.json` (12–15 QA × 2–4 lectures)
- [ ] Cross-validation annotations (5 questions from a classmate)
- [ ] 4–6 page report (`report/main.tex`)
- [ ] `README.md` (declares Track C)
- [ ] `.gitignore`

---

## Key Metrics to Report

Multi-hop VQA requires separate metrics for single-hop and multi-hop questions, reported side-by-side across both retrieval configs.

### Single-hop questions

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

### Multi-hop questions

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|--------------------------|------------------------------|
| Mean Per-Hop IoU | | |
| Complete Retrieval Rate@5 | | |
| Per-Hop Recall@5 | | |
| Multi-hop IoU@0.3 (union) | | |
| LLM-Judge Score (1–5) | | |
| Citation Accuracy | | |

---

## Git Reminder

After every major phase checkpoint: stage the relevant files, commit, and push to `origin/main`. Never leave more than one phase worth of work uncommitted.

---

## Git Checkpoints

| Checkpoint | Commit Message | Date |
|------------|---------------|------|
| Phase 0 complete | `feat: project skeleton and docs` | 2026-04-18 |
| Phase 2 complete | `feat: transcription pipeline (Phase 2)` | 2026-04-20 |
| Phase 3 complete | `feat: chunking pipeline (Phase 3)` | 2026-04-20 |
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
- **NYU Deep Learning (LeCun/Canziani)**: CC BY — most permissive; attribution only.
- **Stanford**: All YouTube uploads return Standard YouTube License (verified 2026-04-19). Not suitable for this benchmark.
- Assignment states: *"each student is assigned 2–4 specific lectures"* — confirmed with TA that selection is free choice.

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
  model: "gpt-4o-mini"        # or "utsa-llama" / "claude-3-haiku-20240307"
  temperature: 0.1
  max_tokens: 512
  citation_format: "[{video_id} @ {start_mm}:{start_ss} to {end_mm}:{end_ss}]"

qa_generation:
  questions_per_lecture: 15
  target_accepted: 12
```

---

## Evaluation Metric Formulas

### Single-hop Temporal IoU
```python
def temporal_iou(pred_start, pred_end, gt_start, gt_end):
    intersection = max(0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0 else 0.0
```
Predicted span = union of cited chunk spans. Thresholds: IoU@0.3 and IoU@0.5.

### Multi-hop Temporal IoU
Ground truth is a **list of spans** (one per hop). Two metrics:

```python
def multihop_per_hop_iou(pred_spans, gt_spans):
    """Mean IoU between each GT hop and its best-matching predicted span."""
    scores = []
    for gt_start, gt_end in gt_spans:
        best = max(temporal_iou(ps, pe, gt_start, gt_end) for ps, pe in pred_spans)
        scores.append(best)
    return sum(scores) / len(scores)

def multihop_union_iou(pred_spans, gt_spans):
    """IoU between the union of all predicted spans and union of all GT spans."""
    # merge overlapping spans, then compute single IoU on merged intervals
    ...
```

### Hit Rate @ k (k = 1, 3, 5)
- **Single-hop:** ≥1 of top-k chunks has IoU > 0.3 with the GT span
- **Multi-hop — Per-hop recall:** fraction of GT hops covered by ≥1 top-k chunk (IoU > 0.3)
- **Multi-hop — Complete retrieval rate:** fraction of questions where ALL hops are covered by top-k

### LLM-Judge Score
Feed `question + generated_answer + reference_answer` to an LLM; score 1–5 for accuracy and grounding. Applied to both single-hop and multi-hop questions.

### Citation Accuracy
Of the chunks the LLM cited `[1]`, `[2]` etc., what fraction actually contained the answer. For multi-hop, check that at least one citation per hop is relevant.

### Cross-Validation IAA
Cohen's Kappa on the `answerable` field between your annotation and the original author's.
Mean temporal IoU between your annotated spans and the original spans.

---

## QA Pair Standard Schema

Single-hop and multi-hop questions use the same schema, with multi-hop using a list of spans instead of one.

```json
{
  "qa_id": "mit_6046_lec01_q007",
  "video_id": "mit_6046_lec01",
  "question": "...",
  "answer": "...",

  "num_hops": 2,
  "ground_truth_spans": [
    {"start": 320.0, "end": 398.0, "hop": 1, "description": "subproblem property introduced"},
    {"start": 2870.0, "end": 2940.0, "hop": 2, "description": "complexity claim relying on subproblem property"}
  ],

  "source_chunk_ids": ["mit_6046_lec01_chunk_009", "mit_6046_lec01_chunk_082"],
  "question_type": "multi-hop|conceptual|procedural|factual|visual",
  "difficulty": "easy|medium|hard",
  "answerable": true,
  "key_concepts": ["memoization", "optimal substructure"],
  "reviewed_by": "human",
  "review_date": "2026-04-20"
}
```

**Notes:**
- Single-hop questions: `num_hops: 1`, `ground_truth_spans` has one entry, `source_chunk_ids` has one entry
- The `description` field per hop is essential for human review — it records *why* that span is needed
- Unanswerable questions: `answerable: false`, `ground_truth_spans: []`

**Target question mix per lecture (12–15 accepted):**

| Type | Count | Notes |
|------|-------|-------|
| Multi-hop | 5–6 | Core contribution; require 2+ non-adjacent spans |
| Single-hop conceptual | 3–4 | Explain a concept from one segment |
| Single-hop factual | 2–3 | Direct fact stated at one timestamp |
| Visual-dependent | 2+ | Require reading a slide/whiteboard; add manually |
| Unanswerable | 1 | Exactly 1 per lecture |

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

## Notes & Observations

**Scale context:**
- 4 lectures (2 MIT + 2 NYU) with ~50–60 total QA pairs is enough for a workshop paper or course project
- For a full venue (EMNLP, ACL, NeurIPS datasets track), you'd want 10–20 lectures and 150–200 QA pairs

**Transcription (Phase 2):**
- YouTube auto-captions chosen over Whisper — pre-downloaded VTTs were clean on technical terms (eigenvectors, memoization, hash table verified). This saves ~1–2 hrs of GPU time per lecture.
- VTT "rolling caption" format alternates word-timing cues (~2s) with display cues (~10ms). The display cues carry one clean subtitle phrase each — these are the source of segments.
- Segment granularity: ~3s per phrase → 1,569 segments for 80-min lecture.

**Chunking (Phase 3):**
- Pure time-based windowing: segment belongs to chunk if `segment.start ∈ [win_start, win_start+45s)`. No silence-gap detection implemented — not needed given dense lecture speech.
- Overlap confirmed by unit test: segment starting at 40s appears in both chunk [0–45s) and chunk [35–80s).
- Chunk counts match theoretical ⌈duration/stride⌉: 138 for 80 min, 92 for 54 min.
- 8/8 unit tests passing (pytest).

---

*Last updated: 2026-04-20*
