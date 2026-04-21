# PROJECT_PLAN.md — Long-Lecture Video RAG Benchmark

**Course:** CS 6263 LLM and Agentic Systems, UTSA  
**Track:** C — Long-Lecture Video RAG and Benchmark Construction  
**GitHub:** https://github.com/NassimF/VQA-Benchmark  
**Instructor:** Dr. Peyman Najafirad | **TA:** Mohammad Bahrami  

---

## What We Are Building

A **multi-hop** Visual Question Answering (VQA) benchmark for **long lecture videos**, paired with a full Retrieval-Augmented Generation (RAG) pipeline. Questions are designed so the answer requires connecting information from **two or more non-adjacent segments** of the video — not just finding a single relevant clip.

> **Multi-hop in plain terms:** A single-hop question ("What is memoization?") has one answer location. A multi-hop question ("How does the subproblem property introduced at the start of the lecture justify the complexity claim made at the end?") requires the model to retrieve chunks from two different parts of the video and synthesize them. This is harder, more realistic, and more useful as a benchmark.

> **RAG in plain terms:** Instead of asking an LLM to answer from memory, we first *retrieve* relevant transcript chunks from a vector database (like searching a library), then feed those chunks as context to the LLM. The LLM answers using only the retrieved text and cites its sources — here, timestamp ranges in the video.

**Scale:** 60 lectures across 15 courses — sufficient for a full venue submission (EMNLP, ACL, NeurIPS datasets track) per advisor guidance. Four lectures have been downloaded and transcribed/chunked (Phases 2–3 complete); the remaining 56 are queued.

---

## Licensing and Publication Rights

### License Compatibility for This Research

All 60 lectures carry open licenses that permit academic use. The key restrictions are:

| License | Non-commercial? | ShareAlike? | Applies to |
|---------|----------------|-------------|------------|
| CC BY-NC-SA 4.0 | Yes — academic use ✓ | Yes — benchmark must carry same license | MIT OCW, Stanford SEE |
| CC BY 4.0 | No restriction | No restriction | NYU DL 2020 |

**NC clause:** This project is academic coursework and non-commercial research — the NC restriction is satisfied.

**SA clause (most important for publication):** CC BY-NC-SA requires that any derivative work use the same license. The benchmark dataset includes transcript excerpts and Qwen2-VL frame captions derived from the MIT and Stanford videos — those are derivative works. Therefore:

> **The benchmark must be released as CC BY-NC-SA 4.0.** The QA pairs themselves (original questions and answers you write) are your own work and not restricted by the video license, but the transcript text and frame captions embedded in the dataset are derivatives and fall under SA.

NYU CC BY 4.0 content is compatible with this — you may include CC BY material in a CC BY-NC-SA collection as long as attribution is preserved.

**Attribution required:** Every video must be credited in the dataset and report. The metadata.json entries contain the required course, instructor, and URL fields for this purpose.

---

## Video Library (60 Lectures)

All video metadata is stored in `data/raw/metadata.json`. ✓ = downloaded and processed; ⏳ = queued.

### Existing — Downloaded and Processed

| # | Video ID | Title | Course | Duration | License | URL | License Source |
|---|----------|-------|--------|----------|---------|-----|----------------|
| 1 | `mit_6046_lec10` ✓ | 10. Dynamic Programming: Advanced DP | MIT 6.046J Algorithms, SP15 | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=Tw1k46ywN6E | MIT OCW blanket policy — ocw.mit.edu/terms |
| 2 | `mit_18065_lec06` ✓ | 6. Singular Value Decomposition (SVD) | MIT 18.065 Matrix Methods, SP18 | 54 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=rYz83XPxiZo | MIT OCW blanket policy — ocw.mit.edu/terms |
| 3 | `nyu_dl_week6` ✓ | Week 6 — CNN, RNN, and Attention | NYU Deep Learning (LeCun/Canziani), SP20 | 89 min | CC BY 4.0 | https://www.youtube.com/watch?v=ycbMGyCPzvE | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 4 | `nyu_dl_week7` ✓ | Week 7 — Energy-Based Models and Self-Supervised Learning | NYU Deep Learning (LeCun/Canziani), SP20 | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=PHxKk5Y5ayc | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |

