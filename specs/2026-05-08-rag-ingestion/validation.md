# Phase 5 — RAG Ingestion: Validation

All checks below must pass before merging into `main`.

---

## 1. Unit Tests

```bash
conda activate vqa-benchmark
pytest tests/test_retriever.py -v
```

Expected: **all tests pass**. Tests cover:
- `add()` + `query()` round-trip (top result is most relevant synthetic chunk)
- Metadata round-trip (`video_id`, `start_time`, `end_time`, `chunk_id` intact)
- No-duplicate guarantee on double `build()` without `--rebuild`
- `count()` returns correct document count

---

## 2. Full Ingestion Run

```bash
python scripts/build_index.py --all --mode both
```

Expected output includes:
- `60 videos ingested` (or skipped with `already exists` if re-run without `--rebuild`)
- No Python exceptions or ChromaDB errors
- Script exits with code 0

---

## 3. Collection Document Counts

After ingestion, verify both collections have the correct total chunk count.
The total across all 60 videos should match the sum of per-video chunk counts from Phase 3/4.

```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_db")

c1 = client.get_collection("lecture_transcript_only")
c2 = client.get_collection("lecture_transcript_plus_frames")

print(c1.count())   # expected: same total as sum of all _chunks.json lengths
print(c2.count())   # expected: same total as sum of all _chunks_augmented.json lengths
assert c1.count() == c2.count(), "Collections should have the same number of chunks"
```

---

## 4. Query Smoke Test

```python
from src.retriever import Retriever

r1 = Retriever(mode="transcript_only")
r2 = Retriever(mode="transcript_plus_frames")

results1 = r1.query("What is the master theorem?", top_k=4)
results2 = r2.query("What is the master theorem?", top_k=4)

assert len(results1) == 4
assert len(results2) == 4

for r in results1 + results2:
    assert {"chunk_id", "video_id", "start_time", "end_time", "text", "score"} <= r.keys()
    assert isinstance(r["start_time"], float)
    assert isinstance(r["end_time"], float)
    assert r["start_time"] < r["end_time"]
    assert 0.0 <= r["score"] <= 1.0
```

---

## 5. Single-Video Ingestion

```bash
python scripts/build_index.py --video_id mit_6046_lec10 --mode both --rebuild
```

Expected: only `mit_6046_lec10` chunks are re-ingested; other videos remain untouched.
Confirm with `c1.count()` — total should be unchanged (same number of documents after rebuild
of one video whose chunk count hasn't changed).

---

## 6. Config Purity Check

```bash
grep -r "all-MiniLM\|chroma_db\|lecture_transcript" src/retriever.py scripts/build_index.py
```

Expected: **zero matches** — all such strings must come from `src/config.py`, not hardcoded.

---

## Merge Criteria

- [ ] All pytest unit tests pass
- [ ] `build_index.py --all --mode both` completes without errors
- [ ] Both ChromaDB collections have matching, non-zero document counts
- [ ] Query smoke test returns 4 results with correct schema and float timestamps
- [ ] Single-video `--video_id` ingestion works
- [ ] No hardcoded model names, paths, or collection names in source files
