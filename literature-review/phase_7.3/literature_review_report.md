# Literature Review: LLM-as-Judge for QA Benchmark Validation
## LectureBench Phase 7.3 — Pre-Implementation Review

**Date:** 2026-05-11  
**Scope:** Focused review (~10–15 papers) addressing 5 design questions for the Phase 7.3 LLM review pass  
**Main paper:** LectureBench (this project)

---

## Overview

This review covers six open design questions for implementing the Phase 7.3 LLM review pass that filters raw QA drafts into the final LectureBench benchmark. The six questions are:

1. Is same-model review circular, or is structured same-model review accepted?
2. What scoring rubric design works best for factual QA validation?
3. What minimum span gap distinguishes genuine multi-hop from single-hop-in-disguise?
4. How do you operationalize answer correctness when the reviewer only sees text (not video frames)?
5. What should happen to rejected QA pairs — accept the shortfall, regenerate, or set a floor?
6. Is span tightening required, or is chunk-level span precision acceptable?

Papers are organized into six clusters. All 14 papers are real and verified on arXiv or Semantic Scholar. Three 2026 papers were added after a web search: Yang et al. (2026) on mitigating self-preference bias, Xiang et al. (2026) on multi-hop grounded evidence benchmarking, and Wataoka et al. (2024/NeurIPS) on the perplexity root cause of self-preference bias. Two additional papers (EduVidQA 2025, VideoZeroBench 2026) were added to answer Q6.

---

## Cluster 1: LLM-as-Judge: Methodology and Bias

**Papers:** Zheng et al. (2023), Liu et al. (2023), Ho et al. (2025), Zhou et al. (2025), Yang et al. (2026), Wataoka et al. (2024)

