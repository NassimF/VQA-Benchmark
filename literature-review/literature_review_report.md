# Literature Review: Long-Lecture Video RAG Benchmark

**Topic:** Long-Lecture Video Question Answering, Temporal Grounding, and Retrieval-Augmented Generation  
**Date:** April 2026  
**Papers reviewed:** 18  

---

## Abstract

This review surveys the literature relevant to constructing a Retrieval-Augmented Generation (RAG) benchmark for long lecture videos. We examine five thematic clusters: long-form video question answering, temporal grounding and moment retrieval, retrieval-augmented generation systems, multimodal models and frame captioning, and educational video understanding. Across all clusters, a consistent gap emerges: existing benchmarks and systems are designed for either short video clips or general-domain content, and none simultaneously supports transcript-grounded retrieval, timestamp-level citation, and systematic evaluation of long instructional videos. This project directly addresses that gap.

---

## 1. Long-form Video Question Answering

### 1.1 Overview

Long-form video QA is a rapidly evolving subfield that extends standard visual question answering from short clips (typically under 30 seconds) to videos spanning minutes or hours. The core challenge is that relevant information is temporally sparse — a question about a specific algorithm may be answered in a 30-second window within a 90-minute lecture — making exhaustive frame-by-frame processing computationally prohibitive.

### 1.2 Key Works

**EgoSchema** (Mangalam et al., 2023) is currently the most directly related benchmark to this project. Derived from the Ego4D dataset, it contains over 5,000 human-curated multiple-choice QA pairs requiring models to reason over 3-minute egocentric video clips. Its emphasis on extended temporal reasoning — asking *why* something happened rather than *what* is visible — represents a meaningful step beyond clip-level understanding. However, EgoSchema is grounded in daily egocentric activity (cooking, sports, social interaction), not instructional or academic content, and does not provide temporal span annotations or transcript-based retrieval evaluation.

**V-STaR** (Cheng et al., 2025) introduces a structured spatio-temporal reasoning benchmark that decomposes video understanding into three sequential steps: identifying *when* a relevant event occurs, locating *where* objects appear, and inferring *what* conclusions follow. This decomposition is well-aligned with the temporal IoU evaluation protocol in this project, where a model must both retrieve the correct temporal window and produce a grounded answer. V-STaR evaluates recent video LLMs including GPT-4V and Gemini Pro, revealing that even state-of-the-art models struggle with fine-grained temporal relational reasoning.

**MovieChat+** (Song et al., 2025) addresses the scalability bottleneck of long video understanding through a question-aware sparse memory mechanism. Rather than compressing all frames uniformly, the system selectively retains tokens relevant to the posed question, enabling processing of hour-long videos without proportional memory growth. This is directly relevant to the lecture video domain, where 60–90 minute videos exceed the context capacity of most video LLMs.

**VideoABC** (Zhao et al., 2022) is notable for using instructional videos — a domain closer to lectures than entertainment — and requiring abductive reasoning across long temporal sequences. Its use of real-world procedural content validates the feasibility of constructing meaningful QA pairs from instructional video transcripts.

### 1.3 Gap Analysis

No existing long-form video QA benchmark uses **academic lecture content** from MIT OpenCourseWare or similar sources. Furthermore, no benchmark simultaneously provides: (1) word-level timestamp annotations from ASR, (2) transcript-chunk retrieval evaluation with temporal IoU, and (3) citation-grounded answer generation. EgoSchema comes closest in scale and temporal depth but lacks all three. This project fills this gap by constructing a benchmark native to the lecture retrieval setting.

---

## 2. Temporal Grounding and Moment Retrieval

### 2.1 Overview

Temporal sentence grounding in videos (TSGV) — also called natural language video localization or video moment retrieval — is the task of identifying the start and end times of a video segment described by a natural language query. Temporal IoU (intersection over union of predicted and ground truth time spans) is the standard evaluation metric, with thresholds at 0.3, 0.5, and 0.7 (Zhang et al., 2023).