### Group A — MIT 6.006 Introduction to Algorithms, Fall 2011

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 5 | `mit_6006f11_lec01` | 1. Algorithmic Thinking, Peak Finding | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=HtSuA80QTyo | MIT OCW blanket policy — ocw.mit.edu/terms |
| 6 | `mit_6006f11_lec03` | 3. Insertion Sort, Merge Sort | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=Kg4bqzAqRBM | MIT OCW blanket policy — ocw.mit.edu/terms |
| 7 | `mit_6006f11_lec04` | 4. Heaps and Heap Sort | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=B7hVxCmfPtM | MIT OCW blanket policy — ocw.mit.edu/terms |
| 8 | `mit_6006f11_lec09` | 9. Table Doubling, Karp-Rabin | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=BRO7mVIFt08 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 9 | `mit_6006f11_lec14` | 14. Depth-First Search, Topological Sort | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=AfSk24UTFS8 | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group B — MIT 6.006 Introduction to Algorithms, Spring 2020

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 10 | `mit_6006sp20_lec04` | 4. Hashing | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=Nu8YGneFCWE | MIT OCW blanket policy — ocw.mit.edu/terms |
| 11 | `mit_6006sp20_lec07` | 7. Binary Trees, Part 2 (AVL) | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=U1JYwHcFfso | MIT OCW blanket policy — ocw.mit.edu/terms |
| 12 | `mit_6006sp20_lec09` | 9. Breadth-First Search | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=oFVYVzlvk9c | MIT OCW blanket policy — ocw.mit.edu/terms |
| 13 | `mit_6006sp20_lec11` | 11. Weighted Shortest Paths | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=5cF5Bgv59Sc | MIT OCW blanket policy — ocw.mit.edu/terms |
| 14 | `mit_6006sp20_lec15` | 15. Dynamic Programming, Part 1 | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=r4-cftqTcdI | MIT OCW blanket policy — ocw.mit.edu/terms |
| 15 | `mit_6006sp20_lec17` | 17. Dynamic Programming, Part 3 | 60 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=TDo3r5M1LNo | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group C — MIT 6.046J Design and Analysis of Algorithms, Spring 2015

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 16 | `mit_6046_lec01` | 1. Overview, Interval Scheduling | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=2P-yW7LQr08 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 17 | `mit_6046_lec03` | 3. Divide & Conquer — FFT | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=iTMn0Kt18tg | MIT OCW blanket policy — ocw.mit.edu/terms |
| 18 | `mit_6046_lec06` | 6. Randomization — Matrix Multiply, Quicksort | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=cNB2lADK3_s | MIT OCW blanket policy — ocw.mit.edu/terms |
| 19 | `mit_6046_lec12` | 12. Greedy Algorithms — MST | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=tKwnms5iRBU | MIT OCW blanket policy — ocw.mit.edu/terms |
| 20 | `mit_6046_lec13` | 13. Incremental Improvement — Max Flow, Min Cut | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=VYZGlgzr_As | MIT OCW blanket policy — ocw.mit.edu/terms |
| 21 | `mit_6046_lec16` | 16. Complexity — P, NP, NP-completeness | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=eHZifpgyH_4 | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group D — MIT 18.06 Linear Algebra, Spring 2010

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 22 | `mit_1806_lec01` | 1. Geometry of Linear Equations | 47 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=J7DzL2_Na80 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 23 | `mit_1806_lec04` | 4. Factorization into A = LU | 47 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=MsIvs_6vC38 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 24 | `mit_1806_lec06` | 6. Column Space and Nullspace | 47 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=8o5Cmfpeo6g | MIT OCW blanket policy — ocw.mit.edu/terms |
| 25 | `mit_1806_lec10` | 10. The Four Fundamental Subspaces | 47 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=nHlE7EgJFds | MIT OCW blanket policy — ocw.mit.edu/terms |
| 26 | `mit_1806_lec15` | 15. Projections onto Subspaces | 47 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=Y_Ac6KiQ1t0 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 27 | `mit_1806_lec21` | 21. Eigenvalues and Eigenvectors | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=cdZnhQjJu4I | MIT OCW blanket policy — ocw.mit.edu/terms |
| 28 | `mit_1806_lec25` | 25. Symmetric Matrices and Positive Definiteness | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=UCc9q_cAhho | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group E — MIT 18.065 Matrix Methods, Spring 2018 (additional)

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 29 | `mit_18065_lec22` | 22. Gradient Descent | 48 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=AeRwohPuUHQ | MIT OCW blanket policy — ocw.mit.edu/terms |
| 30 | `mit_18065_lec26` | 26. Structure of Neural Nets for Deep Learning | 48 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=sx00s7nYmRM | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group F — MIT 6.034 Artificial Intelligence, Fall 2010

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 31 | `mit_6034_lec04` | 4. Search: DFS, Hill Climbing, Beam | 52 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=j1H3jAAGlEA | MIT OCW blanket policy — ocw.mit.edu/terms |
| 32 | `mit_6034_lec05` | 5. Search: Optimal, Branch and Bound, A* | 52 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=gGQ-vAmdAOI | MIT OCW blanket policy — ocw.mit.edu/terms |
| 33 | `mit_6034_lec06` | 6. Search: Games, Minimax, Alpha-Beta | 52 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=STjW3eH0Cik | MIT OCW blanket policy — ocw.mit.edu/terms |
| 34 | `mit_6034_lec17` | 17. Learning: Boosting | 52 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=UHBmv7qCey4 | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group G — MIT 6.042J Mathematics for Computer Science, Fall 2010

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 35 | `mit_6042_lec02` | 2. Induction | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=z8HKWUWS-lA | MIT OCW blanket policy — ocw.mit.edu/terms |
| 36 | `mit_6042_lec04` | 4. Number Theory I | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=NuY7szYSXSw | MIT OCW blanket policy — ocw.mit.edu/terms |
| 37 | `mit_6042_lec06` | 6. Graph Theory and Coloring | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=h9wxtqoa1jY | MIT OCW blanket policy — ocw.mit.edu/terms |
| 38 | `mit_6042_lec18` | 18. Probability Introduction | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=SmFwFdESMHI | MIT OCW blanket policy — ocw.mit.edu/terms |
| 39 | `mit_6042_lec22` | 22. Expectation I | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=gGlMSe7uEkA | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group H — MIT 18.650 Statistics for Applications, Fall 2016

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 40 | `mit_18650_lec03` | 3. Parametric Inference | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=TSkDZbGS94k | MIT OCW blanket policy — ocw.mit.edu/terms |
| 41 | `mit_18650_lec07` | 7. Hypothesis Testing | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=phbw9r1iUDI | MIT OCW blanket policy — ocw.mit.edu/terms |
| 42 | `mit_18650_lec13` | 13. Regression | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=yP1S37BiEsQ | MIT OCW blanket policy — ocw.mit.edu/terms |

