# Phase 5 — RAG Ingestion: Requirements

## Scope

Implement the retrieval layer of the RAG pipeline. Two ChromaDB collections are built from
the chunk files produced in Phases 3 and 4, and a `Retriever` class exposes a unified query
interface used by `run_part1.py`, `run_part2.py`, and the evaluator.

---

## Files Produced

| File | Role |
|------|------|
| `src/retriever.py` | Retriever class — embed, ingest, query |
| `scripts/build_index.py` | CLI to ingest chunks into ChromaDB |
| `tests/test_retriever.py` | Unit tests with synthetic data |

---

## Interface Decisions

### Single class with mode flag
`Retriever(mode="transcript_only" | "transcript_plus_frames")`  
One class handles both collections. The mode determines which chunk files are read and which
ChromaDB collection is targeted. This keeps `run_part1.py` and `run_part2.py` concise — they
iterate over the two modes rather than importing two classes.

### build_index.py supports both `--all` and `--video_id`
Consistent with `parse_vtt.py` and `build_chunks.py`. Allows targeted re-ingestion of a
single video without a full rebuild, which is useful during development and if a lecture's
augmented chunks are updated.

---

## Key Constraints (prescribed — do not change without approval)

| Parameter | Value | Source |
|-----------|-------|--------|
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Assignment spec |
| Vector DB | ChromaDB persistent | Assignment spec |
| Distance metric | cosine | Assignment spec / tech-stack |
| Collection names | `lecture_transcript_only`, `lecture_transcript_plus_frames` | roadmap.md |
| Metadata per chunk | `video_id`, `start_time`, `end_time`, `chunk_id` | roadmap.md |
| Top-k default | 4 | config.yaml `retrieval.top_k` |

---

## Config Values Used

All read from `src/config.py` (backed by `config.yaml`). No hardcoded strings in source:

- `cfg.embedding.model` — embedding model name
- `cfg.embedding.device` — `"cuda"` or `"cpu"`
- `cfg.vector_db.path` — ChromaDB persist directory (`./chroma_db`)
- `cfg.vector_db.transcript_only_collection` — `"lecture_transcript_only"`
- `cfg.vector_db.transcript_frames_collection` — `"lecture_transcript_plus_frames"`
- `cfg.retrieval.top_k` — default query top-k

---

## Input Files

| Mode | Chunk file pattern |
|------|--------------------|
| `transcript_only` | `data/chunks/{video_id}_chunks.json` |
| `transcript_plus_frames` | `data/chunks/{video_id}_chunks_augmented.json` |

Both file types exist for all 60 videos (produced in Phases 3 and 4).

---

## Output Query Schema

Each item returned by `Retriever.query()`:

```python
{
    "chunk_id":   str,   # e.g. "mit_6046_lec10_chunk_009"
    "video_id":   str,
    "start_time": float, # seconds
    "end_time":   float, # seconds
    "text":       str,   # chunk text (+ frame captions if transcript_plus_frames)
    "score":      float  # cosine similarity (0–1, higher = more relevant)
}
```

---

## Test Strategy

`tests/test_retriever.py` uses **synthetic in-memory fixtures only** — no persistent ChromaDB
directory is created on disk and no real embedding model is loaded.

**Why:** The retriever wraps two external systems (sentence-transformers and ChromaDB). Loading
either in a unit test would require a GPU, network access, and gigabytes of model weights —
making tests slow, fragile, and environment-dependent. Keeping them synthetic lets CI run in
seconds on any machine.

**How:**
- ChromaDB is initialised with `chromadb.EphemeralClient()` (in-memory, no disk writes) and
  injected into the `Retriever` via a constructor parameter or monkeypatch.
- The embedding function is replaced with a deterministic stub (e.g. random fixed-seed vectors)
  so that `query()` can be called without loading `all-MiniLM-L6-v2`.
- Chunk dicts are hand-crafted (3–5 entries) with realistic field values but no dependency on
  real chunk files.

Integration smoke-testing (real ChromaDB on disk, real model) is handled by the validation
checklist in `validation.md`, run manually before merge — not in the automated test suite.

---

## Out of Scope for Phase 5

- `src/generator.py` (Phase 6)
- Metadata filtering by video_id within a query (may be added in Phase 6 if needed)
- Evaluation metrics (Phase 8)
