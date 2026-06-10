# Plan: KiRAG Reproduction

## Status summary (as of 2026-06-10)

Two-track plan:
- **Track A (pre-trained aligner):** MuSiQue ✅, 2wiki ✅ COMPLETE, HotPotQA ⏳ not started.
- **Track B (trained aligner):** Next up — download training data + build HotPotQA index (parallel), then train aligner (~4–8 hrs on 2× A100), then re-run all 3 datasets.

Keep all Track A results — they are the baseline for comparison with Track B.

**2wiki QA caveat:** Our 2wiki QA numbers (EM=0.596, F1=0.692) are not comparable to the paper's (EM=0.350, F1=0.540). Cause: the preprocessing script for 2wiki has no fixed random seed, so our 500 dev questions are a different sample from the train set than the paper's. MuSiQue uses `seed_everything(0)` and is directly comparable. HF token saved to `.env` as `HF_TOKEN`.

---

## 1. Environment and Repository Setup ✅

- [x] Clone KiRAG repo into `experiments/kirag/`
- [x] kirag conda env has all deps (torch 2.2.1, transformers 4.44.2, faiss, nltk, dill)
- [x] Aligner checkpoint downloaded → `checkpoint/trained_e5_reasoning_chain_aligner/`
- [x] Llama3-8B-Instruct HF gating approved (token updated to allow public gated repos)
- [x] All datasets downloaded & validated: corpus.json, dev_qa_pairs.json, qrels.tsv for musique/2wiki/hotpotqa
- [x] All KG triple pkls downloaded & validated: musique (143MB), 2wiki (472MB), hotpotqa (4.4GB)
- NOTE: OSF has NO pre-built faiss indices — built them ourselves with compute_corpus_embeddings.py + faiss_index_corpus.py

**KiRAG source code patches applied (do not revert):**
1. `dataset/corpus.py` — hardcoded `/nfs/common/data/` paths → relative paths via `_BASE`
2. `compute_corpus_embeddings.py` — added `@torch.no_grad()` to `cal_doc_embeddings` (was accumulating BERT computation graph → OOM)
3. `retrieve.py` line 165 — removed `[:5]` debug slice from `questions = load_json(...)[:5]`

**GPU rule:** GPU 0 has intermittent external jobs (~40 GB). Always use `CUDA_VISIBLE_DEVICES=1` for KiRAG GPU work. Use `CUDA_VISIBLE_DEVICES=0` only when GPU 1 is busy and GPU 0 is confirmed free via `nvidia-smi`.

---

## 2. Dataset Setup ✅

- [x] All 3 datasets downloaded (musique, 2wikimultihopqa, hotpotqa)
- [x] Splits confirmed: paper uses dev set (500 questions each) as test set
- [x] KG triple pkls used (pre-built by authors); no need to run `construct_kg_corpus.py`
- [x] Faiss indices built: musique ✅, 2wikimultihopqa ✅, hotpotqa ⏳ (not yet needed)

**Faiss index locations:** `checkpoint/e5_retriever/{dataset}/index.faiss`

---

## 3. Reproduce Paper Tables 1–3

### MuSiQue ✅ COMPLETE (Track A — pre-trained aligner)
- [x] Corpus embeddings: `CUDA_VISIBLE_DEVICES=1 python -m compute_corpus_embeddings --corpus musique --retriever_name E5Retriever --save_dir checkpoint --name e5_retriever --index_folder musique --per_gpu_batch_size 512`
- [x] Faiss index: `python -m faiss_index_corpus --index_folder checkpoint/e5_retriever/musique --embedding_size 1024`
- [x] Retrieval: `CUDA_VISIBLE_DEVICES=1 python -m retrieve --dataset musique --query_file original/data/musique/open_domain_data/dev_qa_pairs.json --corpus musique --index_folder checkpoint/e5_retriever/musique --embedding_size 1024 --retriever_name E5Retriever --hf_token $HF_TOK --llm llama3 --aligner_model e5 --aligner_model_name_or_path checkpoint/trained_e5_reasoning_chain_aligner --cached_kg_triples_file checkpoint/kg_corpus/musique/cached_kg_triples.pkl --save_dir checkpoint --name e5_retriever --save_file dev_musique_retrieval_results.json`
- [x] Retrieval eval R@3 and R@5
- [x] QA eval EM and F1: `CUDA_VISIBLE_DEVICES=1 python -m evaluation.qa_eval --hf_token $HF_TOK --save_file checkpoint/e5_retriever/dev_musique_retrieval_results.json --k 3`
- Results saved: `original/results/musique_results.json` → committed copy at `data/kirag_results/musique_results.json`

**MuSiQue results vs paper:**
| Metric | Ours | Paper | Δ |
|---|---|---|---|
| R@3 | 0.626 | 0.545 | +8.1% |
| R@5 | 0.680 | 0.612 | +6.8% |
| EM | 0.266 | 0.192 | +7.4% |
| F1 | 0.364 | 0.300 | +6.4% |

Note: consistently above paper by ~7% — likely due to improved KG triple cache in released OSF checkpoint vs checkpoint used for paper submission. Same 500-question dev split confirmed.

