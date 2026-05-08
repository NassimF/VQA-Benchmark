# Plan — Full Pipeline Run (Phases 2.2, 3.2, 4.2)

## Current Status (as of 2026-04-26)

| Task Group | Status | Notes |
|------------|--------|-------|
| 1 — VTT Parsing (2.2) | ✅ Done | 60/60 transcripts in `data/transcripts/` |
| 2 — Chunking (3.2) | ✅ Done | 60/60 chunk files in `data/chunks/` |
| 3 — Frame Captions (4.2) | ⏳ Blocked | System fork limit (~90K processes); see below |
| 4 — Validation & Merge | ⏳ Pending | Awaiting Task Group 3 |

### Resuming Phase 4.2 after system load drops

Before running, verify ffmpeg can fork with this quick test:
```bash
ffmpeg -threads 1 -ss 30 -i data/raw/videos/mit_6046_lec10.mp4 -frames:v 1 -threads 1 -q:v 2 /tmp/test_frame.jpg && echo "OK"
```

If the test passes, run:
```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/build_frame_captions.py --all --device cuda >> logs/phase4_2_frame_captions.log 2>&1
```

The script skips videos whose `data/frame_captions/{video_id}_frame_captions.json` already
exists — safe to re-run after a partial failure.

**Note on existing 4 frame caption files:** The 4 files already in `data/frame_captions/`
(mit_6046_lec10, mit_18065_lec06, nyu_dl_week6, nyu_dl_week7) were produced under the old
30s interval with the old nearest-midpoint schema (`frame_caption` scalar field). They must
be regenerated with the new 15s interval + all-in-window schema (`frame_captions` list).
Delete them before running so the skip logic re-processes them:
```bash
rm data/frame_captions/*.json data/chunks/*_chunks_augmented.json
```

**What was fixed in this session (already in current code):**
- `src/frame_extractor.py` — added `-threads 1` to ffmpeg input and output args
- `scripts/build_frame_captions.py` — fixed `ValueError: min() arg is an empty sequence`
  in fallback path; switched augmented chunks to `frame_captions` list schema
- `data/raw/metadata.json` — corrected 43 entries with wrong `.mp4` extension
  (actual files are `.webm`/`.mkv`)

---

## Task Group 1 — VTT Parsing (Phase 2.2)

1. Run `python scripts/parse_vtt.py --all`
   - Parses all 60 VTT files → `data/transcripts/{video_id}.json`
   - Skips videos whose transcript JSON already exists
2. Confirm 60 files present in `data/transcripts/`
3. Spot-check ≥2 technical terms per new lecture in the output JSON; log any quality issues

## Task Group 2 — Chunking (Phase 3.2)

4. Run `python scripts/build_chunks.py --all`
   - Slides a 45s window (stride 35s) over each transcript → `data/chunks/{video_id}_chunks.json`
   - Skips videos whose chunks JSON already exists
5. Confirm 60 files present in `data/chunks/`
6. Run `pytest tests/test_chunker.py` — all 8 tests must pass

## Task Group 3 — Frame Extraction + Captioning (Phase 4.2)

> **Design change from original spec:** interval changed 30s → 15s; assignment changed
> from nearest-midpoint to all-in-window. Reason: 30s + nearest-midpoint gave ~1 caption
> per chunk with the frame potentially 22.5s from a window edge, missing slide transitions
> and whiteboard build-up. 15s + all-in-window gives ~3 captions per chunk, covering the
> full 45s window. Frames in the 10s overlap are included in both neighboring chunks,
> matching the chunk overlap design. GPU cost: ~4–8 hrs on A100 (one overnight run).

7. Run `python scripts/build_frame_captions.py --all --device cuda`
   - Extracts 1 frame every 15s via ffmpeg (reads `cfg.frame_extraction.interval_seconds`)
   - Captions each frame with Qwen2-VL-7B-Instruct in bfloat16 on A100
   - Saves `data/frame_captions/{video_id}_frame_captions.json`
   - Builds augmented chunks: appends all in-window `[frame caption: ...]` entries;
     saves `data/chunks/{video_id}_chunks_augmented.json` with `frame_captions` list field
   - Skips videos whose frame caption JSON already exists
8. Confirm 60 frame caption files and 60 augmented chunk files present
9. Spot-check ≥1 frame caption per new lecture; verify slide text / equations are captured

## Task Group 4 — Validation & Merge

10. Run full validation checklist from `validation.md`
11. Update `specs/roadmap.md`: mark 2.2, 3.2, 4.2 ✅
12. Run `/changelog`
13. Commit: `feat: run full data pipeline (phases 2.2–4.2)` and push