> **Temporal IoU in plain terms:** If the model predicts that the answer is between 30:00 and 31:00, and the ground truth is 30:20 to 31:10, the intersection is 40 seconds and the union is 70 seconds, giving an IoU of 0.57. A system that achieves IoU@0.5 "passes" on that question.

### 2.2 Key Works

**Zhang et al. (2023)** provide the authoritative survey of TSGV, establishing the canonical evaluation protocol this project adopts. The survey traces the field from early proposal-based methods (which generate candidate spans and rank them) through modern proposal-free transformers, and identifies cross-modal alignment as the dominant challenge: the semantic gap between a natural language query and the visual or spoken content of a video segment.

**Flanagan et al. (2025)** introduce Negative-Aware Video Moment Retrieval (NA-VMR), which addresses a critical blind spot in standard TSGV evaluation: all existing benchmarks assume that every query has a valid temporal span in the video. In practice, some queries are unanswerable — the relevant content simply does not exist. NA-VMR proposes metrics that penalize false positive moment predictions for unanswerable queries. This is directly relevant to this project's requirement of marking one question per lecture as unanswerable, and motivates including unanswerable questions in evaluation to test retrieval robustness.

**CALCE** (Xie et al., 2025) proposes a coarse-to-fine retrieval framework in which frame captions assist multimodal LLMs in temporal localization. The coarse stage uses caption similarity to narrow candidate segments; the fine stage applies full MLLM reasoning to rerank them. The core finding — that frame captions measurably improve temporal retrieval accuracy over text-only retrieval — is the primary motivation for including the transcript-plus-frame-caption retrieval configuration in this project as a required experimental condition.

### 2.3 Gap Analysis

TSGV research has focused predominantly on short videos (ActivityNet-Captions, TACoS, Charades-STA) with clips under 3 minutes. Evaluation typically assumes a single relevant moment per query, while lecture content may have multiple relevant spans (e.g., a concept introduced early and revisited later). Additionally, TSGV systems directly predict temporal spans from video features, whereas this project uses a retrieval pipeline that maps questions to pre-indexed chunks — an approach that is computationally lighter and easier to update, but that has not been systematically evaluated in the temporal grounding literature.

---

## 3. Retrieval-Augmented Generation

### 3.1 Overview

Retrieval-Augmented Generation (RAG) is a paradigm introduced to address the fundamental limitations of parametric language models: their knowledge is static (fixed at training time), they cannot cite sources, and they hallucinate when queried on content not well represented in training data. RAG solves this by maintaining an external knowledge store, retrieving relevant documents at query time, and conditioning generation on the retrieved context.

> **RAG in plain terms for this project:** The vector database stores transcript chunks from lecture videos. When a user asks a question, the system embeds the question, finds the most similar transcript chunks (by cosine similarity), and passes those chunks to the LLM with a prompt that says "answer using only these excerpts and cite the timestamp of each one you use."

### 3.2 Key Works

**Lewis et al. (2020)** introduce the original RAG framework, combining Dense Passage Retrieval (DPR) with a BART-based sequence-to-sequence generator. They demonstrate that retrieved-context generation outperforms parametric-only models on open-domain QA benchmarks (Natural Questions, TriviaQA, WebQuestions). The two key architectural choices — a bi-encoder retriever for scalable similarity search and a grounded generation prompt that conditions only on retrieved documents — are directly adopted in this project. The lecture transcript chunks in this project are analogous to the Wikipedia passages in Lewis et al.

**Wampler et al. (2025)** provide a comprehensive review of RAG system architectures from 2018 to 2025, covering chunking strategies, embedding model selection, vector database options, and reranking approaches. Their analysis of chunking is particularly relevant: they find that fixed-size windows (the approach prescribed in this project) are the most common baseline, while sentence-boundary-aware chunking can improve retrieval precision. They also identify a consistent finding that chunk size significantly impacts retrieval quality: chunks that are too short lose context; chunks that are too long dilute the relevant signal. The 45-second window prescribed for this project falls within their recommended range for spoken-language content.

