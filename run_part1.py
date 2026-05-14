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
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.retriever import Retriever
from src.generator import Generator


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


def run_demo(question: str, video_id: str | None, cfg) -> None:
    retriever = Retriever(cfg)
    generator = Generator(cfg)

    print("=" * 70)
    print(f"QUESTION: {question}")
    if video_id:
        print(f"FILTER:   video_id = {video_id}")
    print("=" * 70)

    for config_name, use_frames in [
        ("Config 1: Transcript-Only", False),
        ("Config 2: Transcript + Frames", True),
    ]:
        print(f"\n--- {config_name} ---")
        chunks = retriever.retrieve(
            query=question,
            video_id=video_id,
            use_frames=use_frames,
        )
        print(f"Retrieved {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] {chunk['chunk_id']}  "
                  f"({_fmt_time(chunk['start_time'])}–{_fmt_time(chunk['end_time'])})")

        answer = generator.generate(
            question=question,
            chunks=chunks,
            video_id=video_id,
        )
        print(f"\nAnswer:\n{answer}")

    print()


def _fmt_time(seconds: float) -> str:
    t = int(seconds)
    return f"{t // 60:02d}:{t % 60:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description="LectureBench RAG demo (Part 1)")
    parser.add_argument("--question", help="Question to answer")
    parser.add_argument("--video_id", help="Restrict retrieval to one lecture")
    args = parser.parse_args()

    cfg = load_config()

    if args.question:
        run_demo(args.question, args.video_id, cfg)
    else:
        print("No question provided — running 3 demo questions.\n")
        for demo in _DEMO_QUESTIONS:
            run_demo(demo["question"], demo["video_id"], cfg)


if __name__ == "__main__":
    main()
