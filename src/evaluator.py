"""Evaluator — temporal IoU, hit rate, LLM-judge scores, and Krippendorff's α.

Public API:
  evaluate_all(benchmark_path, output_path, cfg)  — main entry point
  evaluate_question(qa_pair, config, retriever, cfg)  — single question
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date
from pathlib import Path
from typing import Literal

import anthropic
import numpy as np
import openai

from src.config import Config, load_config
from src.generator import generate
from src.retriever import Retriever

logger = logging.getLogger(__name__)

EvalMode = Literal["transcript_only", "transcript_plus_frames"]

# ─── Task Group 1: Mathematical Metrics ───────────────────────────────────────


def temporal_iou(pred_start: float, pred_end: float, gt_start: float, gt_end: float) -> float:
    """Interval IoU between a predicted span and a ground-truth span."""
    intersection = max(0.0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0.0 else 0.0


def iou_at_threshold(iou: float, threshold: float) -> bool:
    return iou >= threshold


def merge_spans(spans: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Return a sorted, non-overlapping list of spans by merging overlapping ones."""
    if not spans:
        return []
    sorted_spans = sorted(spans, key=lambda s: s[0])
    merged: list[tuple[float, float]] = [sorted_spans[0]]
    for start, end in sorted_spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def predicted_span_from_chunks(chunks: list[dict]) -> tuple[float, float]:
    """Return (min_start, max_end) across all cited chunks. Returns (0.0, 0.0) if empty."""
    if not chunks:
        return (0.0, 0.0)
    return (
        min(c["start_time"] for c in chunks),
        max(c["end_time"] for c in chunks),
    )


def _interval_intersection_length(
    spans_a: list[tuple[float, float]],
    spans_b: list[tuple[float, float]],
) -> float:
    """Total length of intersection between two non-overlapping span lists."""
    total = 0.0
    for s_a, e_a in spans_a:
        for s_b, e_b in spans_b:
            total += max(0.0, min(e_a, e_b) - max(s_a, s_b))
    return total


def _interval_total_length(spans: list[tuple[float, float]]) -> float:
    return sum(e - s for s, e in spans)


def _gt_to_intervals(gt_spans: list[dict]) -> list[tuple[float, float]]:
    return [(s["start"], s["end"]) for s in gt_spans]


def _cited_to_intervals(cited_chunks: list[dict]) -> list[tuple[float, float]]:
    return [(c["start_time"], c["end_time"]) for c in cited_chunks]


def hit_rate_at_k(
    retrieved_chunks: list[dict],
    gt_spans: list[dict],
    k: int,
    iou_threshold: float = 0.3,
) -> bool:
    """True if ≥1 of the top-k retrieved chunks has IoU ≥ threshold with any GT span."""
    if not gt_spans:
        return False
    for chunk in retrieved_chunks[:k]:
        for span in gt_spans:
            if temporal_iou(chunk["start_time"], chunk["end_time"], span["start"], span["end"]) >= iou_threshold:
                return True
    return False


def multihop_per_hop_iou(
    pred_spans: list[tuple[float, float]],
    gt_spans: list[dict],
) -> float:
    """Mean IoU between each GT hop and its best-matching predicted span."""
    if not gt_spans or not pred_spans:
        return 0.0
    per_hop = []
    for span in gt_spans:
        best = max(
            temporal_iou(ps, pe, span["start"], span["end"])
            for ps, pe in pred_spans
        )
        per_hop.append(best)
    return float(np.mean(per_hop))


def multihop_union_iou(
    pred_spans: list[tuple[float, float]],
    gt_spans: list[dict],
) -> float:
    """IoU between the merged union of predicted spans and the merged union of GT spans."""
    if not gt_spans or not pred_spans:
        return 0.0
    merged_pred = merge_spans(pred_spans)
    merged_gt = merge_spans(_gt_to_intervals(gt_spans))
    intersection = _interval_intersection_length(merged_pred, merged_gt)
    pred_len = _interval_total_length(merged_pred)
    gt_len = _interval_total_length(merged_gt)
    union = pred_len + gt_len - intersection
    return intersection / union if union > 0.0 else 0.0


