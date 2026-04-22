# Validation: download_videos.py

## 1. Skip detection works
```bash
python scripts/download_videos.py --video_id mit_6046_lec10
```
Expected output:
```
Done. Downloaded: 0  Skipped: 1  Failed: 0
```
`mit_6046_lec10.mp4` and `mit_6046_lec10.en.vtt` are already on disk — no yt-dlp call should be made.

## 2. All 4 existing videos skipped
```bash
python scripts/download_videos.py --all
```
With only 4 videos on disk, expected output starts with:
```
Done. Downloaded: 0  Skipped: 4  Failed: 56
```
(The 56 failures are expected here since we're not actually downloading in validation — or run with a real connection for a real download test.)

## 3. Single download (real network test)
```bash
python scripts/download_videos.py --video_id mit_6006f11_lec01
```
Expected:
- `data/raw/videos/mit_6006f11_lec01.mp4` appears on disk
- `data/raw/videos/mit_6006f11_lec01.en.vtt` appears on disk
- `metadata.json` entry for `mit_6006f11_lec01` has `"downloaded": true`
- Output: `Done. Downloaded: 1  Skipped: 0  Failed: 0`
- Re-running immediately: `Done. Downloaded: 0  Skipped: 1  Failed: 0`

## 4. Failure handling
Remove a VTT file to simulate partial state, then run again — should re-download that video.

To simulate a bad URL, temporarily edit metadata for a test entry. Expected:
- Script continues past the failure
- Failed `video_id` appears in the failed list
- `metadata.json` has `"downloaded": false` for that entry
- All other videos still processed

## 5. Metadata integrity
After any run, verify:
```bash
python -c "
import json
d = json.load(open('data/raw/metadata.json'))
assert len(d) == 60, 'Must still have 60 entries'
for v in d:
    assert 'downloaded' in v, f'Missing downloaded field: {v[\"video_id\"]}'
print('metadata.json OK')
"
```

## Merge criteria
- [ ] Skip detection passes test 1 and 2
- [ ] Single download passes test 3 (requires network)
- [ ] Metadata has 60 entries, all with `downloaded` field
- [ ] `specs/roadmap.md` Phase 1.1 updated to ✅
