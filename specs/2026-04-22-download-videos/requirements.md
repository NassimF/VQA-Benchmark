# Requirements: download_videos.py

## Scope
Write `scripts/download_videos.py` — a yt-dlp wrapper that downloads full video files and `.en.vtt` auto-caption files for all 60 lectures in the corpus. This script is **download-only**; it does not trigger VTT parsing or chunking.

## Inputs
- `data/raw/metadata.json` — 60 entries, each with `youtube_id`, `url`, and `video_file` path

## Outputs
- Video files in `data/raw/videos/` (`.mp4` for MIT/Stanford, `.mkv` for NYU)
- VTT files in `data/raw/videos/` as `{video_id}.en.vtt`
- Updated `data/raw/metadata.json` with `"downloaded": true/false` per entry

## CLI Interface
```
python scripts/download_videos.py --all
python scripts/download_videos.py --video_id mit_6046_lec10
```

## Skip Logic
A video is skipped if **both** of these exist on disk:
- `data/raw/videos/{video_id}.mp4` OR `data/raw/videos/{video_id}.mkv`
- `data/raw/videos/{video_id}.en.vtt`

Skip detection is based on file existence — not on any metadata field.

## Failure Handling
- On yt-dlp error: log the error, set `"downloaded": false` in metadata, continue to next video
- Do not abort the run on a single failure
- Failed video_ids are collected and printed at the end

## Metadata Schema Change
Each entry in `metadata.json` gains a `"downloaded"` boolean field:
- `true` — video and VTT confirmed on disk after this run (or were already there)
- `false` — yt-dlp failed for this entry

## Decisions
| Decision | Choice | Reason |
|----------|--------|--------|
| Full video vs audio-only | Full video | Frame extraction (Phase 4) requires video frames |
| MKV output for NYU | Allowed | ffmpeg handles AV1/MKV downstream |
| Parse/chunk after download | No | Keeps responsibilities separated; Phases 2/3 run independently |
| Metadata write timing | End of run | Atomic single write avoids partial corruption |
| Failure behavior | Skip + log | Allows partial runs; one bad URL shouldn't block 59 others |

## Constraints
- All paths via `pathlib.Path`
- Logging via `logging` module; `print` only for final summary
- Must work with Python 3.10+
- `yt-dlp` must be on PATH
