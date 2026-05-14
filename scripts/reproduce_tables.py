"""Reproduce all paper tables from evaluation artifacts.

Each function regenerates one paper table from data/benchmark/evaluation_results.json.
A single top-level call regenerates every table.

Usage:
    python scripts/reproduce_tables.py
    python scripts/reproduce_tables.py --table 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

_RESULTS_PATH = PROJECT_ROOT / "data" / "benchmark" / "evaluation_results.json"


def _load_results() -> dict:
    if not _RESULTS_PATH.exists():
        print(f"ERROR: evaluation_results.json not found at {_RESULTS_PATH}")
        print("Run python run_part2.py first.")
        sys.exit(1)
    return json.loads(_RESULTS_PATH.read_text())


def _filter_by_type(per_pair: list[dict], question_types: list[str]) -> list[dict]:
    return [r for r in per_pair if r.get("question_type") in question_types]


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def reproduce_table_1() -> None:
    """Table 1 — Overall retrieval metrics, both configs side by side."""
    results = _load_results()
    c1 = results["transcript_only"]
    c2 = results["transcript_plus_frames"]

    rows = [
        ("Mean Temporal IoU",
            c1["aggregate"]["mean_temporal_iou"],
            c2["aggregate"]["mean_temporal_iou"]),
        ("IoU@0.3",
            c1["aggregate"]["iou_at_03"],
            c2["aggregate"]["iou_at_03"]),
        ("IoU@0.5",
            c1["aggregate"]["iou_at_05"],
            c2["aggregate"]["iou_at_05"]),
        ("Hit Rate@1",
            c1["aggregate"].get("hit_rate_at_1", 0),
            c2["aggregate"].get("hit_rate_at_1", 0)),
        ("Hit Rate@3",
            c1["aggregate"].get("hit_rate_at_3", 0),
            c2["aggregate"].get("hit_rate_at_3", 0)),
        ("Hit Rate@5",
            c1["aggregate"].get("hit_rate_at_5", 0),
            c2["aggregate"].get("hit_rate_at_5", 0)),
        ("LLM-Judge Score (1–5)",
            c1["aggregate"]["llm_judge_mean"],
            c2["aggregate"]["llm_judge_mean"]),
        ("Citation Accuracy",
            c1["aggregate"]["citation_accuracy"],
            c2["aggregate"]["citation_accuracy"]),
    ]

    print("\nTable 1 — Overall Results (all question types)")
    print(f"{'Metric':<30}  {'Config 1':<12}  {'Config 2':<12}  {'Δ (C2−C1)':<12}")
    print("-" * 70)
    for metric, v1, v2 in rows:
        delta = v2 - v1
        sign = "+" if delta >= 0 else ""
        print(f"{metric:<30}  {v1:<12.3f}  {v2:<12.3f}  {sign}{delta:.3f}")


def reproduce_table_2() -> None:
    """Table 2 — Retrieval metrics by question type."""
    results = _load_results()
    c1_pairs = results["transcript_only"]["per_pair"]
    c2_pairs = results["transcript_plus_frames"]["per_pair"]

    type_groups = {
        "multi-hop-visual": ["multi-hop-visual"],
        "visual": ["visual"],
        "multi-hop": ["multi-hop"],
        "text": ["text"],
        "all visual": ["multi-hop-visual", "visual"],
    }

    print("\nTable 2 — Mean Temporal IoU by Question Type")
    print(f"{'Type':<22}  {'N':<6}  {'Config 1':<12}  {'Config 2':<12}  {'Δ':<10}")
    print("-" * 65)
    for label, types in type_groups.items():
        p1 = _filter_by_type(c1_pairs, types)
        p2 = _filter_by_type(c2_pairs, types)
        v1 = _mean([r["temporal_iou"] for r in p1])
        v2 = _mean([r["temporal_iou"] for r in p2])
        delta = v2 - v1
        sign = "+" if delta >= 0 else ""
        print(f"{label:<22}  {len(p1):<6}  {v1:<12.3f}  {v2:<12.3f}  {sign}{delta:.3f}")


def reproduce_table_3() -> None:
    """Table 3 — Hit Rate@k by question type."""
    results = _load_results()
    c1_pairs = results["transcript_only"]["per_pair"]
    c2_pairs = results["transcript_plus_frames"]["per_pair"]

    qtypes = ["multi-hop-visual", "visual", "multi-hop", "text"]
    k_vals = [1, 3, 5]

    print("\nTable 3 — Hit Rate@k by Question Type (Config 2 / Config 1)")
    header = f"{'Type':<22}"
    for k in k_vals:
        header += f"  {'HR@' + str(k) + ' C1':<10}  {'HR@' + str(k) + ' C2':<10}"
    print(header)
    print("-" * (22 + len(k_vals) * 24))

    for qt in qtypes:
        p1 = _filter_by_type(c1_pairs, [qt])
        p2 = _filter_by_type(c2_pairs, [qt])
        row = f"{qt:<22}"
        for k in k_vals:
            v1 = _mean([r.get(f"hit_rate_at_{k}", 0) for r in p1])
            v2 = _mean([r.get(f"hit_rate_at_{k}", 0) for r in p2])
            row += f"  {v1:<10.3f}  {v2:<10.3f}"
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce paper tables from evaluation results")
    parser.add_argument("--table", type=int, choices=[1, 2, 3],
                        help="Reproduce only one table (default: all)")
    args = parser.parse_args()

    if args.table == 1:
        reproduce_table_1()
    elif args.table == 2:
        reproduce_table_2()
    elif args.table == 3:
        reproduce_table_3()
    else:
        reproduce_table_1()
        reproduce_table_2()
        reproduce_table_3()


if __name__ == "__main__":
    main()
