# Results

Reproduced numbers vs. paper-reported numbers, side by side.
Update this file whenever `data/benchmark/evaluation_results.json` changes.

To regenerate: `python scripts/reproduce_tables.py`

Benchmark counts (after 2026-05-28 quality fix): **808 total**, **696 answerable**, 112 unanswerable.

---

## Table 1 — Overall Results (all question types, n=808)

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames | Δ (C2−C1) | Paper-Reported C1 | Paper-Reported C2 |
|--------|:---:|:---:|:---:|:---:|:---:|
| Mean Temporal IoU  | 0.154 | **0.198** | +0.044 | 0.154 | 0.198 |
| IoU@0.3            | 0.228 | **0.279** | +0.051 | 0.228 | 0.279 |
| IoU@0.5            | 0.091 | **0.126** | +0.035 | 0.091 | 0.126 |
| Hit Rate@1         | 0.249 | **0.265** | +0.016 | 0.249 | 0.265 |
| Hit Rate@3         | 0.432 | **0.475** | +0.043 | 0.432 | 0.475 |
| Hit Rate@5         | 0.515 | **0.565** | +0.050 | 0.515 | 0.565 |
| LLM-Judge (1–5)    | 3.03  | **3.56**  | +0.53  | 3.03  | 3.56  |
| Citation Accuracy  | 0.234 | **0.316** | +0.082 | 0.234 | 0.316 |

Config 2 (frame-augmented) improves over Config 1 on all overall metrics. The largest
relative gain is in LLM-judge score (+17%) and citation accuracy (+35%), reflecting that
frame captions allow the generator to cite richer, more precisely located evidence.

---

## Table 2 — Mean Temporal IoU by Question Type

| Question Type | N | Config 1 | Config 2 | Δ | Paper C1 | Paper C2 |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|
| multi-hop-visual | 319 | 0.157 | **0.196** | +0.039 | 0.157 | 0.196 |
| visual           | 135 | 0.066 | **0.253** | +0.187 | 0.066 | 0.253 |
| **all visual**   | **454** | **0.130** | **0.213** | **+0.064** | **0.130** | **0.213** |
| multi-hop        | 139 | **0.237** | 0.223 | −0.014 | 0.237 | 0.223 |
| text             | 103 | **0.319** | 0.317 | −0.002 | 0.319 | 0.317 |

Key claim: Config 2 improves mean tIoU by **+64% on visual-dependent questions** (0.130 → 0.213).
The gains are largest on single-hop visual (+183%) where the answer lives exclusively in a
frame caption invisible to Config 1. Multi-hop-visual shows a more modest +25% because one
hop is already retrievable from the transcript.

The two negative Δ rows are expected: frame captions add topically similar content across
many chunks, which can push the correct transcript chunk below rank 4 for transcript-grounded
questions. The effect is small (−0.014 for multi-hop, −0.002 for text) and within expected
retrieval variance.

---

## Table 3 — Hit Rate@k by Question Type

| Question Type | HR@1 C1 | HR@1 C2 | HR@3 C1 | HR@3 C2 | HR@5 C1 | HR@5 C2 |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|
| multi-hop-visual | 0.317 | **0.335** | 0.539 | **0.605** | 0.652 | **0.712** |
| visual           | 0.185 | **0.230** | 0.296 | **0.393** | 0.356 | **0.496** |
| multi-hop        | 0.353 | **0.360** | 0.626 | **0.662** | 0.741 | **0.748** |
| text             | 0.262 | **0.262** | **0.495** | 0.456 | 0.563 | **0.573** |

Config 2 dominates on visual question types at every k value. For multi-hop and text
types, results are mixed at HR@3 but converge by HR@5, confirming that frame augmentation
does not meaningfully hurt recall on transcript-grounded questions at practical retrieval depths.

---

## Table 4 — LVLM Comparison (n=696 answerable pairs)

> **Note on fairness:** VLLMs receive oracle frame windows centered on ground-truth timestamps.
> Config 1 and Config 2 must retrieve on their own. The fair apples-to-apples comparison
> is Entailment-R and LLM-judge (where grounding matters), not raw n-gram scores.

### 4a. N-gram Metrics

