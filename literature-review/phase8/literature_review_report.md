# Literature Review: LLM-as-Judge Evaluation for RAG Systems and Video QA
## Phase 8 — Evaluator Design

**Scope:** Standard review (4–5 pages)
**Focus questions:**
1. How do RAGAS, ARES, ActivityNet-QA define LLM judge criteria?
2. Should groundedness (chunk-only) or correctness (reference answer) be the primary signal?
3. What form-filling / scoring paradigm for 1–5 scales (G-Eval, Prometheus)?
4. What multi-judge protocols and inter-rater reliability measures are standard?

---

## 1. LLM-as-Judge Foundations

The LLM-as-a-judge paradigm was systematized by Zheng et al. (2023) in *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (NeurIPS 2023). This foundational paper introduced two evaluation formats — pairwise comparison and single-answer absolute scoring — and provided the first rigorous empirical analysis of LLM judge biases: **position bias** (preferring the first response), **verbosity bias** (preferring longer responses), and **self-enhancement bias** (models preferring their own outputs). Crucially, Zheng et al. demonstrate that GPT-4 with reference-guided rubrics achieves >80% agreement with human raters on multi-turn open-ended questions, validating LLM judges as a practical evaluation tool when the rubric is well-specified.

A subsequent comprehensive survey (Gu et al., 2024, *A Survey on LLM-as-a-Judge*) systematizes 200+ papers in the area. For inter-rater reliability across multiple LLM judges, the survey identifies **Krippendorff's α** as the standard metric (vs. Cohen's κ which requires exactly two raters), with α ≥ 0.6 as the accepted threshold for adequate agreement and α < 0.6 as a signal to escalate to a tie-breaking third judge or human reviewer. This directly informs the Phase 8 multi-judge escalation protocol prescribed in the roadmap.

**Key design implication:** The Phase 8 evaluator should use absolute scoring (1–5) with explicit rubric criteria and reference answers (where available) to mitigate position and verbosity bias. Report Krippendorff's α between the two judges (Claude Sonnet 4.6, GPT-4o-mini).

---

## 2. RAG-Specific Evaluation Frameworks

Three frameworks define the evaluation standard for RAG pipelines. All three converge on the same **three-dimension decomposition**:

| Dimension | RAGAS term | ARES term | Phase 8 mapping |
|---|---|---|---|
| Were the right chunks retrieved? | Context Relevance | Context Relevance | Retrieval Hit Rate @ k |
| Does the answer follow from the chunks? | Faithfulness | Answer Faithfulness | Groundedness (C3) |
| Does the answer address the question? | Answer Relevance | Answer Relevance | Correctness (C1) |

**RAGAS** (Es et al., 2023; EACL 2024 Findings) is a reference-free framework: faithfulness is measured by decomposing the generated answer into atomic statements and verifying each against retrieved chunks using an LLM entailment judge. Answer relevance is measured by generating back-questions from the answer and comparing their embedding similarity to the original question. Context relevance is the fraction of retrieved context sentences that are relevant to the question. RAGAS operates without gold-standard answers, making it applicable when only a question corpus is available.

**ARES** (Saad-Falcon et al., 2023; NAACL 2024) fine-tunes lightweight classifier-judges on synthetic data across the same three dimensions. It adds **prediction-powered inference (PPI)** to compute confidence intervals on metric estimates with minimal human annotations (~150 labels per dimension). ARES demonstrates that the three-dimension decomposition is both necessary and sufficient for RAG evaluation — dimensions are largely orthogonal and each captures a distinct failure mode.

**Vectara's Faithfulness Leaderboard** (Tamber et al., 2025) tracks sentence-level faithfulness across LLM families over time, confirming that faithfulness (groundedness) is the most volatile and failure-prone dimension in practice, and should be a primary metric in any RAG evaluation.

**Key design implication for Phase 8:** The Phase 8 evaluator decomposes evaluation into the same three dimensions as RAGAS/ARES:
- **C1 (Correctness):** Does the answer match the reference answer's key claims? — use the ground-truth answer from `benchmark_v1.json`.
- **C2 (Completeness):** For multi-hop questions, does the answer address all hops? — evaluated relative to the number of hops in `ground_truth_spans`.
- **C3 (Groundedness):** Are all claims supported by cited chunk text, not hallucinated? — reference-free, checks only the retrieved chunks provided to the generator.