### Group I — NYU Deep Learning, Spring 2020 (additional)

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 43 | `nyu_dl_week1` | Week 1 — History and Motivation | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=0bMe_vCZo30 | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 44 | `nyu_dl_week2` | Week 2 — SGD and Backpropagation | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=d9vdh3b787Y | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 45 | `nyu_dl_week3` | Week 3 — CNNs and Parameter Transformations | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=FW5gFiJb-ig | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 46 | `nyu_dl_week5` | Week 5 — Optimization for Deep Learning | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=--NZb480zlg | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 47 | `nyu_dl_week9` | Week 9 — World Models and Recurrent Nets | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=Pgct8PKV7iw | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 48 | `nyu_dl_week10` | Week 10 — Self-Supervised Learning in CV | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=0KeR6i1_56g | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 49 | `nyu_dl_week11` | Week 11 — Activation and Loss Functions | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=bj1fh3BvqSU | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 50 | `nyu_dl_week12` | Week 12 — NLP and Transformers | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=6D4EWKJgNn0 | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 51 | `nyu_dl_week13` | Week 13 — Graph Convolutional Networks | 75 min | CC BY 4.0 | https://www.youtube.com/watch?v=Iiv9R6BjxHM | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |

### Group J — Stanford CS229 Machine Learning, Fall 2008 (Stanford Engineering Everywhere)

| # | Video ID | Title | Duration | License | URL | License Source |
|---|----------|-------|----------|---------|-----|----------------|
| 52 | `stanford_cs229_lec03` | Lecture 3: Locally Weighted Regression, Logistic Regression | 78 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=HZ4cvaztQEs | SEE FAQ — see.stanford.edu/FAQ |
| 53 | `stanford_cs229_lec07` | Lecture 7: Optimal Margin Classifier, Kernels | 78 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=s8B4A5ubw6c | SEE FAQ — see.stanford.edu/FAQ |
| 54 | `stanford_cs229_lec12` | Lecture 12: EM Algorithm | 78 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=ZZGTuAkF-Hw | SEE FAQ — see.stanford.edu/FAQ |
| 55 | `stanford_cs229_lec14` | Lecture 14: Factor Analysis, PCA, Dimensionality Reduction | 78 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=ey2PE5xi9-A | SEE FAQ — see.stanford.edu/FAQ |

### Group K — New Topics

| # | Video ID | Title | Course | Duration | License | URL | License Source |
|---|----------|-------|--------|----------|---------|-----|----------------|
| 56 | `mit_18404_lec05` | 5. CF Pumping Lemma, Turing Machines | MIT 18.404J Theory of Computation, FA20 | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=IycOPFmEQk8 | MIT OCW blanket policy — ocw.mit.edu/terms |
| 57 | `mit_6004_lec14` | L14: Cache Implementation | MIT 6.004 Computation Structures, SP17 | 51 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=-XqdkA931ag | MIT OCW blanket policy — ocw.mit.edu/terms |
| 58 | `mit_6851_ses07` | Session 7: Memory Hierarchy Models | MIT 6.851 Advanced Data Structures, SP12 | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=V3omVLzI0WE | MIT OCW blanket policy — ocw.mit.edu/terms |
| 59 | `mit_6858_lec08` | 8. Web Security Model | MIT 6.858 Computer Systems Security, FA14 | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=_1C62Twf0vs | MIT OCW blanket policy — ocw.mit.edu/terms |
| 60 | `mit_6041_lec16` | 16. Markov Chains — Steady State and Absorption | MIT 6.041 Probabilistic Systems Analysis, FA10 | 50 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=IkbkEtOOC1Y | MIT OCW blanket policy — ocw.mit.edu/terms |

