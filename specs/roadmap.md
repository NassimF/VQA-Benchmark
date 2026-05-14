# Roadmap

Implementation order in small phases of 1–3 files each. Each phase has a clear deliverable and a git checkpoint.

Status: ✅ Complete | ⚠️ Partial | ⏳ Pending

---

## Overview

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0.1 | Project skeleton (CLAUDE.md, config, .gitignore) | ✅ |
| 0.2 | Literature review | ✅ |
| 1.1 | `scripts/download_videos.py` | ✅ |
| 1.2 | Download all 60 videos + VTTs | ✅ 60/60 done |
| 2.1 | `scripts/parse_vtt.py` — VTT → transcript JSON | ✅ |
| 2.2 | Run transcription for remaining 56 lectures | ✅ 60/60 done |
| 3.1 | `scripts/build_chunks.py` — chunking pipeline | ✅ |
| 3.2 | Run chunking for remaining 56 lectures | ✅ 60/60 done |
| 4.1 | `src/frame_captioner.py` — Qwen2-VL-7B captioner | ✅ |
| 4.2 | Run `scripts/build_frame_captions.py --all --device cuda` | ✅ 60/60 done |
| 5.1 | `src/retriever.py` — two ChromaDB collections | ✅ |
| 5.2 | `scripts/build_index.py` — ingest all chunks | ✅ 60/60, both collections |
| 6.1 | `src/generator.py` — grounded prompt + citations | ✅ |
| 7.1 | `src/qa_generator.py` — LLM draft QA | ✅ |
| 7.2 | `scripts/generate_qa.py` — CLI for draft generation | ✅ 60/60 done |
| 7.3 | LLM review + `scripts/regenerate_qa.py` — populate `data/qa_pairs/reviewed/` | ⏳ |
| 7.4 | `scripts/build_benchmark.py` + `validate_benchmark.py` | ⏳ |
| 7.5 | `scripts/audit_span_precision.py` — empirical span error → validate tIoU@0.3 | ⏳ |
| 8.1 | `src/evaluator.py` — temporal IoU, hit rate@k, LLM-judge | ⏳ |
| 9.1 | `run_part1.py` — end-to-end RAG demo | ⏳ |
| 9.2 | `run_part2.py` — full benchmark eval, both configs | ⏳ |
| 9.3 | `scripts/reproduce_tables.py` — one function per paper table | ⏳ |
| 9.4 | `results.md` — reproduced vs. reported numbers, Config 1 vs Config 2 | ⏳ |
| 10.1 | `overleaf/assets/vqa_benchmark.tex` — conference paper | ⚠️ |
| 10.2 | `README.md` | ⏳ |

---

## Phase 0 — Setup ✅

### 0.1 — Project skeleton
- [x] `CLAUDE.md` — coding conventions, architecture rules
- [x] `config.yaml` — all parameters; nothing hardcoded in source
- [x] `requirements.txt`
- [x] `.gitignore` — excludes `chroma_db/`, `*.mp4`, `*.mkv`, `*.webm`, `*.m4a`, `.env`, `__pycache__/`, `data/raw/videos/`
- [x] `data/raw/metadata.json` — 60 entries with video_id, URL, license, duration

### 0.2 — Literature review
- [x] `/literature-review` skill run; 28 papers across 7 clusters
- [x] `literature-review/literature_review_report.md` committed

**Key papers by cluster:**

| Topic | Key Papers |
|-------|-----------|
| Video QA Benchmarks | ActivityNet-QA, NExT-QA, EgoSchema, MSVD-QA |
| Temporal Grounding | Gao et al. 2017 (defines temporal IoU), 2D-TAN, Moment-DETR |
| RAG Systems | Lewis et al. 2020 (original RAG), REALM, REPLUG |
| Whisper ASR | Radford et al. 2023 |
| Educational Video QA | LectureSQA and similar |
| Chunking & Retrieval | RAPTOR, HyDE |
| Multimodal Retrieval | CLIP (Radford 2021), Qwen2-VL |

**Git checkpoint:** `feat: project skeleton and docs`

**Paper reminder — `sections/related_work.tex`:** Literature review is complete. Draft the Related Work section now (~0.75 page): Video QA benchmarks (ActivityNet-QA, NExT-QA, EgoSchema), temporal grounding (Gao et al. 2017, 2D-TAN, Moment-DETR), RAG (Lewis et al. 2020, REALM, REPLUG), Whisper (Radford 2023), educational video QA (LectureSQA), multimodal retrieval (CLIP, Qwen2-VL).