**Amugongo et al. (2025)** survey RAG in healthcare and provide a detailed failure mode taxonomy: retrieval failure (the relevant chunk is not retrieved), grounding failure (the LLM ignores retrieved context), citation failure (cited passages do not support the claim), and hallucination despite retrieval. This taxonomy directly structures the failure mode analysis section required in the project report.

### 3.3 Gap Analysis

The RAG literature has focused exclusively on text documents (Wikipedia, PubMed, legal texts, code). No existing RAG evaluation protocol accounts for **temporal metadata** attached to retrieved chunks, **timestamp-formatted citations**, or **temporal IoU as a retrieval metric**. Standard RAG metrics (Recall@k, MRR, NDCG) measure whether the correct document is retrieved, but not whether the correct *time window* within a long document is retrieved. This project introduces temporal IoU and hit rate at k as RAG-native metrics for the video domain.

---

## 4. Multimodal Models and Frame Captioning

### 4.1 Overview

The transcript-plus-frame-caption retrieval configuration in this project requires extracting visual information from video keyframes and representing it as text that can be embedded alongside transcript chunks. Two families of models are relevant: vision-language models for image captioning, and multimodal LLMs that combine visual encoders with language models.

### 4.2 Key Works

**BLIP-2** (Li et al., 2023) introduces a Querying Transformer (Q-Former) that bridges a frozen image encoder (CLIP ViT-G) and a frozen LLM (OPT or FlanT5) for image captioning and visual QA. Because both the image encoder and LLM are frozen, BLIP-2 requires no task-specific fine-tuning — it can generate descriptive captions of lecture slides and whiteboard content out of the box. This makes it the primary candidate for the frame captioning component. A BLIP-2 caption of a slide showing a merge sort diagram would produce text like "A diagram showing the merge sort algorithm with arrays being split and merged recursively" — text that is then embedded alongside the transcript chunk and indexed into ChromaDB.

**Yin et al. (2023)** survey multimodal LLMs including GPT-4V, LLaVA, and InstructBLIP, covering the spectrum of vision-language integration approaches. Their analysis clarifies the trade-off between lightweight CLIP-based zero-shot captioning (fast, no GPU required for inference, lower caption quality) and full MLLM captioning (BLIP-2, LLaVA — richer descriptions, requires GPU). For this project, the choice between CLIP zero-shot and BLIP-2 is a key pending decision that should be evaluated empirically and reported.

**Gong et al. (2023)** analyze Whisper's internal audio representations through the lens of audio event tagging, finding that Whisper's features are correlated with non-speech sounds (music, audience noise, slide transitions). This suggests that Whisper is robust to the kinds of background audio typical in lecture recordings — audience questions, projector hum, marker-on-whiteboard sounds — making it a reliable choice for lecture transcription without additional noise filtering.

**Rouditchenko et al. (2024)** extend Whisper with lip-reading visual features (Whisper-Flamingo), improving recognition in noisy environments. While not directly applicable (lecture recordings lack synchronized lip video), this work motivates future exploration of slide-conditioned transcription correction as a way to improve accuracy on technical terminology.

### 4.3 Gap Analysis

Frame captioning for lecture videos has not been systematically studied. Existing captioning models are evaluated on natural scene images (COCO, NoCaps) and do not account for the specific visual vocabulary of academic slides: mathematical notation, algorithm pseudocode, graph diagrams, and whiteboard equations. The quality of frame captions for these visual types may be substantially lower than for natural images, potentially limiting the gains from the transcript-plus-frames retrieval configuration. This is an important failure mode to investigate and report.

---

## 5. Automatic Speech Recognition and Transcription

### 5.1 Overview

Automatic speech recognition (ASR) quality is the foundation of the entire pipeline. Word-level timestamp accuracy determines the precision of temporal span annotations; transcription errors propagate into chunking, embedding, retrieval, and QA generation. The choice of ASR model and its configuration is therefore the highest-leverage decision in the data preparation phase.