### Topic Distribution Summary

| Broad Area | Count | % |
|------------|-------|---|
| Algorithms (sorting, graph, DP, complexity) | 19 | 32% |
| Linear Algebra / Matrix Methods | 9 | 15% |
| ML / Deep Learning | 16 | 27% |
| AI Search | 4 | 7% |
| Math Foundations (proof, number theory, probability) | 7 | 12% |
| Statistics | 3 | 5% |
| Systems (architecture, security, data structures) | 3 | 5% |

### Source Distribution

| Source | Count | % | License |
|--------|-------|---|---------|
| MIT OpenCourseWare (13 courses) | 45 | 75% | CC BY-NC-SA 4.0 |
| NYU Deep Learning 2020 | 11 | 18% | CC BY 4.0 |
| Stanford CS229 2008 via SEE | 4 | 7% | CC BY-NC-SA 4.0 |

---

## Project File Structure

```
VQA_Benchmark/
├── CLAUDE.md
├── PROJECT_PLAN.md                    # Living progress tracker (this file)
├── README.md                          # Track declaration, setup, usage
├── requirements.txt
├── config.yaml
├── .gitignore                         # chroma_db/, *.mp4, *.m4a, .env, __pycache__/
│
├── data/
│   ├── raw/
│   │   ├── videos/                    # git-ignored
│   │   └── metadata.json              # 60 entries — video_id, title, URL, duration, license
│   ├── transcripts/                   # Segment JSON from YouTube VTT captions
│   ├── chunks/                        # 45s windows, 10s overlap
│   ├── frame_captions/                # Qwen2-VL-7B captions per keyframe
│   ├── qa_pairs/
│   │   ├── raw/                       # LLM-generated before human review
│   │   └── reviewed/                  # Human-approved, standard schema
│   └── benchmark/
│       └── benchmark_v1.json          # Merged final benchmark
│
├── chroma_db/                         # git-ignored
│   ├── transcript_only/               # Collection 1
│   └── transcript_plus_frames/        # Collection 2
│
├── src/
│   ├── config.py                      # Loads config.yaml, validates all settings
│   ├── transcriber.py                 # YouTube VTT parser → segment JSON
│   ├── chunker.py                     # 45s windows, 10s overlap (prescribed)
│   ├── frame_extractor.py             # Extract keyframes from video
│   ├── frame_captioner.py             # Qwen2-VL-7B captions for keyframes
│   ├── retriever.py                   # Two modes: transcript-only / +frames (CRITICAL)
│   ├── generator.py                   # Grounded prompt + [video_id @ mm:ss] citations
│   ├── qa_generator.py                # 15 draft QA per lecture via LLM
│   └── evaluator.py                   # Temporal IoU, hit rate@k, LLM-judge
│
├── run_part1.py                       # Deliverable: end-to-end RAG demo
├── run_part2.py                       # Deliverable: benchmark eval (both configs)
│
├── scripts/
│   ├── parse_vtt.py                   # ✅ VTT → transcript JSON
│   ├── build_chunks.py                # ✅ transcript JSON → chunk JSON
│   ├── download_videos.py             # yt-dlp wrapper for all 60 videos
│   ├── build_frame_captions.py        # frame extraction + Qwen2-VL captioning
│   ├── build_benchmark.py             # Merge reviewed QA → benchmark_v1.json
│   ├── validate_benchmark.py          # Schema + quality checks
│   └── cross_validate.py             # IAA metrics for cross-student annotation
│
├── notebooks/
│   ├── 01_transcription_exploration.ipynb
│   ├── 02_chunking_analysis.ipynb
│   ├── 03_qa_generation_review.ipynb
│   └── 04_evaluation_analysis.ipynb
│
├── tests/
│   ├── test_chunker.py
│   ├── test_retriever.py
│   └── test_evaluator.py
│
└── report/
    ├── main.tex
    └── figures/
```

---

