# Results

Reproduced numbers vs. paper-reported numbers, side by side.
Update this file whenever `data/benchmark/evaluation_results.json` changes.

To regenerate: `python scripts/reproduce_tables.py`

---

## Table 1 — Overall Results (all question types)

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames | Δ (C2−C1) | Paper-Reported C1 | Paper-Reported C2 |
|--------|:---:|:---:|:---:|:---:|:---:|
| Mean Temporal IoU | TBD | TBD | TBD | TBD | TBD |
| IoU@0.3 | TBD | TBD | TBD | TBD | TBD |
| IoU@0.5 | TBD | TBD | TBD | TBD | TBD |
| Hit Rate@1 | TBD | TBD | TBD | TBD | TBD |
| Hit Rate@3 | TBD | TBD | TBD | TBD | TBD |
| Hit Rate@5 | TBD | TBD | TBD | TBD | TBD |
| LLM-Judge Score (1–5) | TBD | TBD | TBD | TBD | TBD |
| Citation Accuracy | TBD | TBD | TBD | TBD | TBD |

---

## Table 2 — Mean Temporal IoU by Question Type

| Question Type | N | Config 1 | Config 2 | Δ | Paper C1 | Paper C2 |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|
| multi-hop-visual | TBD | TBD | TBD | TBD | TBD | TBD |
| visual | TBD | TBD | TBD | TBD | TBD | TBD |
| multi-hop | TBD | TBD | TBD | TBD | TBD | TBD |
| text | TBD | TBD | TBD | TBD | TBD | TBD |
| **all visual** | TBD | TBD | TBD | TBD | TBD | TBD |

Key claim: Config 2 must meet or beat Config 1 on visual-dependent questions
(multi-hop-visual + visual). The Δ column for those rows should be ≥ 0.

---

## Table 3 — Hit Rate@k by Question Type

| Question Type | HR@1 C1 | HR@1 C2 | HR@3 C1 | HR@3 C2 | HR@5 C1 | HR@5 C2 |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|
| multi-hop-visual | TBD | TBD | TBD | TBD | TBD | TBD |
| visual | TBD | TBD | TBD | TBD | TBD | TBD |
| multi-hop | TBD | TBD | TBD | TBD | TBD | TBD |
| text | TBD | TBD | TBD | TBD | TBD | TBD |

---

## Reproduction Status

| Table | Reproduced | Matches Paper |
|-------|:---:|:---:|
| Table 1 — Overall | ⏳ | ⏳ |
| Table 2 — By type | ⏳ | ⏳ |
| Table 3 — Hit Rate@k | ⏳ | ⏳ |

Last updated: 2026-05-14 (placeholder — no evaluation run yet)
