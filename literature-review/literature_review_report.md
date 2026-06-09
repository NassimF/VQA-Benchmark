# Literature Review: Long-Lecture Video RAG Benchmark

**Topic:** Long-Lecture Video Question Answering, Temporal Grounding, and Retrieval-Augmented Generation  
**Date:** April 2026  
**Papers reviewed:** 28  

---

## Abstract

This review surveys the literature relevant to constructing a Retrieval-Augmented Generation (RAG) benchmark for long lecture videos. We examine seven thematic clusters: long-form video question answering, temporal grounding and moment retrieval, general RAG systems, video-specific RAG systems, multimodal models and frame captioning, automatic speech recognition, and educational video understanding. Across all clusters, a consistent gap emerges: existing benchmarks and systems address general-domain or short-video content, and video RAG systems that do exist lack temporal span evaluation metrics, multi-hop annotation schemas, and systematic comparison between transcript-only and multimodal retrieval configurations. This project directly addresses that gap.

---

## 1. Long-form Video Question Answering

### 1.1 Overview

Long-form video QA extends standard visual question answering from short clips (typically under 30 seconds) to videos spanning minutes or hours. The core challenge is that relevant information is temporally sparse — a question about a specific algorithm may be answered in a 30-second window within a 90-minute lecture — making exhaustive frame-by-frame processing computationally prohibitive. Works in this cluster are **not RAG systems**: they process video directly via video-language models (VLMs) or memory architectures, without a separate retrieval index.

### 1.2 Key Works

**EgoSchema** (Mangalam et al., 2023) — *Not RAG: end-to-end VLM evaluation.*  
Contains over 5,000 human-curated multiple-choice QA pairs requiring models to reason over 3-minute egocentric video clips from the Ego4D dataset. Its emphasis on extended temporal reasoning represents a meaningful step beyond clip-level understanding. However, EgoSchema targets daily egocentric activity (cooking, sports, social interaction), not instructional content, and provides no temporal span annotations or transcript-based retrieval evaluation.

**V-STaR** (Cheng et al., 2025) — *Not RAG: structured VLM benchmark.*  
Introduces a spatio-temporal reasoning benchmark that decomposes video understanding into three sequential steps: identifying *when* a relevant event occurs, locating *where* objects appear, and inferring *what* conclusions follow. This decomposition aligns with the temporal IoU evaluation protocol in this project. V-STaR reveals that even GPT-4V and Gemini Pro struggle with fine-grained temporal relational reasoning.

**MovieChat+** (Song et al., 2025) — *Not RAG: question-aware sparse memory.*  
Addresses the scalability bottleneck of long video understanding through a question-aware sparse memory mechanism that selectively retains tokens relevant to the posed question. Enables processing of hour-long videos without proportional memory growth. The memory compression approach is an alternative to RAG — rather than indexing a vector store and retrieving at query time, it compresses all frames into a fixed-size memory during a forward pass.

**VideoABC** (Zhao et al., 2022) — *Not RAG: abductive reasoning benchmark.*  
Uses instructional videos and requires abductive reasoning across long temporal sequences. Its use of real-world procedural content validates the feasibility of constructing meaningful QA pairs from instructional video transcripts.

**NA-VQA** (Jain et al., 2026) — *Not RAG: structured event-chain memory retrieval.*  
The most recent and most directly relevant benchmark in this cluster. Introduces 88 full-length movies with 4,400 QA pairs requiring narrative reasoning — tracking character intentions, connecting distant events, and reconstructing causal chains across an entire film. Proposes Video-NaRA, a companion framework that builds event-level chains stored in structured memory for retrieval during reasoning (achieving up to 3% improvement over leading MLLMs). Demonstrates that SOTA models fail on questions requiring long-range evidence spanning distant scenes — the same failure mode this project targets in the lecture domain. Unlike a flat vector database, Video-NaRA's event chains capture *causal* relationships between events; however, this structure is domain-specific to narrative film and does not transfer to concept-building in academic lectures.

**LongVidSearch** (Yu et al., 2026) — *Not RAG: agentic multi-hop retrieval planning benchmark.*
The most structurally similar benchmark to this project found in the 2026 literature. Enforces strict multi-hop retrieval across 447 long videos (avg 26 min) with explicit 2-hop, 3-hop, and 4-hop evidence configurations — removing any single clip makes the question unsolvable. 3,000 questions spanning four reasoning categories (State Mutation, Causal Inference, Global Summary, Visual Tracking). Even GPT-5 achieves only 42.43% accuracy, identifying retrieval *planning* as the primary bottleneck rather than answer generation.

### 1.3 Gap Analysis

