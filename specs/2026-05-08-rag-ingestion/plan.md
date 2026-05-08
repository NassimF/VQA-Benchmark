# Phase 5 — RAG Ingestion: Task Plan

## Task Group 1 — `src/retriever.py` ✅ 2026-05-08

1.1 ✅ Define `Retriever` class with `mode: Literal["transcript_only", "transcript_plus_frames"]` constructor argument.  
1.2 ✅ Implement `build(video_ids: list[str], *, rebuild: bool = False) -> int` — loads chunk JSON files and calls ChromaDB `add()` for each chunk; skips if collection already populated (unless `rebuild=True`). Returns chunk count added.  
1.3 ✅ Implement `query(question: str, top_k: int | None, *, video_id: str | None) -> list[dict]` — embeds query, calls ChromaDB `query()`, converts cosine distance → similarity score, returns ranked list of `{chunk_id, video_id, start_time, end_time, text, score}`.  
1.4 ✅ Wire embedding model and ChromaDB persistent client to config values from `src/config.py`; constructor accepts `chroma_client` and `embedder` overrides for test injection.  
1.5 ✅ Implement `count() -> int` — delegates to `collection.count()`.

**Implementation notes:**
- `conda run -n vqa-benchmark` resolves to `/bin/python` (system PATH shadow) — use `/root/miniconda3/envs/vqa-benchmark/bin/python` directly for all commands.
- chromadb 1.5.8, sentence-transformers 5.4.1 confirmed installed in `vqa-benchmark`.
- ChromaDB cosine distance is stored as distance (0=identical); `score = 1.0 - distance` converts to similarity.
- `_video_already_ingested()` uses `collection.get(where={"video_id": ...}, limit=1)` for cheap existence check.

---

## Task Group 2 — `scripts/build_index.py` ✅ 2026-05-08

2.1 ✅ Parse CLI: `--all` ingests all 60 lectures; `--video_id <id>` ingests one lecture; `--mode transcript_only|transcript_plus_frames|both` (default: `both`); `--rebuild` forces re-ingestion.  
2.2 ✅ Resolve chunk file paths from config via `Retriever._chunk_path()` — no path logic duplicated in the script.  
2.3 ✅ Loop: for each target video and mode, instantiate `Retriever(mode=...)` and call `build([video_id])`.  
2.4 ✅ Print progress per collection and final summary: videos ingested, chunks added.

**Implementation notes:**
- `--all` reads video IDs from `cfg.data.metadata_file` (metadata.json, 60 entries).
- Smoke-tested: single video `mit_6046_lec10` ingested 138 chunks; second run correctly skipped (0 added).

---

## Task Group 3 — `tests/test_retriever.py` ✅ 2026-05-08

3.1 ✅ Fixtures: 4 synthetic chunk dicts (3 for `test_vid`, 1 for `other_vid`); `StubEmbedder` returns deterministic unit-basis vectors (384-dim) keyed by chunk text — no model loaded.  
3.2 ✅ Query round-trip — top result is the chunk whose basis vector matches the query text exactly (score ≈ 1.0).  
3.3 ✅ Metadata round-trip — `video_id`, `start_time`, `end_time`, `chunk_id`, `text`, `score` all present and typed correctly.  
3.4 ✅ No-duplicate on double build — second `build()` without `rebuild=True` is a no-op; count unchanged.  
3.5 ✅ `rebuild=True` replaces existing docs — count stays the same (not doubled).  
3.6 ✅ `video_id` filter on `query()` — all results belong to the requested video.  
3.7 ✅ `count()` returns correct total after multi-video ingestion.

**Implementation notes:**
- `chromadb.EphemeralClient()` shares collection state within a process when collection names collide. Fixed by generating a `uuid4` suffix per fixture instance — unique collection names required for test isolation.
- 8/8 tests passing.

---

## Git Checkpoint

Commit message: `feat: RAG ingestion, both configs (Phase 5)`
