"""Compute BLEU, ROUGE-L, METEOR, and Entailment for both RAG configs.

Reads generated answers from data/benchmark/evaluation_results.json and gold
answers from data/benchmark/benchmark_v1.json — no inference required.

Entailment uses cross-encoder/nli-deberta-v3-base (local, ~500 MB, no API key).
The score is the NLI entailment probability: reference = premise, generated = hypothesis.

Usage:
    python scripts/compute_text_metrics.py
    python scripts/compute_text_metrics.py --no-entailment   # skip NLI (faster)
    python scripts/compute_text_metrics.py --by-type         # breakdown per question type
    python scripts/compute_text_metrics.py --results path/to/evaluation_results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import nltk
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer as rouge_lib

nltk.download("punkt_tab", quiet=True)
nltk.download("wordnet", quiet=True)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

_VISUAL_TYPES = {"multi-hop-visual", "visual"}
_SMOOTHER = SmoothingFunction().method1
_ROUGE = rouge_lib.RougeScorer(["rougeL"], use_stemmer=True)


# ---------------------------------------------------------------------------
# Text metrics (no model required)
# ---------------------------------------------------------------------------

def _bleu(ref: str, hyp: str) -> float:
    ref_tok = word_tokenize(ref.lower())
    hyp_tok = word_tokenize(hyp.lower())
    if not hyp_tok:
        return 0.0
    return sentence_bleu([ref_tok], hyp_tok, smoothing_function=_SMOOTHER)


def _rougel(ref: str, hyp: str) -> float:
    return _ROUGE.score(ref, hyp)["rougeL"].fmeasure


def _meteor(ref: str, hyp: str) -> float:
    ref_tok = word_tokenize(ref.lower())
    hyp_tok = word_tokenize(hyp.lower())
    if not hyp_tok:
        return 0.0
    return meteor_score([ref_tok], hyp_tok)


# ---------------------------------------------------------------------------
# Entailment (NLI)
# ---------------------------------------------------------------------------

def _load_nli_pipeline():
    """Load NLI pipeline once; cached at module level after first call."""
    from transformers import pipeline as hf_pipeline
    print("Loading NLI model (cross-encoder/nli-deberta-v3-base) — first run downloads ~500 MB...")
    pipe = hf_pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-deberta-v3-base",
        device=0 if _cuda_available() else -1,
    )
    print("NLI model loaded.")
    return pipe


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _entailment_scores(pairs: list[tuple[str, str]], pipe) -> list[float]:
    """Return entailment probability for each (premise, hypothesis) pair."""
    # zero-shot-classification with entailment/contradiction/neutral labels
    premises = [p for p, _ in pairs]
    hypotheses = [h for _, h in pairs]
    scores = []
    batch_size = 32
    for i in range(0, len(pairs), batch_size):
        batch_p = premises[i:i + batch_size]
        batch_h = hypotheses[i:i + batch_size]
        for premise, hypothesis in zip(batch_p, batch_h):
            if not hypothesis.strip():
                scores.append(0.0)
                continue
            result = pipe(
                premise,
                candidate_labels=["entailment", "neutral", "contradiction"],
                hypothesis_template="{}",
                # pass hypothesis directly as the sequence to classify against
            )
            # result["labels"] order varies; find entailment explicitly
            label_scores = dict(zip(result["labels"], result["scores"]))
            scores.append(label_scores.get("entailment", 0.0))
    return scores


def _entailment_scores_direct(pairs: list[tuple[str, str]], pipe) -> list[float]:
    """Use the NLI model directly for premise/hypothesis entailment."""
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    tokenizer = pipe.tokenizer
    model = pipe.model
    device = next(model.parameters()).device

    scores = []
    batch_size = 16
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        premises = [p for p, _ in batch]
        hypotheses = [h for _, h in batch]
        enc = tokenizer(
            premises,
            hypotheses,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(device)
        with torch.no_grad():
            logits = model(**enc).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        # DeBERTa NLI label order: contradiction=0, neutral=1, entailment=2
        scores.extend(probs[:, 2].tolist())
    return scores


# ---------------------------------------------------------------------------
# Scoring and aggregation
# ---------------------------------------------------------------------------

def _score_pair(ref: str, hyp: str) -> dict[str, float]:
    return {
        "bleu":   _bleu(ref, hyp),
        "rougel": _rougel(ref, hyp),
        "meteor": _meteor(ref, hyp),
    }


def _agg(scores: list[dict], include_entailment: bool = False) -> dict[str, float]:
    if not scores:
        base = {"n": 0, "bleu": 0.0, "rougel": 0.0, "meteor": 0.0}
        if include_entailment:
            base["entailment_p"] = 0.0
            base["entailment_r"] = 0.0
        return base
    result = {
        "n":      len(scores),
        "bleu":   round(float(np.mean([s["bleu"]   for s in scores])), 4),
        "rougel": round(float(np.mean([s["rougel"] for s in scores])), 4),
        "meteor": round(float(np.mean([s["meteor"] for s in scores])), 4),
    }
    if include_entailment:
        result["entailment_p"] = round(float(np.mean([s["entailment_p"] for s in scores])), 4)
        result["entailment_r"] = round(float(np.mean([s["entailment_r"] for s in scores])), 4)
    return result


def _print_single_model_table(title: str, agg: dict, include_entailment: bool = False) -> None:
    w = 28
    sep = "=" * (w * 2 + 4)
    print(f"\n{title} (n={agg.get('n', 0)})")
    print(sep)
    print(f"{'Metric':<{w}}  {'Score':<{w}}")
    print("-" * (w * 2 + 4))
    rows = [
        ("BLEU",    f"{agg['bleu']:.4f}"),
        ("ROUGE-L", f"{agg['rougel']:.4f}"),
        ("METEOR",  f"{agg['meteor']:.4f}"),
    ]
    if include_entailment:
        rows.append(("Entailment-P (ref→gen)", f"{agg['entailment_p']:.4f}"))
        rows.append(("Entailment-R (gen→ref)", f"{agg['entailment_r']:.4f}"))
    for metric, val in rows:
        print(f"{metric:<{w}}  {val:<{w}}")
    print(sep)


def _print_table(title: str, c1: dict, c2: dict, include_entailment: bool = False) -> None:
    w = 28
    sep = "=" * (w * 3 + 6)
    n = c1.get("n", 0)
    print(f"\n{title} (n={n} per config)")
    print(sep)
    print(f"{'Metric':<{w}}  {'Config 1: Transcript-Only':<{w}}  {'Config 2: +Frames':<{w}}")
    print("-" * (w * 3 + 6))
    rows = [
        ("BLEU",    f"{c1['bleu']:.4f}",   f"{c2['bleu']:.4f}"),
        ("ROUGE-L", f"{c1['rougel']:.4f}", f"{c2['rougel']:.4f}"),
        ("METEOR",  f"{c1['meteor']:.4f}", f"{c2['meteor']:.4f}"),
    ]
    if include_entailment:
        rows.append(("Entailment-P (ref→gen)", f"{c1['entailment_p']:.4f}", f"{c2['entailment_p']:.4f}"))
        rows.append(("Entailment-R (gen→ref)", f"{c1['entailment_r']:.4f}", f"{c2['entailment_r']:.4f}"))
    for metric, v1, v2 in rows:
        print(f"{metric:<{w}}  {v1:<{w}}  {v2:<{w}}")
    print(sep)


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_text_metrics(
    results_path: Path,
    benchmark_path: Path,
    by_type: bool = False,
    include_entailment: bool = True,
) -> None:
    if not results_path.exists():
        print(f"ERROR: {results_path} not found. Run python run_part2.py first.")
        sys.exit(1)
    if not benchmark_path.exists():
        print(f"ERROR: {benchmark_path} not found.")
        sys.exit(1)

    results: list[dict] = json.loads(results_path.read_text())["results"]
    bm_items: list[dict] = json.loads(benchmark_path.read_text())["qa_pairs"]

    gold: dict[str, str] = {qa["qa_id"]: qa["answer"] for qa in bm_items}
    q_type: dict[str, str] = {qa["qa_id"]: qa["question_type"] for qa in bm_items}

    # Score text metrics for every result
    scored: list[dict] = []
    missing = 0
    pairs_for_nli: list[tuple[str, str]] = []  # (premise=ref, hypothesis=hyp)
    pair_indices: list[int] = []               # maps NLI batch index → scored index

    for r in results:
        ref = gold.get(r["qa_id"])
        hyp = r.get("generated_answer", "")
        if not ref:
            missing += 1
            continue
        entry = _score_pair(ref, hyp)
        entry["config"] = r["config"]
        entry["question_type"] = q_type.get(r["qa_id"], "unknown")
        entry["is_visual"] = entry["question_type"] in _VISUAL_TYPES
        if include_entailment:
            pair_indices.append(len(scored))
            pairs_for_nli.append((ref, hyp))
        scored.append(entry)

    if missing:
        print(f"Warning: {missing} results had no matching gold answer and were skipped.")

    # Batch NLI entailment — both directions
    if include_entailment and pairs_for_nli:
        nli_pipe = _load_nli_pipeline()
        print(f"Computing entailment for {len(pairs_for_nli)} pairs (both directions)...")
        # Forward: ref=premise, hyp=hypothesis  → precision (does reference support generated?)
        fwd_scores = _entailment_scores_direct(pairs_for_nli, nli_pipe)
        # Reverse: hyp=premise, ref=hypothesis  → recall (does generated support reference?)
        rev_pairs = [(h, r) for r, h in pairs_for_nli]
        rev_scores = _entailment_scores_direct(rev_pairs, nli_pipe)
        for idx, fwd, rev in zip(pair_indices, fwd_scores, rev_scores):
            scored[idx]["entailment_p"] = fwd
            scored[idx]["entailment_r"] = rev
        print("Done.")

    c1 = [s for s in scored if s["config"] == "transcript_only"]
    c2 = [s for s in scored if s["config"] == "transcript_plus_frames"]

    # LVLM single-model mode: when neither RAG config is present, print one-column results
    configs = {s["config"] for s in scored}
    rag_configs = {"transcript_only", "transcript_plus_frames"}
    if not configs.intersection(rag_configs):
        model_name = next(iter(configs), "model")
        model_scored = scored
        _print_single_model_table(
            f"Text Generation Metrics — {model_name} — All Questions",
            _agg(model_scored, include_entailment),
            include_entailment,
        )
        _print_single_model_table(
            f"Text Generation Metrics — {model_name} — Visual Questions",
            _agg([s for s in model_scored if s["is_visual"]], include_entailment),
            include_entailment,
        )
        _print_single_model_table(
            f"Text Generation Metrics — {model_name} — Non-Visual (Control)",
            _agg([s for s in model_scored if not s["is_visual"]], include_entailment),
            include_entailment,
        )
        if by_type:
            for qt in sorted({s["question_type"] for s in model_scored}):
                _print_single_model_table(
                    f"Text Generation Metrics — {model_name} — {qt}",
                    _agg([s for s in model_scored if s["question_type"] == qt], include_entailment),
                    include_entailment,
                )
        return

    _print_table(
        "Text Generation Metrics — All Questions",
        _agg(c1, include_entailment),
        _agg(c2, include_entailment),
        include_entailment,
    )
    _print_table(
        "Text Generation Metrics — Visual Questions",
        _agg([s for s in c1 if s["is_visual"]], include_entailment),
        _agg([s for s in c2 if s["is_visual"]], include_entailment),
        include_entailment,
    )
    _print_table(
        "Text Generation Metrics — Non-Visual (Control)",
        _agg([s for s in c1 if not s["is_visual"]], include_entailment),
        _agg([s for s in c2 if not s["is_visual"]], include_entailment),
        include_entailment,
    )

    if by_type:
        for qt in sorted({s["question_type"] for s in scored}):
            _print_table(
                f"Text Generation Metrics — {qt}",
                _agg([s for s in c1 if s["question_type"] == qt], include_entailment),
                _agg([s for s in c2 if s["question_type"] == qt], include_entailment),
                include_entailment,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=PROJECT_ROOT / "data" / "benchmark" / "evaluation_results.json",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=PROJECT_ROOT / "data" / "benchmark" / "benchmark_v1.json",
    )
    parser.add_argument(
        "--by-type",
        action="store_true",
        help="Also print a breakdown per question type.",
    )
    parser.add_argument(
        "--no-entailment",
        action="store_true",
        help="Skip NLI entailment scoring (faster, no model download).",
    )
    args = parser.parse_args()
    compute_text_metrics(
        args.results,
        args.benchmark,
        by_type=args.by_type,
        include_entailment=not args.no_entailment,
    )


if __name__ == "__main__":
    main()