## Phase Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Setup: CLAUDE.md, PROJECT_PLAN.md, git/GitHub, literature review | ✅ Complete |
| 1 | Video collection + metadata (60 videos) | ⚠️ Partial — 4/60 downloaded |
| 2 | Transcription (YouTube VTT → segment JSON) | ⚠️ Partial — 4/60 transcribed |
| 3 | Chunking (45s windows, 10s overlap) | ⚠️ Partial — 4/60 chunked |
| 4 | Frame extraction + Qwen2-VL-7B captions | ⏳ Pending |
| 5 | RAG ingestion — two ChromaDB collections | ⏳ Pending |
| 6 | Generator module (grounded prompt + citations) | ⏳ Pending |
| 7 | QA generation + human review (12–15 per lecture) | ⏳ Pending |
| 8 | Cross-student validation (5 annotations + IAA) | ⏳ Pending |
| 9 | Evaluation (both configs: temporal IoU, hit rate@k, LLM-judge) | ⏳ Pending |
| 10 | run_part1.py + run_part2.py | ⏳ Pending |
| 11 | Report (4–6 pages LaTeX) + README | ⏳ Pending |

---

## Phase Step Details

### Phase 1 — Video Collection
- Download full video with `yt-dlp` — required for frame extraction in Phase 4
  - MKV output (NYU videos) is fine; ffmpeg handles AV1 codec
  - `ffmpeg` extracts audio from the video file for any future Whisper use
- Metadata already written to `data/raw/metadata.json` for all 60 videos
- Run: `python scripts/download_videos.py --all`

### Phase 2 — Transcription ✅ (4 lectures)
**Option A used — YouTube auto-captions:**
- VTT files pre-downloaded to `data/raw/videos/{video_id}.en.vtt`
- `src/transcriber.py` parses rolling-caption VTT: collects ~10ms "display" cues (one clean phrase each), strips inline timing tags, de-duplicates consecutive identical lines
- Output: `data/transcripts/{video_id}.json` — 1,569 segments (mit_6046_lec10), 909 (mit_18065_lec06)
- Quality spot-checked at 20-min mark of mit_6046_lec10 and mit_18065_lec06; 0 errors on technical terms
- NYU VTTs (weeks 6 and 7) are downloaded but not yet quality-checked (`caption_quality_check.decision: "pending"` in metadata)
- Run: `python scripts/parse_vtt.py --all`

**Report note:** Used YouTube auto-captions; quality verified for MIT lectures; VTT phrase-level timestamps (~3s per segment) are sufficient for 45s chunking windows.

### Phase 3 — Chunking (prescribed: 45s / 10s) ✅ (4 lectures)
- Slide a 45s window every 35s (stride = window − overlap)
- Segments assigned to chunk if `start` falls in `[win_start, win_start+45s)` — half-open interval
- Empty windows (no segments) are skipped automatically
- Output: `data/chunks/{video_id}_chunks.json`
- Result: 138 chunks (mit_6046_lec10, 80 min), 92 chunks (mit_18065_lec06, 54 min)
- Report justification: 45s captures one concept; 10s overlap prevents answers at boundaries
- Run: `python scripts/build_chunks.py --all`

### Phase 4 — Frame Captions ⏳ Pending (Qwen2-VL-7B-Instruct)
- Extract 1 frame every 30s with `ffmpeg` (AV1/MKV-compatible; cv2 cannot decode NYU files)
- Caption with **Qwen2-VL-7B-Instruct** — reads slide text, equations, and whiteboard content (Approach A: text augmentation)
- Store: `{"frame_id": ..., "time": 120.0, "caption": "Slide showing merge sort recurrence T(n) = T(n-1) + O(n)"}`
- Append captions to nearest chunk for Collection 2
- Run: `python scripts/build_frame_captions.py --all --device cuda`

### Phase 5 — RAG Ingestion
- Embed with `all-MiniLM-L6-v2`; store in two ChromaDB collections
- Metadata per chunk: `video_id`, `start_time`, `end_time`, `chunk_id`
- Add `--rebuild` CLI flag to force re-ingestion without silently overwriting

### Phase 6 — Generator
- Numbered excerpts prompt with timestamps; structured JSON output for citations
- Parse cited chunk indices → predicted span = union of cited chunk time ranges
- Citation string: `[mit_6046_lec10 @ 30:23 to 31:41](https://youtu.be/Tw1k46ywN6E?t=1823)`

### Phase 7 — QA Generation & Review
- Generate 15 drafts per lecture with Claude/GPT-4 given transcript + keyframe captions
- Human review: watch cited span, tighten spans, rewrite awkward questions
- Add 2–4 visual-dependent questions the LLM missed
- Mark exactly 1 question per lecture `"answerable": false`
- Filter: reject if answer < 10 words or if answer is verbatim in the question

### Phase 8 — Cross-Student Validation
- Receive 5 QA pairs from a classmate; annotate in same schema
- Run `scripts/cross_validate.py` → Cohen's Kappa on `answerable`, mean IoU on spans