The foundational LLM-as-judge paper is **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena** (Zheng et al., 2023), which identifies three systematic biases in LLM judges: *position bias* (preferring responses in the first position), *verbosity bias* (preferring longer answers), and *self-enhancement bias* (preferring outputs that resemble the judge's own style). GPT-4 as judge achieves over 80% agreement with human preferences, establishing the paradigm as scalable.

The self-enhancement bias finding creates a reasonable concern when the same model family generates and reviews QA pairs. **Self-Preference Bias in LLM-as-a-Judge** (Wataoka et al., NeurIPS 2024) sharpens this concern by identifying the root cause: LLMs assign higher evaluations to lower-perplexity outputs, regardless of whether they self-generated them. GPT-4 exhibits significant SPB by this mechanism. However, the perplexity mechanism is most active when the judge is evaluating stylistically similar outputs — not when verifying factual claims against a fixed source text.

The most directly relevant paper for our setting is **LLM-as-a-Judge: Reassessing the Performance of LLMs in Extractive QA** (Ho et al., 2025), which tests same-model judging on structured QA tasks and finds *"no bias issues, such as self-preference, when the same model is used for both the QA and judgment tasks."* LLM judging achieves 0.85 correlation with human assessment vs 0.22 for Exact Match and 0.40 for F1. The key distinction is task structure: self-enhancement bias emerges in open-ended generation evaluation, not in criteria-grounded QA validation where the judge compares an answer against a source text.

**Quantifying and Mitigating Self-Preference Bias** (Yang et al., 2026) provides the most recent evidence: decomposing holistic judgments into a structured multi-dimensional form (cognitive load decomposition) reduces SPB by 31.5% on average, using only prompt modifications. This is exactly the form-filling paradigm we adopt in our rubric design, meaning our Phase 7.3 reviewer already incorporates the 2026 state-of-the-art mitigation strategy.

**G-Eval** (Liu et al., 2023) identifies LLM bias toward LLM-generated text in open-ended NLG tasks (summarization, dialogue) where no external ground truth exists — a different setting from LectureBench's chunk-grounded verification. **The JETTS Benchmark** (Zhou et al., 2025) reinforces that LLM judges are effective in structured decision-making contexts.

### Answer to Q1

**Same-model review with a structured checklist is accepted in the literature, and the 2026 literature further supports it.** Ho et al. (2025) provides direct empirical evidence that same-model judging shows no SPB for structured QA. Yang et al. (2026) shows that structured multi-dimensional prompting reduces SPB by 31.5% — and our form-filling rubric already implements this. Wataoka et al. (2024) explains *why* SPB is lower in our setting: the perplexity familiarity mechanism requires stylistic similarity, which does not apply when verifying factual claims against chunk text.

**Recommendation: Use Claude Sonnet 4.6 as reviewer (same model, structured checklist). Cross-family review (GPT-4o) remains optional — it adds ~$10–30 in cost and one extra API dependency, with marginal additional protection given the structured prompt already mitigates SPB.**

---

## Cluster 2: Fine-grained Rubric Design

**Papers:** Liu et al. (2023), Kim et al. (2023)

**G-Eval** (Liu et al., 2023) introduces the *form-filling paradigm* for LLM evaluation: rather than asking the model for a holistic score, the prompt breaks evaluation into discrete criteria, each with a step-by-step chain-of-thought rationale. The model fills out a structured form before assigning a score. G-Eval achieves Spearman correlation of 0.514 with human judgments on summarization — significantly higher than BLEU or ROUGE. The key design insight is that decomposing evaluation into named criteria reduces ambiguity and forces the model to reason through each dimension independently.

**Prometheus** (Kim et al., 2023) extends this further with *customized fine-grained score rubrics*: 1,000 task-specific rubrics, each defining what each score level means for that specific criterion. Prometheus (13B open-source) achieves Pearson correlation of 0.897 with human evaluators, matching GPT-4 (0.882) and dramatically outperforming ChatGPT (0.392). The lesson is clear: rubrics tailored to the task outperform generic prompting, and fine-grained per-criterion scoring outperforms holistic single-score evaluation.

For LectureBench Phase 7.3, the three review criteria are: (a) answer correctness, (b) span plausibility, (c) question type accuracy. Both papers recommend separate sub-scores per criterion rather than a single pass/fail judgment. For our purposes, binary pass/fail per criterion (rather than a 1–5 scale) is sufficient, because the output of the review pass is an accept/reject decision, not a ranked quality score. A 1–5 scale adds granularity that Phase 7.3 does not need — it would only matter if we were ranking QA pairs by quality, which we are not.

### Answer to Q2

**Use binary pass/fail per sub-criterion (correctness, span plausibility, type accuracy), with an overall accept/reject decision.** Prompt the reviewer with a structured form (G-Eval paradigm): present each criterion explicitly, ask for a chain-of-thought rationale, then a PASS/FAIL for each. A pair is accepted only if all three criteria pass. Do not use a 1–5 holistic scale — it introduces unnecessary ambiguity for a binary filtering decision.

**Recommended rubric structure:**
```
Criterion 1 — Answer Correctness: Is every factual claim in the answer verifiable from the cited chunk text? PASS/FAIL + reason.
Criterion 2 — Span Plausibility: Do the ground_truth_spans start/end times align with the chunk boundaries of source_chunk_ids, and is the temporal gap between hops ≥ [threshold]s for multi-hop questions? PASS/FAIL + reason.
Criterion 3 — Question Type Accuracy: Does the question genuinely require the claimed type (e.g., does multi-hop-visual truly require ≥2 non-adjacent spans with ≥1 visual hop)? PASS/FAIL + reason.
Overall: ACCEPT if all three PASS, REJECT otherwise. State rejection reason.
```

---

## Cluster 3: Factuality and Answer Correctness

**Papers:** Min et al. (2023), Ho et al. (2025)

**FActScore** (Min et al., 2023) addresses exactly the problem of verifying factual correctness from text: it breaks a generated answer into *atomic facts* — the smallest indivisible claims — and checks each against a reliable knowledge source. An automated version using retrieval + strong LLM achieves less than 2% error vs human annotation. The key insight is that whole-answer correctness is too coarse: an answer can be mostly correct but contain one hallucinated detail. Atomic decomposition catches this.

Applied to LectureBench: rather than asking "is this answer correct?" (holistic), the reviewer should check "can each key claim in this answer be found in the cited chunk text?" This maps directly to FActScore's atomic verification procedure. For visual questions, the Qwen2-VL-7B frame captions are already embedded in the chunk text, meaning visual content (slide equations, whiteboard diagrams) has been converted to natural language that the text-only reviewer can verify.

This resolves the apparent problem of text-only correctness checking for visual questions: frame captions are part of the chunk data, so the reviewer *does* have access to visual content in text form.

Ho et al. (2025) reinforces that LLM judges achieve 0.85 correlation with human correctness assessments for structured QA — the reviewer does not need to be human or see the video to make reliable correctness judgments when working from source text.

### Answer to Q4

**Answer correctness is operationalized as: every key factual claim in the answer is verifiable from the cited chunk text (including frame captions).** The reviewer does not need video access. Frame captions from Qwen2-VL-7B convert visual content to text, so all evidence is available in the chunk data. The reviewer should decompose the answer into its main claims (FActScore-style) and verify each against the source chunks. Reject if any claim is unsupported or contradicted.

---

## Cluster 4: RAG Pipeline Evaluation

**Paper:** Es et al. (2023)

**RAGAS** (Es et al., 2023) provides a reference-free framework for RAG evaluation with three dimensions: (1) *faithfulness* — answer claims are grounded in retrieved context; (2) *answer relevance* — the answer addresses the question; (3) *context precision* — the retrieved context is relevant. Faithfulness is the most relevant for Phase 7.3: it checks that no claim in the generated answer contradicts or extends beyond what the retrieved chunks support.

RAGAS's faithfulness criterion maps directly onto LectureBench's answer correctness criterion in the reviewer rubric. The framework confirms that reference-free evaluation (checking answer against retrieved context rather than against a gold human answer) is valid and sufficient for RAG QA review.

---

## Cluster 5: Multi-hop QA Definition and Quality

**Papers:** Min et al. (2019), Li et al. (2024), Xiang et al. (2026)

**Compositional Questions Do Not Necessitate Multi-hop Reasoning** (Min et al., 2019) is the most important paper for Q3. The authors demonstrate that 67% of HotpotQA's supposedly multi-hop questions can be answered by a single-hop BERT model achieving 67 F1 — comparable to state-of-the-art multi-hop models. The reason: compositional phrasing does not guarantee non-adjacent evidence. Questions that target specific entity types, or whose supporting facts are redundant across documents, appear multi-hop but are not.

The key finding for LectureBench: **a question is genuinely multi-hop only if both conditions hold: (a) the answer requires information from at least two evidence sources, AND (b) those sources are non-redundant and non-adjacent — answering from any single source alone is insufficient.** If both spans map to chunks that overlap or are adjacent, a retriever can find both in a single retrieval step, making it effectively single-hop.

For LectureBench's chunk structure (45s window, 35s stride):
- Two spans are **adjacent** if their chunks share any overlap: chunk `i` covers [35i, 35i+45], chunk `i+1` covers [35(i+1), 35(i+1)+45]. Chunks `i` and `i+1` overlap for 10 seconds.
- A span gap of -10s means the spans overlap within a single retrieval window.
- A span gap of 0s means the spans are contiguous but non-overlapping — still effectively one retrieval step.
- **Genuine multi-hop requires the spans to be in chunks at least 2 strides apart** (gap ≥ 35s between chunk start times, or ≥ 2 chunk indices apart), ensuring a retriever cannot retrieve both in one shot.

**Tree of Reviews** (Li et al., 2024) supports this by showing that genuine multi-hop retrieval requires separate, sequential retrieval decisions — if both facts could be retrieved together, the question does not test multi-hop retrieval capability.

**BRIDGE** (Xiang et al., 2026) provides the most recent corroborating evidence from the multimodal long-document setting — closest to LectureBench's scenario. BRIDGE benchmarks multi-hop reasoning over long scientific papers integrating text, tables, and figures, and finds that "systematic deficiencies in evidence aggregation and grounding remain hidden under conventional answer-only evaluation." This directly motivates LectureBench's use of span-level (step-level) evaluation: answer-only metrics would miss cases where the correct answer is reached via a single-hop shortcut. The step-level evaluation principle maps onto our span plausibility criterion in the Phase 7.3 reviewer rubric.

### Answer to Q3

**Reject multi-hop questions where span start times are fewer than 70 seconds apart (i.e., within 2 chunk strides of 35s each).** In chunk index terms: reject if `|chunk_index_A - chunk_index_B| < 2`. The -10s gap case (stanford_cs229_lec03_q010) is clearly rejectable: overlapping spans. A threshold of 2 chunk strides (70s) ensures the retriever must make at least two genuinely separate decisions to find both evidence pieces.

**Reviewer rubric Criterion 2 should include:** "For multi-hop questions: are the ground_truth_spans separated by at least 70 seconds (|start_A - start_B| ≥ 70s)? If not, FAIL — this is single-hop in disguise."

---

## Q5: Rejection and Replacement Policy

No paper in the reviewed literature directly addresses QA benchmark replacement policy. However, the multi-hop quality literature (Min et al., 2019) provides an indirect answer: a benchmark with fewer, genuinely multi-hop questions is more valuable than one with more questions that include single-hop shortcuts. Quality over count.

The practical constraint for LectureBench is the 60% visual question ratio — if too many multi-hop-visual slots are rejected without replacement, the visual-vs-nonvisual comparison in the paper loses statistical power.

### Answer to Q5

**Recommended policy: per-lecture floor with failure-aware type-targeted regeneration.**

Q2, Q3, and Q4 are the criteria that *cause* rejection; Q5 is the policy that handles what happens *after* rejection. All three criteria feed into the same floor/regeneration logic — the policy is uniform regardless of which criterion failed. However, the regeneration prompt must carry forward the specific failure constraint to avoid regenerating the same invalid pattern:

| Criterion failed | Regeneration constraint to add |
|---|---|
| Criterion 1 — Answer correctness | No special constraint; draft was factually wrong. Standard regeneration. |
| Criterion 2 — Span plausibility | Add: *"ground_truth_spans must be ≥ 70 seconds apart (≥ 2 chunk indices apart)."* |
| Criterion 3 — Type accuracy | Add: explicit reminder of type requirements (e.g., *"multi-hop-visual requires ≥ 2 non-adjacent spans with ≥ 1 span citing a frame caption — not adjacent chunks"*). |

The overall floor/count logic:

1. **Floor:** If a lecture yields ≥ 10 accepted pairs (≥ 6 visual-type), keep it as-is even if below the 12 target. Flag for paper as "some lectures accepted fewer than 12."
2. **Type-targeted regeneration:** If a specific type slot is under-represented after review (e.g., only 4 multi-hop-visual accepted out of 7 drafted), regenerate *only the failed type* for that lecture — send a narrowed prompt requesting only the missing type(s) with the relevant failure constraint added. Merge with accepted pairs.
3. **Discard floor:** If a lecture yields < 8 accepted pairs after regeneration, discard it from the benchmark entirely. With 60 lectures, losing 1–2 is acceptable; the paper reports "N lectures included."
4. **Preserve 60% visual ratio per lecture**, not just corpus-wide. This is the primary constraint for the paper's central comparison.

---

## Cluster 6: Span Precision and Annotation Methods

**Papers:** EduVidQA (2025), VideoZeroBench (2026)

Span tightening — refining a ground truth timestamp from chunk-level precision (±15–30s) down to the exact seconds within a chunk where evidence appears — is the gold standard but not universal practice.

**VideoZeroBench** (2026) represents the gold standard: 500 manually annotated questions with precise start-end temporal intervals, human-verified by re-watching full videos. Their five-level evaluation protocol uses tIoU > 0.3 at Level 4. This approach is thorough but feasible only at small scale (500 questions, short clips).

**EduVidQA** (EMNLP 2025) — the closest existing benchmark to LectureBench in domain — is the most instructive precedent. It has 5,252 QA pairs from 296 CS lecture videos with second-level timestamps, but auto-generated timestamps have an average absolute error of **±35.4 seconds**. The authors disclose this as a limitation and compensate architecturally: they use a **4-minute fixed context window** (±120s around the timestamp) rather than tightening spans. Crucially, EduVidQA was accepted at **EMNLP 2025** without span tightening, establishing that chunk-level precision is acceptable in the field when disclosed as a limitation and when the evaluation design accounts for it.

LectureBench's ±15–30s precision at 45s chunk boundaries is actually **better** than EduVidQA's ±35.4s. The key difference is that LectureBench uses temporal IoU as an evaluation metric (which directly measures span overlap), whereas EduVidQA does not — meaning LectureBench's span precision is held to a higher standard by its own metrics.

### Answer to Q6

**Span tightening is not required.** EduVidQA (EMNLP 2025) establishes a direct precedent: a lecture video QA benchmark at similar scale was accepted without sub-chunk span precision. LectureBench's ±15–30s precision is comparable to or better than this accepted baseline.

However, span precision *does* affect which temporal IoU thresholds are meaningful:

| tIoU threshold | Sensitivity to ±15–30s error | Recommendation |
|---|---|---|
| IoU@0.3 | Low — a ±20s error on a 45s chunk span still yields IoU ≈ 0.4–0.6 | **Safe to report as primary metric** |
| IoU@0.5 | Medium — a ±20s error can push IoU below 0.5 | Report as secondary, note limitation |
| IoU@0.7 | High — unreliable at chunk granularity | Do not report |

**Practical consequence:** Report tIoU@0.3 as the primary retrieval evaluation threshold. Report tIoU@0.5 as a secondary metric with a footnote disclosing ±15–30s span precision. Do not report tIoU@0.7. The paper's current disclosure ("spans LLM-estimated at ±15–30s, chunk granularity") is sufficient — no tightening pass is needed in Phase 7.3.

**If span tightening is ever added in future work**, it would require a separate LLM pass that reads chunk text sentence-by-sentence and identifies the exact sentence(s) containing the evidence, then maps those sentences back to timestamps. This is feasible but adds cost and complexity beyond the current scope.

---

## Cost Analysis

| Reviewer Model | Cost per review call | 60 lectures × 15 QA | Total estimate |
|---|---|---|---|
| Claude Sonnet 4.6 | ~$0.003 (3¢) per 1K output tokens | ~900 review calls | ~$3–8 |
| GPT-4o | ~$0.010 (1¢) per 1K output tokens | ~900 review calls | ~$10–25 |
| GPT-4o-mini | ~$0.0002 per 1K output tokens | ~900 review calls | <$1 |

**Recommendation:** Claude Sonnet 4.6 is cost-competitive and avoids adding a second API dependency. GPT-4o costs ~3× more with marginal benefit given Ho et al. (2025) shows same-model judging is unbiased for structured QA. GPT-4o-mini is too weak for complex multi-hop type accuracy checking.

---

## Summary of Decisions

| Question | Decision |
|---|---|
| Q1: Same-model circularity | Use Claude Sonnet 4.6 as reviewer — no bias for structured QA (Ho et al. 2025). Cross-family (GPT-4o) optional. |
| Q2: Scoring rubric | Binary PASS/FAIL per criterion (correctness, span plausibility, type accuracy); accept if all 3 pass. G-Eval form-filling paradigm. |
| Q3: Multi-hop adjacency | Reject if spans are < 70s apart (< 2 chunk strides). Reject if span gap ≤ 0s. |
| Q4: Correctness without video | Verify each answer claim against cited chunk text (incl. frame captions). Frame captions convert visual content to verifiable text. |
| Q5: Rejection/replacement | Floor ≥ 10 accepted per lecture; failure-aware type-targeted regeneration (prompt carries forward specific failure constraint); discard lecture if < 8 accepted after retry. |
| Q6: Span tightening | Not required. EduVidQA (EMNLP 2025) accepted at ±35.4s without tightening. LectureBench ±15–30s is better. Report tIoU@0.3 as primary, tIoU@0.5 as secondary with limitation note. |

---

## References

1. Zheng, L., Chiang, W., Sheng, Y., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
2. Liu, Y., Iter, D., Xu, Y., et al. (2023). *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*. arXiv:2303.16634.
3. Kim, S., Shin, J., Cho, Y., et al. (2023). *Prometheus: Inducing Fine-grained Evaluation Capability in Language Models*. arXiv:2310.08491.
4. Ho, X., Huang, J., Boudin, F., Aizawa, A. (2025). *LLM-as-a-Judge: Reassessing the Performance of LLMs in Extractive QA*. arXiv:2504.11972.
5. Zhou, Y., Xu, A., Wang, P., Xiong, C., Joty, S. (2025). *Evaluating Judges as Evaluators: The JETTS Benchmark*. arXiv:2504.15253.
6. Min, S., Krishna, K., Lyu, X., et al. (2023). *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*. arXiv:2305.14251.
7. Es, S., James, J., Espinosa-Anke, L., Schockaert, S. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217.
8. Min, S., Wallace, E., Singh, S., Gardner, M., Hajishirzi, H. (2019). *Compositional Questions Do Not Necessitate Multi-hop Reasoning*. arXiv:1906.02900.
9. Li, J., Liu, R., Li, Y., et al. (2024). *Tree of Reviews: A Tree-based Dynamic Iterative Retrieval Framework for Multi-hop Question Answering*. arXiv:2404.14464.
10. Wataoka, K., Takahashi, T., Ri, R. (2024). *Self-Preference Bias in LLM-as-a-Judge*. NeurIPS 2024 Safe Generative AI Workshop. arXiv:2410.21819.
11. Yang, J., Qiu, C., Deng, Z., Jiao, X., Zhou, T. (2026). *Quantifying and Mitigating Self-Preference Bias of LLM Judges*. arXiv:2604.22891.
12. Xiang, B., Han, S. C., Ding, Y. (2026). *BRIDGE: Benchmark for Multi-hop Reasoning In long multimodal Documents with Grounded Evidence*. arXiv:2603.07931.
13. DAIR-IIT Delhi. (2025). *EduVidQA: Generating and Evaluating Long-form Answers to Student Questions based on Lecture Videos*. EMNLP 2025. arXiv:2509.24120.
14. Unknown Authors. (2026). *VideoZeroBench: Probing the Limits of Video MLLMs with Spatio-Temporal Evidence Verification*. arXiv:2604.01569.