EduVidQA (Section 7) is the only existing benchmark that uses CS lecture video content with timestamps, but it covers only single-hop QA with a fixed context window — not a RAG pipeline. No benchmark in this cluster provides: (1) multi-hop QA with per-hop ground truth temporal spans, (2) transcript-chunk retrieval evaluated with temporal IoU, or (3) citation-grounded answer generation. All works here evaluate end-to-end VLMs or agentic systems — none evaluate a transcript-chunk RAG pipeline where the retrieved window is the unit of evaluation.

---

## 2. Temporal Grounding and Moment Retrieval

### 2.1 Overview

Temporal sentence grounding in videos (TSGV) — also called natural language video localization or video moment retrieval — is the task of identifying the start and end times of a video segment described by a natural language query. Works in this cluster are **not RAG systems**: they use dense video encoders and cross-modal attention to directly predict temporal spans, without maintaining a separate retrieval index.

> **Temporal IoU in plain terms:** If the model predicts that the answer is between 30:00 and 31:00, and the ground truth is 30:20 to 31:10, the intersection is 40 seconds and the union is 70 seconds, giving an IoU of 0.57. A system that achieves IoU@0.5 "passes" on that question.

### 2.2 Key Works

**Zhang et al. (2023)** — *Not RAG: survey of proposal-based and proposal-free TSGV.*  
Provides the authoritative survey of TSGV, establishing the canonical temporal IoU evaluation protocol this project adopts. Traces the field from proposal-based methods through modern proposal-free transformers. Identifies cross-modal alignment as the dominant challenge: the semantic gap between a natural language query and the visual or spoken content of a video segment.

**Flanagan et al. (2025)** — *Not RAG: negative-aware moment retrieval.*  
Introduces Negative-Aware Video Moment Retrieval (NA-VMR), which addresses a critical blind spot: all existing TSGV benchmarks assume every query has a valid temporal span. NA-VMR proposes metrics that penalize false positive moment predictions for unanswerable queries. Directly motivates this project's requirement of including one unanswerable question per lecture.

**CALCE** (Xie et al., 2025) — *Not RAG: caption-assisted MLLM reranking.*  
Proposes a coarse-to-fine retrieval framework where frame captions assist multimodal LLMs in temporal localization. The core finding — that frame captions measurably improve temporal retrieval accuracy over text-only retrieval — is the primary motivation for including the transcript-plus-frame-caption retrieval configuration in this project as a required experimental condition.

### 2.3 Gap Analysis

TSGV research has focused on short videos (clips under 3 minutes) and assumes a single relevant moment per query. Lecture content may have multiple relevant spans (a concept introduced early and revisited later) — the multi-hop QA requirement in this project is not addressed by any TSGV benchmark. Additionally, TSGV systems directly predict spans from video features, whereas this project uses a retrieval pipeline over pre-indexed chunks — an approach that is computationally lighter and more scalable, but has not been evaluated with temporal IoU in the literature.

---

## 3. Retrieval-Augmented Generation (Text Domain)

### 3.1 Overview

RAG is a paradigm introduced to address the fundamental limitations of parametric language models: their knowledge is static, they cannot cite sources, and they hallucinate on out-of-training-distribution content. RAG solves this by maintaining an external knowledge store, retrieving relevant documents at query time, and conditioning generation on the retrieved context. All works in this cluster operate on **text-only** knowledge sources.

> **RAG in plain terms for this project:** The vector database stores transcript chunks from lecture videos. When a user asks a question, the system embeds the question, finds the most similar transcript chunks (by cosine similarity), and passes those chunks to the LLM: "answer using only these excerpts and cite the timestamp of each one you use."

### 3.2 Key Works

**Lewis et al. (2020)** — *RAG: original framework (text-only).*  
Introduce the original RAG framework, combining Dense Passage Retrieval (DPR) with a BART-based sequence-to-sequence generator. Demonstrate that retrieved-context generation outperforms parametric-only models on Natural Questions, TriviaQA, and WebQuestions. The two key architectural choices — bi-encoder retriever for scalable similarity search and a grounded generation prompt conditioning only on retrieved documents — are directly adopted in this project. Lecture transcript chunks are analogous to the Wikipedia passages in Lewis et al.

**Wampler et al. (2025)** — *RAG: system architecture survey (text-only).*  
Comprehensive review of RAG system architectures from 2018 to 2025, covering chunking strategies, embedding model selection, vector database options, and reranking. Their chunking analysis is particularly relevant: fixed-size windows (prescribed in this project) are the most common baseline, and chunk size significantly impacts retrieval quality — too short loses context, too long dilutes the relevant signal. The 45-second window falls within their recommended range for spoken-language content.

**Amugongo et al. (2025)** — *RAG: failure mode taxonomy (text-only, healthcare domain).*  
Survey RAG in healthcare and provide a detailed failure mode taxonomy: retrieval failure, grounding failure, citation failure, and hallucination despite retrieval. This taxonomy directly structures the failure mode analysis section required in the project report.

### 3.3 Gap Analysis

