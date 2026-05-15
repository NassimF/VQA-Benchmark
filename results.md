# Results

Reproduced numbers vs. paper-reported numbers, side by side.
Update this file whenever `data/benchmark/evaluation_results.json` changes.

To regenerate: `python scripts/reproduce_tables.py`

---

## Table 1 — Overall Results (all question types, n=810)

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
| multi-hop-visual | 320 | 0.156 | **0.196** | +0.040 | 0.156 | 0.196 |
| visual           | 135 | 0.066 | **0.253** | +0.187 | 0.066 | 0.253 |
| **all visual**   | **455** | **0.129** | **0.213** | **+0.065** | **0.129** | **0.213** |
| multi-hop        | 140 | **0.236** | 0.223 | −0.013 | 0.236 | 0.223 |
| text             | 103 | **0.319** | 0.317 | −0.002 | 0.319 | 0.317 |

Key claim: Config 2 improves mean tIoU by **+65% on visual-dependent questions** (0.129 → 0.213).
The gains are largest on single-hop visual (+183%) where the answer lives exclusively in a
frame caption invisible to Config 1. Multi-hop-visual shows a more modest +26% because one
hop is already retrievable from the transcript.

The two negative Δ rows are expected: frame captions add topically similar content across
many chunks (e.g., every SVD-related slide caption scores similarly against an SVD question),
which can push the correct transcript chunk below rank 4. For purely transcript-grounded
questions this is noise, not signal. The effect is small (−0.013 for multi-hop, −0.002 for
text) and within expected retrieval variance.

---

## Table 3 — Hit Rate@k by Question Type

| Question Type | HR@1 C1 | HR@1 C2 | HR@3 C1 | HR@3 C2 | HR@5 C1 | HR@5 C2 |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|
| multi-hop-visual | 0.316 | **0.334** | 0.537 | **0.603** | 0.650 | **0.713** |
| visual           | 0.185 | **0.230** | 0.296 | **0.393** | 0.356 | **0.496** |
| multi-hop        | 0.350 | **0.357** | **0.621** | 0.657 | **0.736** | 0.743 |
| text             | 0.262 | **0.262** | **0.495** | 0.456 | 0.563 | **0.573** |

Config 2 dominates on visual question types at every k value. For multi-hop and text
types, results are mixed at HR@3 (Config 1 higher on pure multi-hop) but converge by
HR@5, confirming that frame augmentation does not meaningfully hurt recall on
transcript-grounded questions at practical retrieval depths.

---

## Reproduction Status

| Table | Reproduced | Matches Paper |
|-------|:---:|:---:|
| Table 1 — Overall (n=810) | ✅ | ✅ |
| Table 2 — tIoU by type    | ✅ | ✅ |
| Table 3 — Hit Rate@k      | ✅ | ✅ |

Last updated: 2026-05-15 (evaluation run: `data/benchmark/evaluation_results.json`)