---

## Phase 1 — Video Collection ✅

### 1.1 — Download script ✅
**File:** `scripts/download_videos.py`

- Reads `data/raw/metadata.json`; iterates all 60 entries
- Uses `yt-dlp` to download full video (`.mp4`, `.mkv`, or `.webm`) — full video required for frame extraction
- Downloads `.en.vtt` auto-caption file in same pass
- Skips entries where both video file and VTT already exist
- CLI: `python scripts/download_videos.py --all` or `--video_id <id>`

Notes:
- MKV and WEBM output (AV1/VP9 codec) is fine — ffmpeg handles all formats downstream
- Do not download audio-only; frames are required for Phase 4

### 1.2 — Execute downloads ✅
- All 60 videos and VTTs on disk as of 2026-04-22
- Mix of `.mkv` and `.webm` formats (yt-dlp format selection)
- 2 videos (`mit_6042_lec06`, `mit_6042_lec22`) required `--remote-components ejs:github` for subtitle retrieval
- 1 video (`nyu_dl_week1`) temp file renamed to `.webm` after interrupted merge

**Git checkpoint:** `feat: download pipeline`

---

## Phase 2 — Transcription ✅

### 2.1 — VTT parser (already written)
**File:** `scripts/parse_vtt.py` | **Module:** `src/transcriber.py`

- Parses YouTube rolling-caption VTT format
- Collects ~10ms "display" cues (one clean subtitle phrase each)
- Strips inline timing tags (`<00:00:00.000>`), deduplicates consecutive identical lines
- Output: `data/transcripts/{video_id}.json` — list of `{text, start_time, end_time}` segments
- CLI: `python scripts/parse_vtt.py --all`

Completed results:
- `mit_6046_lec10`: 1,569 segments
- `mit_18065_lec06`: 909 segments
- `nyu_dl_week6`: 1,761 segments
- `nyu_dl_week7`: 1,966 segments (~97 min actual; metadata duration needs correction)

Quality checks:
- MIT lectures: spot-checked at 20-min mark; 0 errors on technical terms
- NYU lectures: VTTs downloaded, caption quality not yet checked (`decision: "pending"` in metadata)

### 2.2 — Run for remaining 56 lectures
- Run `python scripts/parse_vtt.py --all` after Phase 1.2 completes
- Spot-check at least 2 technical terms per new lecture; update `caption_quality_check` in metadata

**Report note:** YouTube auto-captions chosen over Whisper — VTT phrase-level timestamps (~3s per segment) sufficient for 45s chunking windows; saves ~1–2 GPU-hours per lecture.

**Git checkpoint:** `feat: transcription pipeline (Phase 2)`

**Paper reminder — `sections/pipeline.tex` (transcription):** Add the Transcription subsection: YouTube auto-captions chosen over Whisper, VTT phrase-level timestamps (~3s/segment), deduplication of rolling-caption cues. Justify the choice (saves ~1–2 GPU-hours/lecture; timestamps sufficient for 45s chunks).

---

## Phase 3 — Chunking ✅

### 3.1 — Chunking pipeline (already written)
**File:** `scripts/build_chunks.py` | **Module:** `src/chunker.py`

- Slides a 45s window every 35s (stride = window − overlap = 45 − 10 = 35)
- Segment assigned to chunk if `segment.start ∈ [win_start, win_start + 45s)` — half-open interval
- Empty windows skipped automatically
- Output: `data/chunks/{video_id}_chunks.json`
- CLI: `python scripts/build_chunks.py --all`

Completed results:
- `mit_6046_lec10` (80 min): 138 chunks — matches theoretical ⌈4800/35⌉
- `mit_18065_lec06` (54 min): 92 chunks
- `nyu_dl_week6` (89 min): 153 chunks
- `nyu_dl_week7` (~97 min): 167 chunks

Unit tests: 8/8 passing — verified overlap (segment at 40s in two chunks), boundary behavior, tail coverage, empty-window skipping, `chunk_id` format.

### 3.2 — Run for remaining 56 lectures
- Run `python scripts/build_chunks.py --all` after Phase 2.2 completes

