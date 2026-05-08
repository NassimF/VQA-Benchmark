# Plan — Full Pipeline Run (Phases 2.2, 3.2, 4.2)

## Current Status (as of 2026-05-08)

| Task Group | Status | Notes |
|------------|--------|-------|
| 1 — VTT Parsing (2.2) | ✅ Done | 60/60 transcripts in `data/transcripts/` |
| 2 — Chunking (3.2) | ✅ Done | 60/60 chunk files in `data/chunks/` |
| 3 — Frame Captions (4.2) | ✅ Done | 60/60 frame caption + augmented chunk files; 17,180 total captions |
| 4 — Validation & Merge | ✅ Done | All checks passed; committed 8a811bb; pushed to remote |

### Completion notes (2026-05-08)

**Issues encountered and fixed during run:**
- `spec-kit-mcp` runaway (~90K processes) blocked forking → removed from `/root/.claude.json`
- `qwen_vl_utils` not installed for system Python 3.10 → `python3 -m pip install qwen-vl-utils`
- `transformers` 5.x incompatible with torch 2.3 → pinned to `transformers>=4.45,<5.0`
- `UnicodeEncodeError` on JSON write (math symbols in captions) → added `encoding="utf-8"` to `write_text()`
- Skip logic missing from `main()` → added check before calling `process()`
- `mit_6046_lec10` had 0-byte output file (pre-fix run) → deleted and reprocessed
- conda env `vqa-benchmark` created for reproducible future runs; system Python used for actual run
  (conda torch 2.5.1+cu121 had cuDNN mismatch with this machine's CUDA 12.4)
- Required env vars: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`

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
