# Requirements: KiRAG Reproduction

## Overview

Reproduce the main experimental results from KiRAG (ACL 2025) — Tables 1, 2, and 3 — on HotPotQA, 2WikiMultiHopQA, and MuSiQue, then adapt KiRAG to the VQA benchmark transcript dataset. This establishes KiRAG as a third retrieval configuration alongside Config 1 (transcript-only dense) and Config 2 (transcript+frames dense), demonstrating explicit multi-hop retrieval over video-grounded text.

Paper: Fang et al., "KiRAG: Knowledge-Driven Iterative Retriever for Enhancing Retrieval-Augmented Generation", ACL 2025.
Code: https://github.com/jyfang6/kirag

---

## In Scope

- Reproduce Table 1 (retrieval: R@3, R@5) on HotPotQA, 2WikiMultiHopQA, MuSiQue
- Reproduce Table 2 (QA: EM, F1) on HotPotQA, 2WikiMultiHopQA, MuSiQue
- Reproduce Table 3 (generalization: R@3, R@5, EM, F1) on Bamboogle, WebQA, NQ
- Adapt KiRAG to VQA benchmark transcript chunks and run evaluation
- Temporal grounding post-processing: map retrieved chunks to `[video_id @ mm:ss to mm:ss]` citations
- Integration into `results.md` with KiRAG column

---

## Out of Scope

- KiRAG ablation studies (Tables 4, 5) — main tables only
- Appendix results with BGE retriever or Qwen2.5/Flan-T5 readers
- Vgent or any other KG-RAG method — separate spec if needed
- Modifying KiRAG source code beyond input format adaptation
- Visual channel (KiRAG is text-only; frame captions are out of scope for this phase)

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Training (Track A) | Use pre-trained OSF checkpoint | Fastest path to results; establishes baseline |
| Training (Track B) | Train aligner from scratch on HotPotQA/2wiki/MuSiQue data | Measures how close self-trained results are to paper; validates reproducibility |
| Retriever | E5 (`intfloat/e5-large-v2`) | Primary retriever in paper's main results |
| Reader | Llama3-8B (`meta-llama/Meta-Llama-3-8B-Instruct`) | Primary reader in paper's main results |
| Triple constructor | Llama3-8B | Same model as reader; no paid API required |
| VQA input format | One document per 45s chunk, text only | KiRAG expects text corpus; chunk text = transcript + frame captions (Config 2 text) |
| Temporal grounding | Post-processing: look up `start_s`/`end_s` from chunk metadata after retrieval | KiRAG does not natively output timestamps |
| Experiment location | `experiments/kirag/` within existing repo | Unified git history; compatible with `results.md` and paper tables convention |
| Cost | $0 | All models open-source on HuggingFace; no paid API calls |

---

## Dependencies

| Dependency | Source | Notes |
|---|---|---|
| KiRAG codebase | https://github.com/jyfang6/kirag | Clone into `experiments/kirag/` |
| kirag conda env | `/root/miniconda3/envs/kirag/` | Separate env from `vqa-benchmark` — torch 2.2.1 + transformers 4.44.2. Run all KiRAG scripts with `/root/miniconda3/envs/kirag/bin/python` (not `conda run` — PYTHONPATH conflict breaks faiss) |
| Pre-trained aligner checkpoints | OSF (`osf.io/qw594`) | Track A; add to `.gitignore` |
| Aligner training data (`train_aligner.json`, `dev_aligner.json`) | OSF (`osf.io/qw594`) | Track B; one file per dataset; add to `.gitignore` |
| Pre-built corpus indices | OSF (`osf.io/qw594`) | Built ourselves; add to `.gitignore` |
| E5 retriever | HuggingFace: `intfloat/e5-large-v2` | Free |
| Llama3-8B | HuggingFace: `meta-llama/Meta-Llama-3-8B-Instruct` | Free; requires HF token |
| HotPotQA, 2WikiMultiHopQA, MuSiQue | Public datasets | Download to `experiments/kirag/original/data/` |
| `src/evaluator.py` | Existing project module | Reused for temporal IoU and hit rate metrics on VQA dataset |
| `data/benchmark/benchmark_v1.json` | Existing benchmark | Input for VQA adaptation phase |
| `data/chunks/*.json` | Existing chunk files | Source corpus for VQA adaptation |

---

## Open Questions

1. **VQA chunk format**: KiRAG expects a flat document corpus — confirm whether chunk text alone or chunk text + frame captions (Config 2 style) should be used as the KiRAG document.
2. **Aligner fine-tuning on VQA data**: The pre-trained aligner is trained on HotPotQA/2Wiki supervision signal. Performance on VQA may degrade. If R@3 on VQA is significantly lower than on HotPotQA, consider fine-tuning the aligner on a small VQA subset.
3. **Multi-hop citation assembly**: KiRAG iteratively retrieves multiple chunks. For multi-hop questions, all retrieved chunks across all hops should contribute to the final citation span — confirm this assembly logic in `prepare_corpus.py`.
4. **HuggingFace token**: Llama3-8B requires a HuggingFace access token. ✅ Token saved to `.env` as `HF_TOKEN`; load with `export $(cat .env | xargs)` at session start.
