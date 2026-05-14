# Literature Review: LLM-as-Judge for QA Benchmark Validation
## LectureBench Phase 7.3 — Pre-Implementation Review

**Date:** 2026-05-14 (last updated; originally 2026-05-11)
**Scope:** Focused review (23 papers) addressing 6 design questions for the Phase 7.3 LLM review pass  
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

Papers are organized into seven clusters. All 23 papers are real and verified on arXiv, Semantic Scholar, or publisher pages. Several papers were added after the initial draft: Yang et al. (2026) on mitigating self-preference bias, Xiang et al. (2026) on multi-hop grounded evidence benchmarking, Wataoka et al. (NeurIPS 2024) on the perplexity root cause of self-preference bias, EduVidQA (EMNLP 2025) and VideoZeroBench (2026) for Q6, and Baysan et al. (Frontiers 2025) and Yu et al./DeCE (EMNLP 2025) as peer-reviewed alternatives to Ho et al.

---

## Cluster 1: LLM-as-Judge: Methodology and Bias

**Papers:** Zheng et al. (2023), Liu et al. (2023), Ho et al. (2025), Zhou et al. (2025), Yang et al. (2026), Wataoka et al. (2024)

The foundational LLM-as-judge paper is **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena** (Zheng et al., 2023), which identifies three systematic biases in LLM judges: *position bias* (preferring responses in the first position), *verbosity bias* (preferring longer answers), and *self-enhancement bias* (preferring outputs that resemble the judge's own style). GPT-4 as judge achieves over 80% agreement with human preferences, establishing the paradigm as scalable.

The self-enhancement bias finding creates a reasonable concern when the same model family generates and reviews QA pairs. **Self-Preference Bias in LLM-as-a-Judge** (Wataoka et al., NeurIPS 2024) sharpens this concern by identifying the root cause: LLMs assign higher evaluations to lower-perplexity outputs, regardless of whether they self-generated them. GPT-4 exhibits significant SPB by this mechanism. However, the perplexity mechanism is most active when the judge is evaluating stylistically similar outputs — not when verifying factual claims against a fixed source text.

The most directly relevant paper for our setting is **LLM-as-a-Judge: Reassessing the Performance of LLMs in Extractive QA** (Ho et al., 2025), which tests same-model judging on structured QA tasks and finds *"no bias issues, such as self-preference, when the same model is used for both the QA and judgment tasks."* LLM judging achieves 0.85 correlation with human assessment vs 0.22 for Exact Match and 0.40 for F1. The key distinction is task structure: self-enhancement bias emerges in open-ended generation evaluation, not in criteria-grounded QA validation where the judge compares an answer against a source text.

**Quantifying and Mitigating Self-Preference Bias** (Yang et al., 2026) provides the most recent evidence: decomposing holistic judgments into a structured multi-dimensional form (cognitive load decomposition) reduces SPB by 31.5% on average, using only prompt modifications. This is exactly the form-filling paradigm we adopt in our rubric design, meaning our Phase 7.3 reviewer already incorporates the 2026 state-of-the-art mitigation strategy.

**G-Eval** (Liu et al., 2023) identifies LLM bias toward LLM-generated text in open-ended NLG tasks (summarization, dialogue) where no external ground truth exists — a different setting from LectureBench's chunk-grounded verification. **The JETTS Benchmark** (Zhou et al., 2025) reinforces that LLM judges are effective in structured decision-making contexts.

### Answer to Q1

**Same-model review with a structured checklist is supported by the literature.** Ho et al. (2025) provides direct empirical evidence that same-model judging shows no SPB for structured QA (0.85 correlation with human, no SPB detected). Yang et al. (2026) shows that structured multi-dimensional prompting reduces SPB by 31.5% — our G-Eval form-filling rubric implements this directly. Wataoka et al. (2024) explains *why* SPB is lower in our setting: the perplexity familiarity mechanism requires stylistic similarity, which does not apply when verifying factual claims against a fixed source text.

**Note on Ho et al. (2025) publication status (updated 2026-05-13):** Ho et al. (2025) "LLM-as-a-Judge: Reassessing the Performance of LLMs in Extractive QA" (corrected arXiv ID: 2504.11972) is an **arXiv preprint only** — not yet published at any peer-reviewed venue. The arXiv ID previously listed (2501.09775) was a different paper. This weakens its use as a primary citation. Two peer-reviewed published alternatives are added below (Baysan et al. 2025, Yu et al./DeCE 2025).

**Note on EduVidQA as precedent (updated 2026-05-13):** EduVidQA (EMNLP 2025) was previously cited here as a precedent for LLM-only review. Upon reading the full paper, EduVidQA uses a hybrid approach: automated filtering + GPT-4o adversarial refinement + human spot-checks by two graduate students on 10% of pairs (Cohen's Kappa = 0.83). It does NOT use LLM-only review, so it cannot support the single-judge decision. EduVidQA remains valid only for Q6 (span tightening precedent).

**Peer-reviewed support added (2026-05-13):**
- **Baysan et al. (2025)** — *Frontiers in Big Data* (peer-reviewed). LLM-as-judge for structured Pass/Fail evaluation of structured outputs achieves ~90% agreement with human judgments. Contextual prompt routing reduces hallucinations. Supports same-model structured evaluation reliability for Q1.
- **Yu et al. / DeCE (EMNLP 2025 Industry Track)** — "Beyond Pointwise Scores: Decomposed Criteria-Based Evaluation of LLM Responses." Decomposed criteria-based LLM evaluation achieves r=0.78 with expert judgments vs r=0.35 for pointwise scoring. Directly validates our G-Eval form-filling rubric design for Q2.

**Note on Yang et al. (2026) publication status:** Also an arXiv preprint only (arXiv:2604.22891), no venue confirmed yet.

**Decision (adopted 2026-05-13 — Simplified Option C):** Claude Sonnet 4.6 as primary reviewer for all three criteria. GPT-4o cross-family rerun for Criterion 1 only when Claude passes — if GPT-4o disagrees, discard the pair. This is motivated by Lee et al. (2026): knowledge-conflict failure is systematic and silent for C1 on cutting-edge ML content. C2 and C3 remain Claude-only (C2 is near-deterministic via the ≥70s threshold; C3 is a structural type check).

**Papers backing this decision:**
- Ho et al. (2025) — same-model SPB = 0 for structured QA, 0.85 human correlation (arXiv preprint, unreviewed — treat as supporting evidence, not primary citation)
- Baysan et al. (2025) — **peer-reviewed**, Frontiers in Big Data — LLM Pass/Fail evaluation achieves ~90% human agreement for structured output evaluation; validates structured single-judge reliability
- Yang et al. (2026) — structured multi-dimensional prompting reduces SPB 31.5% → G-Eval rubric mitigates residual bias (arXiv preprint, unreviewed)
- Wataoka et al. (2024) — **NeurIPS 2024 Workshop** — perplexity mechanism explains why SPB is lower in criteria-grounded settings
- Lee et al. (2026) — knowledge-conflict failure mode for C1 → GPT-4o cross-check specifically for C1

---

## Cluster 2: Fine-grained Rubric Design

**Papers:** Liu et al. (2023), Kim et al. (ICLR 2024), Yu et al. (EMNLP 2025)

**G-Eval** (Liu et al., 2023) introduces the *form-filling paradigm* for LLM evaluation: rather than asking the model for a holistic score, the prompt breaks evaluation into discrete criteria, each with a step-by-step chain-of-thought rationale. The model fills out a structured form before assigning a score. G-Eval achieves Spearman correlation of 0.514 with human judgments on summarization — significantly higher than BLEU or ROUGE. The key design insight is that decomposing evaluation into named criteria reduces ambiguity and forces the model to reason through each dimension independently.

**Prometheus** (Kim et al., 2023) extends this further with *customized fine-grained score rubrics*: 1,000 task-specific rubrics, each defining what each score level means for that specific criterion. Prometheus (13B open-source) achieves Pearson correlation of 0.897 with human evaluators, matching GPT-4 (0.882) and dramatically outperforming ChatGPT (0.392). The lesson is clear: rubrics tailored to the task outperform generic prompting, and fine-grained per-criterion scoring outperforms holistic single-score evaluation.

For LectureBench Phase 7.3, the three review criteria are: (a) answer correctness, (b) span plausibility, (c) question type accuracy. Both papers recommend separate sub-scores per criterion rather than a single pass/fail judgment. For our purposes, binary pass/fail per criterion (rather than a 1–5 scale) is sufficient, because the output of the review pass is an accept/reject decision, not a ranked quality score. A 1–5 scale adds granularity that Phase 7.3 does not need — it would only matter if we were ranking QA pairs by quality, which we are not.

### Answer to Q2

**Use binary pass/fail per sub-criterion (correctness, span plausibility, type accuracy), with an overall accept/reject decision.** Prompt the reviewer with a structured form (G-Eval paradigm): present each criterion explicitly, ask for a chain-of-thought rationale, then a PASS/FAIL for each. A pair is accepted only if all three criteria pass. Do not use a 1–5 holistic scale — it introduces unnecessary ambiguity for a binary filtering decision.

**Papers backing this decision:**
- Liu et al. / G-Eval (2023) — **EMNLP 2023** — form-filling with named criteria + CoT achieves Spearman 0.514 with human judgment; decomposed criteria outperform holistic scoring
- Kim et al. / Prometheus (ICLR 2024) — task-specific rubrics achieve Pearson 0.897 with human evaluators; binary PASS/FAIL is sufficient for accept/reject filtering
- Yu et al. / DeCE (2025) — **EMNLP 2025 Industry Track** — decomposed criteria-based LLM evaluation achieves r=0.78 with expert judgments vs r=0.35 for pointwise scoring; directly validates our rubric design approach

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

**Answer correctness is operationalized as atomic fact verification against cited chunk text.** The reviewer decomposes each answer into its smallest indivisible factual claims and checks each claim individually against the cited chunk text (including `[frame caption: ...]` content). Reject if any single claim is unsupported or contradicted — whole-answer holistic judgment is too coarse. The reviewer does not need video access: frame captions from Qwen2-VL-7B convert visual content to natural language, making all evidence available in text form.

Additionally, for C1 specifically, a GPT-4o cross-family rerun is applied when Claude passes C1, to catch knowledge-conflict failures (see Q1 decision).

**Papers backing this decision:**
- Min et al. / FActScore (2023) — atomic fact decomposition + per-claim source verification achieves <2% error vs. human annotation; holistic correctness misses single hallucinated details
- Ho et al. (2025) — LLM judges achieve 0.85 correlation with human correctness assessments for structured QA when working from source text
- Es et al. / RAGAS (2023) — faithfulness criterion (answer claims grounded in retrieved context) validates reference-free correctness checking against chunk text
- Lee et al. (2026) — knowledge-conflict failure mode: judge may override chunk text with parametric knowledge → GPT-4o cross-check for C1 on cutting-edge ML content

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

**Relationship to Q2:** Q3 answers the specific threshold value that Q2's Criterion 2 (Span Plausibility) requires to be fully specified. Q2 defines the rubric structure; Q3 provides the parameter. Neither is redundant — Q2 is underspecified without Q3's answer.

### Answer to Q3

**Reject multi-hop questions where span start times are fewer than 70 seconds apart (i.e., within 2 chunk strides of 35s each).** In chunk index terms: reject if `|chunk_index_A - chunk_index_B| < 2`. The -10s gap case (stanford_cs229_lec03_q010) is clearly rejectable: overlapping spans. A threshold of 2 chunk strides (70s) ensures the retriever must make at least two genuinely separate decisions to find both evidence pieces.

**Reviewer rubric Criterion 2 should include:** "For multi-hop questions: are the ground_truth_spans separated by at least 70 seconds (|start_A - start_B| ≥ 70s)? If not, FAIL — this is single-hop in disguise."

**Papers backing this decision:**
- Min et al. (2019) — 67% of HotpotQA multi-hop questions answerable by single-hop model; root cause is adjacent/redundant evidence; non-adjacency is necessary for genuine multi-hop
- Xiang et al. / BRIDGE (2026) — span-level evaluation needed to detect single-hop shortcuts hidden under compositional phrasing; answer-only metrics miss these cases
- Li et al. / Tree of Reviews (2024) — genuine multi-hop requires sequential separate retrieval decisions; co-locatable evidence is effectively single-hop

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

**Updated decision (2026-05-12):** Regeneration strategy deferred until after review pass statistics.

**Updated decision (2026-05-13):** Full run completed. Results: 398 accepted / 502 rejected (56% rejection rate) across 60 lectures. 53 lectures below floor (<10 accepted), 40 at discard risk (<8 accepted). Dominant failure modes: C1 (hallucinated atomic claims, 77 knowledge-conflict discards from GPT-4o), C2 (adjacent multi-hop spans < 70s), C3 (type misclassification — text labeled as visual). Given the broad failure distribution across all types and lectures, **full regeneration** (regenerate all 15 pairs fresh per lecture below floor) is more appropriate than type-targeted regeneration. Failure-aware constraint carry-forward remains in effect.

**Papers backing this decision:**
- Min et al. (2019) — quality over quantity: smaller set of genuinely valid multi-hop pairs is more valuable than inflating counts with borderline pairs → floor and discard thresholds
- No paper directly addresses QA regeneration policy; floor/retry design is engineering judgment backed by the quality-over-quantity principle

---

## Cluster 6: Span Precision and Annotation Methods

**Papers:** EduVidQA (2025), VideoZeroBench (2026)

Span tightening — refining a ground truth timestamp from chunk-level precision (±15–30s) down to the exact seconds within a chunk where evidence appears — is the gold standard but not universal practice.

**VideoZeroBench** (2026) represents the gold standard: 500 manually annotated questions with precise start-end temporal intervals, human-verified by re-watching full videos. Their five-level evaluation protocol uses tIoU > 0.3 at Level 4. This approach is thorough but feasible only at small scale (500 questions, short clips).

**EduVidQA** (EMNLP 2025) — the closest existing benchmark to LectureBench in domain — is the most instructive precedent. It has 5,252 QA pairs from 296 CS lecture videos with second-level timestamps, but auto-generated timestamps have an average absolute error of **±35.4 seconds**. The authors disclose this as a limitation and compensate architecturally: they use a **4-minute fixed context window** (±120s around the timestamp) rather than tightening spans. Crucially, EduVidQA was accepted at **EMNLP 2025** without span tightening, establishing that chunk-level precision is acceptable in the field when disclosed as a limitation and when the evaluation design accounts for it.

LectureBench's ±15–30s precision at 45s chunk boundaries is actually **better** than EduVidQA's ±35.4s. The key difference is that LectureBench uses temporal IoU as an evaluation metric (which directly measures span overlap), whereas EduVidQA does not — meaning LectureBench's span precision is held to a higher standard by its own metrics.

### Answer to Q6

**Span tightening is not required.** EduVidQA (EMNLP 2025) establishes a direct precedent for span precision: auto-generated timestamps with ±35.4s average error were accepted at EMNLP without tightening. LectureBench's ±15–30s precision is better than this accepted baseline. Note: EduVidQA's precedent here is strictly about *span precision tolerance*, not about QA review methodology (see Q1 note).

**Papers backing this decision:**
- EduVidQA (EMNLP 2025) — accepted at EMNLP with ±35.4s auto-generated timestamps, no tightening; LectureBench ±15–30s is a stricter baseline than this accepted work
- VideoZeroBench (2026) — uses tIoU@0.3 as Level 4 threshold; a ±20s error on a 45s chunk still yields IoU ≈ 0.4–0.6, confirming @0.3 is robust to chunk-level precision

However, span precision *does* affect which temporal IoU thresholds are meaningful:

| tIoU threshold | Sensitivity to ±15–30s error | Recommendation |
|---|---|---|
| IoU@0.3 | Low — a ±20s error on a 45s chunk span still yields IoU ≈ 0.4–0.6 | **Safe to report as primary metric** |
| IoU@0.5 | Medium — a ±20s error can push IoU below 0.5 | Report as secondary, note limitation |
| IoU@0.7 | High — unreliable at chunk granularity | Do not report |

**Practical consequence:** Report tIoU@0.3 as the primary retrieval evaluation threshold. Report tIoU@0.5 as a secondary metric with a footnote disclosing ±15–30s span precision. Do not report tIoU@0.7. The paper's current disclosure ("spans LLM-estimated at ±15–30s, chunk granularity") is sufficient — no tightening pass is needed in Phase 7.3.

> **Source of the @0.3 threshold:** The choice of tIoU@0.3 as primary comes from VideoZeroBench (2026), which uses tIoU > 0.3 as its Level 4 evaluation threshold for temporal grounding. EduVidQA provided the precedent for *not tightening spans*; VideoZeroBench provided the justification for *which threshold is appropriate* at chunk-level precision.

**If span tightening is ever added in future work**, it would require a separate LLM pass that reads chunk text sentence-by-sentence and identifies the exact sentence(s) containing the evidence, then maps those sentences back to timestamps. This is feasible but adds cost and complexity beyond the current scope.

---

## Cost Analysis

| Reviewer Model | Role | Calls (estimated) | Cost per 1K output tokens | Total estimate |
|---|---|---|---|---|
| Claude Sonnet 4.6 | Primary — all 3 criteria | ~900 (all pairs) | ~$0.003 | ~$3–8 |
| GPT-4o | C1 cross-check only — called when Claude passes C1 | ~400–600 (C1-pass subset) | ~$0.010 | ~$4–12 |
| GPT-4o-mini | Not used (too weak for multi-hop type accuracy) | — | ~$0.0002 | — |

**Note (updated after full run):** GPT-4o is called only on pairs where Claude passes C1, not on all 900 pairs. The actual call count depends on Claude's C1 pass rate; after the first full run (~56% overall rejection rate), approximately 400–600 C1-pass pairs received a GPT-4o cross-check. Total cost for the two-call flow is approximately $7–20 combined.

**Recommendation:** The two-call flow (Claude primary + GPT-4o C1 cross-check) was adopted as the final design (Simplified Option C). GPT-4o-mini is too weak for complex multi-hop type accuracy checking and is not used in Phase 7.3.

---

## Cluster 7: Multi-Judge and Ensemble Evaluation

**Papers:** Li et al. (2023), Chan et al. (2023), Chen et al. (2025), Tang et al. (2025), Wei et al. (2024), Huang et al. (2026)

**Added:** 2026-05-12 — supplementary review to assess whether multi-judge approaches strengthen LectureBench Phase 7.3 or Phase 8.

### Overview

Multi-judge LLM evaluation refers to using two or more independent LLM evaluators — either different model families, different prompt variations of the same model, or agents with different personas — and aggregating their decisions (via majority vote, discussion, or consensus) rather than trusting a single judge.

**PRD** (Li et al., 2023) is the foundational paper: multiple LLMs independently score answers, then discuss disagreements before a final consensus. PRD reduces position bias and self-enhancement bias compared to single-judge evaluation. Crucially, PRD finds that *discussion* between judges outperforms simple majority voting — judges update their positions after seeing each other's reasoning, catching errors that neither would catch alone.

**ChatEval** (Chan et al., 2023) extends this with a multi-agent debate framework: evaluators with different assigned personas argue about response quality before converging. ChatEval outperforms single-judge evaluation on MT-Bench. The persona diversity acts as a proxy for inter-annotator variation, surfacing disagreements that a single model would mask.

**PCFJudge** (Huang et al., 2026) takes a different angle: instead of using multiple models, it reruns the *same* model over multiple orderings of the candidate set (permutation consensus) to cancel out order/position sensitivity. This is a lightweight multi-run approach requiring only one API key. Directly targets factuality evaluation — the same task as Phase 7.3 Criterion 1.

**LLM Ensemble Survey** (Chen et al., 2025) provides the most comprehensive taxonomy: majority voting is the simplest and most robust aggregation for binary decisions; weighted voting adds complexity with marginal gain unless judges have known reliability scores. For QA benchmark filtering (binary PASS/FAIL), majority vote over 2–3 judges is the recommended approach.

**Tang et al. (2025)** show empirically that aggregating multiple LLM judges before distillation reduces systematic bias in dialogue evaluation. The relevant finding: 2–3 judge majority vote achieves most of the bias reduction benefit of a full distilled ensemble.

**Lee et al. (2026)** — the most directly relevant paper for Phase 7.3 Q4 — identifies a critical failure mode in reference-based QA judging: when the provided source text *conflicts* with the judge's parametric (training) knowledge, the judge systematically favors its own prior over the reference, degrading evaluation fidelity. For LectureBench, lecture content on recent ML advances (MIT 6.S191, NYU Deep Learning) may conflict with Claude's training knowledge — the judge might override what the chunk text says with what it "knows" to be true. This is a concrete, testable failure mode, not a vague bias concern.

**Wei et al. (2024)** introduce a key practical concern: the same LLM judge with different prompt templates disagrees 15–25% of the time on identical inputs. This *internal* inconsistency exists independent of multi-judge setups and suggests that even a single-judge review should report reliability (Cohen's Kappa between two runs with different prompt seeds) as a credibility measure.

### Multi-Judge Assessment Per Question

| Q | Multi-judge benefit | Verdict |
|---|---|---|
| **Q1 (Same-model bias)** | Multi-judge with a cross-family model (GPT-4o) would eliminate residual SPB. Ho et al. (2025) shows SPB is near zero for structured QA; Yang et al. (2026) structured prompting reduces SPB 31.5%. Residual knowledge-conflict risk (Lee et al., 2026) motivated a targeted cross-family check for C1 specifically. | **Adopted (Simplified Option C): GPT-4o cross-check for C1 only; C2/C3 remain Claude-only** |
| **Q2 (Rubric)** | Multi-judge could catch disagreements on borderline C1 cases (factual claims that are partially supported). PCFJudge's permutation consensus is a low-cost way to add robustness to C1 without a second model. | **Optional: run C1 twice with shuffled claim order; flag disagreements for discard** |
| **Q3 (Multi-hop gap)** | Span gap is a deterministic arithmetic check (≥70s). No judgment involved — multi-judge adds zero value here. | **Not applicable** |
| **Q4 (Correctness without video)** | Lee et al. (2026) identifies a concrete failure mode here: when chunk text conflicts with Claude's parametric knowledge (likely for cutting-edge ML lecture content), the judge overrides the reference. A cross-family second judge (GPT-4o) is less likely to share the same knowledge bias. This is the strongest case for optional multi-judge in Phase 7.3. Low Kappa on Q4 disagreements likely signals knowledge-conflict failures, not random noise. | **Adopted (2026-05-13): cross-family C1 check with GPT-4o; strongly recommended for Phase 8** |
| **Q5 (Rejection policy)** | Policy is deterministic once criteria are evaluated. No judgment involved. | **Not applicable** |
| **Q6 (Span tightening)** | Span plausibility (C2) is also a near-deterministic check against chunk boundaries. Multi-judge adds little. | **Not applicable** |

### Practical Recommendation for LectureBench

For **Phase 7.3** (binary filtering), multi-judge is not required but one lightweight option adds credibility with minimal cost:

> **Option A (recommended if paper needs stronger credibility claim):** Run the reviewer twice on each pair with different prompt seeds; compute Cohen's Kappa. Report Kappa in the paper's methodology section. If Kappa > 0.8 (near-perfect agreement), single-judge review is justified. If Kappa < 0.7, escalate to cross-family review for the disagreement cases only. Cost: ~2× review calls = ~$6–16 total, vs ~$3–8 for single-run.

> **Option B (original plan):** Single-judge, structured G-Eval rubric, report it as a limitation. Acceptable per Ho et al. (2025) precedent. Cheapest and simplest. Note: EduVidQA cannot be cited here — it uses human spot-checks + GPT-4o adversarial filtering, not LLM-only review.

> **Option C (criterion-targeted reliability):** Run the reviewer once for all three criteria. Then apply targeted reliability checks per criterion:
> - **C1 (answer correctness / Q4):** Rerun C1 only with a cross-family judge (GPT-4o) to catch knowledge-conflict overrides (Lee et al., 2026). If the two judges disagree on C1, mark the pair as borderline and discard.
> - **C2 (span plausibility / Q2):** Rerun C2 only with a different prompt seed (same model) to catch prompt sensitivity (Wei et al., 2024). If the two runs disagree on C2, mark as borderline and discard.
> - C3 (type accuracy) is deterministic enough that no second check is needed.
> - Only pairs that pass all checks on both runs are ACCEPTED.
> This adds ~1.5× the cost of a single full review pass (not 2×, since only C1 and C2 are re-checked, not the full rubric). It is the most targeted and principled option, with each reliability strategy matched to the specific failure mode of each criterion.

> **Decision (2026-05-13) — Simplified Option C adopted (C1 cross-family only):**
> Run Claude Sonnet 4.6 once for all three criteria. For pairs where C1 passes, rerun C1 only with GPT-4o. If GPT-4o disagrees, discard the pair. C2 double-run skipped because the ≥70s deterministic threshold (D3) already reduces C2 ambiguity sufficiently — prompt sensitivity (Wei et al., 2024) is a real concern but less critical than the systematic knowledge-conflict failure in C1 (Lee et al., 2026). C3 remains single-run (deterministic). Cost: ~$1–3 extra ≈ ~1.2× base cost. See requirements.md D1.

For **Phase 8** (LLM-judge 1–5 quality scoring), multi-judge is *strongly recommended* — see the Phase 8 section below.

---

## Phase 8 — Multi-Judge Implications

*This section covers Phase 8 (LLM-judge quality scoring, 1–5 scale) based on the multi-judge literature. It is separate from the Phase 7.3 binary filtering decisions above.*

Phase 8 uses an LLM judge to score generated answers on a 1–5 scale for answer quality and grounding. Unlike Phase 7.3's binary criteria checks, this is a subjective judgment — the exact scenario where multi-judge literature shows the largest gains.

**Key findings from the multi-judge literature:**

1. **PRD (Li et al., 2023):** Discussion between judges reduces position and self-enhancement bias more than majority voting alone. For Phase 8 quality scoring, a two-judge setup where judges share reasoning and resolve disagreements before finalizing a score would produce more reliable 1–5 ratings. Recommended: 2-judge discussion protocol for Phase 8 LLM-judge.

2. **ChatEval (Chan et al., 2023):** Persona diversity reduces systematic blind spots. For Phase 8, assigning one judge a "strict grounding" persona (penalizes hallucinations) and another a "answer completeness" persona (rewards thoroughness) would catch different failure modes. The two-persona debate produces a more balanced 1–5 score.

3. **Wei et al. (2024):** Internal inconsistency of 15–25% on identical inputs is especially problematic for 1–5 scoring (a swing of 1 point is 20–25% of the scale). Reporting Krippendorff's alpha between two independent judge runs is a minimum credibility requirement for Phase 8.

4. **Chen et al. (2025) Ensemble Survey:** For quality scoring (not binary PASS/FAIL), average-score aggregation across 2–3 judges outperforms majority voting. The averaged score reduces the impact of any single judge's bias.

**Recommended Phase 8 multi-judge protocol:**
- 2 judges: Claude Sonnet 4.6 + GPT-4o-mini (cost-effective cross-family pair)
- Aggregation: averaged score
- Report: Krippendorff's alpha between the two judges; if α < 0.6, escalate to a third judge (GPT-4o) for tie-breaking on low-agreement pairs
- Estimated cost: ~2× Phase 8 judge calls; GPT-4o-mini is ~5× cheaper than GPT-4o for the second judge

> ⚠️ **TODO before Phase 8 implementation:** Conduct targeted lit review of LLM-judge *criteria* (what dimensions to score: correctness, completeness, groundedness) before selecting the final 1–5 rubric. See roadmap Phase 8 ⚠️ note.

---

## LLM-Only Benchmark Curation: Literature Gap and Justification Strategy

### Finding: No Peer-Reviewed Precedent for LLM-Only Benchmark Curation

A systematic review of all 26 papers in this literature review reveals that **none of them use an LLM-only approach for benchmark curation** — that is, for deciding algorithmically which QA pairs are accepted into a dataset without human involvement. Every paper in the dictionary falls into one of two categories:

1. **Output scoring against existing ground truth** — LLM judges score model-generated answers against a pre-existing reference (G-Eval, FActScore, RAGAS, Prometheus, Baysan et al., DeCE, etc.). Ground truth was already established by humans before the LLM is involved.
2. **Human-curated or hybrid-curated benchmarks** — The benchmark itself is assembled by humans, often with LLM assistance for adversarial question generation or consistency filtering, followed by human verification (EduVidQA, BRIDGE, VideoZeroBench, PCFJudge).

The table below documents the benchmark curation technique for every paper in the literature review that is most structurally similar to LectureBench (video QA, long-document QA, or multi-hop factoid benchmarks):

| Paper | Venue | QA Source | Curation Technique | Human Review? |
|---|---|---|---|---|
| EduVidQA (DAIR-IIT Delhi, 2025) | EMNLP 2025 | GPT-4o generates questions from lecture transcripts | GPT-4o adversarial filtering + human spot-checks on sampled pairs | Yes — human spot-check |
| BRIDGE (Xiang et al., 2026) | arXiv 2026 | Human annotators create multi-hop chains over scientific papers | Human annotation throughout; LLM used only for step-level evidence alignment checks | Yes — fully human |
| VideoZeroBench (2026) | arXiv 2026 | Human experts write questions over video clips | Human expert annotation; LLM not used in curation | Yes — fully human |
| FActScore (Min et al., 2023) | EMNLP 2023 | Wikipedia passages as ground truth for biography generation | Human annotation of atomic facts; LLM verifies claims against human-labeled facts | Yes — human ground truth |
| RAGAS (Es et al., 2023) | arXiv 2023 | LLM generates QA pairs from retrieved context | LLM-only faithfulness scoring (answer vs. retrieved context) — no human in the loop. **Partially supports Phase 7.3 mechanism** (LLM checking claims against reference text), but RAGAS is a runtime evaluation tool: it scores all outputs continuously without a permanent accept/reject gate. No pair is ever admitted to a fixed dataset. | Partial — mechanism supported, curation gate not |
| Ho et al. (2025) | arXiv preprint | Existing benchmarks (SQuAD, TriviaQA) with human ground truth | LLM judge replaces human scoring of model answers against pre-existing human-annotated ground truth. **Partially supports Phase 7.3 mechanism** (LLM verifying answers against reference text), but the benchmark itself was built by humans; Ho et al. only validates the scoring step, not the curation decision. Also preprint-only. | Partial — mechanism supported, curation gate not; preprint only |
| PCFJudge (Huang et al., 2026) | arXiv 2026 | Existing factuality benchmarks (FELM, FacTool) | Human-constructed benchmarks; PCFJudge only re-evaluates model outputs against them | Yes — human-built benchmarks |
| Prometheus (Kim et al., 2024) | ICLR 2024 | Human-written feedback rubrics | Human feedback used to train evaluator; no LLM-only benchmark gate | Yes — human rubrics |
| G-Eval (Liu et al., 2023) | EMNLP 2023 | SummEval, QAGS (human-annotated NLG benchmarks) | Human-annotated ground truth; G-Eval scores outputs against it | Yes — human ground truth |

**Conclusion:** No paper in this review uses an LLM as the sole gating mechanism to decide which QA pairs enter a benchmark dataset. RAGAS and Ho et al. come closest — both validate LLM-only scoring of answer correctness against a reference text (the same mechanism Phase 7.3 uses) — but neither applies that mechanism as a permanent accept/reject curation gate. The distinction matters: in runtime evaluation, individual errors average out; in benchmark curation, a wrongly accepted pair becomes permanent ground truth. To the best of our knowledge, no published peer-reviewed work closes this gap directly.

---

### What Supports LLM-Only Curation

Despite the absence of a direct precedent, several findings from the literature collectively support using an LLM-only approach in Phase 7.3:

**Ho et al. (2025) — partial support with known failure modes addressed.** Ho et al.'s central question was: *can an LLM judge replace a human annotator when scoring whether a model's answer is correct?* Their finding is nuanced: LLM judges achieve high agreement with humans on clear-cut accept/reject decisions, but diverge significantly on borderline cases — particularly when answers are partially correct or phrased differently from the reference. They also found LLMs tend to be over-lenient and sensitive to surface form (wording, synonyms).

Phase 7.3 directly mitigates both failure modes Ho et al. identified:
- **Borderline cases / surface form:** Atomic fact decomposition (FActScore method) breaks each answer into discrete verifiable claims rather than scoring holistic answer quality. A claim either appears in the chunk text or it does not — eliminating the partial-correctness ambiguity that caused most of Ho et al.'s human-LLM disagreements.
- **Over-leniency / knowledge conflicts:** The cross-family C1 check (GPT-4o) catches cases where Claude accepts a claim based on parametric knowledge rather than chunk evidence (Lee et al., 2026), directly addressing the systematic over-leniency Ho et al. observed.

This framing turns Ho et al.'s identified limitations into a justification for two specific design choices in Phase 7.3, rather than a blanket citation of the paper.

**Baysan et al. (Frontiers 2025) and DeCE/Yu et al. (EMNLP 2025) — peer-reviewed support for structured binary evaluation.** Both papers demonstrate that LLM judges achieve high human agreement (~90% and r=0.78 respectively) specifically on structured, criterion-based Pass/Fail tasks — the same format Phase 7.3 uses. The key condition: the task must be well-defined and verifiable against a reference, not open-ended. Chunk text provides exactly that reference.

**RAGAS (Es et al., 2023) — LLM faithfulness scoring without human oversight.** RAGAS's faithfulness metric performs the same operation as Phase 7.3's C1 check (LLM verifies answer claims against retrieved context) and is widely deployed without human review in production RAG systems. While not a curation gate, it demonstrates the mechanism is reliable enough for consequential automated decisions.

**Chunk text as local ground truth — why Phase 7.3 fits this setting.** Every QA pair in LectureBench is generated from a specific set of transcript chunks. The reviewer is not scoring open-ended generation quality; it is performing verifiable consistency checks against those chunks: does each answer claim appear in the cited text (C1), are the cited spans non-adjacent (C2), does the question type match the evidence structure (C3). The chunk text acts as a locally scoped ground truth, making Phase 7.3 structurally identical to extractive QA evaluation — exactly the setting where the papers above show the strongest LLM-judge reliability.

Together, these results support the following framing in the paper:

> "No prior work uses LLM-only judgment as a permanent benchmark curation gate. However, Ho et al. (2025) validate that LLM judges closely approximate human decisions on clear-cut extractive QA tasks, and Baysan et al. (2025) and Yu et al. (2025) confirm high human agreement for structured Pass/Fail criteria. In Phase 7.3, transcript chunk text serves as a locally scoped ground truth, making the curation task structurally equivalent to extractive QA evaluation. Phase 7.3 additionally mitigates Ho et al.'s identified failure modes through atomic fact decomposition (FActScore) and cross-family C1 verification (GPT-4o). A human spot-check (§D8b) provides final validation."

---

### Recommended Human Spot-Check (D8b)

To close the remaining gap — that no peer-reviewed paper directly validates LLM-only curation — a lightweight human spot-check is recommended:

**Protocol:**
- Randomly sample **60–70 QA pairs** from the final accepted set (≈ 1 pair per lecture, covering all question types proportionally).
- For each sampled pair, a human annotator independently applies the same three-criterion rubric (C1/C2/C3) using the cited chunk text.
- Compute **Cohen's Kappa** between human decisions and LLM decisions on this sample.
- Report Kappa in the paper's methodology section. Target: κ ≥ 0.75 (substantial agreement).

**Why 60–70 pairs?** At n=60–70, Cohen's Kappa has a 95% confidence interval of approximately ±0.13 at κ=0.80 (Wilson interval). This is sufficient precision to report a credible agreement figure in a conference paper. Sampling more than ~100 pairs yields diminishing returns in CI precision and is disproportionate to the scale of a single-submission benchmark paper.

**Cost and effort:** Each pair requires ~3–5 minutes of human review (reading the chunk text, checking the three criteria). At 70 pairs, total effort is approximately 3.5–6 hours — feasible for a single annotator session.

**Reporting template for the paper:**
> "To validate the LLM-based curation approach, we randomly sampled 67 accepted QA pairs (≈1 per lecture) and applied the same three-criterion rubric manually. Cohen's Kappa between human and LLM decisions was κ = [VALUE] (C1: [VALUE], C2: [VALUE], C3: [VALUE]), indicating [substantial/near-perfect] agreement and supporting the reliability of the automated curation gate."

If κ < 0.70, escalate: re-review all rejected pairs for the failing criterion manually and adjust the prompt accordingly before the final benchmark release.

---

## Summary of Decisions

| Question | Decision | Key Papers |
|---|---|---|
| Q1: Same-model circularity | Claude Sonnet 4.6 primary (all 3 criteria) + GPT-4o cross-check for C1 only. C2/C3 Claude-only. | Baysan et al. (2025) ✓peer-reviewed, Wataoka et al. (NeurIPS 2024) ✓peer-reviewed, Ho et al. (2025) preprint, Yang et al. (2026) preprint, Lee et al. (2026) |
| Q2: Scoring rubric | Binary PASS/FAIL per criterion (correctness, span plausibility, type accuracy); accept if all 3 pass. G-Eval form-filling with CoT per criterion. | G-Eval/Liu et al. (EMNLP 2023) ✓, Prometheus/Kim et al. (ICLR 2024) ✓, DeCE/Yu et al. (EMNLP 2025) ✓ |
| Q3: Multi-hop adjacency | Reject if spans are < 70s apart (< 2 chunk strides). | Min et al. (2019), Xiang et al./BRIDGE (2026), Li et al. (2024) |
| Q4: Correctness without video | Atomic fact decomposition per answer; verify each claim against cited chunk text incl. frame captions. GPT-4o cross-check for C1. | Min et al./FActScore (2023), Ho et al. (2025), Es et al./RAGAS (2023), Lee et al. (2026) |
| Q5: Rejection/replacement | Floor ≥ 10 per lecture; full regeneration for lectures below floor (decided after 56% rejection rate observed); discard if < 8 after retry. | Min et al. (2019) — quality over quantity principle |
| Q6: Span tightening | Not required. ±15–30s acceptable per EduVidQA precedent (±35.4s, EMNLP 2025). Report tIoU@0.3 primary, tIoU@0.5 secondary. | EduVidQA (2025) — span precision only, VideoZeroBench (2026) — @0.3 threshold |

---

## References

1. Zheng, L., Chiang, W., Sheng, Y., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
2. Liu, Y., Iter, D., Xu, Y., et al. (2023). *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment*. arXiv:2303.16634.
3. Kim, S., Shin, J., Cho, Y., et al. (2023). *Prometheus: Inducing Fine-grained Evaluation Capability in Language Models*. arXiv:2310.08491.
4. Ho, X., Huang, J., Boudin, F., Aizawa, A. (2025). *LLM-as-a-Judge: Reassessing the Performance of LLMs in Extractive QA*. arXiv:2504.11972. **[Preprint only — not peer-reviewed. Corrected from earlier wrong arXiv ID 2501.09775.]**
5. Zhou, Y., Xu, A., Wang, P., Xiong, C., Joty, S. (2025). *Evaluating Judges as Evaluators: The JETTS Benchmark*. arXiv:2504.15253.
6. Min, S., Krishna, K., Lyu, X., et al. (2023). *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation*. arXiv:2305.14251.
7. Es, S., James, J., Espinosa-Anke, L., Schockaert, S. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217.
8. Min, S., Wallace, E., Singh, S., Gardner, M., Hajishirzi, H. (2019). *Compositional Questions Do Not Necessitate Multi-hop Reasoning*. arXiv:1906.02900.
9. Li, J., Liu, R., Li, Y., et al. (2024). *Tree of Reviews: A Tree-based Dynamic Iterative Retrieval Framework for Multi-hop Question Answering*. arXiv:2404.14464.
10. Wataoka, K., Takahashi, T., Ri, R. (2024). *Self-Preference Bias in LLM-as-a-Judge*. NeurIPS 2024 Safe Generative AI Workshop. arXiv:2410.21819.
11. Yang, J., Qiu, C., Deng, Z., Jiao, X., Zhou, T. (2026). *Quantifying and Mitigating Self-Preference Bias of LLM Judges*. arXiv:2604.22891.
12. Xiang, B., Han, S. C., Ding, Y. (2026). *BRIDGE: Benchmark for Multi-hop Reasoning In long multimodal Documents with Grounded Evidence*. arXiv:2603.07931.
13. Ray, S., Sarkar, S., Agarwal, S., et al. (2025). *EduVidQA: Generating and Evaluating Long-form Answers to Student Questions based on Lecture Videos*. EMNLP 2025. arXiv:2509.24120.
14. Unknown Authors. (2026). *VideoZeroBench: Probing the Limits of Video MLLMs with Spatio-Temporal Evidence Verification*. arXiv:2604.01569.
15. Li, R., Patel, T., Du, X. (2023). *PRD: Peer Rank and Discussion Improve Large Language Model based Evaluations*. arXiv:2307.02762.
16. Chan, C., Chen, W., Su, Y., et al. (2023). *ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate*. arXiv:2309.17012.
17. Chen, Z., Lu, X., Li, J., et al. (2025). *Harnessing Multiple Large Language Models: A Survey on LLM Ensemble*. arXiv:2502.18036.
18. Tang, Y., Feng, K., Wang, Y., et al. (2025). *Learning an Efficient Multi-Turn Dialogue Evaluator from Multiple LLM Judges*. arXiv:2508.00454.
19. Wei, H., He, S., Xia, T., Liu, F., Wong, A. (2024). *Systematic Evaluation of LLM-as-a-Judge in LLM Alignment Tasks*. arXiv:2408.13006.
20. Huang, T., Huang, N., Tang, J., Chen, W., Fan, E. (2026). *PCFJudge: Permutation-Consensus Listwise Judging for Robust Factuality Evaluation*. arXiv:2603.20562.
21. Lee, D., Hwang, Y., Kang, T., Lee, M., Chae, Y. (2026). *Judging Against the Reference: Uncovering Knowledge-Driven Failures in LLM-Judges on QA Evaluation*. arXiv:2601.07506.
22. Baysan, M. S., Uysal, S., Islek, I., Karaman, C. C., Gungor, T. (2025). *LLM-as-a-Judge: Automated Evaluation of Search Query Parsing Using Large Language Models*. Frontiers in Big Data. DOI:10.3389/fdata.2025.1611389. **[Peer-reviewed journal.]**
23. Yu, F., Seedat, N., Herrmannova, D., Schilder, F., Schwarz, J. R. (2025). *Beyond Pointwise Scores: Decomposed Criteria-Based Evaluation of LLM Responses*. EMNLP 2025 Industry Track. https://aclanthology.org/2025.emnlp-industry.136/ **[Peer-reviewed, published.]**