### 5.2 Key Works

Whisper (Radford et al., 2022, referenced via Gong et al., 2023 and Rouditchenko et al., 2024) is a general-purpose speech recognition model trained on 680,000 hours of weakly supervised internet audio. Its `large-v3` variant achieves state-of-the-art word error rate (WER) across diverse languages and acoustic conditions. The `word_timestamps=True` flag enables word-level timestamp extraction essential for precise temporal span annotation. For lecture audio — relatively clean, single-speaker, English — `whisper-large-v3` consistently achieves WER under 5%, making transcript quality a minor concern compared to the downstream chunking and retrieval quality.

### 5.3 Gap Analysis

No prior work has systematically evaluated Whisper's timestamp accuracy for lecture content specifically. Technical terminology (algorithm names, mathematical terms, author citations) may be transcribed incorrectly, potentially causing retrieval failures for queries containing those terms. A brief WER analysis on a held-out lecture segment would strengthen the pipeline validation section of the report.

---

## 6. Educational Video Understanding and QA Generation

### 6.1 Overview

The QA generation component of this project — using an LLM to generate question-answer pairs conditioned on transcript chunks — is an instance of automatic question generation (AQG), a field with roots in educational technology. Generating high-quality questions for benchmarks requires not only linguistic fluency but conceptual correctness, appropriate difficulty calibration, and resistance to answer leakage (where the answer is trivially extractable from the question stem).

### 6.2 Key Works

**Mane et al. (2025)** propose the closest existing system to this project's QA generation pipeline: a Whisper-to-Flan-T5 pipeline that transcribes live lecture audio and generates contextually relevant questions in real time. They validate on a small set of engineering lectures and find that Flan-T5 produces fluent but occasionally shallow questions that can be answered without watching the video. This motivates the human review step in this project — the LLM-generated questions must be verified by watching the cited video span and rewritten or rejected if they are trivially answerable from the question text alone.

**Vachev et al. (2021)** address answer-aware question generation and distractor generation for educational quizzes. The answer-aware framing — conditioning the question generator on a specific answer span — is analogous to this project's approach of conditioning on a specific transcript chunk. Their finding that QA quality degrades when the answer is generated jointly with the question (as opposed to separately conditioning on a known answer span) supports the design choice of generating answers from specific chunks rather than from the full lecture transcript.

### 6.3 Gap Analysis

No existing system generates lecture video QA pairs with **temporal span annotations** and evaluates them through a retrieval pipeline. Mane et al. (2025) generate questions from transcripts but do not annotate timestamps or evaluate retrieval. Vachev et al. (2021) address text-only educational QA without any video grounding. The benchmark constructed in this project is the first (to our knowledge) to combine lecture-domain QA generation with temporal span annotation and RAG pipeline evaluation.

---

## 7. Overall Gap Analysis and Project Positioning

Across all five clusters, a convergent gap emerges:

| Dimension | Existing Work | This Project |
|-----------|--------------|-------------|
| Video domain | Egocentric, movie, sports, news | Academic lectures (MIT OCW, Stanford) |
| Video length | Clips <3 min (mostly) | Full lectures, 60–90 min |
| QA grounding | Multiple choice or free-form | Timestamp-grounded with citation |
| Retrieval evaluation | Document recall, MRR | Temporal IoU, Hit Rate@k |
| Two modalities | Visual-only or text-only | Transcript + frame captions (compared) |
| Unanswerable Qs | Rare in benchmarks | Required (1 per lecture) |
| Citation format | None / title+URL | `[video_id @ mm:ss to mm:ss]` with deep link |

The combination of long-form academic lecture content, transcript-chunk retrieval with temporal IoU evaluation, and a required comparison between text-only and multimodal retrieval configurations positions this benchmark as a novel contribution at the intersection of temporal grounding, RAG evaluation, and educational video understanding. The closest related work (EgoSchema for long-form QA; Lewis et al. for RAG; Zhang et al. for temporal grounding) addresses each dimension in isolation; no prior work integrates all three.

