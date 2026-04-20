"""Unit tests for src/chunker.py using synthetic data."""

import pytest
from src.chunker import build_chunks, Chunk
from src.config import ChunkingConfig

CFG = ChunkingConfig(window_seconds=45.0, overlap_seconds=10.0)


def make_transcript(video_id: str, segments: list[tuple[float, float, str]]) -> dict:
    return {
        "video_id": video_id,
        "source": "test",
        "segments": [{"start": s, "end": e, "text": t} for s, e, t in segments],
    }


def test_chunk_id_format():
    transcript = make_transcript("test_vid", [(0.0, 3.0, "hello world")])
    chunks = build_chunks(transcript, CFG)
    assert chunks[0].chunk_id == "test_vid_chunk_000"


def test_window_and_stride():
    """137 windows for an 80-min (4800s) lecture with stride=35s."""
    segments = [(float(i * 3), float(i * 3 + 3), f"seg {i}") for i in range(1600)]
    transcript = make_transcript("long_vid", segments)
    chunks = build_chunks(transcript, CFG)
    # stride=35, total=4800 → ceil(4800/35) windows
    assert len(chunks) == pytest.approx(137, abs=2)


def test_overlap_means_segment_appears_in_two_chunks():
    """A segment starting at 40s falls in both chunk 0 [0–45) and chunk 1 [35–80)."""
    segments = [
        (0.0, 5.0, "early"),
        (40.0, 43.0, "overlap zone"),
        (50.0, 55.0, "later"),
    ]
    transcript = make_transcript("vid", segments)
    chunks = build_chunks(transcript, CFG)

    texts = [c.text for c in chunks]
    chunks_with_overlap = [t for t in texts if "overlap zone" in t]
    assert len(chunks_with_overlap) == 2


def test_empty_windows_skipped():
    """A gap in the lecture produces no empty chunks."""
    segments = [(0.0, 5.0, "start"), (300.0, 305.0, "after long silence")]
    transcript = make_transcript("vid", segments)
    chunks = build_chunks(transcript, CFG)
    for c in chunks:
        assert c.text.strip() != ""


def test_tail_coverage():
    """Last segment is included even if the final window is shorter than 45s."""
    segments = [(0.0, 3.0, "first"), (4790.0, 4795.0, "very last")]
    transcript = make_transcript("vid", segments)
    chunks = build_chunks(transcript, CFG)
    last_chunk_texts = " ".join(c.text for c in chunks)
    assert "very last" in last_chunk_texts


def test_empty_transcript():
    transcript = make_transcript("vid", [])
    assert build_chunks(transcript, CFG) == []


def test_chunk_video_id():
    transcript = make_transcript("mit_6046_lec10", [(0.0, 3.0, "hello")])
    chunks = build_chunks(transcript, CFG)
    assert all(c.video_id == "mit_6046_lec10" for c in chunks)


def test_window_boundaries():
    """Segment at exactly win_end is NOT in the chunk (half-open interval)."""
    segments = [(0.0, 3.0, "inside"), (45.0, 48.0, "at boundary")]
    transcript = make_transcript("vid", segments)
    chunks = build_chunks(transcript, CFG)
    assert "at boundary" not in chunks[0].text
