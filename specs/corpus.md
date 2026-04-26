# Corpus

60 CC-licensed academic lecture videos across 15 courses. All metadata is stored in `data/raw/metadata.json`.

Status: ✓ = downloaded and processed | ⏳ = queued

---

## Licensing and Publication Rights

| License | Non-commercial? | ShareAlike? | Applies to |
|---------|----------------|-------------|------------|
| CC BY-NC-SA 4.0 | Yes — academic use ✓ | Yes — benchmark must carry same license | MIT OCW, Stanford SEE |
| CC BY 4.0 | No restriction | No restriction | NYU DL 2020 |

**NC clause:** This project is non-commercial academic research — satisfied.

**SA clause (publication-critical):** CC BY-NC-SA requires derivative works to carry the same license. The benchmark dataset includes transcript excerpts and Qwen2-VL frame captions derived from MIT and Stanford videos — those are derivative works.

> **The benchmark must be released as CC BY-NC-SA 4.0.** QA pairs (original questions and answers) are your own work and not restricted by the video license, but transcript text and frame captions embedded in the dataset are derivatives and fall under SA.

NYU CC BY 4.0 content is compatible — CC BY material may be included in a CC BY-NC-SA collection as long as attribution is preserved.

**Attribution required:** Every video must be credited in the dataset and report. The `data/raw/metadata.json` entries contain the required course, instructor, and URL fields.

---

## Source Distribution

| Source | Count | % | License |
|--------|-------|---|---------|
| MIT OpenCourseWare (13 courses) | 45 | 75% | CC BY-NC-SA 4.0 |
| NYU Deep Learning 2020 | 11 | 18% | CC BY 4.0 |
| Stanford CS229 2008 via SEE | 4 | 7% | CC BY-NC-SA 4.0 |

## Topic Distribution

| Broad Area | Count | % |
|------------|-------|---|
| Algorithms (sorting, graph, DP, complexity) | 19 | 32% |
| ML / Deep Learning | 16 | 27% |
| Linear Algebra / Matrix Methods | 9 | 15% |
| Math Foundations (proof, number theory, probability) | 7 | 12% |
| AI Search | 4 | 7% |
| Statistics | 3 | 5% |
| Systems (architecture, security, data structures) | 3 | 5% |

---

## Video Library

### Existing — Downloaded and Processed

| # | Video ID | Title | Course | Duration | License | URL | License Source |
|---|----------|-------|--------|----------|---------|-----|----------------|
| 1 | `mit_6046_lec10` ✓ | 10. Dynamic Programming: Advanced DP | MIT 6.046J Algorithms, SP15 | 80 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=Tw1k46ywN6E | MIT OCW blanket policy — ocw.mit.edu/terms |
| 2 | `mit_18065_lec06` ✓ | 6. Singular Value Decomposition (SVD) | MIT 18.065 Matrix Methods, SP18 | 54 min | CC BY-NC-SA 4.0 | https://www.youtube.com/watch?v=rYz83XPxiZo | MIT OCW blanket policy — ocw.mit.edu/terms |
| 3 | `nyu_dl_week6` ✓ | Week 6 — CNN, RNN, and Attention | NYU Deep Learning (LeCun/Canziani), SP20 | 89 min | CC BY 4.0 | https://www.youtube.com/watch?v=ycbMGyCPzvE | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |
| 4 | `nyu_dl_week7` ✓ | Week 7 — Energy-Based Models and Self-Supervised Learning | NYU Deep Learning (LeCun/Canziani), SP20 | 75 min* | CC BY 4.0 | https://www.youtube.com/watch?v=PHxKk5Y5ayc | GitHub LICENSE file — github.com/Atcold/pytorch-Deep-Learning |

*nyu_dl_week7: metadata lists 75 min but chunk count (167 × 35s stride) implies ~97 min actual. Verify with `yt-dlp --get-duration` and correct `metadata.json`.

---

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