### 2WikiMultiHopQA ⚠️ PARTIAL (Track A — pre-trained aligner)
- [x] Corpus embeddings: done (431k docs, 1.7 GB)
- [x] Faiss index: built (`checkpoint/e5_retriever/2wikimultihopqa/index.faiss`, 1.7 GB)
- [x] Retrieval (500 questions): done → `checkpoint/e5_retriever/dev_2wiki_retrieval_results.json`
- [x] Retrieval eval R@3=0.809, R@5=0.869
- [x] QA eval EM=0.596, F1=0.692
- Results saved: `original/results/2wiki_results.json` → committed copy at `data/kirag_results/2wiki_results.json`

### HotPotQA ⏳ NOT STARTED (Track A)
- [ ] Corpus embeddings (5.2M docs — estimate ~3 hrs on A100): same command with `--corpus hotpotqa --index_folder hotpotqa`
- [ ] Faiss index
- [ ] Retrieval, retrieval eval, QA eval
- NOTE: also required for Track B aligner training data

### Table 3 (Bamboogle, WebQA, NQ) ⏳ NOT STARTED
- Requires Wikipedia corpus (psgs_w100.tsv from DPR) — large download (~20 GB)
- Low priority; do after Tables 1–2 are confirmed

---

## 3b. Train Aligner (Track B) ⏳

**Goal:** Train aligner from scratch on official training data; re-run all 3 datasets; compare results to paper and Track A.

**Prerequisites:** HotPotQA corpus index must be built first (needed for training data).

### Step 1 — Download training data ⏳
- [ ] Download `train_aligner.json` and `dev_aligner.json` for all 3 datasets from OSF (`osf.io/qw594/files/osfstorage`)
- [ ] Save to `original/data/{dataset}/open_domain_data/`

### Step 2 — Train aligner ⏳
```bash
CUDA_VISIBLE_DEVICES=0,1 /root/miniconda3/envs/kirag/bin/python -m torch.distributed.launch \
    --nproc_per_node 2 -m train_aligner \
    --data_folders original/data/hotpotqa/open_domain_data \
                   original/data/2wikimultihopqa/open_domain_data \
                   original/data/musique/open_domain_data \
    --backbone E5Retriever \
    --backbone_model_name intfloat/e5-large-v2 \
    --save_dir checkpoint \
    --name trained_e5_aligner_ours
```
- Estimated time: 4–8 hours on 2× A100
- Checkpoint saved to: `checkpoint/trained_e5_aligner_ours/`
- Do NOT overwrite `checkpoint/trained_e5_reasoning_chain_aligner/` (Track A pre-trained)

### Step 3 — Re-run retrieval with trained aligner ⏳
Re-run the same retrieve commands for all 3 datasets, substituting:
- `--aligner_model_name_or_path checkpoint/trained_e5_aligner_ours`
- `--save_file dev_{dataset}_retrieval_results_ours.json`

Save results to `original/results/{dataset}_results_ours.json` (separate from Track A results).

### Step 4 — Compare results ⏳
- [ ] Record Track B results in a comparison table (see below)
- [ ] Update `experiments/kirag/reproduce_kirag_tables.py` to print Track A vs Track B vs paper

**Comparison table (fill after Track B runs):**

| Dataset | Metric | Paper | Track A (pre-trained) | Track B (trained) |
|---------|--------|-------|----------------------|-------------------|
| MuSiQue | R@3 | 0.545 | 0.626 | TBD |
| MuSiQue | R@5 | 0.612 | 0.680 | TBD |
| MuSiQue | EM | 0.192 | 0.266 | TBD |
| MuSiQue | F1 | 0.300 | 0.364 | TBD |
| 2WikiMultiHopQA | R@3 | 0.778 | 0.809 (+3.1%) | TBD |
| 2WikiMultiHopQA | R@5 | 0.853 | 0.869 (+1.6%) | TBD |
| 2WikiMultiHopQA | EM | 0.350 | 0.596 (+24.6%) | TBD |
| 2WikiMultiHopQA | F1 | 0.540 | 0.692 (+15.2%) | TBD |
| HotPotQA | R@3 | — | TBD | TBD |
| HotPotQA | R@5 | — | TBD | TBD |
| HotPotQA | EM | — | TBD | TBD |
| HotPotQA | F1 | — | TBD | TBD |

---

## 4. Adapt KiRAG to VQA Benchmark Dataset ⏳

- [ ] Write `experiments/kirag/vqa_benchmark/prepare_corpus.py` — converts `data/chunks/*.json` to KiRAG input format
- [ ] Build KG corpus from VQA transcript chunks using `construct_kg_corpus.py`
- [ ] Run KiRAG retrieval on `data/benchmark/benchmark_v1.json`
- [ ] Post-process: map retrieved chunks → `[video_id @ mm:ss to mm:ss]` citations
- [ ] Save results to `experiments/kirag/vqa_benchmark/results/kirag_vqa_results.json`

---

## 5. Results Reporting ⏳

- [ ] Write `experiments/kirag/reproduce_kirag_tables.py` — reproduced vs. paper numbers side-by-side
- [ ] Compute VQA metrics using `src/evaluator.py`
- [ ] Update `results.md` with KiRAG column
- [ ] Add `.gitignore` entries for large data/checkpoint/index dirs
- [ ] Commit + push to `feature/kirag-reproduction`
