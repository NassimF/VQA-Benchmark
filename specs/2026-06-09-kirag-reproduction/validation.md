# Validation: KiRAG Reproduction

## Automated Checks

### Paper result tolerance (Tables 1–3)
All reproduced numbers must be within ±2% absolute of the values reported in the KiRAG paper.

| Table | Metric | Datasets |
|---|---|---|
| Table 1 | R@3, R@5 | HotPotQA, 2WikiMultiHopQA, MuSiQue |
| Table 2 | EM, F1 | HotPotQA, 2WikiMultiHopQA, MuSiQue |
| Table 3 | R@3, R@5, EM, F1 | Bamboogle, WebQA, NQ |

Run `python experiments/kirag/reproduce_kirag_tables.py` — must print PASS for every metric within tolerance, FAIL otherwise.

### VQA benchmark evaluation
```bash
python experiments/kirag/vqa_benchmark/evaluate.py \
    --results experiments/kirag/vqa_benchmark/results/kirag_vqa_results.json \
    --benchmark data/benchmark/benchmark_v1.json
```
Must complete without errors and produce a results summary covering:
- R@3, R@5 (retrieval)
- EM, F1 (QA)
- Temporal IoU@0.3, IoU@0.5
- Hit Rate@1, @3, @5

### .gitignore check
```bash
git status experiments/kirag/
```
Large directories (`data/`, `checkpoints/`, `indices/`) must not appear as untracked files.

---

## Output Artifacts

| Artifact | Location | Description |
|---|---|---|
| Table 1 results | `experiments/kirag/original/results/table1_retrieval.json` | R@3, R@5 per dataset |
| Table 2 results | `experiments/kirag/original/results/table2_qa.json` | EM, F1 per dataset |
| Table 3 results | `experiments/kirag/original/results/table3_generalization.json` | Unseen datasets |
| VQA results | `experiments/kirag/vqa_benchmark/results/kirag_vqa_results.json` | Per-question results with chunk_id and temporal spans |
| Reproduction script | `experiments/kirag/reproduce_kirag_tables.py` | Prints reproduced vs. paper side-by-side |
| Updated results tracker | `results.md` | KiRAG column added alongside Config 1 and Config 2 |

---

## Manual Checks

- [ ] Spot-check 5 multi-hop answers from HotPotQA — confirm KiRAG retrieved both required paragraphs
- [ ] Spot-check 5 multi-hop answers from VQA benchmark — confirm retrieved chunks map to correct `[video_id @ mm:ss to mm:ss]` citations
- [ ] Confirm no data leakage: KiRAG indices built from corpus only, not from QA pair answers
- [ ] Confirm `reproduce_kirag_tables.py` runs from a clean environment (no cached results)

---

## Merge Criteria

All of the following must be true before merging `feature/kirag-reproduction` into `main`:

1. `reproduce_kirag_tables.py` prints PASS for all Tables 1–3 metrics (within ±2% tolerance)
2. VQA benchmark evaluation completes without errors and results JSON is committed
3. `results.md` updated with KiRAG column
4. All large files (checkpoints, indices, datasets) confirmed absent from git tracking
5. Existing tests still pass: `pytest tests/` — all green
