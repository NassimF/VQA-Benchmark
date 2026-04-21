# Log

Running record of decisions and observations. Update this file whenever a non-obvious design choice is made or a phase produces notable findings — these feed directly into the report's Pipeline and Results sections.

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Track C selected | Research exposure + co-authorship eligibility |
| 2026-04-18 | Chunking: 45s window, 10s overlap | Prescribed by assignment |
| 2026-04-18 | Embedding: all-MiniLM-L6-v2 | Prescribed by assignment |
| 2026-04-20 | Transcription: YouTube auto-captions (Option A) | Quality spot-checked at 20-min mark; 0 errors on technical terms (eigenvectors, memoization, hash table verified). Saves ~1–2 GPU-hours per lecture vs. Whisper |
| 2026-04-20 | Generator model: gpt-4o-mini | Cost-effective; reliable structured JSON output |
| 2026-04-21 | Frame captioner: Qwen2-VL-7B-Instruct, Approach A (text augmentation) | Strongest OCR/math on lecture slides; Apache 2.0; fits on one A100 (14 GB); Approach A keeps both ChromaDB collections under the same embedding model as prescribed |
| 2026-04-21 | Expanded to 60 lectures | Advisor requires 60+ videos for full venue publication |
| 2026-04-21 | Benchmark license: CC BY-NC-SA 4.0 | Required by ShareAlike clause — derived transcript/frame-caption content from MIT OCW and Stanford SEE videos must carry same license |

---

## Notes & Observations

### Transcription (Phase 2)

- YouTube auto-captions chosen over Whisper — pre-downloaded VTTs were clean on technical terms. Saves ~1–2 GPU-hours per lecture.
- VTT "rolling caption" format alternates word-timing cues (~2s) with display cues (~10ms). The display cues carry one clean subtitle phrase each — these are the source of transcript segments.
- Segment granularity: ~3s per phrase → 1,569 segments for an 80-min lecture.
- Results:
  - `mit_6046_lec10`: 1,569 segments
  - `mit_18065_lec06`: 909 segments
  - `nyu_dl_week6`: 1,761 segments
  - `nyu_dl_week7`: 1,966 segments
- Quality check: MIT lectures spot-checked at 20-min mark; 0 errors on technical terms. NYU lectures: VTTs downloaded, quality not yet verified (`caption_quality_check.decision: "pending"` in metadata).

### Chunking (Phase 3)

- Pure time-based windowing: segment belongs to chunk if `segment.start ∈ [win_start, win_start+45s)`. No silence-gap detection — not needed given dense lecture speech.
- Overlap confirmed by unit test: segment starting at 40s appears in both chunk [0–45s) and chunk [35–80s).
- Chunk counts match theoretical ⌈duration/stride⌉:
  - `mit_6046_lec10` (80 min): 138 chunks
  - `mit_18065_lec06` (54 min): 92 chunks
  - `nyu_dl_week6` (89 min): 153 chunks
  - `nyu_dl_week7` (~97 min actual): 167 chunks
- 8/8 unit tests passing (pytest) — verified overlap, half-open boundary, tail coverage, empty-window skipping, `chunk_id` format.

### NYU Lectures

- Downloaded as MKV (AV1 codec) — cv2 cannot decode AV1 on this platform; frame extractor updated to use ffmpeg instead.
- `nyu_dl_week7` duration discrepancy: metadata lists 75 min but chunk count (167 × 35s stride ≈ 97 min) implies the actual video is ~97 min. Verify with `yt-dlp --get-duration` and correct `metadata.json` before Phase 4.

### Frame Captioning (Phase 4)

- **Qwen2-VL-7B-Instruct** (Apache 2.0) on A100 GPU — reads slide text, equations, and whiteboard diagrams. Replaces BLIP base, which produced generic captions ("a man standing in front of a blackboard") unsuitable for academic retrieval.
- Frame extraction uses ffmpeg at 30s intervals (AV1/MKV-compatible); estimated ~642 frames across the first 4 lectures.
- Approach A: captions appended as `[frame caption: ...]` to chunk text → embedded with all-MiniLM-L6-v2 into Collection 2. No fusion layer needed; both collections use the same embedding model as prescribed.
- Phase 4 is pending — must complete before Phase 5 (Collection 2 ingests augmented chunks).
