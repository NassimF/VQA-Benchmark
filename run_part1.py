"""Part 1 deliverable — end-to-end RAG demo.

Accepts a question and an optional video_id filter, retrieves relevant chunks from
both configs, and generates a grounded answer with timestamp citations.

Usage:
    python run_part1.py --question "What is the SVD geometric interpretation?"
    python run_part1.py --question "..." --video_id mit_18065_lec06
    python run_part1.py  # runs 3 hardcoded demo questions
"""

from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.generator import generate
from src.retriever import Retriever


_DEMO_QUESTIONS = [
    {
        "question": "What is the geometric interpretation of SVD and how does it relate to matrix multiplication?",
        "video_id": "mit_18065_lec06",
    },
    {
        "question": "How does backpropagation compute gradients through a neural network?",
        "video_id": None,
    },
    {
        "question": "What is the difference between L1 and L2 regularization in terms of sparsity?",
        "video_id": None,
    },
]

_CONFIGS = [
    ("transcript_only",        "Config 1: Transcript-Only"),
    ("transcript_plus_frames", "Config 2: Transcript + Frames"),
]


def _fmt_time(seconds: float) -> str:
    t = int(seconds)
    return f"{t // 60:02d}:{t % 60:02d}"


def run_demo(question: str, video_id: str | None, retrievers: dict, cfg) -> None:
    print("=" * 70)
    print(f"QUESTION: {question}")
    if video_id:
        print(f"FILTER:   video_id = {video_id}")
    print("=" * 70)

    for mode, label in _CONFIGS:
        print(f"\n--- {label} ---")
        chunks = retrievers[mode].query(question, video_id=video_id)

        print(f"Retrieved {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            preview = chunk["text"][:80].replace("\n", " ")
            start = _fmt_time(chunk["start_time"])
            end = _fmt_time(chunk["end_time"])
            print(f"  [{i}] {chunk['video_id']} @ {start}–{end}  {preview!r}")

        result = generate(question, chunks, mode=mode, cfg=cfg)
        print(f"\nAnswer:\n  {result.answer}")
        if result.citations:
            print("\nCitations:")
            for citation in result.citations:
                print(f"  {citation}")

    print()


@contextmanager
def _tee(output_path: Path | None):
    """Write stdout to a file in addition to the terminal when output_path is given."""
    if output_path is None:
        yield
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as fh:
        class _Tee:
            def write(self, msg):
                sys.__stdout__.write(msg)
                fh.write(msg)
            def flush(self):
                sys.__stdout__.flush()
                fh.flush()
        old = sys.stdout
        sys.stdout = _Tee()
        try:
            yield
        finally:
            sys.stdout = old
    print(f"\nOutput saved → {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="LectureBench RAG demo (Part 1)")
    parser.add_argument("--question", help="Question to answer")
    parser.add_argument("--video_id", help="Restrict retrieval to one lecture")
    parser.add_argument("--output", type=Path, help="Also save output to this file")
    args = parser.parse_args()

    cfg = load_config()
    retrievers = {mode: Retriever(mode, cfg=cfg) for mode, _ in _CONFIGS}

    with _tee(args.output):
        if args.question:
            run_demo(args.question, args.video_id, retrievers, cfg)
        else:
            print("No question provided — running 3 demo questions.\n")
            for demo in _DEMO_QUESTIONS:
                run_demo(demo["question"], demo["video_id"], retrievers, cfg)


if __name__ == "__main__":
    main()