---

## References

1. Mangalam, K., Akshulakov, R., & Malik, J. (2023). *EgoSchema: A Diagnostic Benchmark for Very Long-form Video Language Understanding*. arXiv:2308.09126. https://arxiv.org/abs/2308.09126v1

2. Cheng, Z., Hu, J., Liu, Z., Si, C., Li, W., et al. (2025). *V-STaR: Benchmarking Video-LLMs on Video Spatio-Temporal Reasoning*. arXiv:2503.11495. https://arxiv.org/abs/2503.11495v1

3. Song, Chai, Ye, Hwang, Li, et al. (2025). *MovieChat+: Question-Aware Sparse Memory for Long Video Question Answering*. PubMed.

4. Zhao, Rao, Tang, Zhou, & Lu. (2022). *VideoABC: A Real-World Video Dataset for Abductive Visual Reasoning*. PubMed.

5. Zhang, Li, Zhang, & Bai. (2025). *Dual-level Dynamic Heterogeneous Graph Network for Video Question Answering*. PubMed.

6. Zhang, Sun, Jing, & Zhou. (2023). *Temporal Sentence Grounding in Videos: A Survey and Future Directions*. PubMed.

7. Flanagan, K., Damen, D., & Wray, M. (2025). *Moment of Untruth: Dealing with Negative Queries in Video Moment Retrieval*. arXiv:2502.08544. https://arxiv.org/abs/2502.08544v2

8. Xie, Li, Lu, Xu, & Zhang. (2025). *Caption Assisted Multimodal Large Language Model for Video Moment Retrieval (CALCE)*. PubMed.

9. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401. https://arxiv.org/abs/2005.11401v4

10. Wampler, D., Nielson, D., & Seddighi, A. (2025). *Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems*. arXiv:2601.05264. https://arxiv.org/abs/2601.05264v1

11. Amugongo, Mascheroni, Brooks, Doering, & Seidel. (2025). *Retrieval Augmented Generation for Large Language Models in Healthcare: A Systematic Review*. PubMed.

12. Li, J., Li, D., Savarese, S., & Hoi, S. C. H. (2023). *BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models*. arXiv:2301.12597. http://arxiv.org/pdf/2301.12597

13. Yin, S., Fu, C., Zhao, S., Li, K., Sun, X., et al. (2023). *A Survey on Multimodal Large Language Models*. arXiv:2306.13549. https://arxiv.org/abs/2306.13549v4

14. Gong, Y., Khurana, S., Karlinsky, L., & Glass, J. (2023). *Whisper-AT: Noise-Robust Automatic Speech Recognizers are Also Strong General Audio Event Taggers*. arXiv:2307.03183. https://arxiv.org/abs/2307.03183v1

15. Rouditchenko, A., Gong, Y., Thomas, S., Karlinsky, L., Kuehne, H., et al. (2024). *Whisper-Flamingo: Integrating Visual Features into Whisper for Audio-Visual Speech Recognition and Translation*. arXiv:2406.10082. https://arxiv.org/abs/2406.10082v3

16. Mane, D., Nimbalkar, R., Gavali, S., Deogade, S., & Khopade, S. (2025). *Real-Time Question Generation from Educational Video Lectures using Deep Learning*. Semantic Scholar. [PAYWALLED]

17. Vachev, K., Hardalov, M., Karadzhov, G., Georgiev, G., Koychev, I., et al. (2021). *Generating Answer Candidates for Quizzes and Answer-Aware Question Generators*. arXiv:2108.12898. https://arxiv.org/abs/2108.12898v1

18. Muksimova, S., Umirzakova, S., Sultanov, M., & Cho, Y.-I. (2025). *Cross-Modal Transformer-Based Streaming Dense Video Captioning with Neural ODE Temporal Localization*. Sensors. https://doi.org/10.3390/s25030707
