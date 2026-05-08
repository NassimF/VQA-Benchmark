"""Retriever — embeds, ingests, and queries two ChromaDB collections.

Two modes driven by a single class:
  - "transcript_only"        → lecture_transcript_only collection
  - "transcript_plus_frames" → lecture_transcript_plus_frames collection
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI
from sentence_transformers import SentenceTransformer

from src.config import Config, load_config

logger = logging.getLogger(__name__)

Mode = Literal["transcript_only", "transcript_plus_frames"]


class Retriever:
    """Embed-and-retrieve over one of the two prescribed ChromaDB collections."""

    def __init__(
        self,
        mode: Mode,
        cfg: Config | None = None,
        *,
        chroma_client: ClientAPI | None = None,
        embedder: SentenceTransformer | None = None,
    ) -> None:
        """
        Args:
            mode: Which collection to target.
            cfg: Loaded Config; if None, loaded from default config.yaml.
            chroma_client: Override ChromaDB client (used in tests for ephemeral client).
            embedder: Override embedding model (used in tests for stubs).
        """
        self._cfg = cfg or load_config()
        self._mode = mode

        self._client: ClientAPI = chroma_client or chromadb.PersistentClient(
            path=str(self._cfg.vector_db.path)
        )

        collection_name = (
            self._cfg.vector_db.transcript_only_collection
            if mode == "transcript_only"
            else self._cfg.vector_db.transcript_frames_collection
        )
        self._collection: Collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self._embedder: SentenceTransformer = embedder or SentenceTransformer(
            self._cfg.embedding.model,
            device=self._cfg.embedding.device,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, video_ids: list[str], *, rebuild: bool = False) -> int:
        """Ingest chunks for the given video IDs into the active collection.

        Skips a video if its chunks are already present, unless rebuild=True.

        Returns:
            Number of chunks added (0 if all skipped).
        """
        added = 0
        for video_id in video_ids:
            chunk_file = self._chunk_path(video_id)
            if not chunk_file.exists():
                logger.warning(f"Chunk file not found, skipping: {chunk_file}")
                continue

            if not rebuild and self._video_already_ingested(video_id):
                logger.info(f"Skipping {video_id} — already in collection")
                continue

            if rebuild:
                self._delete_video(video_id)

            chunks = json.loads(chunk_file.read_text())
            ids = [c["chunk_id"] for c in chunks]
            documents = [c["text"] for c in chunks]
            metadatas = [
                {
                    "chunk_id": c["chunk_id"],
                    "video_id": c["video_id"],
                    "start_time": float(c["start_time"]),
                    "end_time": float(c["end_time"]),
                }
                for c in chunks
            ]
            embeddings = self._embedder.encode(documents, show_progress_bar=False).tolist()

            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            added += len(chunks)
            logger.info(f"Ingested {len(chunks)} chunks for {video_id}")

        return added

    def query(
        self,
        question: str,
        top_k: int | None = None,
        *,
        video_id: str | None = None,
    ) -> list[dict]:
        """Retrieve the top-k most relevant chunks for a question.

        Args:
            question: Natural-language query.
            top_k: Number of results; defaults to cfg.retrieval.top_k.
            video_id: If provided, restrict results to this video.

        Returns:
            List of dicts with keys: chunk_id, video_id, start_time, end_time, text, score.
        """
        k = top_k if top_k is not None else self._cfg.retrieval.top_k
        query_embedding = self._embedder.encode([question], show_progress_bar=False).tolist()

        where = {"video_id": video_id} if video_id else None
        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append(
                {
                    "chunk_id": meta["chunk_id"],
                    "video_id": meta["video_id"],
                    "start_time": float(meta["start_time"]),
                    "end_time": float(meta["end_time"]),
                    "text": doc,
                    "score": float(1.0 - dist),  # cosine distance → similarity
                }
            )
        return hits

    def count(self) -> int:
        """Return the number of documents in the active collection."""
        return self._collection.count()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _chunk_path(self, video_id: str) -> Path:
        chunks_dir = self._cfg.data.chunks_dir
        if self._mode == "transcript_only":
            return chunks_dir / f"{video_id}_chunks.json"
        return chunks_dir / f"{video_id}_chunks_augmented.json"

    def _video_already_ingested(self, video_id: str) -> bool:
        results = self._collection.get(where={"video_id": video_id}, limit=1)
        return len(results["ids"]) > 0

    def _delete_video(self, video_id: str) -> None:
        results = self._collection.get(where={"video_id": video_id})
        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} existing chunks for {video_id}")
