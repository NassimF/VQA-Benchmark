# Plan: download_videos.py

## Task Group 1 — Script scaffold
- `argparse` with `--all` (boolean flag) and `--video_id` (string)
- Load `data/raw/metadata.json` at startup
- Resolve `data/raw/videos/` directory path relative to project root via `Path(__file__).parent.parent`
- Set up `logging` with INFO level; logger name `download_videos`
- Validate: exactly one of `--all` or `--video_id` must be provided; error and exit if neither or both

## Task Group 2 — Skip detection
- For a given entry, check if video file exists:
  - `videos_dir / f"{video_id}.mp4"` OR `videos_dir / f"{video_id}.mkv"`
- AND VTT file exists: `videos_dir / f"{video_id}.en.vtt"`
- If both exist → mark as skipped, do not call yt-dlp

## Task Group 3 — yt-dlp download
- Build command:
  ```
  yt-dlp
    --write-auto-sub --sub-lang en --sub-format vtt --convert-subs vtt
    --no-playlist
    -o "{videos_dir}/{video_id}.%(ext)s"
    {url}
  ```
- Run via `subprocess.run(cmd, check=False, capture_output=True, text=True)`
- On non-zero return code: log `stderr`, record failure
- On success: verify expected files now exist on disk before marking `downloaded: true`

## Task Group 4 — Metadata status update
- After processing each entry, update the in-memory dict with `"downloaded": True/False`
- After all entries processed, write full metadata list back to `metadata.json` with 2-space indentation

## Task Group 5 — Summary output
```
print(f"Done. Downloaded: {n_downloaded}  Skipped: {n_skipped}  Failed: {n_failed}")
if failed_ids:
    print("Failed video_ids:")
    for vid in failed_ids:
        print(f"  {vid}")
```
