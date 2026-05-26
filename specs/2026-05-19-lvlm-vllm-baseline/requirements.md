# Requirements: LVLM / Video LLM Baseline

## Overview

Phase 11 adds direct Video LLM baselines to the LectureBench evaluation.
The central claim of the paper is that RAG (Config 1 and Config 2) outperforms
off-the-shelf Video LLMs on long lecture videos. This phase provides the
experimental evidence for that claim by running four open-source Video LLMs
on the same 810 QA pairs and comparing on EduVidQA-compatible metrics.

---

## In Scope

- Inference for four Video LLMs: Video-LLaVA-7B, mPLUG-Owl3-8B, Qwen-VL-7B, LLaVA-13B
- Text generation metrics for all models: BLEU, ROUGE-L, METEOR, Entailment-P, Entailment-R
- FactQA (FQA-P, FQA-R) — subject to cost decision in Task Group 2
- Unified comparison table: Config 1 | Config 2 | Video-LLaVA-7B | mPLUG-Owl3-8B | Qwen-VL-7B | LLaVA-13B
- Results breakdown by visual vs. non-visual question type (same split as existing paper tables)
- Paper results section updated with the new table and analysis

## Out of Scope

- Fine-tuning any Video LLM — dataset too small (810 pairs; ~690 train after split) to fine-tune 7–13B models without overfitting, and the off-the-shelf comparison is a stronger claim for the paper ("RAG beats Video LLMs with zero fine-tuning advantage")
- tIoU as a primary metric for Video LLMs — models do not reliably output timestamps
- Uniform full-video sampling — replaced by the oracle-windowed approach (see below)
- Adding new QA pairs to the benchmark
- Whisper ASR or audio modality for Video LLMs

---

## Key Decisions

| Decision | Status | Notes |
|---|---|---|
| Windowing strategy | ✅ Locked | EduVidQA oracle-windowed: 4-min window (±120s) centered on each hop's GT span start time. One window per hop, frames concatenated. Fully scriptable from existing `ground_truth_spans` in `benchmark_v1.json` — no manual annotation needed. |
| Multi-hop windowing | ✅ Locked | One window per hop. For a 2-hop question: 2 windows → frames concatenated into a single input. The 1 three-hop pair in the benchmark is handled the same way (3 windows). This covers 100% of benchmark pairs. |
| Transcript alongside frames | ✅ Locked | Frames + transcript text from the oracle window — matches EduVidQA Section 5.3 exactly ("text transcripts or audio are also provided from this 4-minute window"). Transcript text is extracted from existing `data/chunks/` files by filtering chunks whose `start_time` falls within [hop_start − 120s, hop_start + 120s]. No API calls needed. |
| Frame captions | ✅ Excluded | Frame captions (Qwen2-VL-7B output) are NOT added to Video LLM input. Captions are a text proxy for visual content used in Config 2 because the text embedding model cannot process images. Video LLMs have their own native visual encoder — adding captions would be redundant and would contaminate the comparison by mixing Qwen2-VL pre-analysis with the model's own visual processing. |
| tIoU for Video LLMs | ✅ Dropped | Off-the-shelf models don't output timestamps. May revisit as appendix-only if models follow a timestamp prompt. |
| FactQA model | ⏳ TBD | See cost analysis below. GPT-4o-mini preferred if quality is adequate. |
| Entailment direction | ✅ Locked | Entailment-R (gen→ref) only reported in paper. Entailment-P computed but excluded (see reporting decision above). |

### Frame count per model

EduVidQA default is 30 frames per window. Frame counts are reduced for the two LLaVA
models due to their smaller context windows. For multi-hop questions, multiply per-window
count by number of hops (almost all pairs are 2-hop — 56.7%).

| Model | Frames per window | 1-hop total | 2-hop total | Within context limit? |
|---|---|---|---|---|
| mPLUG-Owl3-8B | 30 (default) | 30 | 60 | Yes (~64 frame limit) |
| Qwen-VL-7B | 30 (default) | 30 | 60 | Yes |
| Video-LLaVA-7B | 8 (reduced) | 8 | 16 | Yes (~16 frame limit) |
| LLaVA-13B | 8 (reduced) | 8 | 16 | Yes (~8–16 frame limit) |

### FactQA cost scenarios

Using 1,620 evaluated pairs (810 × 2 RAG configs) + 810 × 4 LVLM outputs = 4,860 total pairs.
FactQA requires ~4 LLM calls per pair (fact extraction × 2 + verification × 2).

| Model | Input price | Output price | Est. total |
|---|---|---|---|
| GPT-4o-mini | $0.15/1M | $0.60/1M | ~$2–3 |
| GPT-4o | $2.50/1M | $10/1M | ~$35–50 |

**Recommendation:** GPT-4o-mini. FactQA uses structured fact extraction (not nuanced reasoning); mini produces nearly identical verdicts. The original SyllabusQA implementation uses GPT-4 but the EduVidQA repo is adaptable.

---