def multihop_per_hop_recall_at_k(
    retrieved_chunks: list[dict],
    gt_spans: list[dict],
    k: int,
    iou_threshold: float = 0.3,
) -> float:
    """Fraction of GT hops covered by ≥1 of the top-k retrieved chunks."""
    if not gt_spans:
        return 0.0
    top_k = retrieved_chunks[:k]
    covered = 0
    for span in gt_spans:
        for chunk in top_k:
            if temporal_iou(chunk["start_time"], chunk["end_time"], span["start"], span["end"]) >= iou_threshold:
                covered += 1
                break
    return covered / len(gt_spans)


def multihop_complete_retrieval_at_k(
    retrieved_chunks: list[dict],
    gt_spans: list[dict],
    k: int,
    iou_threshold: float = 0.3,
) -> bool:
    """True if ALL GT hops are covered by ≥1 of the top-k retrieved chunks."""
    if not gt_spans:
        return False
    return multihop_per_hop_recall_at_k(retrieved_chunks, gt_spans, k, iou_threshold) == 1.0


def citation_accuracy(
    cited_chunks: list[dict],
    gt_spans: list[dict],
    iou_threshold: float = 0.3,
) -> float:
    """Fraction of GT hops covered by ≥1 cited chunk (IoU ≥ threshold).

    For single-hop: 1.0 if any cited chunk covers the GT span, else 0.0.
    """
    if not gt_spans or not cited_chunks:
        return 0.0
    covered = 0
    for span in gt_spans:
        for chunk in cited_chunks:
            if temporal_iou(chunk["start_time"], chunk["end_time"], span["start"], span["end"]) >= iou_threshold:
                covered += 1
                break
    return covered / len(gt_spans)


# ─── Task Group 2: LLM Judge ──────────────────────────────────────────────────

_JUDGE_SYSTEM = (
    "You are an expert evaluator assessing the quality of answers generated by a "
    "video-lecture RAG system. Follow the rubric precisely. Output valid JSON only."
)

_JUDGE_TEMPLATE = """\
## Question
{question}

## Reference Answer (Gold)
{reference_answer}

## Retrieved Chunks (Context provided to the generator)
{chunks_text}

## Generated Answer
{generated_answer}

## Evaluation Rubric
Score each criterion from 1 (very poor) to 5 (excellent). Reason step by step before scoring.

**C1 — Correctness**: Does the generated answer match the reference answer in meaning and accuracy?
  1 = Completely wrong or contradicts the reference
  3 = Partially correct, key information missing
  5 = Fully accurate, matches the reference answer

{c2_rubric}

**C3 — Groundedness**: Are all claims in the generated answer supported by the retrieved chunks?
  1 = Claims not found in chunks, or chunks ignored entirely
  3 = Most claims supported but some unsupported
  5 = All claims clearly supported by the retrieved chunks

## Instructions
1. For each criterion, write 1–2 sentences of reasoning.
2. Then output exactly this JSON (no extra keys, no markdown):

{output_schema}
"""

_C2_MULTI = """\
**C2 — Completeness**: Does the generated answer address ALL {num_hops} aspects/hops of the question?
  1 = Only addresses one aspect; others completely ignored
  3 = Addresses some aspects but misses at least one
  5 = Covers all {num_hops} aspects thoroughly
"""

_C2_UNANSWERABLE = """\
**NOTE**: This question has no answer in the lecture material. \
A correct generator response is to state it cannot answer from the given context. \
Score C1 = 5 if the generator correctly declines, 1 if it fabricates a confident answer.
"""


def build_judge_prompt(
    question: str,
    reference_answer: str,
    retrieved_chunks: list[dict],
    generated_answer: str,
    num_hops: int,
    answerable: bool = True,
) -> str:
    """Build G-Eval form-filling prompt for one QA pair."""
    chunks_text_parts = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        start_s = int(chunk["start_time"])
        end_s = int(chunk["end_time"])
        chunks_text_parts.append(
            f"[{i}] {chunk['video_id']} @ {start_s//60:02d}:{start_s%60:02d} "
            f"to {end_s//60:02d}:{end_s%60:02d}\n{chunk['text']}"
        )
    chunks_text = "\n\n".join(chunks_text_parts) if chunks_text_parts else "(none)"

    ref = reference_answer if (answerable and reference_answer) else "(This question has no answer in the lecture.)"

    if not answerable:
        c2_rubric = _C2_UNANSWERABLE
        output_schema = '{"C1": <1-5>, "C2": <1-5>, "C3": <1-5>, "aggregate": <1-5>}'
    elif num_hops == 1:
        c2_rubric = (
            "**C2 — Completeness**: Not separately scored for single-hop questions. "
            "Set C2 = C1 in your output."
        )
        output_schema = '{"C1": <1-5>, "C2": <same as C1>, "C3": <1-5>, "aggregate": <round(mean(C1,C2,C3))>}'
    else:
        c2_rubric = _C2_MULTI.format(num_hops=num_hops)
        output_schema = '{"C1": <1-5>, "C2": <1-5>, "C3": <1-5>, "aggregate": <round(mean(C1,C2,C3))>}'

    return _JUDGE_TEMPLATE.format(
        question=question,
        reference_answer=ref,
        chunks_text=chunks_text,
        generated_answer=generated_answer,
        c2_rubric=c2_rubric,
        output_schema=output_schema,
    )