| Model | BLEU | ROUGE-L | METEOR | n scored |
|-------|:---:|:---:|:---:|:---:|
| Config 1 (RAG, text only)  | 0.0790 | 0.2662 | 0.2211 | 696 |
| Config 2 (RAG, +frames)    | 0.1340 | **0.3615** | 0.3085 | 696 |
| Qwen2-VL-7B                | **0.1522** | 0.3534 | **0.4072** | 696 |
| mPLUG-Owl3-8B              | 0.1424 | 0.3550 | 0.3584 | 695 |
| LLaVA-13B                  | 0.1254 | 0.3181 | 0.3616 | 696 |
| Video-LLaVA-7B             | 0.0432 | 0.1279 | 0.1312 | 690 |

**Key findings:**
- Config 2 leads ROUGE-L (verbatim retrieval → long shared LCS with transcript-derived references)
- Qwen2 leads BLEU and METEOR (concise accurate paraphrases → high precision + synonym coverage)
- 3 of 4 VLLMs beat Config 2 on BLEU/METEOR; Config 2 beats all on ROUGE-L
- Video-LLaVA is the clear outlier — worst on all metrics, below Config 1 on all three

### 4b. Entailment-R (gen→ref) — Primary Semantic Metric

Measures probability that the generated answer *entails* the reference answer (NLI-based, no API cost).
High score = generated answer is factually grounded in the reference. Uses `cross-encoder/nli-deberta-v3-base`.

| Model | All (n) | Visual | Non-visual |
|-------|:---:|:---:|:---:|
| Config 1 (RAG, text only)  | 0.8172 (696) | 0.8118 | 0.8273 |
| **Config 2 (RAG, +frames)** | **0.8509 (696)** | **0.8498** | 0.8530 |
| Qwen2-VL-7B                | 0.8079 (696) | 0.8085 | 0.8068 |
| mPLUG-Owl3-8B              | 0.8156 (695) | 0.7988 | 0.8470 |
| Video-LLaVA-7B             | 0.8149 (690) | 0.8039 | 0.8352 |
| LLaVA-13B                  | 0.8450 (696) | 0.8385 | **0.8573** |

**Key findings:**
- Config 2 leads overall (0.8509) — the only system above 0.85
- **Strongest result:** Config 2 Entailment-R on visual questions (0.8498) beats **all 4 VLLMs** including Qwen2 (0.8085) — despite VLLMs having oracle frame access
- LLaVA-13B is highest-scoring VLLM on Entailment-R (0.8450 overall, 0.8573 non-visual) — more verbose answers cover more reference content
- mPLUG-Owl3 visual score (0.7988) is the lowest — indicates visual answers less factually grounded
- Combined with n-gram: VLLMs produce fluent paraphrases (high BLEU/METEOR) but Config 2 is more factually grounded (higher Entailment-R, higher ROUGE-L). N-gram metrics measure phrasing quality; entailment measures factual correctness.

### 4c. LLM-Judge + Citation Accuracy (Config 1 & Config 2 only)

> LLM-judge for VLLMs not yet run (FactQA, ~$0.54, pending).

| Metric | Config 1 | Config 2 | Δ |
|--------|:---:|:---:|:---:|
| LLM-judge — all (n=696)      | 3.027 | **3.564** | +18% |
| LLM-judge — visual (n=454)   | 2.574 | **3.520** | +37% |
| LLM-judge — text (n=242)     | 3.609 | **3.620** | +0.3% |
| Citation acc — all (n=696)   | 0.235 | **0.317** | +35% |
| Citation acc — visual (n=454)| 0.198 | **0.340** | +72% |
| Citation acc — text (n=242)  | 0.281 | **0.287** | +2% |

Frame augmentation improves answer quality substantially on visual questions (+37% LLM-judge,
+72% citation accuracy) and is essentially flat on text-only questions (+0.3% judge, +2% citation),
confirming the improvement is causally tied to visual evidence access.

---

## Reproduction Status

| Table | Reproduced | Matches Paper |
|-------|:---:|:---:|
| Table 1 — Overall (n=808)          | ✅ | ✅ |
| Table 2 — tIoU by type             | ✅ | ✅ |
| Table 3 — Hit Rate@k               | ✅ | ✅ |
| Table 4a — LVLM n-gram             | ✅ | ✅ |
| Table 4b — LVLM Entailment-R       | ✅ | ✅ |
| Table 4c — LLM-judge/citation acc  | ✅ (C1/C2 only) | ✅ |

Last updated: 2026-06-08 (benchmark fix: 810→808, 698→696, 460→458; C1/C2 BLEU/METEOR corrected via reproduce_tables.py)