**Report justification:** 45s captures one complete concept explanation; 10s overlap prevents answers from falling at chunk boundaries.

**Git checkpoint:** `feat: chunking pipeline (Phase 3)`

**Paper reminder — `sections/pipeline.tex` (chunking):** Add the Chunking subsection: 45s windows, 10s overlap (stride 35s), half-open interval assignment, empty-window skipping. Justify: 45s captures one complete concept; 10s overlap prevents answers falling at chunk boundaries.

---

## Phase 4 — Frame Captions ✅

### 4.1 — Frame captioner (already written)
**File:** `src/frame_captioner.py`

- Loads `Qwen2VLForConditionalGeneration` in bfloat16 on CUDA
- Prompt: *"Describe this lecture slide or whiteboard frame in detail. Include all visible text, equations, diagrams, and labels. Be specific — this caption will be used for academic retrieval."*
- Input: BGR numpy array → PIL RGB → Qwen2-VL chat template via `process_vision_info`
- Output: `FrameCaption(frame_id, video_id, time, caption)`
- Model name and `max_new_tokens` read from `cfg.frame_captioner`

### 4.2 — Run frame extraction + captioning
**File:** `scripts/build_frame_captions.py`

- Extracts 1 frame every 15s via ffmpeg (handles mp4/mkv/webm, AV1/VP9/H.264)
- Calls `caption_frames()` with `cfg.frame_captioner.model` and `cfg.frame_captioner.max_new_tokens`
- Saves: `data/frame_captions/{video_id}_frame_captions.json`
- Builds augmented chunks: appends `[frame caption: ...]` to each chunk's text; saves `data/chunks/{video_id}_chunks_augmented.json`
- CLI: `python scripts/build_frame_captions.py --all --device cuda`

**Must complete before Phase 5** — Collection 2 ingests augmented chunks.

**Design rationale — 15s frame interval (changed from 30s):**
The original 30s interval used a nearest-midpoint strategy (one caption per chunk), which
could assign a frame up to 22.5s from one edge of the window — missing a slide transition
or mid-chunk whiteboard step. Changed to 15s with all-in-window assignment: all frames
whose timestamp falls within `[chunk.start_time, chunk.end_time)` are concatenated into
the chunk text, giving ~3 captions per 45s chunk consistently. This better supports visual
multi-hop questions (slide text + equations captured across the full window).
At ~0.5–2s/frame on an A100 (Qwen2-VL-7B in bfloat16): 15,020 frames ≈ 4–8 GPU-hours.

**Design rationale — frames and chunk overlap:**
Frames whose timestamp falls in the 10s overlap zone (e.g. t=0:35 for chunks A: 0:00–0:45
and B: 0:35–1:20) are included in both neighboring chunks. This is intentional — it mirrors
how transcript segments in the overlap appear in both chunks and ensures evidence at a chunk
boundary is retrievable from either side.

**Git checkpoint:** `feat: frame caption pipeline (Phase 4)`

**Paper reminder — `sections/pipeline.tex` (frame captions):** Add the Frame Caption subsection: 1 frame every 15s via ffmpeg, all-in-window assignment (~3 captions/45s chunk), Qwen2-VL-7B-Instruct in bfloat16 on A100, Approach A (captions appended to chunk text). Justify: 15s + all-in-window captures slide transitions missed by 30s nearest-midpoint; Qwen2-VL reads slide text and equations; Approach A keeps both collections under the same embedding model.

---

## Phase 5 — RAG Ingestion ✅

### 5.1 — Retriever module ✅
**File:** `src/retriever.py`

Single `Retriever(mode="transcript_only" | "transcript_plus_frames")` class (not two classes —
see `specs/2026-05-08-rag-ingestion/requirements.md`). Injects `chroma_client` and `embedder`
overrides for unit-test isolation.

- `build(video_ids, rebuild=False) -> int` — encodes and ingests chunks; skips existing unless `rebuild=True`
- `query(question, top_k, video_id=None) -> list[dict]` — returns `{chunk_id, video_id, start_time, end_time, text, score}`; `score = 1 - cosine_distance`
- `count() -> int`

Collections: `lecture_transcript_only`, `lecture_transcript_plus_frames`  
Metadata per chunk: `video_id`, `start_time`, `end_time`, `chunk_id`  
Packages: chromadb 1.5.8, sentence-transformers 5.4.1

