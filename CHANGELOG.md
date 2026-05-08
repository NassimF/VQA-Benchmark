# Changelog

## 2026-05-08

- docs: mark pipeline run spec complete (phases 2.2–4.2) (8df7e4c)
- feat: run full data pipeline (phases 2.2–4.2) (8a811bb)

## 2026-04-26

- docs: add Overleaf sync rule to CLAUDE.md and roadmap (453903b)
- docs: reframe as conference paper; remove Phase 8 cross-validation (06fe49a)
- docs: add per-phase paper writing reminders to roadmap (c567527)
- docs: sync Overleaf fixes, update roadmap and changelog (206ce17)
- docs: update CHANGELOG.md for Overleaf submodule (a770067)

## 2026-04-26

- fix: BMVC compliance (ack, tables) + bib missing entries (a95ebc8)
- docs: sync Overleaf submodule — paper skeleton (83f724c)
- docs: add Specs & Roadmap section to CLAUDE.md (7b6d14c)

## 2026-04-26

- docs: reflect Overleaf submodule in specs (e469714)
- docs: update CHANGELOG.md (2b08e1a)
- Add Overleaf submodule under overleaf/ (e12f6e8)

## 2026-04-23

- docs: fix roadmap discrepancies in phases 1-4 (75ef8f4)
- docs: add frame interval and overlap rationale to Phase 4.2 (a2faf93)

## 2026-04-22

- docs: update CHANGELOG.md for Phase 1 completion (3f7ae76)
- docs: mark Phase 1 complete in roadmap (e0e3213)

## 2026-04-22

- data: all 60 VTTs + metadata downloaded (Phase 1.2 ✅) (6e7492b)
- fix: add webm support and initialize downloaded field for all entries (f021580)
- docs: mark Phase 1.1 complete in roadmap (d4fd51a)
- feat: download_videos.py + Phase 1.1 feature spec (Phase 1.1) (969d75d)
- docs: remove log.md (migrated to CHANGELOG.md), fix tech-stack header (aa1825c)

## 2026-04-21

- docs: add CHANGELOG.md with git history, decisions, and observations (8d2fdba)

## 2026-04-21

- docs: add deliverables, lit review, decisions log, and observations (cad5a5c)
- docs: add config.yaml reference and directory structure to tech-stack (979887c)
- docs: add multihop metric formulas and report tables to roadmap (571c065)
- docs: add specs/corpus.md with 60-video library and licensing (dc2a000)
- docs: add specs constitution (mission, tech-stack, roadmap) (3227be4)
- feat: expand to 60 lectures, replace BLIP with Qwen2-VL (52b1a4c)

## 2026-04-20

- docs: update plan for Phase 4 completion and NYU lectures (de77578)
- feat: frame caption pipeline complete (Phase 4) (1703106)
- feat: add NYU lectures + frame caption pipeline (Phase 4) (695e069)
- docs: add scale context note to PROJECT_PLAN.md (776d637)
- docs: sync PROJECT_PLAN.md with phases 2 and 3 (26806f4)
- feat: chunking pipeline (Phase 3) (6185799)
- feat: transcription pipeline (Phase 2) (7d805a2)
- docs: update literature review and project plan (9af7363)

## 2026-04-19

- feat: Phase 0+1 complete — literature review and video collection (eacb15d)

## 2026-04-18

- feat: project skeleton and documentation (31571fc)

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
- Results: `mit_6046_lec10`: 1,569 segments | `mit_18065_lec06`: 909 segments | `nyu_dl_week6`: 1,761 segments | `nyu_dl_week7`: 1,966 segments
- Quality check: MIT lectures spot-checked at 20-min mark; 0 errors on technical terms. NYU lectures: quality not yet verified (`caption_quality_check.decision: "pending"` in metadata).

### Chunking (Phase 3)

- Pure time-based windowing: segment belongs to chunk if `segment.start ∈ [win_start, win_start+45s)`. No silence-gap detection needed.
- Overlap confirmed by unit test: segment at 40s appears in both chunk [0–45s) and chunk [35–80s).
- Chunk counts: `mit_6046_lec10` 138 | `mit_18065_lec06` 92 | `nyu_dl_week6` 153 | `nyu_dl_week7` 167 (~97 min actual; metadata says 75 min — verify with `yt-dlp --get-duration`)
- 8/8 unit tests passing.

### NYU Lectures

- Downloaded as MKV (AV1 codec) — cv2 cannot decode AV1; frame extractor uses ffmpeg instead.
- `nyu_dl_week7` duration discrepancy: metadata lists 75 min, chunk count implies ~97 min actual. Verify before Phase 4.

### Frame Captioning (Phase 4)

- Qwen2-VL-7B-Instruct (Apache 2.0) replaces BLIP base — reads slide text, equations, whiteboard diagrams.
- Frame extraction via ffmpeg at 15s intervals (changed from 30s); all-in-window assignment gives ~3 captions per 45s chunk.
- 60/60 videos captioned; 17,180 total captions. Approach A: captions appended as `[frame caption: ...]` to chunk text, embedded with all-MiniLM-L6-v2 into Collection 2.
