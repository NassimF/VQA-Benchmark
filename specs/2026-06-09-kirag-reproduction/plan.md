# Plan: KiRAG Reproduction

## 1. Environment and Repository Setup
- [ ] Clone KiRAG repo into `experiments/kirag/` (`git clone https://github.com/jyfang6/kirag`)
- [ ] Install KiRAG dependencies in `vqa-benchmark` conda env (`pip install -r requirements.txt`)
- [ ] Download pre-trained Reasoning Chain Aligner checkpoints from KiRAG GitHub
- [ ] Download pre-built corpus indices for HotPotQA, 2WikiMultiHopQA, MuSiQue from KiRAG GitHub
- [ ] Verify E5 retriever (`intfloat/e5-large-v2`) and Llama3-8B reader available on HuggingFace

## 2. Original Dataset Setup
- [ ] Download HotPotQA, 2WikiMultiHopQA, and MuSiQue datasets to `experiments/kirag/original/data/`
- [ ] Confirm dataset splits match those used in the paper (Table 6 in KiRAG paper — dataset statistics)
- [ ] Run `compute_corpus_embeddings.py` if pre-built indices are incomplete for any dataset
- [ ] Run `construct_kg_corpus.py` if pre-built KG triples are missing for any dataset

## 3. Reproduce Paper Tables 1–3
- [ ] Run `retrieve.py` with E5 retriever + pre-trained aligner on HotPotQA, 2Wiki, MuSiQue
- [ ] Run `retrieval_eval` script — record R@3 and R@5 per dataset (Table 1)
- [ ] Run `qa_eval` with Llama3-8B reader — record EM and F1 per dataset (Table 2)
- [ ] Run on unseen datasets (Bamboogle, WebQA, NQ) for generalization results (Table 3)
- [ ] Save all raw result JSONs to `experiments/kirag/original/results/`

## 4. Adapt KiRAG to VQA Benchmark Dataset
- [ ] Write `experiments/kirag/vqa_benchmark/prepare_corpus.py` — converts `data/chunks/*.json` transcript chunks to KiRAG input format (one document per chunk, preserving `chunk_id`, `start_s`, `end_s` metadata)
- [ ] Build KG corpus from VQA transcript chunks using `construct_kg_corpus.py`
- [ ] Run KiRAG retrieval on VQA benchmark QA pairs (`data/benchmark/benchmark_v1.json`)
- [ ] Post-process: map retrieved chunks back to temporal spans → format as `[video_id @ mm:ss to mm:ss]` citations
- [ ] Save results to `experiments/kirag/vqa_benchmark/results/kirag_vqa_results.json`

## 5. Results Reporting and Integration
- [ ] Write `experiments/kirag/reproduce_kirag_tables.py` — prints reproduced vs. paper numbers side-by-side for Tables 1–3
- [ ] Compute VQA benchmark metrics (R@3, R@5, EM, F1, temporal IoU) using existing `src/evaluator.py`
- [ ] Update `results.md` with KiRAG column alongside Config 1 and Config 2
- [ ] Add `.gitignore` entries for `experiments/kirag/data/`, `experiments/kirag/checkpoints/`, `experiments/kirag/indices/`
- [ ] Commit results JSONs and reproduction script; push to `feature/kirag-reproduction`