### 5.2 — Ingestion script ✅
**File:** `scripts/build_index.py`

- Ingests all chunks for all 60 lectures into both collections
- CLI: `python scripts/build_index.py --all [--video_id <id>] [--mode transcript_only|transcript_plus_frames|both] [--rebuild]`
- Unit tests: `tests/test_retriever.py` — 8/8 passing with synthetic in-memory fixtures

**Git checkpoint:** `feat: RAG ingestion, both configs (Phase 5)`

**Paper reminder — `sections/pipeline.tex` (retrieval):** Add the Retrieval subsection: two ChromaDB collections, all-MiniLM-L6-v2 embeddings (prescribed), cosine distance, top-k=4. Finalize and review the full Pipeline section — it should now be complete.

---

## Phase 6 — Generator ✅

### 6.1 — Generator module ✅
**File:** `src/generator.py`

- Accepts a question and list of retrieved chunks (with timestamps)
- Builds a numbered-excerpt prompt: each chunk shown as `[N] {video_id} @ mm:ss–mm:ss\n{text}`
- Calls configured LLM (gpt-4o-mini / utsa-llama / claude-haiku) with `temperature=0.1`
- Requests structured JSON output: `{"answer": "...", "citations": [1, 3]}`
- Parses cited chunk indices → predicted span = union of cited chunk time ranges
- Formats citation string: `[video_id @ mm:ss to mm:ss](https://youtu.be/VIDEO_ID?t=SECONDS)`

**Git checkpoint:** `feat: generator module (Phase 6)`

---

## Phase 7 — QA Generation & Review ⏳