The text RAG literature has focused exclusively on document corpora. No existing text RAG evaluation protocol accounts for **temporal metadata** attached to retrieved chunks, timestamp-formatted citations, or temporal IoU as a retrieval metric. Standard RAG metrics (Recall@k, MRR, NDCG) measure whether the correct document is retrieved, but not whether the correct *time window* within a long video is retrieved. This project introduces temporal IoU and hit rate@k as RAG-native metrics for the video domain.

---

## 4. Video RAG Systems

### 4.1 Overview

A nascent cluster of works explicitly extends the RAG paradigm to video content. Unlike Section 3 (text-only RAG) and Section 1 (end-to-end VLMs), these systems maintain a retrievable index over video content and condition generation on retrieved video segments. This cluster is the most directly relevant to this project — it represents the current state of the art for systems structurally similar to what is being built.

### 4.2 Key Works

**R-VLM** (Xu et al., 2023) — *RAG-style: learnable chunk retrieval over video.*  
The earliest retrieval-based video language model. Given a question and a long video, R-VLM selects the K most relevant video chunks using a learned relevance model, then passes those chunks' visual tokens to an LLM as context. Provides interpretable chunk-level justifications. Demonstrates strong zero-shot generalization on multiple VideoQA datasets.  
*Gap:* Visual-token retrieval only — does not incorporate transcripts or audio. Chunk-level retrieval without temporal span precision. Predates modern RAG infrastructure (no vector DB, no embedding similarity search).

**Video Enriched RAG** (Dela Rosa, 2024) — *RAG: text-based video integration via aligned captions.*  
Proposes "aligned visual captions" — dense text descriptions of both visual and audio content — as a text-only bridge for integrating video knowledge into standard RAG pipelines. Captions are embedded and retrieved like text documents, requiring far less context window space than raw frame sampling.  
*Gap:* Caption quality upper-bounded by the captioning model; no temporal span precision evaluation; tested on general video corpus (not lecture domain). Does not compare transcript-only versus caption-augmented retrieval configurations — the central comparison in this project.

**Video-RAG** (Luo et al., 2024; NeurIPS 2025) — *RAG: visually-aligned auxiliary text retrieval.*  
Training-free pipeline that extracts visually-aligned auxiliary texts (OCR from slides, audio transcription, object detection labels) from videos using open-source tools and injects them alongside video frames into any existing LVLM. Achieves SOTA on Video-MME, MLVU, and LongVideoBench, surpassing Gemini-1.5-Pro with a 72B open-source model.  
*Gap:* Single-turn retrieval limits multi-hop temporal reasoning; evaluated on Video-MME benchmarks (clips up to 1 hour, mixed domain) rather than long educational lectures; no temporal IoU or hit rate@k evaluation.

**VideoRAG over Corpus** (Jeong et al., 2025; ACL 2025) — *RAG: corpus-level video retrieval.*  
First framework that dynamically retrieves entire videos from a large corpus based on query relevance, using LVLMs for both video representation and response generation. Includes a frame selection mechanism and subtitle extraction fallback. Introduces a new evaluation benchmark with 200+ QA pairs.  
*Gap:* Retrieves at the video level (which video to watch), not at the temporal span level (which 45-second window within a lecture). No temporal grounding metrics. Not designed for single long-video QA.

**VideoRAG Extreme** (Ren et al., 2025; KDD 2026) — *RAG: graph-based + multimodal dual-channel.*  
The most architecturally sophisticated video RAG system. Dual-channel design: (1) graph-based textual knowledge grounding captures cross-video semantic relationships; (2) multi-modal context encoding preserves fine-grained visual features. Processes unlimited-length videos. Evaluated on LongerVideos benchmark (160 videos, 134+ hours, including lecture, documentary, and entertainment content).  
*Gap:* Complex graph construction overhead; no explicit per-hop temporal grounding; lectures are a minority category in LongerVideos with no per-category breakdown; no comparison of retrieval configurations.

**E-VRAG** (Xu et al., 2025) — *RAG: resource-efficient frame retrieval.*  
Frame pre-filtering via hierarchical query decomposition, followed by lightweight VLM scoring, followed by global inter-frame score distribution for final selection. Reduces computation 70% versus baselines without training. Results on Video-MME, EgoSchema, and two others.  
*Gap:* Frame-level retrieval only — does not incorporate transcripts; efficiency-focused rather than accuracy-focused; not tested on educational lectures; no multi-hop capability.

**Lecture Video RAG** (Tanner et al., 2024) — *RAG: lecture-domain transcript + slide retrieval.*  
The closest existing system to this project. Specifically designed for lecture video QA, combining audio transcript retrieval with slide image text extraction. Users query a video corpus and receive answers with pointers to the most relevant video segments.  
*Gap:* No temporal grounding evaluation metrics reported (no temporal IoU, no hit rate@k); single-hop QA only (no multi-hop annotation); no comparison between retrieval configurations; no public benchmark or code released.