### Phase 9 — Evaluation
- Both configs × all verified questions
- Save per-question results to `data/benchmark/evaluation_results.json`
- Generate summary tables and plots for the report

### Phase 10 — run_part1.py / run_part2.py
- `run_part1.py`: demo pipeline, accepts question via `argparse` or uses 3 hardcoded examples
- `run_part2.py`: full eval loop → both configs → summary table → save JSON + plots

### Phase 11 — Report & README
- LaTeX, 4–6 pages; every parameter choice explained and justified (not just stated)
- README declares Track C; includes setup and usage instructions
- **Dataset release:** license the benchmark as CC BY-NC-SA 4.0 (required by SA clause from MIT/Stanford content)

---

## Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Chunking strategy | YouTube VTT phrase segments, 45s/10s time window | Prescribed; phrase boundaries from VTT naturally align with speech |
| Overlapping chunks | Yes, 10s overlap | Prevents answers falling at chunk edges |
| Embedding model | all-MiniLM-L6-v2 | Prescribed; fast, lightweight, strong retrieval |
| Vector DB | ChromaDB persistent | Prescribed |
| Citation format | `[video_id @ mm:ss to mm:ss]` | Prescribed; YouTube deep-linkable |
| Structured output | JSON from LLM | More reliable than regex-parsing `[1]` |
| Span aggregation | Union of cited chunk spans | Standard for multi-chunk answers |
| Frame interval | 30s | Balances coverage vs. storage |
| Frame captioner | Qwen2-VL-7B-Instruct (Approach A) | Best OCR/math on lecture content; Apache 2.0; fits on one A100 (14GB); Approach A keeps both collections under same embedding model as prescribed |
| Benchmark license | CC BY-NC-SA 4.0 | Required by ShareAlike clause of MIT/Stanford source material |

---

## Report Structure (4–6 pages)

| Section | Length | Content |
|---------|--------|---------|
| Abstract | ~150 words | What was built, key metrics |
| Introduction | ~0.5 page | Motivation, gap in long-video QA benchmarks |
| Related Work | ~0.75 page | Video QA, temporal grounding, RAG, Whisper |
| Pipeline | ~1 page | Transcription, chunking, frame captions, retrieval, generation |
| Benchmark Contribution | ~1 page | Lecture selection, QA generation method, IAA, QA breakdown |
| Results | ~1 page | Both configs side-by-side, failure mode analysis |
| Conclusion | ~0.25 page | Limitations, future work |

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Track C selected | Research exposure + co-authorship eligibility |
| 2026-04-18 | Chunking: 45s window, 10s overlap | Prescribed by assignment |
| 2026-04-18 | Embedding: all-MiniLM-L6-v2 | Prescribed by assignment |
| 2026-04-20 | Transcription: YouTube auto-captions (Option A) | Quality spot-checked at 20-min mark; 0 errors on technical terms |
| 2026-04-20 | Generator model: gpt-4o-mini | Cost-effective; reliable structured JSON output |
| 2026-04-21 | Frame captioner: Qwen2-VL-7B-Instruct, Approach A (text augmentation) | Strongest OCR/math on lecture slides; Apache 2.0; fits on one A100 (14GB); Approach A keeps both ChromaDB collections under the same embedding model as prescribed |
| 2026-04-21 | Expanded to 60 lectures | Advisor requires 60+ videos for full venue publication |
| 2026-04-21 | Benchmark license: CC BY-NC-SA 4.0 | Required by ShareAlike clause — derived transcript/frame-caption content from MIT OCW videos must carry same license |

---

## Required Deliverables

- [x] `config.yaml`
- [ ] `src/retriever.py` (transcript-only and transcript+frames modes)
- [ ] `src/generator.py`
- [ ] `run_part1.py` — end-to-end RAG demo
- [ ] `run_part2.py` — full benchmark evaluation (both retrieval configs)
- [x] `requirements.txt`
- [ ] `data/benchmark/benchmark_v1.json` (12–15 QA × 60 lectures)
- [ ] Cross-validation annotations (5 questions from a classmate)
- [ ] 4–6 page report (`report/main.tex`)
- [ ] `README.md` (declares Track C)
- [ ] `.gitignore`

---

## Key Metrics to Report

Multi-hop VQA requires separate metrics for single-hop and multi-hop questions, reported side-by-side across both retrieval configs.

### Single-hop questions

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|--------------------------|------------------------------|
| Mean Temporal IoU | | |
| IoU@0.3 | | |
| IoU@0.5 | | |
| Hit Rate@1 | | |
| Hit Rate@3 | | |
| Hit Rate@5 | | |
| LLM-Judge Score (1–5) | | |
| Citation Accuracy | | |

### Multi-hop questions