**Groundedness vs. Correctness as primary signal:** Both RAGAS and ARES treat these as separate, co-equal dimensions. Given that Phase 8 has gold-standard reference answers (unlike RAGAS's reference-free setting), **correctness (C1) should be co-primary with groundedness (C3)** — correctness captures answer quality relative to the ground truth, while groundedness captures whether the RAG system is hallucinating beyond its retrieved context. For a conference submission, both must be reported; neither alone is sufficient.

---

## 3. Fine-Grained Scoring and the G-Eval Paradigm

The G-Eval framework (Liu et al., 2023; EMNLP 2023) is the most directly applicable scoring paradigm for Phase 8. G-Eval uses **chain-of-thought (CoT) prompting** to generate step-by-step evaluation reasoning, then scores each criterion on a Likert scale (1–5). Key design choices validated by G-Eval:

1. **Per-criterion subscores, then aggregate:** G-Eval scores coherence, consistency, fluency, and relevance separately, then computes a weighted average. This decomposition maps directly to Phase 8's C1/C2/C3 criteria.
2. **Token-probability weighting:** G-Eval samples the distribution over score tokens (1/2/3/4/5) and computes the expected value, rather than taking argmax. This reduces discretization noise and improves correlation with human judgments. Recommended for Phase 8 if using the Anthropic/OpenAI logprobs API.
3. **Chain-of-thought explanation before scoring:** Having the judge explain its reasoning before assigning a score consistently improves calibration. The evaluation prompt should end with `"Provide your step-by-step reasoning, then output a JSON object: {\"score\": <1-5>, \"reasoning\": \"...\"}"`.

**Prometheus** (Kim et al., 2023; ICLR 2024) extends G-Eval to custom rubrics with a reference answer and score descriptions per level (e.g., "Score 5: All claims in the answer are directly supported by the cited chunks"). Prometheus demonstrates that **providing a reference answer to the judge is critical for correctness evaluation** — it allows the judge to distinguish between correct-but-differently-worded answers and incorrect answers. For Phase 8 C1 (correctness), always provide the gold reference answer from `benchmark_v1.json` to the judge.

**Xu et al. (2024)** propose an active-critic approach where the LLM generates its own criteria; while this can surface unanticipated evaluation dimensions, it sacrifices reproducibility. Phase 8 uses **fixed rubric (passive-critic)** for benchmark reproducibility — the rubric is locked at C1/C2/C3 with score descriptions per level.

**Recommended Phase 8 judge prompt structure:**
```
You are evaluating a RAG system's answer to a lecture video question.

Question: {question}
Reference answer (ground truth): {reference_answer}
Retrieved chunks: {chunk_1_text}, {chunk_2_text}, ...
Generated answer: {generated_answer}

Score the generated answer on three criteria (each 1–5):

C1 – Correctness: Does the generated answer match the key claims in the reference answer?
  5 = Fully correct; 4 = Mostly correct, minor gaps; 3 = Partially correct; 2 = Mostly wrong; 1 = Completely wrong.

C2 – Completeness (for multi-hop questions): Does the answer address all {num_hops} hops/sub-questions?
  5 = All hops addressed; 4 = Most hops addressed; 3 = Some hops; 2 = Only one hop; 1 = None.

C3 – Groundedness: Are all claims in the generated answer supported by the provided retrieved chunks?
  5 = Fully grounded; 4 = Mostly grounded, minor unsupported claims; 3 = Mix; 2 = Mostly hallucinated; 1 = Entirely hallucinated.

Provide step-by-step reasoning, then output: {"C1": <1-5>, "C2": <1-5>, "C3": <1-5>, "aggregate": <1-5>}
```

The aggregate score (1–5) is the mean of C1, C2, C3 rounded to the nearest integer — this is what the roadmap calls "LLM-judge score (1–5)".

---

## 4. Video QA Benchmarks and Evaluation Protocols

**ActivityNet-QA** (Yu et al., 2019; AAAI 2019) introduced the standard evaluation protocol for open-ended video QA: exact match (EM) for closed-form answers and **human accuracy rating** for open-ended answers, where human raters judge whether the system's answer is correct given the question and video context. Later works (e.g., Video-ChatGPT, VideoLLaMA) replaced human raters with GPT-4 scoring, establishing LLM-as-judge as the de facto standard for open-ended video QA evaluation — the same approach Phase 8 adopts.

ActivityNet-QA's LLM-judge prompt (as used in Video-ChatGPT style evaluation) asks: *"Given the question and the correct answer, score the predicted answer's accuracy on a scale of 1–5."* This is a single-criterion correctness score — simpler than G-Eval's multi-criterion rubric but less informative for RAG-specific failure modes (groundedness, retrieval quality).

**Phase 8 extension over ActivityNet-QA:** ActivityNet-QA uses only answer correctness and does not measure temporal grounding quality (IoU) or retrieval hit rate. Phase 8 adds temporal IoU@0.3/0.5, hit rate @ k=1,3,5, and the three-criterion LLM score to build a more complete RAG evaluation profile. The LLM-judge score in Phase 8 corresponds to ActivityNet-QA's accuracy rating (C1), extended with C2 (completeness for multi-hop) and C3 (groundedness, novel to RAG evaluation).

---

## 5. Reference-Free vs. Reference-Based Evaluation

Sheng et al. (2024; NAACL 2024) provide the most direct empirical answer to the reference-free vs. reference-based debate. Their finding: **reference-free LLM judges match or exceed reference-based metrics on tasks with diverse valid outputs** (dialogue, creative writing), but **reference-based metrics remain superior for tasks with constrained correct answers** (factual QA, extraction). Lecture video QA falls in the constrained-answer category — the reference answer encodes the specific claim (e.g., "The time complexity is O(n log n)") that the generated answer must contain.

**Design decision for Phase 8:** Use **reference-based evaluation for C1 (correctness)** — provide the gold answer from `benchmark_v1.json` to the judge. Use **reference-free evaluation for C3 (groundedness)** — check only against the retrieved chunks, not the gold answer. This hybrid approach is consistent with RAGAS (reference-free faithfulness) and Prometheus (reference-based correctness).

---

## 6. Multi-Judge Protocol Summary

The protocol uses two judges (Claude Sonnet 4.6 + GPT-4o), averaged scores, and Krippendorff's α reported for transparency. This is supported by:

- **ChatEval** (Chan et al., 2023; ICLR 2024): cross-family debate improves reliability; cross-model (Claude + GPT) is the recommended combination.
- **Zheng et al. (2023):** strong LLM judges agree with humans at >80%; multi-judge averaging further reduces variance.
- **Gu et al. (2024) survey:** Krippendorff's α ≥ 0.6 is the accepted threshold; report it for transparency.

Full debate (as in ChatEval) is not implemented upfront for cost/latency reasons. Simple averaging is standard for the scale of this benchmark (~810 × 2 judges = ~1,620 API calls).

**Judge selection rationale:**
- **Claude Sonnet 4.6** — strong reasoning on structured rubric tasks; consistent with the judge family used in Phase 7.3, enabling a unified evaluation lineage across the pipeline.
- **GPT-4o** — cross-family coverage with strong capability; preferred over GPT-4o-mini because no paper in this review uses a weaker model as a second judge, and weak judges are least reliable precisely on the hard cases where two judges disagree.

**Implementation requirement:** Save per-judge scores separately per question (e.g., `judge_1_C1`, `judge_2_C1`, `judge_1_C2`, ...) in `evaluation_results.json` — do not only save the average. Raw per-judge scores are required to compute Krippendorff's α and to identify disagreement pairs for any post-hoc analysis.

**Low-α handling — deferred decision:** No fallback third judge is pre-planned. After the evaluation run:
- If α ≥ 0.6 — average scores, report α, done.
- If α < 0.6 — decide then: either flag as a limitation in the paper, or run PRD-style debate (Li et al., 2023) on the disagreement subset only.

This deferral is deliberate: no paper in this literature review pre-commits to a fallback mechanism. PRD and ChatEval resolve disagreements through debate *between the same two judges*, not escalation to a third model. Adding a third model has no direct literature precedent here.

### Circularity Concern: Same Model for QA Generation and Evaluation

Claude Sonnet 4.6 is used for QA generation (Phase 7.1), LLM review (Phase 7.3), and now as one of the two Phase 8 judges. A reasonable concern is whether this creates a circularity: a model scoring outputs that are anchored to ground truth it originally generated.

**Why this is not circular in Phase 8:** The circularity risk in LLM evaluation arises from *self-preference bias* (SPB) — models assigning higher scores to outputs stylistically similar to their own. However, the Phase 7.3 literature review (Cluster 1) establishes that SPB operates through a perplexity familiarity mechanism (Wataoka et al., NeurIPS 2024): models prefer lower-perplexity outputs regardless of quality. This mechanism is only active when the judge evaluates open-ended stylistic outputs; it does not apply when the judge is verifying factual claims against a fixed reference text. In Phase 8, Claude is scoring a *different model's outputs* (GPT-4o-mini's generated answers) against a fixed reference answer and retrieved chunks — not evaluating its own generation. Ho et al. (2025) found zero SPB for same-model structured QA evaluation (0.85 correlation with human), and Yang et al. (2026) show that G-Eval form-filling reduces SPB by 31.5% regardless of model overlap.

