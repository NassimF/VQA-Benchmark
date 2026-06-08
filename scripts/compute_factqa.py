"""Compute FactQA (FQA-P, FQA-R, FQA-F1) for both RAG configs using stored results.

Implements the FactQA metric from EduVidQA (Fernandez et al., ACL 2024 / SyllabusQA).
Each pair requires 2 LLM calls: one for precision (reference→generated) and one for
recall (generated→reference). Results are checkpointed after every pair so the run
can be interrupted and resumed.

Usage:
    python scripts/compute_factqa.py
    python scripts/compute_factqa.py --model gpt-4o          # use GPT-4o instead of mini
    python scripts/compute_factqa.py --no-resume             # restart from scratch
    python scripts/compute_factqa.py --by-type               # breakdown per question type
    python scripts/compute_factqa.py --results path/to/evaluation_results.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_MODEL = "gpt-4o-mini"
CHECKPOINT_PATH = PROJECT_ROOT / "data" / "benchmark" / "factqa_checkpoint.jsonl"
RESULTS_PATH = PROJECT_ROOT / "data" / "benchmark" / "factqa_results.json"

_VISUAL_TYPES = {"multi-hop-visual", "visual"}
_SCORE_RE = re.compile(r"Score:\s*(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)")


# ---------------------------------------------------------------------------
# Prompt (EduVidQA variant, domain-adjusted for lecture content)
# ---------------------------------------------------------------------------

def _factqa_prompt(question: str, answer_1: str, answer_2: str) -> str:
    question = question.replace("\n", " ").strip()
    answer_1 = answer_1.replace("\n", " ").strip()
    answer_2 = answer_2.replace("\n", " ").strip()
    return (
        "Your job is to evaluate the similarity of different answers to a single question. "
        "You will be given a question from an academic lecture on computer science or mathematics. "
        "You will also be given two possible answers to that question, "
        "and will have to evaluate the claims in one answer against the other.\n\n"
        "Steps:\n"
        "1. List all of the atomic claims made by Answer 1. "
        "Note that an answer saying that there is no information counts as a single claim.\n"
        "2. Tell me which of those claims are supported by Answer 2.\n"
        "3. Summarize the results using the template \"Score: <num supported claims>/<num total claims>\". "
        "Ensure that both numbers are integers.\n\n"
        f"Question: {question}\n"
        f"Answer 1: {answer_1}\n"
        f"Answer 2: {answer_2}"
    )


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def _call(client: OpenAI, prompt: str, model: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=500,
            )
            return resp.choices[0].message.content
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e
    return ""


def _extract_score(response: str) -> float | None:
    match = _SCORE_RE.search(response)
    if not match:
        return None
    num, denom = float(match.group(1)), float(match.group(2))
    if denom <= 0 or num < 0 or num > denom:
        return None
    return num / denom


def _score_pair(
    client: OpenAI,
    model: str,
    question: str,
    ref: str,
    hyp: str,
) -> dict[str, float]:
    # Precision: how many claims in ref are supported by hyp
    p_raw = _call(client, _factqa_prompt(question, ref, hyp), model)
    # Recall: how many claims in hyp are supported by ref
    r_raw = _call(client, _factqa_prompt(question, hyp, ref), model)

    p = _extract_score(p_raw)
    r = _extract_score(r_raw)

    if p is None or r is None:
        return {"fqa_p": 0.0, "fqa_r": 0.0, "fqa_f1": 0.0, "parse_error": True}

    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return {"fqa_p": p, "fqa_r": r, "fqa_f1": f1, "parse_error": False}


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint() -> dict[str, dict]:
    if not CHECKPOINT_PATH.exists():
        return {}
    done = {}
    for line in CHECKPOINT_PATH.read_text().splitlines():
        if line.strip():
            entry = json.loads(line)
            done[entry["key"]] = entry
    return done


def _append_checkpoint(entry: dict) -> None:
    with CHECKPOINT_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Aggregation and display
# ---------------------------------------------------------------------------

def _agg(scores: list[dict]) -> dict:
    if not scores:
        return {"n": 0, "fqa_p": 0.0, "fqa_r": 0.0, "fqa_f1": 0.0, "errors": 0}
    return {
        "n":      len(scores),
        "fqa_p":  round(float(np.mean([s["fqa_p"]  for s in scores])), 4),
        "fqa_r":  round(float(np.mean([s["fqa_r"]  for s in scores])), 4),
        "fqa_f1": round(float(np.mean([s["fqa_f1"] for s in scores])), 4),
        "errors": sum(1 for s in scores if s.get("parse_error")),
    }


def _print_table(title: str, c1: dict, c2: dict) -> None:
    w = 28
    sep = "=" * (w * 3 + 6)
    print(f"\n{title} (n={c1.get('n', 0)} per config)")
    print(sep)
    print(f"{'Metric':<{w}}  {'Config 1: Transcript-Only':<{w}}  {'Config 2: +Frames':<{w}}")
    print("-" * (w * 3 + 6))
    for label, key in [("FQA-P (precision)", "fqa_p"), ("FQA-R (recall)", "fqa_r"), ("FQA-F1", "fqa_f1")]:
        print(f"{label:<{w}}  {c1[key]:.4f}{'':<{w-6}}  {c2[key]:.4f}")
    if c1.get("errors", 0) or c2.get("errors", 0):
        print(f"{'Parse errors':<{w}}  {c1['errors']:<{w}}  {c2['errors']}")
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compute_factqa(
    results_path: Path,
    benchmark_path: Path,
    model: str,
    resume: bool,
    by_type: bool,
) -> None:
    if not results_path.exists():
        print(f"ERROR: {results_path} not found. Run python run_part2.py first.")
        sys.exit(1)

    import os
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    results: list[dict] = json.loads(results_path.read_text())["results"]
    bm_items: list[dict] = json.loads(benchmark_path.read_text())["qa_pairs"]

    gold_answers: dict[str, str] = {qa["qa_id"]: qa["answer"] for qa in bm_items}
    questions: dict[str, str]    = {qa["qa_id"]: qa["question"] for qa in bm_items}
    q_type: dict[str, str]       = {qa["qa_id"]: qa["question_type"] for qa in bm_items}

    checkpoint = _load_checkpoint() if resume else {}
    if not resume and CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()

    scored: list[dict] = []
    missing = skipped = 0
    total = len(results)

    for i, r in enumerate(results):
        ref = gold_answers.get(r["qa_id"])
        hyp = r.get("generated_answer", "")
        if not ref:
            missing += 1
            continue

        key = f"{r['qa_id']}|{r['config']}"
        if key in checkpoint:
            entry = checkpoint[key]
            skipped += 1
        else:
            print(f"[{i+1}/{total}] {key}", end=" ", flush=True)
            entry = _score_pair(client, model, questions[r["qa_id"]], ref, hyp)
            entry["key"] = key
            entry["qa_id"] = r["qa_id"]
            entry["config"] = r["config"]
            entry["question_type"] = q_type.get(r["qa_id"], "unknown")
            _append_checkpoint(entry)
            status = "ERR" if entry.get("parse_error") else f"P={entry['fqa_p']:.2f} R={entry['fqa_r']:.2f}"
            print(status)

        entry["is_visual"] = entry.get("question_type", "") in _VISUAL_TYPES
        scored.append(entry)

    if missing:
        print(f"\nWarning: {missing} results had no matching gold answer and were skipped.")
    if skipped:
        print(f"Resumed: {skipped} pairs loaded from checkpoint.")

    # Save full results
    RESULTS_PATH.write_text(json.dumps(scored, indent=2))
    print(f"\nResults saved to {RESULTS_PATH}")

    c1 = [s for s in scored if s["config"] == "transcript_only"]
    c2 = [s for s in scored if s["config"] == "transcript_plus_frames"]

    _print_table("FactQA Metrics — All Questions", _agg(c1), _agg(c2))
    _print_table(
        "FactQA Metrics — Visual Questions",
        _agg([s for s in c1 if s["is_visual"]]),
        _agg([s for s in c2 if s["is_visual"]]),
    )
    _print_table(
        "FactQA Metrics — Non-Visual (Control)",
        _agg([s for s in c1 if not s["is_visual"]]),
        _agg([s for s in c2 if not s["is_visual"]]),
    )

    if by_type:
        for qt in sorted({s["question_type"] for s in scored}):
            _print_table(
                f"FactQA Metrics — {qt}",
                _agg([s for s in c1 if s["question_type"] == qt]),
                _agg([s for s in c2 if s["question_type"] == qt]),
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=PROJECT_ROOT / "data" / "benchmark" / "evaluation_results.json")
    parser.add_argument("--benchmark", type=Path,
                        default=PROJECT_ROOT / "data" / "benchmark" / "benchmark_v1.json")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"OpenAI model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Restart from scratch, ignoring any existing checkpoint.")
    parser.add_argument("--by-type", action="store_true",
                        help="Also print breakdown per question type.")
    args = parser.parse_args()
    compute_factqa(args.results, args.benchmark, args.model, args.resume, args.by_type)


if __name__ == "__main__":
    main()
