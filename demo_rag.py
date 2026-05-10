"""RAG quality demo — runs one QA pair through both retrieval configs and compares answers.

Usage:
  python demo_rag.py                              # random question from mit_6046_lec10
  python demo_rag.py --video_id nyu_dl_week6      # random question from that lecture
  python demo_rag.py --video_id mit_6046_lec10 --index 2   # specific question index
  python demo_rag.py --type multi-hop-visual      # pick by question type
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.generator import generate
from src.retriever import Retriever

# ── formatting helpers ────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
GREY   = "\033[90m"

def _w(text: str, width: int = 90, indent: str = "  ") -> str:
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=indent)

def _header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'─' * 90}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 90}{RESET}")

def _section(label: str) -> None:
    print(f"\n{BOLD}{YELLOW}  {label}{RESET}")

def _seconds_to_mmss(s: float) -> str:
    t = int(s)
    return f"{t // 60:02d}:{t % 60:02d}"

# ── load QA pair ──────────────────────────────────────────────────────────────

def load_qa_pair(video_id: str, index: int | None, qtype: str | None) -> dict:
    path = PROJECT_ROOT / "data" / "qa_pairs" / "raw" / f"{video_id}_qa_raw.json"
    if not path.exists():
        print(f"No QA file for {video_id}. Run scripts/generate_qa.py first.")
        sys.exit(1)
    items = json.loads(path.read_text())
    if qtype:
        items = [i for i in items if i["question_type"] == qtype]
        if not items:
            print(f"No questions of type '{qtype}' in {video_id}.")
            sys.exit(1)
    if index is not None:
        return items[index % len(items)]
    return random.choice(items)

# ── run one config ────────────────────────────────────────────────────────────

def run_config(question: str, video_id: str, mode: str, top_k: int) -> dict:
    retriever = Retriever(mode=mode)  # type: ignore[arg-type]
    chunks = retriever.query(question, top_k=top_k, video_id=video_id)
    result = generate(question, chunks, mode=mode)
    return {"chunks": chunks, "result": result}

# ── display ───────────────────────────────────────────────────────────────────

def show_qa(qa: dict) -> None:
    _header(f"QUESTION  [{qa['question_type']}  ·  difficulty: {qa['difficulty']}]")
    print(_w(qa["question"]))
    _section("Reference answer")
    print(_w(qa["answer"]))
    _section("Ground-truth spans")
    for span in qa.get("ground_truth_spans", []):
        start = _seconds_to_mmss(span["start"])
        end   = _seconds_to_mmss(span["end"])
        print(f"  Hop {span['hop']}  {start}–{end}  {GREY}{span['description']}{RESET}")


def show_config(label: str, data: dict) -> None:
    result = data["result"]
    chunks = data["chunks"]
    _section(f"{label}  →  retrieved {len(chunks)} chunks")

    for i, c in enumerate(chunks, 1):
        start = _seconds_to_mmss(c["start_time"])
        end   = _seconds_to_mmss(c["end_time"])
        preview = c["text"][:120].replace("\n", " ")
        print(f"  {GREY}[{i}] {c['chunk_id']}  {start}–{end}{RESET}")
        print(f"  {GREY}    {preview}…{RESET}")

    print(f"\n{GREEN}  Answer:{RESET}")
    print(_w(result.answer))

    if result.citations:
        print(f"\n{GREEN}  Citations:{RESET}")
        for cite in result.citations:
            print(f"  {cite}")
    else:
        print(f"\n{YELLOW}  (no citations returned){RESET}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_id", default="mit_6046_lec10")
    parser.add_argument("--index", type=int, default=None, help="QA item index (0-based)")
    parser.add_argument("--type", dest="qtype", default=None,
                        choices=["multi-hop-visual", "multi-hop", "visual", "text", "unanswerable"])
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    load_config()  # validate config on startup

    qa = load_qa_pair(args.video_id, args.index, args.qtype)
    show_qa(qa)

    question = qa["question"]

    print(f"\n{BOLD}Running Config 1 (transcript-only)…{RESET}")
    c1 = run_config(question, args.video_id, "transcript_only", args.top_k)

    print(f"{BOLD}Running Config 2 (transcript + frames)…{RESET}")
    c2 = run_config(question, args.video_id, "transcript_plus_frames", args.top_k)

    _header("CONFIG 1 — transcript only")
    show_config("transcript_only", c1)

    _header("CONFIG 2 — transcript + frame captions")
    show_config("transcript_plus_frames", c2)

    print(f"\n{BOLD}{CYAN}{'─' * 90}{RESET}\n")


if __name__ == "__main__":
    main()