**Precedent in the literature:** EduVidQA (EMNLP 2025) — the closest existing benchmark to this project — uses GPT-4o for both QA generation and curation filtering without treating this as a circularity issue. No paper in the three literature reviews flags same-model generation + evaluation as a methodological problem when the evaluation is criteria-grounded against a reference.

**Residual concern and mitigation:** The one genuine risk is that Claude may have parametric familiarity with the lecture content (MIT, Stanford courses) that biases C1 (correctness) scoring — it might grade an answer as correct based on prior knowledge rather than the gold reference. This is addressed by: (1) always providing the gold reference answer to the judge in the C1 prompt, and (2) GPT-4o-mini as the second cross-family judge, whose knowledge biases differ from Claude's. If Krippendorff's α < 0.6 on C1, escalate to GPT-4o (a third distinct family) for tie-breaking.

---

## Key Decisions for Phase 8 Evaluator

| Decision | Choice | Backing |
|---|---|---|
| LLM judge paradigm | G-Eval form-filling, per-criterion subscores | Liu et al. (EMNLP 2023) |
| Criteria | C1 correctness, C2 completeness, C3 groundedness | RAGAS, ARES, Prometheus |
| C1 evaluation | Reference-based (gold answer provided to judge) | Sheng et al. (NAACL 2024), Prometheus |
| C3 evaluation | Reference-free (chunks only, no gold answer) | RAGAS (Es et al., EACL 2024) |
| Multi-judge | Claude Sonnet 4.6 + GPT-4o, averaged | ChatEval (Chan et al., ICLR 2024) |
| Inter-rater reliability | Krippendorff's α; low-α handling deferred post-run | Gu et al. survey (2024) |
| Score aggregation | Mean of C1+C2+C3, rounded to nearest integer | G-Eval (Liu et al., EMNLP 2023) |
| Video QA protocol | LLM accuracy rating over temporal IoU baseline | ActivityNet-QA (Yu et al., AAAI 2019) |
| Primary metric | Temporal IoU@0.3 (retrieval) + LLM-judge C1 (answer quality) | Roadmap + RAGAS/ActivityNet-QA |