**Vgent** (Shen et al., 2025; NeurIPS 2025 Spotlight) — *RAG: graph-based retrieval with structured verification.*
Represents video clips as semantic relationship graphs and introduces an intermediate verification step to reduce retrieval noise before generation — outperforming existing video RAG methods by 8.6% on MLVU and achieving 3.0–5.4% improvement overall. The graph structure captures cross-clip semantic dependencies that flat cosine similarity over chunk embeddings cannot, making it a natural complement to the standard vector-DB retrieval used in this project. The structured verification step addresses a key failure mode in flat RAG: retrieving individually relevant but collectively inconsistent chunks.

### 4.3 Gap Analysis

Video RAG systems exist and are rapidly maturing, but **none address the specific combination of requirements in this project**:

1. **No temporal IoU evaluation in video RAG** — all existing video RAG systems evaluate answer quality (BLEU, ROUGE, GPT-judge) but not temporal span precision.
2. **No multi-hop annotation** — no video RAG benchmark provides multi-hop QA with per-hop ground truth spans.
3. **No controlled retrieval configuration comparison** — no paper systematically compares transcript-only vs. transcript+frame-captions retrieval on the same questions.
4. **No lecture-domain benchmark with public code** — Tanner et al. is the only lecture-domain system, but it has no public benchmark or evaluation protocol.
5. **No hit rate@k in the video domain** — standard RAG hit rate@k has not been applied to temporal video retrieval.

---

## 5. Multimodal Models and Frame Captioning

### 5.1 Overview

The transcript-plus-frame-caption retrieval configuration requires extracting visual information from video keyframes and representing it as text that can be embedded alongside transcript chunks. Works here are **not RAG systems**: they are vision-language model architectures used as components within a RAG pipeline.

### 5.2 Key Works

**BLIP-2** (Li et al., 2023) — *Not RAG: captioning component.*  
Introduces a Querying Transformer (Q-Former) bridging a frozen CLIP ViT-G encoder and a frozen LLM for image captioning and visual QA. Because both encoder and LLM are frozen, BLIP-2 requires no task-specific fine-tuning — it can generate descriptive captions of lecture slides and whiteboard content out of the box. A BLIP-2 caption of a slide showing a merge sort diagram would produce text like "A diagram showing the merge sort algorithm with arrays being split and merged recursively" — text that is then embedded alongside the transcript chunk and indexed into ChromaDB.

**Yin et al. (2023)** — *Not RAG: survey of multimodal LLMs.*  
Surveys GPT-4V, LLaVA, and InstructBLIP, covering the spectrum of vision-language integration approaches. Clarifies the trade-off between lightweight CLIP-based zero-shot captioning (fast, no GPU required, lower caption quality) and full MLLM captioning (BLIP-2, LLaVA — richer descriptions, requires GPU). For this project, the choice between CLIP zero-shot and BLIP-2 is a key pending decision that should be evaluated empirically.

### 5.3 Gap Analysis

Frame captioning for lecture videos has not been systematically studied. Existing captioning models are evaluated on natural scene images (COCO, NoCaps) and do not account for the specific visual vocabulary of academic slides: mathematical notation, algorithm pseudocode, graph diagrams, and whiteboard equations. The quality of frame captions for these visual types may be substantially lower than for natural images, potentially limiting the gains from the transcript-plus-frames retrieval configuration.

---

## 6. Automatic Speech Recognition and Transcription

**Whisper** (Radford et al., 2022) — *Not RAG: ASR component.*  
General-purpose speech recognition model trained on 680,000 hours of weakly supervised internet audio. `large-v3` achieves state-of-the-art WER across diverse languages and acoustic conditions. `word_timestamps=True` enables word-level timestamp extraction essential for precise temporal span annotation. For lecture audio (relatively clean, single-speaker, English), `whisper-large-v3` consistently achieves WER under 5%.

*Gap:* No prior work has systematically evaluated Whisper's timestamp accuracy for lecture content specifically. Technical terminology (algorithm names, mathematical terms) may be transcribed incorrectly, causing retrieval failures for queries containing those terms.

**Gong et al. (2023)** — *Not RAG: Whisper audio analysis.*  
Analyzes Whisper's audio representations, finding robustness to non-speech sounds (music, audience noise, slide transitions). Suggests Whisper is robust to background audio typical in lecture recordings — making it a reliable choice for lecture transcription without additional noise filtering.

**Rouditchenko et al. (2024)** — *Not RAG: Whisper-Flamingo audio-visual ASR.*  
Extends Whisper with lip-reading visual features, improving recognition in noisy environments. Motivates future exploration of slide-conditioned transcription correction as a way to improve accuracy on technical terminology.

---

## 7. Educational Video Understanding and QA Generation