| Metric | Config 1: Transcript-Only | Config 2: Transcript+Frames |
|--------|--------------------------|------------------------------|
| Mean Per-Hop IoU | | |
| Complete Retrieval Rate@5 | | |
| Per-Hop Recall@5 | | |
| Multi-hop IoU@0.3 (union) | | |
| LLM-Judge Score (1–5) | | |
| Citation Accuracy | | |

---

## Git Checkpoints

| Checkpoint | Commit Message | Date |
|------------|---------------|------|
| Phase 0 complete | `feat: project skeleton and docs` | 2026-04-18 |
| Phase 2 complete | `feat: transcription pipeline (Phase 2)` | 2026-04-20 |
| Phase 3 complete | `feat: chunking pipeline (Phase 3)` | 2026-04-20 |
| Phase 4 complete | `feat: frame caption pipeline` | — |
| Phase 5 complete | `feat: RAG ingestion (both configs)` | — |
| Phase 6 complete | `feat: generator module` | — |
| Phase 7 complete | `data: reviewed QA pairs` | — |
| Phase 8 complete | `data: cross-validation annotations` | — |
| Phase 9 complete | `feat: evaluation pipeline` | — |
| Phase 10 complete | `feat: run_part1 and run_part2` | — |
| Phase 11 complete | `docs: final report and README` | — |

---

## config.yaml (Reference)

```yaml
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cuda"  # or "cpu"

retrieval:
  top_k: 4
  k_values: [1, 3, 5]        # for hit rate evaluation
  distance_metric: "cosine"
  iou_threshold: 0.3

vector_db:
  path: "./chroma_db"
  transcript_only_collection: "lecture_transcript_only"
  transcript_frames_collection: "lecture_transcript_plus_frames"

chunking:
  window_seconds: 45
  overlap_seconds: 10         # stride = 35s

frame_extraction:
  interval_seconds: 30

frame_captioner:
  model: "Qwen/Qwen2-VL-7B-Instruct"
  device: "cuda"
  max_new_tokens: 128

generator:
  model: "gpt-4o-mini"        # or "utsa-llama" / "claude-3-haiku-20240307"
  temperature: 0.1
  max_tokens: 512
  citation_format: "[{video_id} @ {start_mm}:{start_ss} to {end_mm}:{end_ss}]"

qa_generation:
  questions_per_lecture: 15
  target_accepted: 12
```

---

## Evaluation Metric Formulas

### Single-hop Temporal IoU
```python
def temporal_iou(pred_start, pred_end, gt_start, gt_end):
    intersection = max(0, min(pred_end, gt_end) - max(pred_start, gt_start))
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    return intersection / union if union > 0 else 0.0
```
Predicted span = union of cited chunk spans. Thresholds: IoU@0.3 and IoU@0.5.

### Multi-hop Temporal IoU
Ground truth is a **list of spans** (one per hop). Two metrics:

```python
def multihop_per_hop_iou(pred_spans, gt_spans):
    """Mean IoU between each GT hop and its best-matching predicted span."""
    scores = []
    for gt_start, gt_end in gt_spans:
        best = max(temporal_iou(ps, pe, gt_start, gt_end) for ps, pe in pred_spans)
        scores.append(best)
    return sum(scores) / len(scores)

def multihop_union_iou(pred_spans, gt_spans):
    """IoU between the union of all predicted spans and union of all GT spans."""
    # merge overlapping spans, then compute single IoU on merged intervals
    ...
```

### Hit Rate @ k (k = 1, 3, 5)
- **Single-hop:** ≥1 of top-k chunks has IoU > 0.3 with the GT span
- **Multi-hop — Per-hop recall:** fraction of GT hops covered by ≥1 top-k chunk (IoU > 0.3)
- **Multi-hop — Complete retrieval rate:** fraction of questions where ALL hops are covered by top-k

### LLM-Judge Score
Feed `question + generated_answer + reference_answer` to an LLM; score 1–5 for accuracy and grounding. Applied to both single-hop and multi-hop questions.

### Citation Accuracy
Of the chunks the LLM cited `[1]`, `[2]` etc., what fraction actually contained the answer. For multi-hop, check that at least one citation per hop is relevant.

### Cross-Validation IAA
Cohen's Kappa on the `answerable` field between your annotation and the original author's.
Mean temporal IoU between your annotated spans and the original spans.

---

## QA Pair Standard Schema

Single-hop and multi-hop questions use the same schema, with multi-hop using a list of spans instead of one.