> Review method: LLM-only curation gate (Claude Sonnet 4.6 + GPT-4o C1 cross-check).
> Ground truth spans are LLM-estimated (~±15–30s precision) — disclosed as a limitation.
> Note: a human spot-check (D8b, ~60–70 pairs, Cohen's κ) is documented as optional future
> validation but not planned for the current submission. See `specs/2026-05-12-llm-review/requirements.md`.

**Report note — model asymmetry justification (✅ written in `sections/benchmark.tex`):** Ground truth QA pairs are generated by a strong model (claude-sonnet-4-6) and LLM-reviewed; candidate answers at evaluation time are generated by a weaker model (gpt-4o-mini) constrained to retrieved chunks only. This asymmetry is intentional: using the same model for both would be circular.

### 7.1 — QA generator module
**File:** `src/qa_generator.py`

- Sends augmented chunks (`data/chunks/{video_id}_chunks_augmented.json`) for one lecture to `claude-sonnet-4-6`
- Prompt instructs: generate 15 QA pairs with the locked question type mix (see below)
- Returns list of draft QA dicts matching the standard schema (`qa_id`, `question`, `answer`, `ground_truth_spans`, etc.)

### 7.2 — Generation script
**File:** `scripts/generate_qa.py`

- CLI: `python scripts/generate_qa.py --video_id <id>` or `--all`
- Saves raw drafts to `data/qa_pairs/raw/{video_id}_qa_raw.json`

### 7.3 — LLM Review ⏳

**Status: First full run complete (2026-05-13). Pre-regeneration fixes applied (2026-05-14). Regeneration running.**

Full run results: 398/900 accepted (56% rejection rate). 53 lectures below floor (<10 accepted),
4 at floor (10–11). 77 knowledge-conflict discards (GPT-4o C1 disagreement).
No lectures are discarded — all 60 must appear in the benchmark (policy change 2026-05-14).
208 additional rejections (23.1%) were reviewer parse errors caused by `max_tokens=1024` truncating
the JSON response on complex multi-hop questions. All 6 root-cause fixes applied before regeneration.

**Fixes applied 2026-05-14 before regeneration:**

| # | Fix | File |
|---|-----|------|
| 1 | Span gap formula corrected: `\|span_A.start - span_B.start\| ≥ 70s` (was end-to-start 60s) | `src/qa_generator.py` |
| 2 | Frame caption marker pre-check: confirm `[frame caption:` present before assigning visual types | `src/qa_generator.py` |
| 3 | Answer atomicity rule added: every claim must trace to specific chunk text | `src/qa_generator.py` |
| 4 | qa_id offset: regenerated pairs use q016–q030 to avoid collision with first-run ids | `scripts/regenerate_qa.py` |
| 5 | Temperature 0.9 + diversity instruction for regeneration (was 0.0 → identical pairs) | `scripts/regenerate_qa.py` |
| 6 | Reviewer max_tokens 1024 → 4096 (root cause of 23.1% parse-error rejections) | `src/qa_reviewer.py` |

Regeneration script: `scripts/regenerate_qa.py --all` — targets all 53 below-floor lectures,
injects failure-aware constraints (C1/C2/C3 blocks) based on each lecture's per-criterion reject rate.
See `specs/2026-05-12-llm-review/` for full spec and locked decisions.

Review method: Claude Sonnet 4.6 (all 3 criteria) + GPT-4o C1 cross-check (knowledge-conflict
detection). Three-criterion binary rubric: answer correctness, span plausibility (≥70s gap),
question type accuracy. Pairs accepted only if all three PASS.

Target: 12 accepted QA pairs per lecture (~720 total) saved to `data/qa_pairs/reviewed/`.

**Known raw data quality issue (found during 6.3 spot-check):**
`stanford_cs229_lec03_q010` (multi-hop) has a span gap of -10s — two adjacent chunks,
not truly multi-hop. The LLM review pass must catch and reject these.

Ground-truth spans are LLM-estimated (~±15–30s precision) — disclosed as a limitation in
the paper. No human tightening of spans.

**Target question mix per lecture (locked):**

| `question_type` | Count | Role |
|---|---|---|
| `"multi-hop-visual"` | 7 | Primary — ≥2 spans, ≥1 visual hop; serves both contributions |
| `"visual"` | 2 | Primary — single-hop visual |
| `"multi-hop"` | 3 | Control — ≥2 spans, transcript-only |
| `"text"` | 2 | Control — single-hop transcript-only, lecture-specific |
| `"unanswerable"` | 1 | Required |
| **Total** | **15** | 10 multi-hop (67%) / 9 visual (60%) / 2 text / 1 unanswerable |

### 7.4 — Benchmark merge and validation
**Files:** `scripts/check_coverage.py`, `scripts/build_benchmark.py`, `scripts/validate_benchmark.py`

Run in this order:
1. `python scripts/check_coverage.py --fix` — zero-pair retry (Pass 1) + total/visual count check vs 500/300 minimums (Pass 2, user-confirmed). All 60 lectures must be present; no lecture is discarded.
2. `build_benchmark.py`: merges all reviewed JSON files → `data/benchmark/benchmark_v1.json`
3. `validate_benchmark.py`: checks schema completeness, span validity, `num_hops` consistency, unanswerable count per lecture

### 7.5 — Span precision audit (required before Phase 8)
**File:** `scripts/audit_span_precision.py`

Empirically measures how accurate the LLM-estimated ground-truth spans are, to
validate the tIoU@0.3 threshold before the evaluator is built.

**Method:** For a stratified sample of ~120 reviewed QA pairs (2 per lecture —
1 visual-type, 1 non-visual):
1. Load the cited chunk text from `data/chunks/`
2. Check whether the answer text (or its key claims) appears within the cited
   `[start_time, end_time]` window by searching the transcript segments
3. If the answer text is found, compute how much of the span is "wasted"
   (evidence occupies only part of the window) → estimate effective span error in seconds
4. Report: mean span error, worst-case span error, % of spans where evidence
   falls within the inner 50% of the window vs. near the edges

**Sample size justification:** 120 samples from a population of ~720 QA pairs.
For estimating a mean span error with σ ≈ 15s, n=120 gives a margin of error of
±σ/√120 ≈ ±1.4s — precise enough to distinguish the two decision-gate thresholds
(≤20s vs >30s), which have a 10s buffer between them. Stratifying by question type
(visual vs non-visual, 1 each per lecture) ensures span error is measured across both
types, since visual questions cite frame-caption chunks whose boundaries may differ
systematically from transcript-only chunks. Pure random sampling of 60 (1 per lecture)
would miss this and could underestimate tail error in one type.

**Decision gate:** If mean span error > 30s → reconsider tIoU@0.3 as primary threshold
(may need to drop to @0.2 or report only Hit Rate@k without IoU).
If mean span error ≤ 20s → tIoU@0.3 is well-justified; add the measured value to
the paper's limitation disclosure (replacing the current "±15–30s estimate").

**Git checkpoint:** `data: reviewed QA pairs, all lectures`

**Paper reminder — `sections/benchmark.tex`:** Draft the Benchmark Contribution section now (~1 page): lecture selection rationale, QA generation process, LLM review procedure, QA type breakdown table (multi-hop-visual / visual / multi-hop / text / unanswerable counts).

---

## Phase 8 — Evaluation ⏳

### 8.1 — Evaluator module
**File:** `src/evaluator.py`

Implements all required metrics:

```python
def temporal_iou(pred_start, pred_end, gt_start, gt_end) -> float:
    intersection = max(0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0 else 0.0
```

- **IoU@0.3, IoU@0.5** — fraction of questions where temporal IoU exceeds threshold
- **Hit Rate@k** (k=1,3,5) — ≥1 of top-k chunks has IoU > 0.3 with GT span
- **Hit Rate@k multi-hop (per-hop recall)** — fraction of GT hops covered by ≥1 top-k chunk (IoU > 0.3)
- **Hit Rate@k multi-hop (complete retrieval)** — fraction of questions where ALL hops covered by top-k
- **LLM-judge score (1–5)** — feed `question + generated_answer + reference_answer` to LLM.
  Candidate scoring criteria (to be confirmed via literature review before implementing):
  1. Factual correctness — does the answer match the reference answer's key claims?
  2. Completeness — for multi-hop questions, does it address all hops?
  3. Groundedness — are claims supported by cited chunks, not hallucinated from general knowledge?
  Use G-Eval form-filling paradigm (sub-score per criterion, then aggregate to 1–5).
  **⚠️ TODO before Phase 8: conduct a targeted literature review of how similar RAG
  benchmarks (RAGAS, EduVidQA, NA-VQA, ActivityNet-QA) define their LLM judge criteria.
  Confirm which of the three candidate criteria above are standard, and whether
  groundedness (chunk-only) vs. correctness (reference answer) should be the primary
  signal. This decision must be made before `src/evaluator.py` is written.**

  **Multi-judge protocol (decided via Phase 7.3 lit review, 2026-05-12):**
  Phase 8 LLM-judge scoring is subjective (1–5 scale) — the scenario where multi-judge
  literature shows the largest gains. Recommended protocol:
  - 2 judges: Claude Sonnet 4.6 + GPT-4o-mini (cross-family, cost-effective)
  - Aggregation: averaged score across both judges
  - Reliability: report Krippendorff's alpha between the two judges; if α < 0.6, escalate
    to a third judge (GPT-4o) for tie-breaking on low-agreement pairs
  - Backing: PRD (Li et al., 2023), ChatEval (Chan et al., 2023), Chen et al. (2025)
  - See `literature-review/phase_7.3/literature_review_report.md` — Phase 8 section
- **Citation accuracy** — fraction of cited chunks that actually contained the answer; for multi-hop, check ≥1 citation per hop

**Multi-hop metric implementations:**

```python
def multihop_per_hop_iou(pred_spans: list[tuple], gt_spans: list[tuple]) -> float:
    """Mean IoU between each GT hop and its best-matching predicted span."""
    scores = []
    for gt_start, gt_end in gt_spans:
        best = max(temporal_iou(ps, pe, gt_start, gt_end) for ps, pe in pred_spans)
        scores.append(best)
    return sum(scores) / len(scores)

def multihop_union_iou(pred_spans: list[tuple], gt_spans: list[tuple]) -> float:
    """IoU between the union of all predicted spans and union of all GT spans."""
    def merge_spans(spans):
        merged = []
        for start, end in sorted(spans):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return merged

    pred_merged = merge_spans(pred_spans)
    gt_merged = merge_spans(gt_spans)

    def total_length(spans):
        return sum(e - s for s, e in spans)

    def intersection_length(a_spans, b_spans):
        total = 0.0
        for a_s, a_e in a_spans:
            for b_s, b_e in b_spans:
                total += max(0.0, min(a_e, b_e) - max(a_s, b_s))
        return total

    inter = intersection_length(pred_merged, gt_merged)
    union = total_length(pred_merged) + total_length(gt_merged) - inter
    return inter / union if union > 0 else 0.0
```

Runs both configs × all verified questions; saves per-question results to `data/benchmark/evaluation_results.json`.

---

## Report Results Tables

Fill these in after Phase 8. Both configs side by side, split by question type.

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
| Multi-hop Union IoU | | |
| Complete Retrieval Rate@5 | | |
| Per-Hop Recall@5 | | |
| Multi-hop IoU@0.3 (union) | | |
| LLM-Judge Score (1–5) | | |
| Citation Accuracy | | |

**Git checkpoint:** `feat: evaluation pipeline (Phase 8)`

**Paper reminder — `sections/results.tex`:** Fill the results tables (both configs side by side) from `data/benchmark/evaluation_results.json`. Include failure mode analysis — if transcript+frames ≤ transcript-only, explain likely cause (generic Qwen2-VL captions on slides).

**Paper reminder — `sections/introduction.tex`:** Draft Introduction now that results are known (~0.5 page): motivate long-video RAG benchmarks, state the gap, summarise contributions and key findings.

**Paper reminder — `sections/conclusion.tex`:** Draft Conclusion (~0.25 page): summarise findings, limitations (corpus size, single embedding model), future work (larger corpus, multimodal retrieval).

**Paper reminder — `sections/abstract.tex`:** Write Abstract last (~150 words): what was built, key metrics from results tables, one-sentence contribution claim.

---

## Phase 9 — Deliverable Scripts ⏳

### 9.1 — Demo script
**File:** `run_part1.py`

- Accepts a question via `argparse` (or uses 3 hardcoded examples if none provided)
- Loads both retrieval configs; shows retrieved chunks and generated answer with citations
- Uses `print` for output (not `logging`) — this is the demo entrypoint
- Example citation output: `[mit_6046_lec10 @ 30:23 to 31:41](https://youtu.be/Tw1k46ywN6E?t=1823)`

### 9.2 — Full evaluation script
**File:** `run_part2.py`

- Runs full eval loop: both configs × all benchmark questions
- Prints results table side-by-side (transcript-only vs transcript+frames)
- Saves `data/benchmark/evaluation_results.json`
- Generates summary plots for the report

### 9.3 — Table reproduction script
**File:** `scripts/reproduce_tables.py`

One function per paper table, named `reproduce_table_1`, `reproduce_table_2`, etc.
Reads from `data/benchmark/evaluation_results.json` and prints/saves each table.
A single top-level call `python scripts/reproduce_tables.py` regenerates every table.

### 9.4 — Results tracking
**File:** `results.md` (repo root)

Side-by-side comparison of reproduced numbers vs. paper-reported numbers.
Must include a clear Config 1 vs Config 2 comparison showing the visual grounding
improvement on visual-dependent questions. Update whenever evaluation results change.

**Git checkpoint:** `feat: run_part1, run_part2, reproduce_tables (Phase 9)`

---

## Phase 10 — Report & README ⏳

### 10.1 — Report
**File:** `overleaf/assets/vqa_benchmark.tex` (git submodule → Overleaf; sections in `overleaf/assets/sections/`)

Overleaf submodule set up under `overleaf/` with sync scripts (`sync_overleaf.sh`, `push_to_overleaf.sh`, `check_status.sh`). Edit in Overleaf, pull via `sync_overleaf.sh`, push local changes via `push_to_overleaf.sh`.

> **Sync rule:** Any time `overleaf/assets/` is edited — locally or in Overleaf — follow the workflow in `overleaf/Overleaf sync instructions.md` before committing. Do not commit changes to the submodule without syncing first.

| Section | Target length | Content |
|---------|--------------|---------|
| Abstract | ~150 words | What was built, key metrics |
| Introduction | ~0.5 page | Motivation, gap in long-video QA |
| Related Work | ~0.75 page | Video QA benchmarks, temporal grounding, RAG, Whisper |
| Pipeline | ~1 page | Transcription, chunking, frame captions, retrieval, generation — every parameter justified |
| Benchmark Contribution | ~1 page | Lecture selection, QA generation, QA type breakdown |
| Results | ~1 page | Both configs side-by-side; failure mode analysis |
| Conclusion | ~0.25 page | Limitations, future work |

Every parameter choice (window size, overlap, k values, embedding model, frame interval, max_new_tokens) must be **explained and justified** — not just stated.

**Draft paper requirements (enforced from first draft):**
1. All sections written end-to-end, even if not final.
2. All results tables must have complete row/column structure. Unfinalized cells: `\textcolor{red}{TBD}` — never blank.
3. All figures must be present. Use `\fbox{\rule{0pt}{4cm}\rule{6cm}{0pt}}` as placeholder if final figure not ready. Never omit.

**Dataset release note:** License as CC BY-NC-SA 4.0 — required by the ShareAlike clause of the MIT OCW and Stanford SEE source material.

### 10.2 — README
**File:** `README.md`

- Setup instructions (Python env, system deps: ffmpeg, yt-dlp)
- Usage: `run_part1.py` and `run_part2.py`
- Dataset description and license
- How to reproduce all paper tables from a clean checkout: `python scripts/reproduce_tables.py`

**Git checkpoint:** `docs: final report and README (Phase 10)`

---

## Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Chunking | 45s window, 10s overlap (stride 35s) | Prescribed; 45s captures one concept; overlap prevents boundary misses |
| Embedding | all-MiniLM-L6-v2 | Prescribed; fast, 384-dim, strong retrieval |
| Vector DB | ChromaDB persistent | Prescribed; no server required |
| Frame captioner | Qwen2-VL-7B-Instruct, Approach A | Best OCR/math on lecture slides; Apache 2.0; fits on one A100; Approach A keeps both collections under same embedding model |
| Citation format | `[video_id @ mm:ss to mm:ss]` | Prescribed; YouTube deep-linkable |
| Generator output | Structured JSON | More reliable than regex-parsing `[1]` bracket citations |
| Span aggregation | Union of cited chunk spans | Standard for multi-chunk answers |
| Frame interval | 15s | All-in-window assignment gives ~3 captions/chunk; 30s nearest-midpoint missed slide transitions |
| Benchmark license | CC BY-NC-SA 4.0 | Required by ShareAlike clause from MIT/Stanford source material |

---

## QA Pair Standard Schema

```json
{
  "qa_id": "mit_6046_lec10_q007",
  "video_id": "mit_6046_lec10",
  "question": "...",
  "answer": "...",
  "num_hops": 2,
  "ground_truth_spans": [
    {"start": 320.0, "end": 398.0, "hop": 1, "description": "subproblem property introduced"},
    {"start": 2870.0, "end": 2940.0, "hop": 2, "description": "complexity claim relying on subproblem property"}
  ],
  "source_chunk_ids": ["mit_6046_lec10_chunk_009", "mit_6046_lec10_chunk_082"],
  "question_type": "multi-hop-visual|multi-hop|visual|text|unanswerable",
  "difficulty": "easy|medium|hard",
  "answerable": true,
  "key_concepts": ["memoization", "optimal substructure"],
  "reviewed_by": "llm_draft",
  "review_date": "2026-05-10"
}
```

- Single-hop: `num_hops: 1`, one entry in `ground_truth_spans`, one in `source_chunk_ids`
- Unanswerable: `answerable: false`, `ground_truth_spans: []`
- `description` per hop is required — records *why* that span is needed, essential for review

---

## Evaluation Results Schema

Results saved to `data/benchmark/evaluation_results.json` after Phase 9.

| Metric | Single-hop | Multi-hop |
|--------|-----------|-----------|
| Mean Temporal IoU | ✓ | Per-hop + union |
| IoU@0.3 | ✓ | ✓ (union) |
| IoU@0.5 | ✓ | ✓ (union) |
| Hit Rate@1 | ✓ | Complete retrieval rate |
| Hit Rate@3 | ✓ | Per-hop recall |
| Hit Rate@5 | ✓ | Per-hop recall |
| LLM-Judge (1–5) | ✓ | ✓ |
| Citation Accuracy | ✓ | Per-hop |

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| ChromaDB collection exists on rerun | Add `--rebuild` flag; default is skip |
| LLM citation output unreliable | Structured JSON output, not `[1]` regex parsing |
| Trivial QA pairs | Reject if answer < 10 words or verbatim in question |
| Predicted span too wide | Factual Qs: intersection; multi-chunk: union of cited spans |
| MKV/WEBM with AV1/VP9 codec | Use ffmpeg, not cv2, for frame extraction — affects NYU (MKV) and many MIT (WEBM) videos |
| nyu_dl_week7 duration mismatch | Metadata says 75 min; chunk count implies ~97 min — verify with `yt-dlp --get-duration` |