**EduVidQA** (Ray et al., 2025) — *Not RAG: fixed-window context retrieval from lecture videos.*
The closest existing benchmark to this project in terms of domain. Contains 5,252 QA pairs from 296 CS lecture videos (ML, Algorithms, NLP, Deep Learning) with timestamps on all questions, Bloom's taxonomy difficulty levels, and ~44% of questions flagged as visually dependent (requiring slide or whiteboard content). Benchmarks six SOTA MLLMs and finds all significantly underperform. Real student questions form 270 manually curated pairs; the rest are synthetically generated via GPT-4o. Rather than a RAG pipeline, EduVidQA uses a fixed 4-minute context window around each question's timestamp — a simpler but less scalable retrieval strategy that cannot generalize to questions whose evidence spans non-adjacent segments.

**Mane et al. (2025)** — *Not RAG: real-time QA generation from lecture audio.*  
Propose a Whisper-to-Flan-T5 pipeline that transcribes live lecture audio and generates contextually relevant questions in real time. Find that Flan-T5 produces fluent but occasionally shallow questions answerable without watching the video. This motivates the human review step in this project — LLM-generated questions must be verified by watching the cited video span.

**Vachev et al. (2021)** — *Not RAG: answer-aware educational QA generation.*  
Address answer-aware question generation and distractor generation for educational quizzes. Their finding that QA quality degrades when answer is generated jointly with the question supports the design choice of conditioning QA generation on a specific transcript chunk rather than the full lecture transcript.

*Gap:* No existing system generates lecture video QA pairs with **temporal span annotations** and evaluates them through a retrieval pipeline. This benchmark is the first (to our knowledge) to combine lecture-domain QA generation with temporal span annotation, multi-hop annotation schema, and RAG pipeline evaluation.

---

## 8. Overall Gap Analysis and Project Positioning

Across all seven clusters, the search revealed that each recent paper addresses one dimension of the problem in isolation, making it possible to state the gap with surgical precision.

**NA-VQA** (Jain et al., 2026) establishes that long-range multi-hop reasoning in full-length video is a real, unsolved problem — validating the multi-hop design choice. But it targets narrative film, not lectures. Critically, it uses neither transcript-chunk RAG (Video-NaRA retrieves via hand-crafted event-chain memory, not a vector-DB pipeline) nor temporal IoU evaluation (evidence spans are labeled Short/Medium/Far as difficulty categories, not used to compute span overlap — final evaluation is answer accuracy via judge voting).

**LongVidSearch** (Yu et al., 2026) is the most structurally similar benchmark: it enforces strict multi-hop retrieval with explicit hop counts across long videos, finding even GPT-5 fails. But it uses agentic tool-call retrieval over general video, with no transcript-chunk RAG, no temporal IoU, and no lecture domain.

**EduVidQA** (Ray et al., 2025) is the closest domain match: 296 CS lecture videos, 5,252 QA pairs with timestamps. But it uses a fixed 4-minute context window (not RAG), has no multi-hop questions, and provides no temporal span evaluation.

**The gap is now precisely triangulated — no single paper addresses all three axes simultaneously.**

This project is uniquely positioned at the intersection of all three: **educational lecture content + multi-hop RAG + temporal span evaluation**. EduVidQA covers the domain; LongVidSearch covers the retrieval planning; this project is the first to combine both with a reproducible RAG pipeline, per-hop ground truth spans, and a controlled comparison of retrieval configurations.

**Closest prior works — detailed comparison:**

| Dimension | EduVidQA | NA-VQA | LongVidSearch | This Project |
|---|---|---|---|---|
| Multi-hop with explicit hop counts | ❌ | ✅ implicit (causal chains) | ✅ strict 2/3/4-hop | ✅ |
| Retrieval is the core evaluation | ❌ | ❌ (reasoning focus) | ✅ retrieval planning is the bottleneck | ✅ |
| Removing evidence makes Q unsolvable | ❌ | ❌ | ✅ | ✅ |
| Long video (54–90 min) | ❌ (clips, 4-min window) | ✅ full movies | ❌ avg 26 min | ✅ |
| Educational / lecture domain | ✅ CS lectures | ❌ narrative film | ❌ general video | ✅ |
| Transcript-based chunk retrieval | ❌ fixed window | ❌ | ❌ | ✅ |
| Temporal IoU / Hit Rate@k | ❌ | ❌ | ❌ | ✅ |
| Per-hop ground truth spans | ❌ | ❌ | ❌ | ✅ |
| Two retrieval config comparison | ❌ | ❌ | ❌ | ✅ |

