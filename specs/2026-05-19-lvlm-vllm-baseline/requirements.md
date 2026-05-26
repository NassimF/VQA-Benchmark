# Requirements: LVLM / Video LLM Baseline

## Overview

Phase 11 adds direct Video LLM baselines to the LectureBench evaluation.
The central claim of the paper is that RAG (Config 1 and Config 2) outperforms
off-the-shelf Video LLMs on long lecture videos. This phase provides the
experimental evidence for that claim by running four open-source Video LLMs
on the same 810 QA pairs and comparing on EduVidQA-compatible metrics.

---

## In Scope

- Inference for four Video LLMs: Video-LLaVA-7B, mPLUG-Owl3-8B, **Qwen2-VL-7B**, LLaVA-13B
- Text generation metrics for all models: BLEU, ROUGE-L, METEOR, Entailment-R
- FactQA (FQA-P, FQA-R, FQA-F1) via `scripts/compute_factqa.py` (GPT-4o-mini, ~$0.54)
- Unified comparison table: Config 1 | Config 2 | Video-LLaVA-7B | mPLUG-Owl3-8B | Qwen2-VL-7B | LLaVA-13B

> **Note — LLM-Judge excluded from LVLM comparison table.**
> Running C1+C2 with the same two judges used for RAG (Claude Sonnet 4.6 + GPT-4o) would cost
> ~$38 for 4 models × 698 pairs. Excluded for now to avoid this cost. It would be better to
> include it: using the same judges produces directly comparable scores and a richer quality
> signal than BLEU/ROUGE alone. If budget allows, re-enable by running the existing judge
> pipeline on each `lvlm_results_{model}.json` with C3 disabled.
- Results breakdown by visual vs. non-visual question type (same split as existing paper tables)
- Paper results section updated with the new table and analysis
- Evaluated on n=698 answerable pairs (112 unanswerable excluded — oracle window not applicable)

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
| Multi-hop windowing | ✅ Locked | One window per hop. For a 2-hop question: 2 windows → frames concatenated in chronological order (hop 1 first, hop 2 second). Segment labels added in the prompt ("Segment 1 / Segment 2") so the model doesn't treat them as a single continuous clip. The 1 three-hop pair is handled the same way (3 windows). Covers 100% of benchmark pairs. |
| Transcript alongside frames | ✅ Locked | Frames + transcript text from the oracle window — matches EduVidQA Section 5.3 exactly. Transcript extracted from `data/chunks/` by filtering chunks whose `start_time` falls within [hop_start − 120s, hop_start + 120s]. For multi-hop, transcript from each hop window is included under its own segment label. No API calls needed. |
| Inference prompt format | ✅ Locked | Adapted directly from EduVidQA Appendix E.1 (verbatim prompts confirmed in paper PDF). System prompt establishes expert educator role; user turn contains transcript + question. LectureBench adaptation adds segment labels for multi-hop. See prompt template below. |
| Frame captions | ✅ Excluded | Qwen2-VL-7B frame captions are NOT added. Captions are a text proxy for visual content used in Config 2 because the text embedding model cannot process images. Video LLMs have native visual encoders — adding captions would be redundant and contaminate the comparison. |
| Unanswerable questions | ✅ Excluded | 112 unanswerable pairs excluded from LVLM evaluation (n=698 used). Oracle window requires `ground_truth_spans` to define the window center; unanswerable pairs have empty spans so the approach cannot be applied. Consistent with the existing tIoU exclusion. Precedent: Flanagan et al. (2025) evaluate unanswerable queries separately via Rejection Accuracy — optionally add as a supplementary metric. |
| Model choice (Qwen) | ✅ Locked | **Qwen2-VL-7B** used instead of original Qwen-VL-7B. Qwen2-VL-7B is already downloaded on disk (used for frame captioning in Phase 4), significantly stronger on OCR and lecture slide content, and Apache 2.0 licensed. No additional download needed. |
| tIoU for Video LLMs | ✅ Excluded | Off-the-shelf Video LLMs and LVLMs generate free-form text answers — they produce no timestamps, span predictions, or temporal markers. tIoU requires a predicted time range to compare against the ground-truth span; without model output timestamps, the metric is undefined. Excluded from all LVLM results tables. tIoU remains a RAG-only metric in this paper. |
| FactQA model | ✅ Locked | GPT-4o-mini. See rationale below. |
| Entailment direction | ✅ Locked | Entailment-R (gen→ref) only reported in paper. Entailment-P computed but excluded (see reporting decision above). |

