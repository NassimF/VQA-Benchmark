"""Slide a fixed-size window over transcript segments to produce overlapping chunks.

Window: 45s, overlap: 10s, stride: 35s (prescribed by assignment).
A segment is assigned to a chunk if its start time falls within [chunk_start, chunk_end).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from src.config import ChunkingConfig

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    chunk_id: str
    video_id: str
    start_time: float
    end_time: float
    text: str


def build_chunks(
    transcript: dict,
    chunking: ChunkingConfig,
) -> list[Chunk]:
    """Slide a window over transcript segments and return non-empty chunks."""
    video_id: str = transcript["video_id"]
    segments: list[dict] = transcript["segments"]

    if not segments:
        return []

    window = chunking.window_seconds
    stride = chunking.stride_seconds
    total_duration = segments[-1]["end"]

    chunks: list[Chunk] = []
    chunk_index = 0
    win_start = 0.0

    while win_start < total_duration:
        win_end = win_start + window
        in_window = [s for s in segments if win_start <= s["start"] < win_end]

        if in_window:
            text = " ".join(s["text"] for s in in_window)
            chunks.append(
                Chunk(
                    chunk_id=f"{video_id}_chunk_{chunk_index:03d}",
                    video_id=video_id,
                    start_time=win_start,
                    end_time=win_end,
                    text=text,
                )
            )
            chunk_index += 1

        win_start += stride

    logger.info(f"{video_id}: {len(chunks)} chunks (window={window}s, stride={stride}s)")
    return chunks


def chunks_to_json(chunks: list[Chunk], output_path: Path) -> list[dict]:
    """Serialise chunks and write to output_path."""
    records = [
        {
            "chunk_id": c.chunk_id,
            "video_id": c.video_id,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "text": c.text,
        }
        for c in chunks
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    return records


def chunk_transcript(transcript_path: Path, output_path: Path, chunking: ChunkingConfig) -> list[dict]:
    """Load a transcript JSON, chunk it, and write the result."""
    transcript = json.loads(transcript_path.read_text())
    chunks = build_chunks(transcript, chunking)
    records = chunks_to_json(chunks, output_path)
    logger.info(f"Wrote {len(records)} chunks to {output_path}")
    return records
