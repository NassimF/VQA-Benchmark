"""Reproduce all results tables from evaluation artifacts.

Tables 1–3 regenerate from data/benchmark/evaluation_results.json (RAG configs).
Table 4 (LVLM comparison) regenerates from data/benchmark/lvlm_results_*.json files.

Usage:
    python scripts/reproduce_tables.py               # all tables (no entailment)
    python scripts/reproduce_tables.py --table 4     # LVLM table only
    python scripts/reproduce_tables.py --table 4 --entailment  # LVLM + Entailment-R
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


def reproduce_table_lvlm(
    lvlm_dir: Path,
    benchmark_path: Path,
    include_entailment: bool = False,
) -> None:
    """Table 4 — LVLM comparison: n-gram metrics + optional Entailment-R (6 systems, n≈696)."""
    from scripts.compute_text_metrics import (  # type: ignore[import]
        _bleu, _rougel, _meteor, _load_nli_pipeline, _entailment_scores_direct,
    )

    _VISUAL = {"multi-hop-visual", "visual"}

    bm = json.loads(benchmark_path.read_text())
    gold: dict[str, str] = {qa["qa_id"]: qa["answer"] for qa in bm["qa_pairs"]}
    q_type: dict[str, str] = {qa["qa_id"]: qa["question_type"] for qa in bm["qa_pairs"]}

    MODEL_FILES = [
        ("Config 1 (RAG, text only)", "lvlm_results_config1_rag.json"),
        ("Config 2 (RAG, +frames)",   "lvlm_results_config2_rag.json"),
        ("Qwen2-VL-7B",               "lvlm_results_qwen2_vl_7b.json"),
        ("mPLUG-Owl3-8B",             "lvlm_results_mplug_owl3_8b.json"),
        ("LLaVA-13B",                 "lvlm_results_llava_13b.json"),
        ("Video-LLaVA-7B",            "lvlm_results_video_llava_7b.json"),
    ]

    # Load all pairs per model
    all_model_data: list[tuple[str, list[dict]]] = []
    for display, fname in MODEL_FILES:
        fpath = lvlm_dir / fname
        if not fpath.exists():
            print(f"  WARNING: {fname} not found — skipping {display}.")
            all_model_data.append((display, []))
            continue
        records = json.loads(fpath.read_text())["results"]
        pairs = [
            {
                "ref": gold[r["qa_id"]],
                "hyp": r.get("generated_answer", ""),
                "is_visual": q_type.get(r["qa_id"]) in _VISUAL,
            }
            for r in records
            if r["qa_id"] in gold and r.get("generated_answer", "").strip()
        ]
        all_model_data.append((display, pairs))

    # Batch-compute Entailment-R across all models in one NLI pass
    ent_by_model: dict[str, dict[str, float]] = {}
    if include_entailment:
        flat_pairs: list[tuple[str, str]] = []
        flat_tags: list[tuple[int, bool]] = []
        for model_idx, (_, pairs) in enumerate(all_model_data):
            for p in pairs:
                flat_pairs.append((p["ref"], p["hyp"]))
                flat_tags.append((model_idx, p["is_visual"]))

        if flat_pairs:
            nli_pipe = _load_nli_pipeline()
            print(f"Computing Entailment-R for {len(flat_pairs)} pairs across {len(all_model_data)} models...")
            rev_pairs = [(h, r) for r, h in flat_pairs]  # gen→ref direction
            rev_scores = _entailment_scores_direct(rev_pairs, nli_pipe)

            from collections import defaultdict
            buckets: dict[int, dict[str, list[float]]] = defaultdict(
                lambda: {"all": [], "vis": [], "nonvis": []}
            )
            for score, (model_idx, is_visual) in zip(rev_scores, flat_tags):
                buckets[model_idx]["all"].append(score)
                (buckets[model_idx]["vis"] if is_visual else buckets[model_idx]["nonvis"]).append(score)

            for model_idx, (display, _) in enumerate(all_model_data):
                b = buckets[model_idx]
                ent_by_model[display] = {
                    k: round(float(np.mean(v)), 4) if v else 0.0
                    for k, v in b.items()
                }

    # Compute n-gram scores
    rows: list[dict] = []
    for display, pairs in all_model_data:
        if not pairs:
            rows.append({"model": display, "n": 0, "bleu": 0.0, "rougel": 0.0, "meteor": 0.0})
            continue
        rows.append({
            "model":  display,
            "n":      len(pairs),
            "bleu":   round(float(np.mean([_bleu(p["ref"],   p["hyp"]) for p in pairs])), 4),
            "rougel": round(float(np.mean([_rougel(p["ref"], p["hyp"]) for p in pairs])), 4),
            "meteor": round(float(np.mean([_meteor(p["ref"], p["hyp"]) for p in pairs])), 4),
        })

    # --- Print tables ---
    W = 26
    sep = "=" * (W + 42)
    print("\nTable 4 — LVLM Comparison (n=696 answerable pairs)")
    print(sep)

    # N-gram subtable
    print(f"\n  {'Model':<{W}}  {'n':>5}  {'BLEU':>8}  {'ROUGE-L':>8}  {'METEOR':>8}")
    print("  " + "-" * (W + 38))
    for row in rows:
        print(f"  {row['model']:<{W}}  {row['n']:>5}  "
              f"{row['bleu']:>8.4f}  {row['rougel']:>8.4f}  {row['meteor']:>8.4f}")

    # Entailment-R subtable
    if include_entailment and ent_by_model:
        print(f"\n  Entailment-R (gen→ref):")
        print(f"  {'Model':<{W}}  {'n':>5}  {'All':>8}  {'Visual':>8}  {'Non-vis':>8}")
        print("  " + "-" * (W + 38))
        for row in rows:
            e = ent_by_model.get(row["model"], {})
            print(f"  {row['model']:<{W}}  {row['n']:>5}  "
                  f"{e.get('all', 0.0):>8.4f}  {e.get('vis', 0.0):>8.4f}  "
                  f"{e.get('nonvis', 0.0):>8.4f}")

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
    parser.add_argument("--lvlm-dir",  type=Path, default=cfg.data.benchmark_dir,
                        help="Directory containing lvlm_results_*.json files (table 4)")
    parser.add_argument("--table", type=int, choices=[1, 2, 3, 4],
                        help="Reproduce only one table (default: all)")
    parser.add_argument("--entailment", action="store_true",
                        help="Include Entailment-R in table 4 (slow, requires NLI model)")
    parser.add_argument("--output", type=Path, help="Also save output to this file")
    args = parser.parse_args()

    rag_fns = [reproduce_table_1, reproduce_table_2, reproduce_table_3]

    with _tee(args.output):
        if args.table == 4:
            reproduce_table_lvlm(args.lvlm_dir, args.benchmark, args.entailment)
        elif args.table:
            rag_fns[args.table - 1](args.results, args.benchmark)
        else:
            for fn in rag_fns:
                fn(args.results, args.benchmark)
            reproduce_table_lvlm(args.lvlm_dir, args.benchmark, args.entailment)


if __name__ == "__main__":
    main()
