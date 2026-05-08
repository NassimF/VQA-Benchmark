# Validation — Full Pipeline Run (Phases 2.2, 3.2, 4.2)

All checks below must pass before merging this branch.

---

## 1. File Count Check

```bash
# Transcripts
python3 -c "
from pathlib import Path
t = list(Path('data/transcripts').glob('*_transcript.json')) + list(Path('data/transcripts').glob('*.json'))
print(f'Transcripts: {len(set(t))} (need 60)')
c = list(Path('data/chunks').glob('*_chunks.json'))
ca = list(Path('data/chunks').glob('*_chunks_augmented.json'))
fc = list(Path('data/frame_captions').glob('*_frame_captions.json'))
print(f'Chunks: {len(c)} (need 60)')
print(f'Augmented chunks: {len(ca)} (need 60)')
print(f'Frame captions: {len(fc)} (need 60)')
"
```

Expected: all four counts = 60.

---

## 2. Summary Stats — No Zero-Output Videos

Each script logs segment/chunk/frame counts per video. After each phase, confirm no video
logged 0 outputs. A video with 0 segments means the VTT was empty or malformed. A video
with 0 frames means ffmpeg failed (likely a codec issue on AV1/VP9 content).

Quick check after Phase 4.2:

```bash
python3 -c "
import json
from pathlib import Path
errors = []
for f in sorted(Path('data/frame_captions').glob('*_frame_captions.json')):
    caps = json.loads(f.read_text())
    if len(caps) == 0:
        errors.append(f.stem)
    else:
        print(f'{f.stem}: {len(caps)} captions')
if errors:
    print(f'ZERO-OUTPUT VIDEOS: {errors}')
else:
    print('All videos have frame captions.')
"
```

---

## 3. Spot-Check Content (≥2 technical terms per new lecture)

For at least 2 new lectures from different courses (e.g. one MIT, one Stanford), open the
transcript JSON and verify a technical term is correctly transcribed:

```bash
python3 -c "
import json
from pathlib import Path
data = json.loads(Path('data/transcripts/mit_6046_lec01.json').read_text())
# print a segment near the 20-minute mark
target = 20 * 60
seg = min(data, key=lambda s: abs(s['start_time'] - target))
print(seg)
"
```

Also verify at least 1 frame caption per new lecture captures slide text (not just "a blank
screen" or generic descriptions):

```bash
python3 -c "
import json
from pathlib import Path
caps = json.loads(Path('data/frame_captions/mit_6046_lec01_frame_captions.json').read_text())
for c in caps[:3]:
    print(f't={c[\"time\"]:.0f}s: {c[\"caption\"][:120]}')
"
```

---

## 4. Pytest — No Regressions

```bash
pytest tests/test_chunker.py -v
```

All 8 tests must pass. These cover overlap, boundary behavior, tail coverage, empty-window
skipping, and `chunk_id` format.

Also run a quick import smoke test to verify the augmented-chunk schema change didn't break
anything:

```bash
python3 -c "
import json
from pathlib import Path
# Check augmented chunks have new schema (list, not scalar)
f = next(Path('data/chunks').glob('*_chunks_augmented.json'))
chunks = json.loads(f.read_text())
assert 'frame_captions' in chunks[0], 'Missing frame_captions list'
assert isinstance(chunks[0]['frame_captions'], list), 'frame_captions should be a list'
print(f'Schema OK — {len(chunks[0][\"frame_captions\"])} captions on first chunk of {f.stem}')
"
```

---

## 5. Roadmap Update

After all checks pass:
- Mark Phase 2.2, 3.2, 4.2 as ✅ in `specs/roadmap.md`
- Update `specs/tech-stack.md` frame interval entry from 30s to 15s with justification
- Run `/changelog`