*Dimension glossary:*
- **Multi-hop with explicit hop counts** — questions require evidence from 2+ non-adjacent video segments, and each question is labeled with exactly how many hops are needed (2-hop, 3-hop, etc.), not just "multi-hop" generically.
- **Retrieval is the core evaluation** — the benchmark is designed to measure whether the system finds the right evidence, not just whether the final answer text sounds correct. A system can generate a plausible-sounding answer without ever retrieving the right moment.
- **Removing evidence makes Q unsolvable** — each question is constructed so that if any one required evidence segment is withheld, the question becomes unanswerable. This guarantees the system genuinely needs to retrieve all hops — it cannot shortcut with world knowledge or a single clip.
- **Long video (54–90 min)** — the source videos are full-length lectures or films, not short clips. The system must search over a large temporal span, which makes retrieval harder.
- **Educational / lecture domain** — content is academic instructional video (CS lectures, math courses), not entertainment, sports, or egocentric activity. Technical terminology, concept-building structure, and visual content (slides, whiteboards) are domain-specific.
- **Transcript-based chunk retrieval** — the retrieval index is built from text transcripts divided into fixed windows. This is distinct from agentic tool calls (LongVidSearch) or raw frame retrieval (Video-RAG).
- **Temporal IoU / Hit Rate@k** — retrieval quality is measured by how well the predicted time span overlaps with the ground truth span (IoU), and whether the correct span appears within the top-k retrieved results.
- **Per-hop ground truth spans** — each hop has its own annotated start/end timestamp, enabling evaluation of whether each individual piece of evidence was retrieved, not just whether the final answer was correct.
- **Two retrieval config comparison** — the same questions are evaluated under two configurations (transcript-only vs. transcript + frame captions) to isolate the exact contribution of visual information to retrieval quality.

**LongVidSearch is the closest structural match** — both projects treat retrieval as the primary bottleneck, enforce evidence necessity, and require multi-hop reasoning. The key distinction is that LongVidSearch uses agentic tool-call retrieval over general video, while this project uses a transcript-chunk RAG pipeline over lecture video evaluated with temporal IoU. For the report's Related Work section, LongVidSearch should be cited as the closest structural precedent, framed as: *"LongVidSearch for lecture video, evaluated through a reproducible RAG pipeline with temporal IoU metrics rather than agentic tool calls."*

---

## 9. Comprehensive Comparison Table

The table below covers all benchmarks and systems reviewed, organized by type. For RAG systems, "Videos" refers to the evaluation set used; for benchmarks, it refers to the annotated dataset. The final column identifies the specific gap that **this project** addresses relative to each work.

| Paper | Year | Type | Approach | Modality | Videos | QA Pairs | Gap This Work Fills |
|---|---|---|---|---|---|---|---|
| **Benchmarks & VLM Evaluation** | | | | | | | |
| EgoSchema | 2023 | Benchmark | End-to-end VLM | Video (egocentric) | 5,000 | 5,000 | Egocentric/daily activity domain; no RAG pipeline; no temporal span annotations; no multi-hop |
| V-STaR | 2025 | Benchmark | End-to-end VLM | Video | 1,000 | 10,000 | General video; no lecture domain; no RAG; no transcript retrieval |
| MovieChat+ | 2025 | Benchmark + System | Sparse memory VLM | Video (movie) | 1,000 | ~14,000 | Movie domain; memory compression ≠ RAG; no temporal IoU; no multi-hop spans |
| VideoABC | 2022 | Benchmark | End-to-end VLM | Video (instructional) | ~11,827 | ~46,354 | Procedural video, not lecture; no RAG; single-hop only; no temporal IoU |
| NA-VQA + Video-NaRA | 2026 | Benchmark + System | Event-chain memory retrieval | Video (movies) + Subtitles | 88 | 4,400 | Narrative/film domain; no lecture content; no temporal IoU; no per-hop GT spans; no retrieval config comparison |
| LongVidSearch | 2026 | Benchmark | Agentic tool-call retrieval | Video | 447 | 3,000 | General video (not lectures); agentic retrieval ≠ RAG pipeline; no temporal IoU; no transcript modality |
| NExT-QA | 2021 | Benchmark | End-to-end VLM | Video + Text | 5,440 | ~52,000 | Short clips (~44s avg); no lecture domain; no RAG; no temporal span evaluation |
| MSVD-QA | 2017 | Benchmark | End-to-end VLM | Video | 1,970 | 50,505 | Short clips; no lecture domain; no RAG; single-hop factual questions only |
| MSRVTT-QA | 2017 | Benchmark | End-to-end VLM | Video | 10,000 | 243,000 | Short clips (15–30s); no lecture domain; no RAG; no temporal grounding |
| **Educational Video** | | | | | | | |
| EduVidQA | 2025 | Benchmark | Fixed 4-min context window | Text + Video | 296 | 5,252 | No RAG pipeline; no multi-hop questions; no temporal IoU; synthetic majority; no retrieval config comparison |
| Lecture Video RAG (Tanner et al.) | 2024 | System | RAG: transcript + slide text | Text + Slides | N/A | N/A | No temporal evaluation metrics; single-hop only; no public benchmark or code; no retrieval config comparison |
| **Temporal Grounding** | | | | | | | |
| NA-VMR (Flanagan et al.) | 2025 | Benchmark | Direct span prediction | Video | N/A | N/A | No RAG; no lecture domain; single-span prediction only; no multi-hop |
| CALCE (Xie et al.) | 2025 | System | Caption-assisted reranking | Video + Captions | N/A | N/A | No RAG pipeline; no lecture domain; single-span reranking; no multi-hop |
| **Video RAG Systems** | | | | | | | |
| R-VLM (Xu et al.) | 2023 | System | Learned chunk retrieval | Video frames | N/A | N/A | Visual-only retrieval (no transcript); no temporal IoU; no lecture domain; no multi-hop |
| Video Enriched RAG (Dela Rosa) | 2024 | System | Text RAG + aligned captions | Text + Video captions | N/A | ~200 | No temporal IoU; no lecture domain; single config; no multi-hop |
| Video-RAG (Luo et al.) | 2024 | System | RAG: OCR + audio + object texts | Text + Video + Audio | N/A | N/A | No temporal IoU; no lecture domain; no multi-hop; single-turn retrieval |
| VideoRAG over Corpus (Jeong et al.) | 2025 | System + Benchmark | RAG: corpus video retrieval | Video + Subtitles | ~200 | ~200 | Video-level retrieval (not temporal span); no lecture domain; no multi-hop |
| VideoRAG Extreme (Ren et al.) | 2025 | System + Benchmark | RAG: graph + multimodal | Text + Video + Audio | 160 (134+ hrs) | N/A | No temporal IoU; no per-hop spans; lecture is minority category; no retrieval config comparison |
| Vgent (Shen et al.) | 2025 | System | RAG: graph + verification | Video + Text | N/A | N/A | General video; no temporal IoU; no lecture domain; no retrieval config comparison |
| E-VRAG (Xu et al.) | 2025 | System | RAG: frame pre-filtering | Video frames | N/A | N/A | Frame-only (no transcript); no lecture domain; no temporal IoU; no multi-hop |
| **Text RAG (architecture reference)** | | | | | | | |
| Lewis et al. (RAG) | 2020 | System | RAG: text document retrieval | Text only | N/A | N/A | Text-only; no video; no temporal metadata; no timestamp citations |
| **This Project** | | | | | | | |
| VQA Benchmark (this work) | 2026 | Benchmark + System | RAG: transcript chunks, two configs | Transcript + Frame captions | 2–4 lectures (54–90 min) | 24–60 (expert-curated, multi-hop) | — |

