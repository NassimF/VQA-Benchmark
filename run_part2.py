"""Part 2 deliverable — full benchmark evaluation across both retrieval configs.

Runs every QA pair in data/benchmark/benchmark_v1.json through both configs,
computes temporal IoU, hit rate@k, and LLM-judge scores, then prints a
side-by-side results table and saves data/benchmark/evaluation_results.json.

Usage:
    python run_part2.py
    python run_part2.py --limit 20      # quick smoke test on first 20 pairs
    python run_part2.py --video_id mit_18065_lec06   # single lecture
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.retriever import Retriever
from src.generator import Generator
from src.evaluator import Evaluator


def load_benchmark(cfg) -> list[dict]:
    path = cfg.data.benchmark_dir / "benchmark_v1.json"
    if not path.exists():
        print(f"ERROR: benchmark not found at {path}")
        print("Run scripts/build_benchmark.py first.")
        sys.exit(1)
    return json.loads(path.read_text())


def run_eval(pairs: list[dict], cfg) -> dict:
    retriever = Retriever(cfg)
    generator = Generator(cfg)
    evaluator = Evaluator(cfg)

    results: dict[str, list[dict]] = {"transcript_only": [], "transcript_plus_frames": []}

    for i, qa in enumerate(pairs):
        print(f"  [{i + 1}/{len(pairs)}] {qa['qa_id']}", end="\r", flush=True)
        for config_key, use_frames in [
            ("transcript_only", False),
            ("transcript_plus_frames", True),
        ]:
            chunks = retriever.retrieve(
                query=qa["question"],
                video_id=qa["video_id"],
                use_frames=use_frames,
            )
            answer = generator.generate(
                question=qa["question"],
                chunks=chunks,
                video_id=qa["video_id"],
            )
            metrics = evaluator.evaluate_pair(
                qa=qa,
                retrieved_chunks=chunks,
                generated_answer=answer,
            )
            results[config_key].append({
                "qa_id": qa["qa_id"],
                "question_type": qa["question_type"],
                **metrics,
            })

    print()
    return results


def aggregate(results: list[dict], k_values: list[int]) -> dict:
    import numpy as np

    iou_vals = [r["temporal_iou"] for r in results]
    judge_vals = [r["llm_judge_score"] for r in results if r.get("llm_judge_score") is not None]
    citation_vals = [r["citation_accuracy"] for r in results]

    agg: dict = {
        "mean_temporal_iou": float(np.mean(iou_vals)) if iou_vals else 0.0,
        "llm_judge_mean": float(np.mean(judge_vals)) if judge_vals else 0.0,
        "citation_accuracy": float(np.mean(citation_vals)) if citation_vals else 0.0,
    }
    for k in k_values:
        agg[f"hit_rate_at_{k}"] = float(np.mean([r.get(f"hit_rate_at_{k}", 0) for r in results]))
    for thresh in [0.3, 0.5]:
        key = f"iou_at_{str(thresh).replace('.', '')}"
        agg[key] = float(np.mean([1.0 if r["temporal_iou"] >= thresh else 0.0 for r in results]))
    return agg


def print_results_table(agg1: dict, agg2: dict, k_values: list[int]) -> None:
    rows = [
        ("Mean Temporal IoU",    f"{agg1['mean_temporal_iou']:.3f}",  f"{agg2['mean_temporal_iou']:.3f}"),
        ("IoU@0.3",              f"{agg1['iou_at_03']:.3f}",          f"{agg2['iou_at_03']:.3f}"),
        ("IoU@0.5",              f"{agg1['iou_at_05']:.3f}",          f"{agg2['iou_at_05']:.3f}"),
    ]
    for k in k_values:
        rows.append((
            f"Hit Rate@{k}",
            f"{agg1[f'hit_rate_at_{k}']:.3f}",
            f"{agg2[f'hit_rate_at_{k}']:.3f}",
        ))
    rows += [
        ("LLM-Judge Score",      f"{agg1['llm_judge_mean']:.2f}",     f"{agg2['llm_judge_mean']:.2f}"),
        ("Citation Accuracy",    f"{agg1['citation_accuracy']:.3f}",   f"{agg2['citation_accuracy']:.3f}"),
    ]

    col_w = 30
    print("\n" + "=" * (col_w * 3 + 4))
    print(f"{'Metric':<{col_w}}  {'Config 1: Transcript-Only':<{col_w}}  {'Config 2: +Frames':<{col_w}}")
    print("-" * (col_w * 3 + 4))
    for metric, v1, v2 in rows:
        print(f"{metric:<{col_w}}  {v1:<{col_w}}  {v2:<{col_w}}")
    print("=" * (col_w * 3 + 4))


def main() -> None:
    parser = argparse.ArgumentParser(description="LectureBench full evaluation (Part 2)")
    parser.add_argument("--limit", type=int, help="Evaluate only first N pairs (smoke test)")
    parser.add_argument("--video_id", help="Evaluate only one lecture")
    args = parser.parse_args()

    cfg = load_config()
    pairs = load_benchmark(cfg)

    if args.video_id:
        pairs = [p for p in pairs if p["video_id"] == args.video_id]
        print(f"Filtered to {len(pairs)} pairs for {args.video_id}")
    if args.limit:
        pairs = pairs[: args.limit]
        print(f"Limited to first {len(pairs)} pairs")

    print(f"Evaluating {len(pairs)} QA pairs across both configs...")
    results = run_eval(pairs, cfg)

    agg1 = aggregate(results["transcript_only"], cfg.retrieval.k_values)
    agg2 = aggregate(results["transcript_plus_frames"], cfg.retrieval.k_values)

    print_results_table(agg1, agg2, cfg.retrieval.k_values)

    out = {
        "total_pairs": len(pairs),
        "transcript_only": {"aggregate": agg1, "per_pair": results["transcript_only"]},
        "transcript_plus_frames": {"aggregate": agg2, "per_pair": results["transcript_plus_frames"]},
    }
    out_path = cfg.data.benchmark_dir / "evaluation_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nResults saved → {out_path}")


if __name__ == "__main__":
    main()
