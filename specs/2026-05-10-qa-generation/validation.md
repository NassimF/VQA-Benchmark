# Phase 7.1–7.2 — QA Generation: Validation

Run all checks below before merging the branch. Record pass/fail for each.

---

## V1 — Unit Tests

```bash
conda activate vqa-benchmark
pytest tests/test_qa_generator.py -v
```

**Pass:** All tests green. No real API calls made. `reviewed_by == "llm_draft"` confirmed.

---

## V2 — Schema Validation (pilot lectures)

For each pilot lecture (`mit_6046_lec10`, `mit_18065_lec06`, `nyu_dl_week6`):

```bash
python -c "
import json, pathlib, sys
for vid in ['mit_6046_lec10', 'mit_18065_lec06', 'nyu_dl_week6']:
    path = pathlib.Path(f'data/qa_pairs/raw/{vid}_qa_raw.json')
    items = json.loads(path.read_text())
    required = {'qa_id','video_id','question','answer','num_hops',
                'ground_truth_spans','source_chunk_ids','question_type',
                'difficulty','answerable','key_concepts','reviewed_by','review_date'}
    for i, item in enumerate(items):
        missing = required - set(item)
        if missing:
            print(f'{vid}[{i}] MISSING: {missing}'); sys.exit(1)
    print(f'{vid}: {len(items)} items OK')
"
```

**Pass:** All 3 pilot files print `{video_id}: 15 items OK`.

---

## V3 — Question Count

```bash
python -c "
import json, pathlib
for vid in ['mit_6046_lec10', 'mit_18065_lec06', 'nyu_dl_week6']:
    items = json.loads(pathlib.Path(f'data/qa_pairs/raw/{vid}_qa_raw.json').read_text())
    print(f'{vid}: {len(items)} questions')
"
```

**Pass:** Each lecture has exactly 15 questions.

---

## V4 — Question Type Distribution (automated)

```bash
python -c "
import json, pathlib, collections
VISUAL_TYPES = {'visual', 'multi-hop-visual'}
VALID_TYPES = {'multi-hop-visual', 'multi-hop', 'visual', 'text', 'unanswerable'}
for vid in ['mit_6046_lec10', 'mit_18065_lec06', 'nyu_dl_week6']:
    items = json.loads(pathlib.Path(f'data/qa_pairs/raw/{vid}_qa_raw.json').read_text())
    counts = collections.Counter(i['question_type'] for i in items)
    invalid = set(counts) - VALID_TYPES
    if invalid:
        print(f'{vid} INVALID types: {invalid}'); continue
    visual = counts['multi-hop-visual'] + counts['visual']
    unanswerable = counts['unanswerable']
    multihop_visual = counts['multi-hop-visual']
    print(f'{vid}: {dict(counts)} | visual={visual}/15 unanswerable={unanswerable}')
    assert multihop_visual == 7, f'multi-hop-visual should be 7, got {multihop_visual}'
    assert counts['visual'] == 2, f'visual should be 2, got {counts[\"visual\"]}'
    assert counts['multi-hop'] == 3, f'multi-hop should be 3, got {counts[\"multi-hop\"]}'
    assert counts['text'] == 2, f'text should be 2, got {counts[\"text\"]}'
    assert unanswerable == 1, f'unanswerable should be 1, got {unanswerable}'
print('All distribution checks passed')
"
```

**Pass:** All 3 pilot files print counts matching `{multi-hop-visual: 7, visual: 2, multi-hop: 3, text: 2, unanswerable: 1}` and `All distribution checks passed`.

Also verify `num_hops` consistency:

```bash
python -c "
import json, pathlib, sys
MULTIHOP_TYPES = {'multi-hop', 'multi-hop-visual'}
for vid in ['mit_6046_lec10', 'mit_18065_lec06', 'nyu_dl_week6']:
    for item in json.loads(pathlib.Path(f'data/qa_pairs/raw/{vid}_qa_raw.json').read_text()):
        qt = item['question_type']
        hops = item['num_hops']
        if qt in MULTIHOP_TYPES and hops < 2:
            print(f'{item[\"qa_id\"]}: {qt} but num_hops={hops}'); sys.exit(1)
        if qt not in MULTIHOP_TYPES and hops != 1:
            print(f'{item[\"qa_id\"]}: {qt} but num_hops={hops}'); sys.exit(1)
print('num_hops consistent with question_type for all items')
"
```

**Pass:** Output is `num_hops consistent with question_type for all items`.

## V5 — Full-run File Count

After `python scripts/generate_qa.py --all`:

```bash
ls data/qa_pairs/raw/ | wc -l
```

**Pass:** Output is `60`.

---

## V6 — Skip Behaviour

```bash
python scripts/generate_qa.py --video_id mit_6046_lec10
```

Re-run without `--overwrite`. Check log output says `Skipping mit_6046_lec10 (already exists)`.

**Pass:** File is not overwritten; no API call is made on the second run.

---

## V7 — Rejection Criteria (automated)

```bash
python -c "
import json, pathlib
failures = []
for path in sorted(pathlib.Path('data/qa_pairs/raw').glob('*_qa_raw.json')):
    for item in json.loads(path.read_text()):
        if not item['answerable']:
            continue  # unanswerable questions have no reference answer
        q, a = item['question'].lower(), item['answer'].lower()
        if len(item['answer'].split()) < 10:
            failures.append(f'{item[\"qa_id\"]}: answer too short')
        if a.strip() in q:
            failures.append(f'{item[\"qa_id\"]}: answer verbatim in question')
if failures:
    print('\n'.join(failures))
else:
    print('All answers pass rejection criteria')
"
```

**Pass:** Output is `All answers pass rejection criteria`.

---

## Merge Checklist

- [x] V1 unit tests: all green
- [x] V2 schema: all 3 pilot files valid
- [x] V3 question count: 15 per pilot lecture
- [x] V4 type distribution: meets thresholds
- [x] V5 full-run count: 60 files
- [x] V6 skip behaviour: confirmed
- [x] V7 rejection criteria: no failures
- [ ] `git status` clean; no untracked files outside expected paths
- [ ] `/changelog` run before merge