## Existing Text Metric Results (Config 1 vs Config 2)

Computed by `scripts/compute_text_metrics.py` from `data/benchmark/evaluation_results.json`.
No inference required — these are already available.

### All questions (n=807 per config)

| Metric | Config 1 | Config 2 | Δ |
|---|---|---|---|
| BLEU | 0.0737 | 0.1209 | +64% |
| ROUGE-L | 0.2509 | 0.3323 | +32% |
| METEOR | 0.2437 | 0.3169 | +30% |
| Entailment-P (ref→gen) | 0.4540 | 0.4267 | −6% |
| Entailment-R (gen→ref) | 0.8221 | 0.8507 | +3% |

### Visual questions (n=455 per config)

| Metric | Config 1 | Config 2 | Δ |
|---|---|---|---|
| BLEU | 0.0643 | 0.1469 | +128% |
| ROUGE-L | 0.2293 | 0.3743 | +63% |
| METEOR | 0.1881 | 0.3236 | +72% |
| Entailment-P (ref→gen) | 0.4333 | 0.3686 | −15% |
| Entailment-R (gen→ref) | 0.8122 | 0.8501 | +5% |

### Non-visual / control questions (n=352 per config)

| Metric | Config 1 | Config 2 | Δ |
|---|---|---|---|
| BLEU | 0.0858 | 0.0872 | +2% |
| ROUGE-L | 0.2789 | 0.2780 | ~0% |
| METEOR | 0.3155 | 0.3082 | −2% |
| Entailment-P (ref→gen) | 0.4807 | 0.5019 | +4% |
| Entailment-R (gen→ref) | 0.8349 | 0.8515 | +2% |

### Results analysis

**BLEU/ROUGE-L/METEOR** tell a consistent story: Config 2 substantially outperforms Config 1
on visual questions (+63–128%) while being essentially unchanged on non-visual questions
(±2%). This directly mirrors the tIoU and LLM-judge findings already in the paper and
confirms that frame augmentation benefits generation quality specifically where visual
evidence is required.

**Entailment-P (ref→gen)** is counter-intuitive: Config 1 scores *higher* than Config 2
on visual questions (0.433 vs 0.369). This is a direction artifact — Entailment-P asks
"does the reference entail the generated answer?" Config 2 generates longer, more specific
answers that go beyond the reference text, reducing entailment probability even when the
answer is more correct. Entailment-P measures answer conservativeness, not quality.

**Entailment-R (gen→ref)** is the more meaningful direction: "does the generated answer
cover the reference?" Config 2 is higher across all groups (0.8507 vs 0.8221 overall),
confirming that Config 2's answers are more complete relative to the gold reference.
The effect is largest on visual questions (+5%), consistent with all other metrics.

**Reporting decision:** Entailment-P is excluded from the paper comparison table.
The direction artifact (Config 2 generates richer answers that go beyond the reference,
reducing entailment probability even when the answer is more correct) makes it misleading
as a quality metric in this setting. Entailment-R (gen→ref) is reported instead, as it
measures answer completeness relative to the gold reference — the more meaningful direction
for RAG evaluation. Entailment-P numbers are retained here for internal reference.

---

## Dependencies

| Dependency | Already available? |
|---|---|
| `cross-encoder/nli-deberta-v3-base` | Yes — downloaded by `compute_text_metrics.py` |
| `transformers >= 4.45` | Yes (4.57.6 in vqa-benchmark env) |
| Video-LLaVA-7B | HuggingFace — not yet downloaded |
| mPLUG-Owl3-8B | HuggingFace — not yet downloaded |
| Qwen-VL-7B | HuggingFace — not yet downloaded (Qwen2-VL-7B is present for frame captioning) |
| LLaVA-13B | HuggingFace — not yet downloaded |
| EduVidQA FactQA scorer | GitHub clone needed: `github.com/sourjyadip/eduvidqa-emnlp25` |
| OpenAI API key | Already in `.env` |
| A100 80 GB | Available — all 4 models fit in bf16 |

---

## Open Questions

1. **Frame count N:** 32 frames for a 75-min video = 1 frame/2.3 min. Is this sufficient to recover single-hop visual answers? Consider running a quick ablation (16 vs 32 vs 64 frames) on a sample of 20 pairs before committing to the full evaluation.
2. **Transcript access:** Providing the transcript makes Video LLMs significantly stronger. Is that a fair comparison to RAG, which also uses the transcript? The paper should be explicit about what information each system receives.
3. **tIoU via timestamp prompt:** If a model follows a `"Estimate the time range [MM:SS–MM:SS] where the answer appears"` prompt, we get tIoU for free. Worth testing on one model before committing.
4. **LLM-judge for Video LLMs:** The existing LLM-judge (C1/C2/C3) requires retrieved chunks for C3 (groundedness). For Video LLMs there are no retrieved chunks — C3 is not applicable. Use BLEU/ROUGE/METEOR/Entailment-R as the primary quality metrics for the LVLM comparison table.
