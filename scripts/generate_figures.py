"""Generate paper figures from benchmark and evaluation data.

Usage:
    python scripts/generate_figures.py
    python scripts/generate_figures.py --output-dir path/to/dir
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config

# Colorblind-safe pair (BMVC blue / orange)
C1_COLOR = "#4C72B0"
C2_COLOR = "#DD8452"

_STYLE = {
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 150,
}

_TYPE_LABELS = {
    "multi-hop-visual": "Multi-hop visual",
    "visual":           "Single-hop visual",
    "multi-hop":        "Multi-hop textual",
    "text":             "Single-hop textual",
    "unanswerable":     "Unanswerable",
}


def _save(fig: plt.Figure, stem: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        path = output_dir / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", dpi=300)
        print(f"  Saved → {path}")


def generate_figure_a(benchmark_path: Path, output_dir: Path) -> None:
    """Figure A — QA type distribution, two-level grouped by visual vs control."""
    benchmark = json.loads(benchmark_path.read_text())
    counts: dict[str, int] = {}
    for qa in benchmark["qa_pairs"]:
        qt = qa["question_type"]
        counts[qt] = counts.get(qt, 0) + 1

    total = sum(counts.values())

    # Two groups with their subtypes (visual-dependent first)
    groups = [
        ("Visual-dependent", C1_COLOR, ["multi-hop-visual", "visual"]),
        ("Control",          C2_COLOR, ["multi-hop", "text", "unanswerable"]),
    ]

    # Build rows top-to-bottom; None = blank spacer between groups
    rows: list[tuple[str, int, str, bool] | None] = []
    for idx, (group_label, color, types) in enumerate(groups):
        if idx > 0:
            rows.append(None)  # spacer
        group_total = sum(counts.get(t, 0) for t in types)
        rows.append((group_label, group_total, color, True))
        for t in types:
            rows.append((_TYPE_LABELS[t], counts.get(t, 0), color, False))

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(3.8, 3.0))

        tick_pos, tick_labels = [], []
        for i, row in enumerate(rows):
            if row is None:
                tick_pos.append(i)
                tick_labels.append("")
                continue
            label, val, color, grp = row
            alpha  = 1.0 if grp else 0.55
            height = 0.65 if grp else 0.45
            ax.barh(i, val, color=color, height=height, alpha=alpha)

            pct    = 100 * val / total
            fsize  = 7.5 if grp else 6.5
            weight = "bold" if grp else "normal"
            ax.text(val + 3, i, f"  {val} ({pct:.0f}%)", va="center",
                    ha="left", fontsize=fsize, fontweight=weight, color=color)

            tick_pos.append(i)
            tick_labels.append(("  " + label) if not grp else label)

        ax.set_yticks(tick_pos)
        ax.set_yticklabels(tick_labels, fontsize=8)
        ax.set_xlabel("Number of QA pairs")
        ax.set_xlim(0, max(r[1] for r in rows if r) * 1.32)
        ax.invert_yaxis()
        ax.xaxis.set_major_locator(mticker.MultipleLocator(100))
        ax.tick_params(axis="y", length=0)
        fig.tight_layout()

    _save(fig, "fig_qa_dist", output_dir)
    plt.close(fig)


def generate_figure_b(results_path: Path, benchmark_path: Path, output_dir: Path) -> None:
    """Figure B — Mean tIoU by question type, Config 1 vs Config 2."""
    results = json.loads(results_path.read_text())["results"]
    qa_type = {
        qa["qa_id"]: qa["question_type"]
        for qa in json.loads(benchmark_path.read_text())["qa_pairs"]
    }

    types = ["multi-hop-visual", "visual", "multi-hop", "text"]
    labels = [_TYPE_LABELS[t] for t in types]

    def mean_iou(config: str, qt: str) -> float:
        subset = [r["temporal_iou"] for r in results
                  if r["config"] == config and qa_type.get(r["qa_id"]) == qt]
        return float(np.mean(subset)) if subset else 0.0

    c1_vals = [mean_iou("transcript_only", t) for t in types]
    c2_vals = [mean_iou("transcript_plus_frames", t) for t in types]

    x = np.arange(len(types))
    width = 0.35

    with plt.rc_context(_STYLE):
        fig, ax = plt.subplots(figsize=(3.4, 2.6))

        bars1 = ax.bar(x - width / 2, c1_vals, width, label="Config 1: Transcript-Only",
                       color=C1_COLOR)
        bars2 = ax.bar(x + width / 2, c2_vals, width, label="Config 2: +Frames",
                       color=C2_COLOR)

        # Threshold line
        ax.axhline(0.3, color="gray", linestyle=":", linewidth=0.8, label="IoU@0.3 threshold")

        # Bar value annotations
        for bar in (*bars1, *bars2):
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2, h + 0.005,
                f"{h:.2f}", ha="center", va="bottom", fontsize=6,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.set_ylabel("Mean Temporal IoU")
        ax.set_ylim(0, max(max(c1_vals), max(c2_vals)) * 1.3)
        ax.legend(loc="upper right", frameon=False)
        fig.tight_layout()

    _save(fig, "fig_iou_by_type", output_dir)
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    default_out = PROJECT_ROOT / "overleaf" / "assets" / "images"

    parser = argparse.ArgumentParser(description="Generate paper figures")
    parser.add_argument("--results",   type=Path, default=cfg.evaluator.output_path)
    parser.add_argument("--benchmark", type=Path, default=cfg.data.benchmark_dir / "benchmark_v1.json")
    parser.add_argument("--output-dir", type=Path, default=default_out)
    args = parser.parse_args()

    print("Generating Figure A — QA type distribution...")
    generate_figure_a(args.benchmark, args.output_dir)

    print("Generating Figure B — tIoU by question type...")
    generate_figure_b(args.results, args.benchmark, args.output_dir)

    print("Done.")


if __name__ == "__main__":
    main()