def _parse_judge_response(raw: str) -> dict:
    """Extract JSON dict from judge response, stripping markdown fences if present."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    # Find the JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in judge response: {raw!r}")
    parsed = json.loads(text[start:end])
    for key in ("C1", "C2", "C3", "aggregate"):
        if key not in parsed:
            raise ValueError(f"Missing key '{key}' in judge response: {raw!r}")
        if not isinstance(parsed[key], int) or not (1 <= parsed[key] <= 5):
            raise ValueError(f"Invalid value for '{key}' in judge response: {parsed[key]!r}")
    return parsed


def call_judge(prompt: str, model: str) -> dict:
    """Call LLM judge and parse JSON response. Retries up to 2 times on parse failure."""
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            if model.startswith("claude"):
                client = anthropic.Anthropic()
                msg = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    temperature=0.0,
                    system=_JUDGE_SYSTEM,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = msg.content[0].text
            else:
                client = openai.OpenAI()
                resp = client.chat.completions.create(
                    model=model,
                    temperature=0.0,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": _JUDGE_SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                )
                raw = resp.choices[0].message.content or ""
            return _parse_judge_response(raw)
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            logger.warning(f"Judge {model} parse failure (attempt {attempt + 1}/3): {e}")
            if attempt < 2:
                time.sleep(1.0)
    raise RuntimeError(f"Judge {model} failed after 3 attempts: {last_error}") from last_error


def score_with_both_judges(prompt: str, cfg: Config) -> dict:
    """Run both judges; return per-judge scores and averaged per-criterion scores."""
    j1 = call_judge(prompt, cfg.evaluator.judge_1_model)
    j2 = call_judge(prompt, cfg.evaluator.judge_2_model)

    llm_c1 = (j1["C1"] + j2["C1"]) / 2.0
    llm_c2 = (j1["C2"] + j2["C2"]) / 2.0
    llm_c3 = (j1["C3"] + j2["C3"]) / 2.0
    llm_score = (j1["aggregate"] + j2["aggregate"]) / 2.0

    return {
        "judge_1_C1": j1["C1"],
        "judge_1_C2": j1["C2"],
        "judge_1_C3": j1["C3"],
        "judge_1_aggregate": j1["aggregate"],
        "judge_2_C1": j2["C1"],
        "judge_2_C2": j2["C2"],
        "judge_2_C3": j2["C3"],
        "judge_2_aggregate": j2["aggregate"],
        "llm_judge_C1": llm_c1,
        "llm_judge_C2": llm_c2,
        "llm_judge_C3": llm_c3,
        "llm_judge_score": llm_score,
    }


def compute_krippendorff_alpha(results: list[dict], criterion: str) -> float:
    """Interval-level Krippendorff's α between judge 1 and judge 2 for one criterion.

    Uses the interval metric d²(v1,v2) = (v1−v2)². Requires at least 2 units.
    """
    r1 = np.array([r[f"judge_1_{criterion}"] for r in results], dtype=float)
    r2 = np.array([r[f"judge_2_{criterion}"] for r in results], dtype=float)
    n = len(r1)
    if n < 2:
        return 0.0

    # Observed disagreement: mean squared difference between the two raters
    D_o = float(np.mean((r1 - r2) ** 2))

    # Expected disagreement: pairwise over all N=2n values
    all_vals = np.concatenate([r1, r2])
    N = len(all_vals)
    # sum_{i<j}(v_i - v_j)^2 = N*sum(v^2) - sum(v)^2
    sum_sq = float(np.sum(all_vals ** 2))
    sum_v = float(np.sum(all_vals))
    D_e = 2.0 * (N * sum_sq - sum_v ** 2) / (N * (N - 1))

    if D_e == 0.0:
        return 1.0
    return float(1.0 - D_o / D_e)


# ─── Task Group 3: Evaluation Loop ────────────────────────────────────────────


def evaluate_question(
    qa_pair: dict,
    config: EvalMode,
    retriever: Retriever,
    cfg: Config,
) -> dict:
    """Run one QA pair through retrieval → generation → all metrics.

    Returns a result dict matching the output schema in requirements.md.
    """
    iou_thresh = cfg.evaluator.iou_hit_threshold
    k_values = cfg.retrieval.k_values  # [1, 3, 5]
    max_k = max(k_values)

    # Retrieve top-max_k chunks for hit-rate computation
    all_retrieved = retriever.query(
        qa_pair["question"],
        top_k=max_k,
        video_id=qa_pair["video_id"],
    )

    # Generate answer with top_k chunks (may differ from max_k)
    gen_chunks = all_retrieved[: cfg.retrieval.top_k]
    gen_result = generate(qa_pair["question"], gen_chunks, mode=config, cfg=cfg)

    cited_chunks = gen_result.cited_chunks
    gt_spans = qa_pair["ground_truth_spans"]  # list of {start, end, hop, description}
    answerable = qa_pair["answerable"]

    # Predicted spans (from cited chunks, merged)
    pred_spans: list[tuple[float, float]] = (
        merge_spans(_cited_to_intervals(cited_chunks)) if cited_chunks else []
    )

    # ── Mathematical metrics ──
    if not answerable or not gt_spans:
        t_iou = 0.0
        per_hop_iou = 0.0
        union_iou = 0.0
        hit_rates = {k: False for k in k_values}
        per_hop_recalls = {k: 0.0 for k in k_values}
        complete_at_k = {k: False for k in k_values}
        cit_acc = 0.0
    else:
        union_iou = multihop_union_iou(pred_spans, gt_spans)
        t_iou = union_iou

        per_hop_iou = multihop_per_hop_iou(pred_spans, gt_spans)

        hit_rates = {k: hit_rate_at_k(all_retrieved, gt_spans, k, iou_thresh) for k in k_values}
        per_hop_recalls = {
            k: multihop_per_hop_recall_at_k(all_retrieved, gt_spans, k, iou_thresh)
            for k in k_values
        }
        complete_at_k = {
            k: multihop_complete_retrieval_at_k(all_retrieved, gt_spans, k, iou_thresh)
            for k in k_values
        }
        cit_acc = citation_accuracy(cited_chunks, gt_spans, iou_thresh)

    # ── LLM judge ──
    judge_prompt = build_judge_prompt(
        question=qa_pair["question"],
        reference_answer=qa_pair.get("answer", ""),
        retrieved_chunks=gen_chunks,
        generated_answer=gen_result.answer,
        num_hops=qa_pair["num_hops"],
        answerable=answerable,
    )
    judge_scores = score_with_both_judges(judge_prompt, cfg)

    return {
        "qa_id": qa_pair["qa_id"],
        "video_id": qa_pair["video_id"],
        "question_type": qa_pair["question_type"],
        "config": config,
        "retrieved_chunks": [c["chunk_id"] for c in all_retrieved],
        "predicted_spans": [[s, e] for s, e in pred_spans],
        "generated_answer": gen_result.answer,
        "citations": [c["chunk_id"] for c in cited_chunks],
        "temporal_iou": t_iou,
        "iou_at_03": iou_at_threshold(t_iou, 0.3),
        "iou_at_05": iou_at_threshold(t_iou, 0.5),
        "hit_rate_at_1": hit_rates[1],
        "hit_rate_at_3": hit_rates[3],
        "hit_rate_at_5": hit_rates[5],
        "multihop_per_hop_iou": per_hop_iou,
        "multihop_union_iou": union_iou,
        "multihop_complete_at_5": complete_at_k[5],
        "multihop_per_hop_recall_at_5": per_hop_recalls[5],
        "citation_accuracy": cit_acc,
        **judge_scores,
    }


def _compute_aggregate_metrics(results: list[dict]) -> dict:
    """Compute mean metrics broken down by config and question_type."""
    numeric_fields = [
        "temporal_iou", "iou_at_03", "iou_at_05",
        "hit_rate_at_1", "hit_rate_at_3", "hit_rate_at_5",
        "multihop_per_hop_iou", "multihop_union_iou",
        "multihop_complete_at_5", "multihop_per_hop_recall_at_5",
        "citation_accuracy", "llm_judge_score",
        "llm_judge_C1", "llm_judge_C2", "llm_judge_C3",
    ]

    def _mean_over(subset: list[dict]) -> dict:
        if not subset:
            return {}
        return {f: float(np.mean([r[f] for r in subset])) for f in numeric_fields}

    configs = ["transcript_only", "transcript_plus_frames"]
    qtypes = list({r["question_type"] for r in results})
    hop_groups = {"single_hop": lambda r: r["question_type"] not in ("multi-hop", "multi-hop-visual"),
                  "multi_hop": lambda r: r["question_type"] in ("multi-hop", "multi-hop-visual")}

    agg: dict = {"overall": _mean_over(results)}
    for cfg_name in configs:
        agg[f"config_{cfg_name}"] = _mean_over([r for r in results if r["config"] == cfg_name])
    for qt in qtypes:
        agg[f"qtype_{qt}"] = _mean_over([r for r in results if r["question_type"] == qt])
    for group_name, predicate in hop_groups.items():
        agg[group_name] = _mean_over([r for r in results if predicate(r)])
    return agg


def evaluate_all(
    benchmark_path: Path | None = None,
    output_path: Path | None = None,
    cfg: Config | None = None,
) -> None:
    """Evaluate all 810 QA pairs × 2 configs; save evaluation_results.json.

    Checkpoints each result to a .jsonl file so the run can be resumed on failure.
    """
    _cfg = cfg or load_config()
    _benchmark_path = benchmark_path or (_cfg.data.benchmark_dir / "benchmark_v1.json")
    _output_path = output_path or _cfg.evaluator.output_path

    benchmark = json.loads(_benchmark_path.read_text())
    qa_pairs: list[dict] = benchmark["qa_pairs"]

    checkpoint_path = _output_path.parent / "evaluation_checkpoint.jsonl"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Load completed results from checkpoint
    completed: dict[tuple[str, str], dict] = {}
    if checkpoint_path.exists():
        for line in checkpoint_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                completed[(r["qa_id"], r["config"])] = r
        logger.info(f"Resuming from checkpoint: {len(completed)} results already done")

    retriever_t = Retriever("transcript_only", cfg=_cfg)
    retriever_f = Retriever("transcript_plus_frames", cfg=_cfg)
    retrievers: dict[str, Retriever] = {
        "transcript_only": retriever_t,
        "transcript_plus_frames": retriever_f,
    }

    configs: list[EvalMode] = ["transcript_only", "transcript_plus_frames"]
    total = len(qa_pairs) * len(configs)
    done = len(completed)

    with checkpoint_path.open("a") as ckpt:
        for qa_pair in qa_pairs:
            for config in configs:
                key = (qa_pair["qa_id"], config)
                if key in completed:
                    continue

                result = evaluate_question(qa_pair, config, retrievers[config], _cfg)
                completed[key] = result
                ckpt.write(json.dumps(result) + "\n")
                ckpt.flush()

                done += 1
                if done % 10 == 0:
                    logger.info(f"Progress: {done}/{total} ({100*done//total}%)")

    all_results = list(completed.values())

    alpha = {
        "C1": compute_krippendorff_alpha(all_results, "C1"),
        "C2": compute_krippendorff_alpha(all_results, "C2"),
        "C3": compute_krippendorff_alpha(all_results, "C3"),
        "aggregate": compute_krippendorff_alpha(all_results, "aggregate"),
    }

    output = {
        "metadata": {
            "benchmark_version": "v1",
            "evaluation_date": str(date.today()),
            "generator_model": _cfg.generator.model,
            "judge_1": _cfg.evaluator.judge_1_model,
            "judge_2": _cfg.evaluator.judge_2_model,
            "krippendorff_alpha": alpha,
            "aggregate_metrics": _compute_aggregate_metrics(all_results),
        },
        "results": all_results,
    }

    _output_path.parent.mkdir(parents=True, exist_ok=True)
    _output_path.write_text(json.dumps(output, indent=2))
    logger.info(f"Evaluation complete — {len(all_results)} results saved to {_output_path}")