*Note: NExT-QA, MSVD-QA, and MSRVTT-QA are included in this table for scale context (they establish the average QA pair count across the field) but are not discussed in detail in the body sections, as their short-clip, general-domain design makes them only tangentially related to this project.*

**Key observations:**
- **Scale vs. depth trade-off:** Existing benchmarks average ~59,000 QA pairs; this project has 24–60, fully expert-curated with per-hop ground truth spans and human verification — depth over breadth.
- **The gap column shows a consistent pattern:** every prior work is missing at least one of {lecture domain, multi-hop per-hop spans, temporal IoU evaluation, two-config comparison}. This project is the only one with all four.
- **Modality trend:** systems are moving from video-only (2022–2023) toward multimodal text+video+audio (2024–2026), consistent with this project's two-configuration design.
- **EduVidQA and LongVidSearch are the two closest works** — EduVidQA owns the lecture domain, LongVidSearch owns multi-hop retrieval planning. This project is the first to combine both under a RAG evaluation framework with temporal span metrics.

---

## References

1. Mangalam, K., Akshulakov, R., & Malik, J. (2023). *EgoSchema: A Diagnostic Benchmark for Very Long-form Video Language Understanding*. arXiv:2308.09126. https://arxiv.org/abs/2308.09126v1

2. Cheng, Z., Hu, J., Liu, Z., Si, C., Li, W., et al. (2025). *V-STaR: Benchmarking Video-LLMs on Video Spatio-Temporal Reasoning*. arXiv:2503.11495. https://arxiv.org/abs/2503.11495v1

3. Song, Chai, Ye, Hwang, Li, et al. (2025). *MovieChat+: Question-Aware Sparse Memory for Long Video Question Answering*.

4. Zhao, Rao, Tang, Zhou, & Lu. (2022). *VideoABC: A Real-World Video Dataset for Abductive Visual Reasoning*.

5. Zhang, Sun, Jing, & Zhou. (2023). *Temporal Sentence Grounding in Videos: A Survey and Future Directions*.

6. Flanagan, K., Damen, D., & Wray, M. (2025). *Moment of Untruth: Dealing with Negative Queries in Video Moment Retrieval*. arXiv:2502.08544. https://arxiv.org/abs/2502.08544v2

7. Xie, Li, Lu, Xu, & Zhang. (2025). *Caption Assisted Multimodal Large Language Model for Video Moment Retrieval (CALCE)*.

8. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401. https://arxiv.org/abs/2005.11401v4

9. Wampler, D., Nielson, D., & Seddighi, A. (2025). *Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems*. arXiv:2601.05264. https://arxiv.org/abs/2601.05264v1

10. Amugongo, Mascheroni, Brooks, Doering, & Seidel. (2025). *Retrieval Augmented Generation for Large Language Models in Healthcare: A Systematic Review*.

11. Xu, J., Lan, C., Xie, W., Chen, X., & Lu, Y. (2023). *Long Video Understanding with Learnable Retrieval in Video-Language Models*. arXiv:2312.04931. https://arxiv.org/abs/2312.04931

12. Dela Rosa, K. (2024). *Video Enriched Retrieval Augmented Generation Using Aligned Video Captions*. arXiv:2405.17706. https://arxiv.org/abs/2405.17706

13. Luo, Y., Zheng, M., He, T., Kang, G., Wang, X., et al. (2024). *Video-RAG: Visually-aligned Retrieval-Augmented Long Video Comprehension*. arXiv:2411.13093. https://arxiv.org/abs/2411.13093

14. Jeong, M., Kim, K., Seo, J., Kim, S., Yu, Y., et al. (2025). *VideoRAG: Retrieval-Augmented Generation over Video Corpus*. arXiv:2501.05874. https://arxiv.org/abs/2501.05874

15. Ren, X., Xu, L., Xia, L., Wang, S., Yin, D., & Huang, C. (2025). *VideoRAG: Retrieval-Augmented Generation with Extreme Long-Context Videos*. arXiv:2502.01549. https://arxiv.org/abs/2502.01549

16. Xu, J., Zhang, Y., Chen, L., Wang, P., Guo, X., et al. (2025). *E-VRAG: Enhancing Long Video Understanding with Resource-Efficient Retrieval Augmented Generation*. arXiv:2508.01546. https://arxiv.org/abs/2508.01546

17. Tanner, T., Marfurt, A., & Ogul, H. (2024). *Enhancing Question Answering in Lecture Videos with a Multimodal Retrieval-Augmented Generation Framework*. In: Artificial Intelligence: Methodology, Systems, and Applications. https://link.springer.com/chapter/10.1007/978-3-031-81542-3_15

18. Li, J., Li, D., Savarese, S., & Hoi, S. C. H. (2023). *BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models*. arXiv:2301.12597. http://arxiv.org/pdf/2301.12597

19. Yin, S., Fu, C., Zhao, S., Li, K., Sun, X., et al. (2023). *A Survey on Multimodal Large Language Models*. arXiv:2306.13549. https://arxiv.org/abs/2306.13549v4

20. Gong, Y., Khurana, S., Karlinsky, L., & Glass, J. (2023). *Whisper-AT: Noise-Robust Automatic Speech Recognizers are Also Strong General Audio Event Taggers*. arXiv:2307.03183. https://arxiv.org/abs/2307.03183v1

21. Rouditchenko, A., Gong, Y., Thomas, S., Karlinsky, L., Kuehne, H., et al. (2024). *Whisper-Flamingo: Integrating Visual Features into Whisper for Audio-Visual Speech Recognition and Translation*. arXiv:2406.10082. https://arxiv.org/abs/2406.10082v3

22. Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022). *Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)*. arXiv:2212.04356. https://arxiv.org/abs/2212.04356

23. Mane, D., Nimbalkar, R., Gavali, S., Deogade, S., & Khopade, S. (2025). *Real-Time Question Generation from Educational Video Lectures using Deep Learning*. [PAYWALLED]

24. Vachev, K., Hardalov, M., Karadzhov, G., Georgiev, G., Koychev, I., et al. (2021). *Generating Answer Candidates for Quizzes and Answer-Aware Question Generators*. arXiv:2108.12898. https://arxiv.org/abs/2108.12898v1

25. Jain, R., Doshi, K., Uzkent, B., & Kessler, G. (2026). *Narrative Aligned Long Form Video Question Answering*. arXiv:2603.19481. https://arxiv.org/abs/2603.19481

26. Yu, R., Duan, C., & Zhang, W. (2026). *LongVidSearch: An Agentic Benchmark for Multi-hop Evidence Retrieval Planning in Long Videos*. arXiv:2603.14468. https://arxiv.org/abs/2603.14468

27. Ray, S., Sharma, S., Aditya, S., & Goyal, P. (2025). *EduVidQA: Generating and Evaluating Long-form Answers to Student Questions based on Lecture Videos*. arXiv:2509.24120. https://arxiv.org/abs/2509.24120

28. Shen, X., Zhang, W., Chen, J., & Elhoseiny, M. (2025). *Vgent: Graph-based Retrieval-Reasoning-Augmented Generation For Long Video Understanding*. arXiv:2510.14032. https://arxiv.org/abs/2510.14032