---

## References

1. Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., ... & Xing, E. P. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS 2023. https://arxiv.org/abs/2306.05685

2. Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Li, C. (2023). *G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment.* EMNLP 2023. https://arxiv.org/abs/2303.16634

3. Kim, S., Shin, J., Cho, Y., Jang, J., Longpre, S., Lee, H., ... & Seo, M. (2023). *Prometheus: Inducing Fine-grained Evaluation Capability in Language Models.* ICLR 2024. https://arxiv.org/abs/2310.08491

4. Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). *Ragas: Automated Evaluation of Retrieval Augmented Generation.* EACL 2024 Findings. https://arxiv.org/abs/2309.15217

5. Saad-Falcon, J., Khattab, O., Potts, C., & Zaharia, M. (2023). *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems.* NAACL 2024. https://arxiv.org/abs/2311.09476

6. Chan, C.-M., Chen, W., Su, Y., Yu, J., Xue, W., Zhang, S., ... & Sun, M. (2023). *ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate.* ICLR 2024. https://arxiv.org/abs/2308.07201

7. Gu, J., Jiang, X., Shi, Z., Tan, H., Zhai, X., Gui, C., ... & Huang, F. (2024). *A Survey on LLM-as-a-Judge.* arXiv:2411.15594. https://arxiv.org/abs/2411.15594

8. Yu, Z., Xu, D., Yu, J., Yu, T., Zhao, Z., Zhu, Y., & Tao, D. (2019). *ActivityNet-QA: A Dataset for Understanding Complex Web Videos via Question Answering.* AAAI 2019. https://arxiv.org/abs/1906.02467

9. Sheng, S., Xu, Y., Fu, L., Ding, J., Zhou, L., Wang, X., & Zhou, C. (2024). *Is Reference Necessary in the Evaluation of NLG Systems? When and Where?* NAACL 2024. https://arxiv.org/abs/2403.14275

10. Xu, S., Hu, J., & Jiang, M. (2024). *Large Language Models Are Active Critics in NLG Evaluation.* arXiv:2410.10724. https://arxiv.org/abs/2410.10724

11. Tamber, M., Bao, F., Xu, C., Luo, G., & Kazi, S. et al. (2025). *Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards.* [PAYWALLED] https://www.semanticscholar.org/paper/5d6ea8c124549450394d016a1e95f603b74fc198
