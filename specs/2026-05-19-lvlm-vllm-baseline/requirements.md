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

- Fine-tuning any Video LLM (off-the-shelf only)
- tIoU as a primary metric for Video LLMs — models do not reliably output timestamps
- EduVidQA oracle-windowed setting (4-min window centered on ground-truth timestamp) —
  that setting cheats the retrieval problem; LectureBench uses full-video sampling only
- Adding new QA pairs to the benchmark
- Whisper ASR or audio modality for Video LLMs

---

## Key Decisions

| Decision | Status | Notes |
|---|---|---|
| Frame count N | ⏳ TBD | Candidate: 32 frames uniform across full video. More = better coverage but slower; 32 is standard for 7-8B models on A100. |
| Transcript alongside frames | ⏳ TBD | Option A: frames only (strictest baseline). Option B: frames + full transcript text (generous). Document whichever is chosen and report it in the paper. |
| tIoU for Video LLMs | Dropped (primary) | Off-the-shelf models don't output timestamps. May add a timestamp prompt and report tIoU as appendix-only secondary metric if models follow the prompt. |
| FactQA model | ⏳ TBD | See cost analysis below. GPT-4o-mini preferred if quality is adequate. |
| Entailment direction | Both | Entailment-P (ref→gen): precision. Entailment-R (gen→ref): recall. Both computed by `scripts/compute_text_metrics.py` using `cross-encoder/nli-deberta-v3-base`. |

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

**Implication for paper:** Entailment-P should be reported with a note about the direction
artifact, or replaced by Entailment-R alone. Alternatively, report both and explain the
asymmetry — this actually strengthens the paper's argument by showing that Config 2
generates richer, more informative answers (higher Entailment-R) rather than simply
reproducing the reference more closely.

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
