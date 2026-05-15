"""Reproduce all results tables from evaluation_results.json.

Each function regenerates one results table from data/benchmark/evaluation_results.json.
A single top-level call regenerates every table.

Usage:
    python scripts/reproduce_tables.py
    python scripts/reproduce_tables.py --results path/to/evaluation_results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config

_VISUAL_TYPES = {"multi-hop-visual", "visual"}


def _load(results_path: Path, benchmark_path: Path) -> tuple[list[dict], dict[str, str]]:
    if not results_path.exists():
        print(f"ERROR: {results_path} not found. Run python run_part2.py first.")
        sys.exit(1)
    results = json.loads(results_path.read_text())["results"]
    qa_type = {qa["qa_id"]: qa["question_type"]
               for qa in json.loads(benchmark_path.read_text())["qa_pairs"]}
    return results, qa_type


def _agg(subset: list[dict]) -> dict:
    if not subset:
        return {k: 0.0 for k in ("tIoU", "iou03", "iou05", "hr1", "hr3", "hr5", "llm", "cit")}
    return {
        "n":     len(subset),
        "tIoU":  round(float(np.mean([r["temporal_iou"]      for r in subset])), 3),
        "iou03": round(float(np.mean([r["iou_at_03"]         for r in subset])), 3),
        "iou05": round(float(np.mean([r["iou_at_05"]         for r in subset])), 3),
        "hr1":   round(float(np.mean([r["hit_rate_at_1"]     for r in subset])), 3),
        "hr3":   round(float(np.mean([r["hit_rate_at_3"]     for r in subset])), 3),
        "hr5":   round(float(np.mean([r["hit_rate_at_5"]     for r in subset])), 3),
        "llm":   round(float(np.mean([r["llm_judge_score"]   for r in subset])), 2),
        "cit":   round(float(np.mean([r["citation_accuracy"] for r in subset])), 3),
    }


def reproduce_table_1(results_path: Path, benchmark_path: Path) -> None:
    """Table 1 — Overall results across all 810 pairs, both configs."""
    results, _ = _load(results_path, benchmark_path)

    c1 = _agg([r for r in results if r["config"] == "transcript_only"])
    c2 = _agg([r for r in results if r["config"] == "transcript_plus_frames"])

    w = 28
    sep = "=" * (w * 3 + 6)
    print(f"\nTable 1 — Overall Results (n={c1['n']}, all question types)")
    print(sep)
    print(f"{'Metric':<{w}}  {'Config 1: Transcript-Only':<{w}}  {'Config 2: +Frames':<{w}}")
    print("-" * (w * 3 + 6))
    rows = [
        ("Mean Temporal IoU", f"{c1['tIoU']:.3f}",  f"{c2['tIoU']:.3f}"),
        ("IoU@0.3",           f"{c1['iou03']:.3f}", f"{c2['iou03']:.3f}"),
        ("IoU@0.5",           f"{c1['iou05']:.3f}", f"{c2['iou05']:.3f}"),
        ("Hit Rate@1",        f"{c1['hr1']:.3f}",   f"{c2['hr1']:.3f}"),
        ("Hit Rate@3",        f"{c1['hr3']:.3f}",   f"{c2['hr3']:.3f}"),
        ("Hit Rate@5",        f"{c1['hr5']:.3f}",   f"{c2['hr5']:.3f}"),
        ("LLM-Judge (1–5)",   f"{c1['llm']:.2f}",   f"{c2['llm']:.2f}"),
        ("Citation Accuracy", f"{c1['cit']:.3f}",   f"{c2['cit']:.3f}"),
    ]
    for metric, v1, v2 in rows:
        print(f"{metric:<{w}}  {v1:<{w}}  {v2:<{w}}")
    print(sep)


def reproduce_table_2(results_path: Path, benchmark_path: Path) -> None:
    """Table 2 — Mean temporal IoU broken down by question type."""
    results, qa_type = _load(results_path, benchmark_path)

    type_rows = [
        ("multi-hop-visual", {"multi-hop-visual"}),
        ("visual",           {"visual"}),
        ("all visual",       _VISUAL_TYPES),
        ("multi-hop",        {"multi-hop"}),
        ("text",             {"text"}),
    ]

    w = 20
    sep = "=" * (w * 3 + 20)
    print("\nTable 2 — Mean Temporal IoU by Question Type")
    print(sep)
    print(f"{'Question Type':<{w}}  {'N':>5}  {'Config 1':>{w}}  {'Config 2':>{w}}  {'Δ':>8}")
    print("-" * (w * 3 + 20))
    for label, types in type_rows:
        c1 = _agg([r for r in results if r["config"] == "transcript_only"
                   and qa_type.get(r["qa_id"]) in types])
        c2 = _agg([r for r in results if r["config"] == "transcript_plus_frames"
                   and qa_type.get(r["qa_id"]) in types])
        delta = round(c2["tIoU"] - c1["tIoU"], 3)
        sign = "+" if delta >= 0 else ""
        print(f"{label:<{w}}  {c1['n']:>5}  {c1['tIoU']:>{w}.3f}  {c2['tIoU']:>{w}.3f}  {sign}{delta:>7.3f}")
    print(sep)


def reproduce_table_3(results_path: Path, benchmark_path: Path) -> None:
    """Table 3 — Hit Rate@k broken down by question type."""
    results, qa_type = _load(results_path, benchmark_path)

    type_rows = [
        ("multi-hop-visual", {"multi-hop-visual"}),
        ("visual",           {"visual"}),
        ("multi-hop",        {"multi-hop"}),
        ("text",             {"text"}),
    ]

    w = 7
    sep = "=" * 80
    print("\nTable 3 — Hit Rate@k by Question Type")
    print(sep)
    print(f"{'Question Type':<22}  {'HR@1 C1':>{w}}  {'HR@1 C2':>{w}}  "
          f"{'HR@3 C1':>{w}}  {'HR@3 C2':>{w}}  {'HR@5 C1':>{w}}  {'HR@5 C2':>{w}}")
    print("-" * 80)
    for label, types in type_rows:
        c1 = _agg([r for r in results if r["config"] == "transcript_only"
                   and qa_type.get(r["qa_id"]) in types])
        c2 = _agg([r for r in results if r["config"] == "transcript_plus_frames"
                   and qa_type.get(r["qa_id"]) in types])
        print(f"{label:<22}  {c1['hr1']:>{w}.3f}  {c2['hr1']:>{w}.3f}  "
              f"{c1['hr3']:>{w}.3f}  {c2['hr3']:>{w}.3f}  "
              f"{c1['hr5']:>{w}.3f}  {c2['hr5']:>{w}.3f}")
    print(sep)


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
    cfg = load_config()
    parser = argparse.ArgumentParser(description="Reproduce results tables from evaluation artifacts")
    parser.add_argument("--results",   type=Path, default=cfg.evaluator.output_path)
    parser.add_argument("--benchmark", type=Path, default=cfg.data.benchmark_dir / "benchmark_v1.json")
    parser.add_argument("--table", type=int, choices=[1, 2, 3],
                        help="Reproduce only one table (default: all)")
    parser.add_argument("--output", type=Path, help="Also save output to this file")
    args = parser.parse_args()

    fns = {1: reproduce_table_1, 2: reproduce_table_2, 3: reproduce_table_3}
    targets = [fns[args.table]] if args.table else list(fns.values())

    with _tee(args.output):
        for fn in targets:
            fn(args.results, args.benchmark)


if __name__ == "__main__":
    main()
