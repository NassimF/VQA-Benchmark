"""Part 2 deliverable — full benchmark evaluation across both retrieval configs.

Runs every QA pair in data/benchmark/benchmark_v1.json through both configs,
computes temporal IoU, hit rate@k, and LLM-judge scores, then prints a
side-by-side results table and saves data/benchmark/evaluation_results.json.

Usage:
    python run_part2.py                          # full run: 810 pairs × 2 configs
    python run_part2.py --limit 20               # smoke test: first 20 pairs only
    python run_part2.py --video_id mit_18065_lec06   # single lecture
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.evaluator import evaluate_all, evaluate_question
from src.retriever import Retriever


def _print_table(results: list[dict], cfg) -> None:
    """Print side-by-side results table for transcript_only vs transcript_plus_frames."""
    k_values = cfg.retrieval.k_values

    def _agg(config_name: str) -> dict:
        subset = [r for r in results if r["config"] == config_name]
        if not subset:
            return {}
        return {
            "mean_temporal_iou": float(np.mean([r["temporal_iou"] for r in subset])),
            "iou_at_03": float(np.mean([r["iou_at_03"] for r in subset])),
            "iou_at_05": float(np.mean([r["iou_at_05"] for r in subset])),
            **{f"hit_rate_at_{k}": float(np.mean([r[f"hit_rate_at_{k}"] for r in subset])) for k in k_values},
            "llm_judge_score": float(np.mean([r["llm_judge_score"] for r in subset])),
            "citation_accuracy": float(np.mean([r["citation_accuracy"] for r in subset])),
            "krippendorff_alpha": None,  # computed globally, not per-config
        }

    agg1 = _agg("transcript_only")
    agg2 = _agg("transcript_plus_frames")

    rows = [
        ("Mean Temporal IoU", f"{agg1['mean_temporal_iou']:.3f}", f"{agg2['mean_temporal_iou']:.3f}"),
        ("IoU@0.3",           f"{agg1['iou_at_03']:.3f}",         f"{agg2['iou_at_03']:.3f}"),
        ("IoU@0.5",           f"{agg1['iou_at_05']:.3f}",         f"{agg2['iou_at_05']:.3f}"),
    ]
    for k in k_values:
        rows.append((f"Hit Rate@{k}", f"{agg1[f'hit_rate_at_{k}']:.3f}", f"{agg2[f'hit_rate_at_{k}']:.3f}"))
    rows += [
        ("LLM-Judge Score (1–5)", f"{agg1['llm_judge_score']:.2f}", f"{agg2['llm_judge_score']:.2f}"),
        ("Citation Accuracy",     f"{agg1['citation_accuracy']:.3f}", f"{agg2['citation_accuracy']:.3f}"),
    ]

    w = 32
    print("\n" + "=" * (w * 3 + 4))
    print(f"{'Metric':<{w}}  {'Config 1: Transcript-Only':<{w}}  {'Config 2: +Frames':<{w}}")
    print("-" * (w * 3 + 4))
    for metric, v1, v2 in rows:
        print(f"{metric:<{w}}  {v1:<{w}}  {v2:<{w}}")
    print("=" * (w * 3 + 4))


def _run_filtered(pairs: list[dict], cfg) -> list[dict]:
    """Evaluate a filtered subset without the checkpoint system (for --limit/--video_id)."""
    retriever_t = Retriever("transcript_only", cfg=cfg)
    retriever_f = Retriever("transcript_plus_frames", cfg=cfg)
    retrievers = {"transcript_only": retriever_t, "transcript_plus_frames": retriever_f}

    results: list[dict] = []
    total = len(pairs) * 2
    done = 0
    for qa_pair in pairs:
        for config in ("transcript_only", "transcript_plus_frames"):
            done += 1
            print(f"  [{done}/{total}] {qa_pair['qa_id']} / {config}", end="\r", flush=True)
            result = evaluate_question(qa_pair, config, retrievers[config], cfg)
            results.append(result)
    print()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="LectureBench full evaluation (Part 2)")
    parser.add_argument("--limit", type=int, help="Evaluate only first N pairs (smoke test)")
    parser.add_argument("--video_id", help="Evaluate only one lecture")
    args = parser.parse_args()

    cfg = load_config()

    benchmark_path = cfg.data.benchmark_dir / "benchmark_v1.json"
    if not benchmark_path.exists():
        print(f"ERROR: benchmark not found at {benchmark_path}")
        print("Run scripts/build_benchmark.py first.")
        sys.exit(1)

    benchmark = json.loads(benchmark_path.read_text())
    all_pairs: list[dict] = benchmark["qa_pairs"]

    filtered = args.video_id or args.limit
    if filtered:
        pairs = all_pairs
        if args.video_id:
            pairs = [p for p in pairs if p["video_id"] == args.video_id]
            print(f"Filtered to {len(pairs)} pairs for {args.video_id}")
        if args.limit:
            pairs = pairs[: args.limit]
            print(f"Limited to first {len(pairs)} pairs")

        print(f"Evaluating {len(pairs)} QA pairs across both configs...")
        results = _run_filtered(pairs, cfg)
        _print_table(results, cfg)

        out_path = cfg.data.benchmark_dir / "evaluation_results_partial.json"
        out_path.write_text(json.dumps({"results": results}, indent=2))
        print(f"\nPartial results saved → {out_path}")
    else:
        print(f"Evaluating all {len(all_pairs)} QA pairs across both configs...")
        print("(Checkpointing enabled — safe to interrupt and resume)\n")
        evaluate_all(benchmark_path=benchmark_path, output_path=cfg.evaluator.output_path, cfg=cfg)

        results = json.loads(cfg.evaluator.output_path.read_text())["results"]
        _print_table(results, cfg)
        print(f"\nFull results saved → {cfg.evaluator.output_path}")


if __name__ == "__main__":
    main()
