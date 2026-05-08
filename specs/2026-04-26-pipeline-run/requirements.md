# Requirements — Full Pipeline Run (Phases 2.2, 3.2, 4.2)

## Scope

Execute the three sequential data-preparation phases that convert raw videos and VTTs into
indexed, caption-augmented chunks ready for RAG ingestion (Phase 5). All three phases must
complete for all 60 lectures before Phase 5 can begin.

| Phase | Script | Input | Output |
|-------|--------|-------|--------|
| 2.2 | `scripts/parse_vtt.py --all` | `data/raw/videos/*.vtt` | `data/transcripts/{video_id}.json` |
| 3.2 | `scripts/build_chunks.py --all` | `data/transcripts/{video_id}.json` | `data/chunks/{video_id}_chunks.json` |
| 4.2 | `scripts/build_frame_captions.py --all --device cuda` | video files + chunks | `data/frame_captions/{video_id}_frame_captions.json`, `data/chunks/{video_id}_chunks_augmented.json` |

## Key Decisions

### Re-run behavior: skip silently
All three scripts skip a video if its output file already exists. This makes it safe to
re-run at any time after a partial failure without re-processing completed videos.

### Frame interval: 15 seconds (changed from 30s)
**Why changed:** The original 30s interval was chosen to balance coverage against GPU time,
but the assignment strategy was nearest-midpoint (one caption per chunk), which meant some
chunks received a caption from a frame up to 22.5s away from one edge — potentially missing
a full slide transition within that window.

**New design:** 15s interval + all-in-window assignment. Frames whose timestamp falls within
`[chunk.start_time, chunk.end_time)` are all appended to that chunk's text as concatenated
`[frame caption: ...]` entries. This gives ~3 captions per 45s chunk consistently, covering:
- Slide transitions that happen mid-chunk
- Whiteboard build-up (instructor writes progressively over 30–60s)
- The 10s overlap zone — frames there are included in both neighboring chunks, matching the
  chunk overlap design and improving retrieval recall at boundaries

Frames in the 10s overlap zone appearing in both neighbors is intentional and mirrors how
transcript segments in the overlap are duplicated across chunks.

**Why not 10s:** Marginal improvement over 15s for slide-based content; doubles GPU time
to ~6–13 hours with no meaningful gain for 45s chunks.

**GPU budget:** 15,020 frames × ~1–2s/frame on A100 80GB ≈ 4–8 hours. One overnight run.

### Caption assignment: all-in-window (changed from nearest-midpoint)
`assign_captions_to_chunks` in `scripts/build_frame_captions.py` now collects all frames
within the chunk window rather than the single nearest frame to the midpoint. Falls back to
nearest-midpoint only if no frame falls within the window (edge case: very short tail chunk).

The augmented chunk schema changes accordingly:
- Old: `"frame_caption": str, "frame_time": float`
- New: `"frame_captions": [{"time": float, "caption": str}, ...]`

### Prescribed parameters (unchanged)
- Chunk window: 45s, overlap 10s (stride 35s) — assignment spec, must not change
- Embedding model: all-MiniLM-L6-v2 — assignment spec
- max_new_tokens: 128 — sufficient for slide/whiteboard descriptions

## Context

- 4 lectures already processed (2.1/3.1 done for `mit_6046_lec10`, `mit_18065_lec06`,
  `nyu_dl_week6`, `nyu_dl_week7`); scripts skip these automatically
- NYU lectures use `.mkv` (AV1 codec) — ffmpeg used for frame extraction, not cv2
- `nyu_dl_week7` metadata duration mismatch (~75 min stated, ~97 min actual); chunks
  cover full actual length regardless