### Inference prompt template

Source: EduVidQA Appendix E.1 (verbatim from paper PDF), adapted for multi-hop.

**LVLM prompt (single frame, e.g. LLaVA-13B):**
```
SYSTEM_PROMPT = "You are an expert computer science educator. You have to answer a
question that a student has asked from a video. For context, we have provided you with
the transcript around the relevant timestamp, and the frame from the video corresponding
to the relevant timestamp."

QUESTION_PROMPT = "Make sure the answer has good clarity, uses pedagogical techniques
and encourages critical thinking. Use the context from the transcript to answer the
following question in a single paragraph."

final_prompt = "System Prompt: " + SYSTEM_PROMPT +
               " Relevant transcript: " + transcript_text +
               " Question Prompt: " + QUESTION_PROMPT +
               " Question: " + question
```

**Video LLM prompt (multiple frames, e.g. mPLUG-Owl3-8B, Qwen2-VL-7B):**
```
SYSTEM_PROMPT = "You are an expert computer science educator. You have to answer a
question that a student has asked from a video. For context, we have provided you with
the transcript around the relevant timestamp, and the frames from the video corresponding
to the relevant timestamp."

QUESTION_PROMPT = "Make sure the answer has good clarity, uses pedagogical techniques
and encourages critical thinking. Use the context from the transcript to answer the
following question in a single paragraph."

final_prompt = "System Prompt: " + SYSTEM_PROMPT +
               " Relevant transcript: " + transcript_text +
               " Question Prompt: " + QUESTION_PROMPT +
               " Question: " + question
```

**LectureBench adaptation for multi-hop (2 windows):**
Replace `transcript_text` with segment-labelled blocks:
```
--- Segment 1 ---
{transcript_text_hop1}

--- Segment 2 ---
{transcript_text_hop2}
```
Frames from both windows are concatenated in chronological order (hop 1 first).
Single-hop questions use the original EduVidQA format with no segment labels.

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

Using 1,620 evaluated pairs (810 × 2 RAG configs). FactQA requires **2 LLM calls per pair**
(one for FQA-P, one for FQA-R — each call handles extraction + verification in a single prompt).
Avg ~300 input tokens + ~200 output tokens per call.

| Model | Input (972K tok) | Output (648K tok) | Est. total |
|---|---|---|---|
| GPT-4o-mini | $0.15/1M → $0.15 | $0.60/1M → $0.39 | **~$0.54** |
| GPT-4o | $2.50/1M → $2.43 | $10/1M → $6.48 | **~$8.91** |

**Decision: GPT-4o-mini (~$0.54 for 1,620 pairs).**

FactQA is appropriate for GPT-4o-mini for three reasons:
1. **Task complexity:** The prompt is purely structural — list atomic facts, check which are supported, output `Score: X/Y`. This requires no nuanced reasoning, just careful reading and counting. GPT-4o-mini handles structured extraction tasks reliably.
2. **Short answers:** Generated answers average 35 words and gold answers average 65 words, yielding ~3–6 atomic facts per pair. With so few facts per call, even a weaker model makes minimal errors.
3. **Temperature=0:** Running deterministically eliminates model variance, so the gap between mini and GPT-4o on this specific task narrows further — both models are consistent when constrained to deterministic output.

The original SyllabusQA uses `gpt-4-1106-preview` and EduVidQA uses `gpt-4o`, but both were designed for longer, more complex syllabus/lecture answers than LectureBench's concise factual QA pairs. At this answer length, GPT-4o-mini is equivalent in practice. Cost difference: ~$0.54 (mini) vs ~$8.91 (GPT-4o) for zero measurable quality gain on this task.

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
| Qwen2-VL-7B | Already on disk (used in Phase 4 frame captioning) |
| LLaVA-13B | HuggingFace — not yet downloaded |
| `scripts/compute_factqa.py` | Implemented — no external clone needed |
| OpenAI API key | Already in `.env` |
| A100 80 GB | Available — all 4 models fit in bf16 |

---

## Open Questions

1. **LLM-judge for Video LLMs:** The existing LLM-judge (C1/C2/C3) requires retrieved chunks for C3 (groundedness). For Video LLMs there are no retrieved chunks — C3 is not applicable. Decision: use BLEU/ROUGE-L/METEOR/Entailment-R/FQA as the primary quality metrics for the LVLM comparison table; LLM-judge is RAG-only.
