"""Unit tests for src/retriever.py using synthetic in-memory fixtures.

ChromaDB runs as an EphemeralClient (no disk writes).
Embeddings use a deterministic stub — all-MiniLM-L6-v2 is never loaded.
"""

from __future__ import annotations

import numpy as np
import pytest
import chromadb

from src.retriever import Retriever
from src.config import load_config

DIM = 384  # matches all-MiniLM-L6-v2 output dimension

# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------

CHUNKS = [
    {
        "chunk_id": "test_vid_chunk_000",
        "video_id": "test_vid",
        "start_time": 0.0,
        "end_time": 45.0,
        "text": "dynamic programming and optimal substructure",
    },
    {
        "chunk_id": "test_vid_chunk_001",
        "video_id": "test_vid",
        "start_time": 35.0,
        "end_time": 80.0,
        "text": "merge sort divide and conquer algorithm",
    },
    {
        "chunk_id": "test_vid_chunk_002",
        "video_id": "test_vid",
        "start_time": 70.0,
        "end_time": 115.0,
        "text": "graph traversal breadth first search",
    },
    {
        "chunk_id": "other_vid_chunk_000",
        "video_id": "other_vid",
        "start_time": 0.0,
        "end_time": 45.0,
        "text": "convolutional neural network image classification",
    },
]

# Each chunk text maps to a unit basis vector; query text maps to the same
# vector as its target chunk, guaranteeing it is the nearest neighbour.
_BASIS: dict[str, np.ndarray] = {}
for _i, _chunk in enumerate(CHUNKS):
    _v = np.zeros(DIM, dtype=np.float32)
    _v[_i] = 1.0
    _BASIS[_chunk["text"]] = _v

# Query texts aligned with each chunk
QUERY_DP = "dynamic programming and optimal substructure"
QUERY_SORT = "merge sort divide and conquer algorithm"


class StubEmbedder:
    """Returns pre-assigned unit vectors; unknown texts get a zero vector."""

    def encode(self, sentences: list[str], **kwargs) -> np.ndarray:
        rows = []
        for s in sentences:
            rows.append(_BASIS.get(s, np.zeros(DIM, dtype=np.float32)))
        return np.array(rows, dtype=np.float32)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def retriever(tmp_path) -> Retriever:
    import uuid
    cfg = load_config()
    # Unique collection names per test to prevent EphemeralClient state bleed.
    suffix = uuid.uuid4().hex
    cfg.vector_db.transcript_only_collection = f"test_transcript_only_{suffix}"
    cfg.vector_db.transcript_frames_collection = f"test_transcript_frames_{suffix}"
    client = chromadb.EphemeralClient()
    return Retriever(
        mode="transcript_only",
        cfg=cfg,
        chroma_client=client,
        embedder=StubEmbedder(),
    )


@pytest.fixture()
def loaded_retriever(tmp_path, retriever: Retriever, monkeypatch) -> Retriever:
    """Retriever with CHUNKS already ingested via patched chunk files."""
    import json

    test_vid_chunks = [c for c in CHUNKS if c["video_id"] == "test_vid"]
    other_vid_chunks = [c for c in CHUNKS if c["video_id"] == "other_vid"]

    chunk_file = tmp_path / "test_vid_chunks.json"
    chunk_file.write_text(json.dumps(test_vid_chunks))

    other_file = tmp_path / "other_vid_chunks.json"
    other_file.write_text(json.dumps(other_vid_chunks))

    monkeypatch.setattr(retriever, "_chunk_path", lambda vid: (
        chunk_file if vid == "test_vid" else other_file
    ))

    retriever.build(["test_vid", "other_vid"])
    return retriever


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_count_after_build(loaded_retriever: Retriever) -> None:
    assert loaded_retriever.count() == len(CHUNKS)


def test_query_top_result_is_most_similar(loaded_retriever: Retriever) -> None:
    results = loaded_retriever.query(QUERY_DP, top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "test_vid_chunk_000"


def test_query_returns_requested_k(loaded_retriever: Retriever) -> None:
    results = loaded_retriever.query(QUERY_DP, top_k=3)
    assert len(results) == 3


def test_metadata_round_trip(loaded_retriever: Retriever) -> None:
    results = loaded_retriever.query(QUERY_DP, top_k=1)
    r = results[0]
    assert set(r.keys()) == {"chunk_id", "video_id", "start_time", "end_time", "text", "score"}
    assert r["video_id"] == "test_vid"
    assert isinstance(r["start_time"], float)
    assert isinstance(r["end_time"], float)
    assert r["start_time"] == pytest.approx(0.0)
    assert r["end_time"] == pytest.approx(45.0)


def test_score_is_similarity_not_distance(loaded_retriever: Retriever) -> None:
    results = loaded_retriever.query(QUERY_DP, top_k=1)
    assert 0.0 <= results[0]["score"] <= 1.0
    # Identical vector → score should be very close to 1.0
    assert results[0]["score"] == pytest.approx(1.0, abs=1e-4)


def test_no_duplicate_on_double_build(retriever: Retriever, tmp_path, monkeypatch) -> None:
    import json

    chunk_file = tmp_path / "test_vid_chunks.json"
    chunk_file.write_text(json.dumps([c for c in CHUNKS if c["video_id"] == "test_vid"]))
    monkeypatch.setattr(retriever, "_chunk_path", lambda _: chunk_file)

    retriever.build(["test_vid"])
    retriever.build(["test_vid"])  # second call without rebuild — should be a no-op
    assert retriever.count() == 3  # 3 chunks for test_vid, not 6


def test_rebuild_replaces_existing(retriever: Retriever, tmp_path, monkeypatch) -> None:
    import json

    chunk_file = tmp_path / "test_vid_chunks.json"
    chunk_file.write_text(json.dumps([c for c in CHUNKS if c["video_id"] == "test_vid"]))
    monkeypatch.setattr(retriever, "_chunk_path", lambda _: chunk_file)

    retriever.build(["test_vid"])
    retriever.build(["test_vid"], rebuild=True)
    assert retriever.count() == 3  # still 3, not 6


def test_video_id_filter(loaded_retriever: Retriever) -> None:
    results = loaded_retriever.query(QUERY_DP, top_k=4, video_id="other_vid")
    assert all(r["video_id"] == "other_vid" for r in results)