```json
{
  "qa_id": "mit_6046_lec10_q007",
  "video_id": "mit_6046_lec10",
  "question": "...",
  "answer": "...",

  "num_hops": 2,
  "ground_truth_spans": [
    {"start": 320.0, "end": 398.0, "hop": 1, "description": "subproblem property introduced"},
    {"start": 2870.0, "end": 2940.0, "hop": 2, "description": "complexity claim relying on subproblem property"}
  ],

  "source_chunk_ids": ["mit_6046_lec10_chunk_009", "mit_6046_lec10_chunk_082"],
  "question_type": "multi-hop|conceptual|procedural|factual|visual",
  "difficulty": "easy|medium|hard",
  "answerable": true,
  "key_concepts": ["memoization", "optimal substructure"],
  "reviewed_by": "human",
  "review_date": "2026-04-20"
}
```

**Notes:**
- Single-hop questions: `num_hops: 1`, `ground_truth_spans` has one entry, `source_chunk_ids` has one entry
- The `description` field per hop is essential for human review — it records *why* that span is needed
- Unanswerable questions: `answerable: false`, `ground_truth_spans: []`

**Target question mix per lecture (12–15 accepted):**

| Type | Count | Notes |
|------|-------|-------|
| Multi-hop | 5–6 | Core contribution; require 2+ non-adjacent spans |
| Single-hop conceptual | 3–4 | Explain a concept from one segment |
| Single-hop factual | 2–3 | Direct fact stated at one timestamp |
| Visual-dependent | 2+ | Require reading a slide/whiteboard; add manually |
| Unanswerable | 1 | Exactly 1 per lecture |

---

## Literature Review Topics

| Topic | Key Papers |
|-------|-----------|
| Video QA Benchmarks | ActivityNet-QA, NExT-QA, EgoSchema, MSVD-QA |
| Temporal Grounding | Gao et al. 2017 (defines temporal IoU), 2D-TAN, Moment-DETR |
| RAG Systems | Lewis et al. 2020 (original RAG), REALM, REPLUG |
| Whisper ASR | Radford et al. 2023 |
| Educational Video QA | LectureSQA and similar |
| Chunking & Retrieval | RAPTOR, HyDE |
| Multimodal Retrieval | CLIP (Radford 2021), Qwen2-VL |

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| ChromaDB collection already exists on rerun | Check before creating; add `--rebuild` CLI flag |
| LLM doesn't reliably output `[1]` citations | Use structured JSON output instead of regex parsing |
| Trivial QA pairs | Filter in `validate_benchmark.py`: reject if answer < 10 words or verbatim in question |
| Predicted span too wide | For factual Qs use intersection; for multi-chunk use union of cited spans |
| MKV/AV1 format (NYU videos) | Use ffmpeg for frame extraction, not cv2 |

---

## Notes & Observations

**Scale:**
- 60 lectures × ~12 accepted QA pairs = ~720 total QA pairs — sufficient for a full venue submission (EMNLP, ACL, NeurIPS datasets track).

**Transcription (Phase 2):**
- YouTube auto-captions chosen over Whisper — pre-downloaded VTTs were clean on technical terms (eigenvectors, memoization, hash table verified). This saves ~1–2 hrs of GPU time per lecture.
- VTT "rolling caption" format alternates word-timing cues (~2s) with display cues (~10ms). The display cues carry one clean subtitle phrase each — these are the source of segments.
- Segment granularity: ~3s per phrase → 1,569 segments for 80-min lecture.

**NYU Lectures (Phases 2–3):**
- nyu_dl_week6: 1,761 segments, 153 chunks (89 min); nyu_dl_week7: 1,966 segments, 167 chunks (~97 min actual)
- Note: metadata.json lists nyu_dl_week7 as 75 min — the chunk count implies the actual video is ~97 min; metadata should be corrected once confirmed via `yt-dlp --get-duration`
- Downloaded as MKV (AV1 codec) — cv2 cannot decode AV1; frame extractor updated to use ffmpeg instead

**Frame Captioning (Phase 4):**
- **Qwen2-VL-7B-Instruct** (Apache 2.0) on A100 GPU — reads slide text, equations, and whiteboard diagrams. Prompt instructs it to include all visible text and labels. Phase 4 is pending — must be run before Phase 5.
- Frame extraction uses ffmpeg at 30s intervals (AV1/MKV-compatible); estimated ~642 frames across the first 4 lectures.
- Approach A: captions appended as text to chunk → embedded with all-MiniLM-L6-v2 into Collection 2. No fusion layer needed; both collections use the same embedding model as prescribed.

**Chunking (Phase 3):**
- Pure time-based windowing: segment belongs to chunk if `segment.start ∈ [win_start, win_start+45s)`. No silence-gap detection implemented — not needed given dense lecture speech.
- Overlap confirmed by unit test: segment starting at 40s appears in both chunk [0–45s) and chunk [35–80s).
- Chunk counts match theoretical ⌈duration/stride⌉: 138 for 80 min, 92 for 54 min.
- 8/8 unit tests passing (pytest).

---

*Last updated: 2026-04-21*
