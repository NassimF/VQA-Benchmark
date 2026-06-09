# Knowledge Graph-Based RAG for Multi-hop Video Question Answering: A Literature Review

**Project context:** Long-Lecture Video RAG Benchmark — a conference paper project building a temporally-grounded QA system over educational lecture videos. The goal of this review is to identify KG-RAG architectures that can be adapted to support multi-hop, temporally-grounded QA over lecture corpora, supplemented by the EduVidQA dataset.

**Scope:** Peer-reviewed papers published **2023–2026** at major venues (ACL, EMNLP, NAACL, CVPR, CIKM, MDPI Applied Sciences, etc.). Papers that are a**rXiv-only are excluded**. Three sections cover: (1) primary clusters of multi-hop KG-RAG for text, GraphRAG pipeline design, and video-specific KG/RAG; (2) a separate section for multimodal image/text KG-RAG papers whose methods are transferable to video; (3) a separate section for single-hop KG-RAG architectures that provide useful building blocks.

---

## 1\. Introduction

Retrieval-Augmented Generation (RAG) systems address the knowledge-boundary and hallucination problems of large language models by grounding generation in retrieved context. However, standard dense-retrieval RAG — the dominant paradigm — treats documents as independent vectors and cannot reason about *relationships* between facts spread across multiple documents. This limitation is critical for multi-hop questions, which require synthesising information from two or more non-adjacent evidence sources.

Knowledge Graph-based RAG (KG-RAG) addresses this gap by encoding retrieved content as structured graph nodes and edges, enabling explicit reasoning paths across multiple hops. For educational video QA — where a question may link a concept introduced at minute 12 of a lecture to a theorem applied at minute 58 — KG-RAG is a principled extension of the baseline dense-retrieval approach.

This review covers 20 peer-reviewed KG-RAG papers (2023–2026) plus one non-KG dense-retrieval video baseline (VideoRAG, ACL 2025), organised into five groups: three primary thematic clusters and two separate sections capturing methodologically adjacent work. Note: two papers share the name "VideoRAG" — the KDD 2026 paper (Ren et al.) builds a KG over long-form video and is a KG-RAG paper; the ACL 2025 paper (Jeong et al.) uses dense retrieval only and is included as the non-KG baseline. Both are clearly labelled throughout.

---

## 2\. Primary Cluster 1: Multi-hop KG-RAG for Text QA

**Papers:** CoTKR (EMNLP 2024), GMeLLo (EMNLP 2024), SG-RAG (ICNLSP 2024), GNN-RAG (ACL 2025), KiRAG (ACL 2025), BYOKG-RAG (EMNLP 2025), M³GQA (ACL 2025)

This cluster contains papers that perform ***explicit multi-hop reasoning over a knowledge graph***: the system either traverses multiple KG edges before generating an answer, or iteratively retrieves information to bridge reasoning gaps across hops.

### 2.1 Chain-of-Thought Knowledge Rewriting (CoTKR)

Wu et al. (EMNLP 2024) observe that single-step knowledge rewriting — converting a KG subgraph into a text passage — discards the reasoning structure needed for complex KGQA. **CoTKR** generates interleaved reasoning traces and knowledge snippets in a chain-of-thought style, mirroring how a human expert would annotate a derivation. The accompanying **PAQAF** training strategy uses downstream QA feedback as a preference signal to refine the rewriter. On the standard KGQA benchmarks WebQSP and ComplexWebQ, CoTKR outperforms all prior single-step rewriters.

*Relevance to the project:* The CoT rewriting idea is directly applicable to lecture transcript RAG: instead of concatenating retrieved chunk texts, the system could generate a reasoning trace that links a concept chunk to a later application chunk, making the multi-hop derivation auditable.

### 2.2 Multi-hop QA with Evolving Knowledge (GMeLLo)

Chen et al. (EMNLP 2024 Findings) propose **GMeLLo**, which merges LLM linguistic flexibility with KG structured reasoning for settings where facts change over time. The system uses LLMs to convert natural language questions into structured KG queries and fact triples, enabling rapid KG updates and precise multi-hop inference without full model retraining. GMeLLo significantly outperforms knowledge-editing SOTA on MQuAKE, especially in high-edit-count scenarios.

*Relevance to the project:* The idea of converting natural language lecture content into structured fact triples that can be queried multi-hop is a useful design pattern. Lecture content is effectively “evolving” across weeks of a course — GMeLLo’s update mechanism suggests a path for incremental KG construction.

### 2.3 KG-RAG Through Semantic Graph Matching (SG-RAG)

Saleh et al. (ICNLSP 2024) present **SG-RAG**, which represents questions as semantic graphs, retrieves relevant KG paths via graph matching, and feeds them to an LLM as structured context. The paper demonstrates that explicit KG path retrieval outperforms flat-passage retrieval for multi-hop questions on standard KGQA benchmarks.

*Relevance to the project:* SG-RAG’s semantic graph question representation is applicable to educational questions that span multiple concepts. Its path-retrieval design maps naturally onto a lecture KG where nodes are concept segments and edges represent “introduces”, “applies”, or “contrasts” relationships.

### 2.4 GNN-Based Dense KG Retrieval (GNN-RAG)

Mavromatis and Karypis (ACL 2025 Findings) propose **GNN-RAG**, which uses lightweight Graph Neural Networks as dense subgraph reasoners. The GNN traverses the KG to retrieve multi-hop reasoning paths, which are verbalized and passed to a 7B LLM for generation. GNN-RAG outperforms or matches GPT-4 on WebQSP and CWQ, with 8.9–15.5% F1 improvements over LLM-only retrieval on multi-entity and multi-hop questions.

*Relevance to the project:* The GNN-as-graph-reasoner paradigm separates graph traversal from language generation cleanly, making it modular. For video lecture KGs, a GNN could learn to traverse temporal concept graphs even when the KG is noisy (imperfect entity extraction from transcripts).

### 2.5 Iterative Knowledge-Triple Retrieval (KiRAG)

Fang et al. (ACL 2025) present **KiRAG**, which does not require a pre-built KG. Instead, it decomposes documents into knowledge triples on-the-fly and performs iterative retrieval: at each step, current triples guide the identification of information gaps, and retrieval fetches the next missing piece. KiRAG achieves 9.4% R@3 and 5.1% F1 improvement over iterative RAG baselines on multi-hop QA benchmarks.

*Relevance to the project:* KiRAG’s on-the-fly triple construction is highly applicable to educational video transcripts where building a complete KG upfront is expensive. The iterative gap-filling directly models multi-hop question resolution.

### 2.6 Multi-Strategy Graph Retrieval (BYOKG-RAG)

Mavromatis et al. (EMNLP 2025) extend GNN-RAG into **BYOKG-RAG**, which combines LLMs with specialized graph retrieval tools — graph traversal, entity linking, and OpenCypher queries — for KGQA over custom or domain-specific KGs. The LLM iteratively generates KG artifacts and tools retrieve relevant graph context, achieving 4.5% improvement over the next-best graph retrieval method across five benchmark KG types.

*Relevance to the project:* BYOKG-RAG’s “bring your own KG” design is the most practical among multi-hop methods, as it does not require Freebase/Wikidata schemas. A lecture KG with custom node types (concept, segment, prerequisite) and edges could be queried using BYOKG-RAG’s tool-calling interface.

### 2.7 Multi-hop KG Benchmark (M³GQA)

A benchmarking paper from ACL 2025, **M³GQA** evaluates GraphRAG methods on multi-entity multi-hop questions across six distinct settings. It reveals that current GraphRAG methods fail significantly on complex entity combinations, even when retrieval is successful. M³GQA provides both a diagnostic tool and a gold standard for future multi-hop KG-RAG work.

*Relevance to the project:* M³GQA’s six-setting evaluation design can inform how the project’s own benchmark measures multi-hop performance — particularly the distinction between single-entity multi-hop and multi-entity multi-hop questions.

### 2.8 Cluster Gap Analysis

| Gap | Description |
| --- | --- |
| **No video-grounded KGs** | All papers use text-domain structured KBs (Freebase, Wikidata, Wikipedia). None address KG construction from video transcripts where entities are temporal segments. |
| **Clean schema assumption** | Multi-hop traversal assumes well-structured KG schemas. Noisy ASR transcripts from lecture videos violate this assumption. |
| **No temporal ordering** | KG nodes are unordered symbolic entities. The temporal progression of a lecture (concept introduced → concept applied → concept contrasted) is not encoded. |
| **Modality gap** | Every paper is text-only. No evaluation on visual questions that require both frame content and transcript understanding. |
| **Span prediction not addressed** | None of the papers predict temporal spans (mm:ss to mm:ss) as output — they predict entity answers from structured KBs. |

---

## 3\. Primary Cluster 2: GraphRAG Pipeline Design

**Papers:** KG2RAG (NAACL 2025), GraphRAG-FI (EMNLP 2025), KERAG (EMNLP 2025), LLMs Meet KGs for QA Survey (EMNLP 2025)

This cluster covers papers that propose ***end-to-end GraphRAG architectures*: KG construction from raw text, graph-indexed retrieval,** and LLM generation. The primary contribution is pipeline design rather than novel multi-hop traversal algorithms.

### 3.1 KG-Guided Chunk Expansion (KG2RAG)

Zhu et al. (NAACL 2025) propose **KG2RAG**, which uses a KG to encode fact-level relationships between document chunks. After semantic seed-chunk retrieval, KG2RAG performs KG-guided chunk expansion (adding linked chunks from the KG neighborhood) and KG-based chunk organization (ordering them into coherent paragraphs) before LLM generation. The design is modular and compatible with any dense retriever.

*Relevance to the project:* KG2RAG’s chunk expansion is directly applicable to the project’s 45-second chunk structure. Expanding from a retrieved chunk to its KG-linked neighbors (e.g., the chunk that introduces a concept earlier in the lecture) implements a form of multi-hop retrieval without expensive path traversal.

### 3.2 Filtering and Integration for GraphRAG (GraphRAG-FI)

Guo et al. (EMNLP 2025) address two failure modes of GraphRAG: noisy/irrelevant retrieved subgraphs that degrade generation, and over-reliance on external KG that suppresses the LLM’s intrinsic reasoning. **GraphRAG-FI** adds two-stage filtering (to refine the retrieved subgraph) and logits-based selection (to balance external vs. intrinsic knowledge). Both components are model-agnostic and add minimal overhead.

*Relevance to the project:* For lecture video KGs built from noisy ASR transcripts, the filtering stage is critical — entity extraction will inevitably produce spurious nodes and edges. GraphRAG-FI’s filtering mechanism provides a reusable component for cleaning retrieved subgraphs.

### 3.3 Knowledge-Enhanced RAG with CoT Reasoning (KERAG)

Sun et al. (EMNLP 2025 Findings) propose **KERAG**, which expands retrieval scope by fetching KG subgraphs, filters them, and uses fine-tuned LLMs with Chain-of-Thought reasoning to answer questions. KERAG outperforms GPT-4o by 10–21% on KGQA benchmarks. Its combination of subgraph filtering and CoT reasoning is the strongest single-model result in this cluster.

*Relevance to the project:* The retrieval-filtering-CoT pipeline maps well onto the project’s architecture. The CoT reasoning step makes the answer derivation auditable, which is useful for citing specific lecture timestamps.

### 3.4 Survey: LLMs Meet Knowledge Graphs for QA

Ma et al. (EMNLP 2025) provide the most up-to-date systematic survey of LLM+KG integration patterns for QA, covering KG-augmented LLMs, LLM-augmented KGQA, and hybrid patterns including multi-hop decomposition, iterative reasoning, and RAG-based retrieval over KGs. This paper is essential background for understanding the full design space.

*Relevance to the project:* The survey identifies the “KG as index” pattern — where a KG indexes retrieved chunks rather than replacing them — as an underexplored direction. This is precisely the architecture that would benefit the project’s existing ChromaDB + chunk pipeline.

### 3.5 Cluster Gap Analysis

| Gap | Description |
| --- | --- |
| **Static corpus assumption** | All pipelines build a KG from a fixed document set. I**ncremental KG updates as new lectures are added are not addresse**d (except partially by LightRAG’s incremental updates). |
| **No temporal node attributes** | KG nodes represent text entities, not temporal media segments. Encoding start/end timestamps as node attributes is an open design problem. |
| **No multimodal KG nodes** | **Visual frame content (board equations, diagrams) is not captured** in any KG node, yet visual information is essential for lecture QA. |

---

## 4\. Primary Cluster 3: Video-Specific KG and RAG

**KG-RAG papers:** VHAKG (CIKM 2024), VideoRAG — Ren et al. (KDD 2026), AdaVideoRAG (NeurIPS 2025), Vgent (NeurIPS 2025 Spotlight)  
**Non-KG baseline (included for comparison):** VideoRAG — Jeong et al. (ACL 2025)

This cluster covers papers that build KGs from video content, plus one dense-retrieval video RAG baseline included to contextualise how KG-based approaches compare against the current state of the art in video RAG.

### 4.1 Multi-modal KG from Synchronized Videos (VHAKG)

Egami et al. (CIKM 2024) construct **VHAKG**, a multi-modal RDF knowledge graph from frame-by-frame annotations of synchronized multi-view simulated videos of daily activities. The KG links bounding boxes and scene changes to semantic RDF triples, enabling SPARQL-based cross-modal retrieval over video content.

*Relevance to the project:* VHAKG is a proof-of-concept for video-grounded KGs. Its RDF triple structure (subject–predicate–object with temporal anchoring) is directly applicable to lecture video KG construction where subjects are concepts, predicates are lecture discourse relations, and objects are temporal segments. The SPARQL query interface would enable complex multi-hop queries over the lecture KG.

> **Note on task type:** VHAKG is a KG construction and benchmarking paper — it is not a question answering system. It demonstrates that a video-grounded KG can be queried, but there is no QA model, no QA evaluation, and no answer generation pipeline. It is included here as a structural reference for how to build a video KG, not as evidence of multi-hop video QA.

### 4.2 KG-Based RAG over Long-Form Video (VideoRAG — Ren et al., KDD 2026)

Ren et al. (KDD 2026) present the first KG-RAG framework designed specifically for extremely long-context videos. **VideoRAG** constructs a knowledge graph from video transcripts in three steps: (1) LLM-based semantic entity and relation extraction from transcript chunks; (2) incremental graph construction with entity unification across multiple videos; (3) LLM-powered semantic synthesis to maintain cross-video coherence. At inference time, a dual-channel retrieval combines graph-based textual matching (GraphRAG-style chunk ranking) with multimodal visual retrieval using ImageBind embeddings. Evaluated on the newly introduced **LongerVideos benchmark** — 160+ videos, 134+ hours, including 64h of lectures — VideoRAG outperforms NaiveRAG, GraphRAG, and LightRAG baselines with a 53–57% win rate on open-ended queries.

*Relevance to the project:* This is the most directly relevant paper in the entire review. It targets the same setting — long lecture videos, KG construction from transcripts — and its dual-channel retrieval (textual KG + visual embeddings) closely mirrors the project's Config 1 (transcript) and Config 2 (transcript + frame captions) distinction. The incremental KG construction design also addresses the growing lecture corpus problem. Key adaptations needed: (1) adding temporal span attributes (mm:ss) to KG nodes, which Ren et al. do not implement; (2) evaluating on closed-form VQA with ground-truth answers rather than LLM-judged open-ended generation.

> **Note on evaluation setting:** VideoRAG (KDD 2026) evaluates on open-ended query response using LLM-judge metrics (comprehensiveness, depth, trustworthiness). It does not predict temporal spans, does not use ground-truth answers, and is not a VQA benchmark. This distinguishes it from the project's temporally-grounded citation-accuracy and IoU metrics.

### 4.3 Adaptive Multi-Level KG Retrieval for Long Video (AdaVideoRAG — NeurIPS 2025)

Xue et al. (NeurIPS 2025) propose **AdaVideoRAG**, which avoids uniform retrieval by selecting one of three levels per query: (1) direct MLLM inference with no retrieval; (2) dense embedding search over captions, ASR, and OCR; (3) graph retrieval using a LightRAG-adapted KG built from the same video-grounded text. The KG is constructed offline from clip captions, ASR transcripts, and OCR text via entity/relation extraction. At inference time, the system classifies the query and applies the appropriate retrieval level, reducing computation on simple queries while engaging graph retrieval for complex ones.

*Relevance to the project:* AdaVideoRAG's KG construction pipeline — captions + ASR + OCR → entity extraction → graph — directly mirrors the project's Config 2 (transcript + frame captions). The adaptive level selection is a practical design: simple factual questions in the benchmark can be answered with dense retrieval, while multi-hop questions trigger graph retrieval. The main gap for the project is that the graph retrieval layer is single-pass LightRAG-style — no iterative hop traversal.

### 4.4 Clip-Entity Graph with Structured Query Refinement (Vgent — NeurIPS 2025 Spotlight)

Shen et al. (NeurIPS 2025 Spotlight) present **Vgent**, which represents long videos as clip-entity graphs: nodes are video clips, edges connect clips that share semantic entities extracted by LVLMs from frames and subtitles. Retrieval is a two-stage pipeline: graph-based entity matching retrieves ~20 candidate clips, then structured query refinement decomposes the question into binary/numerical sub-queries to verify each candidate's relevance, trimming to ~5 final clips before generation. Vgent achieves 3.0–5.4% improvement over baselines on MLVU and 8.6% over state-of-the-art video RAG methods.

*Relevance to the project:* Vgent's structured query refinement addresses the noisy retrieval problem directly — irrelevant KG-connected clips are filtered before reaching the LLM, the same problem GraphRAG-FI targets in text-domain KG-RAG. The clip-as-node graph structure maps naturally onto the project's 45-second chunk structure. Key limitation for the project: the verification step refines one candidate batch rather than re-querying for missing facts, so genuinely multi-hop questions that require linking two non-adjacent segments may still be missed.

### 4.5 Dense-Retrieval Video RAG Baseline — Non-KG (VideoRAG — Jeong et al., ACL 2025)

> **Note:** VideoRAG does not construct a knowledge graph. It is included as a comparison baseline to frame the gap between current video RAG systems and KG-guided video RAG.

Jeong et al. (ACL 2025 Findings) present **VideoRAG**, the first RAG system that uses Large Video Language Models (LVLMs) end-to-end for video retrieval and generation. Given a query, VideoRAG dynamically retrieves relevant videos via dense search, selects informative frames, and generates a response by jointly processing visual + textual content from retrieved videos.

*Relevance to the project:* VideoRAG is the closest published system to the project’s Config 2 (transcript + frame captions). Its key insight — using LVLMs for direct frame understanding rather than pre-extracted captions — is a direction to explore for improving visual-dependent questions. As a non-KG baseline it establishes the performance ceiling for dense retrieval, making it a useful reference point for measuring the value-add of KG-based multi-hop retrieval.

> **Note on task type:** VideoRAG targets open-ended response generation over a video corpus — it is not VQA in the standard sense. It does not evaluate on visual multiple-choice or span-prediction benchmarks. The task is closer to video-grounded open QA or summarization: retrieve relevant videos, generate a free-form response. This is a different evaluation setting from the project’s temporally-grounded span-prediction and citation-accuracy metrics.

### 4.6 Cluster Gap Analysis

| Gap | Description |
| --- | --- |
| **No temporal span prediction** | VideoRAG (KDD 2026) builds a video KG but does not predict (mm:ss, mm:ss) citation spans — nodes lack temporal coordinates. VHAKG has temporal anchoring but no QA pipeline. |
| **No ground-truth VQA evaluation** | VideoRAG (KDD 2026) evaluates with an LLM judge on open-ended queries, not a VQA benchmark with ground-truth answers. Citation accuracy and IoU metrics are not measured. |
| **No explicit multi-hop path chaining** | VideoRAG (KDD 2026) supports implicit cross-video connectivity through the KG but does not perform explicit iterative hop traversal. |
| **Controlled scenarios only (VHAKG)** | VHAKG is built from scripted daily-activity simulations; application to long unstructured lecture videos is unexplored. |
| **No curriculum-aware KG structure** | Neither paper encodes lecture discourse relations (introduces, applies, contrasts, prerequisite\_of) as typed KG edges. |

---

## 5\. Separate Section: Multimodal KG-RAG — Image/Text Domain

**Papers (methodologically transferable, image/text domain):** Query-Driven Multimodal GraphRAG (ACL 2025), MDKAG (Applied Sciences 2025), KA-RAG (Applied Sciences 2025)

T**hese papers build multimodal KGs from image-text or structured educational content and use them for RAG-based QA. While the primary modality is not long-form video, their architectural patterns translate to the lecture video setting.**

### 5.1 Dynamic Local KG for Multimodal Reasoning (Query-Driven Multimodal GraphRAG)

Bu et al. (ACL 2025 Findings) propose dynamically constructing a query-relevant local KG from multimodal documents rather than building one static global KG. Graph patterns derived from query semantics guide multimodal entity extraction, and the local subgraph is used for reasoning and generation.

*Transferability:* Query-driven local KG construction avoids the costly global KG build step and is directly applicable to the project. For each lecture QA query, a local subgraph of relevant chunks (text + frames) could be constructed on-the-fly, then traversed for multi-hop reasoning.

### 5.2 Multimodal Disciplinary KG for Educational QA (MDKAG)

Zhao et al. (Applied Sciences 2025) **extract entities from textbooks, lecture slides, and classroom videos** using ERNIE 3.0 and link them into a **multimodal disciplinary KG.** At inference time, a relevance-prioritized retrieval strategy fetches KG-adjacent passages, and an answer verification loop corrects LLM hallucinations.

*Transferability:* **MDKAG is the closest published system to the project’s setting** — it explicitly targets educational video content as one of its KG construction sources. The entity extraction pipeline and answer verification loop are directly adoptable. However, two important distinctions apply:

1. **Video is not the retrieval corpus.** At query time, MDKAG retrieves passages from textbooks and slides (same curriculum domain, but not video). Video contributes concept entities to the KG at build time only — once built, video plays no role at inference. By contrast, in this project the video-derived chunks (transcripts + frame captions) *are* the corpus: every retrieved passage is anchored to a video segment.

2. **No temporal grounding.** When MDKAG extracts an entity such as "gradient descent" from the video, it records only that the concept exists — not *where* in the video it appears. There is no timestamp, no segment ID, no mm:ss span attached to the entity node. The project’s chunks carry `[video_id @ mm:ss to mm:ss]` by design, so any KG built on top would inherit temporal coordinates as node attributes.

### 5.3 KG + Agentic RAG for Educational QA (KA-RAG)

KA-RAG (Applied Sciences 2025) combines a domain curriculum **KG** with an **agentic RAG system**. An **agent** dynamically d**ecides when to retrieve from the KG**, when to use standard dense retrieval, and when to rely on LLM intrinsic knowledge. The agentic retrieval strategy avoids over-fetching irrelevant KG facts.

*Transferability:* **The agentic decision layer** — **choosing between KG-guided and dense retrieval per query** — is a practical design for the project’s two-configuration benchmark. Visual-dependent questions could trigger dense retrieval with frame captions, while multi-hop conceptual questions could trigger KG-guided traversal.

### 5.4 Gap Analysis for This Section

| Gap | Description |
| --- | --- |
| **No temporal segment retrieval** | All three papers retrieve text passages or static images, **not temporal video segments with (start, end) timestamps.** |
| **No temporal ordering in KG** | Educational KGs encode curriculum relationships (prerequisite, extends) but not the sequential temporal position of content within a lecture. |
| **English lecture generalization untested** | **MDKAG and KA-RAG are validated on closed-domain Chinese educational content**; generalization to English lecture transcripts (MIT OCW, Stanford SEE) is an open question. |

---

## 6\. Separate Section: Single-Hop KG-RAG

**Papers (KG-based pipeline, single-hop reasoning):** LightRAG (EMNLP 2025), GRAG (NAACL 2025)

These papers use **knowledge graphs to structure retrieval but perform a single retrieval s**tep per query without iterative multi-hop path traversal. **They are not video grounded text either**. They are included because their graph-construction and subgraph-retrieval designs are reusable building blocks for a multi-hop extension.

### 6.1 Dual-Level Graph RAG (LightRAG)

Guo et al. (EMNLP 2025 Findings) build a KG from documents and use dual-level retrieval: low-level (specific entity relationships) + high-level (broader thematic community summaries). This captures both precise fact lookup and holistic context without multi-hop traversal. LightRAG also supports incremental KG updates — adding new documents without rebuilding the full KG.

*Relevance:* LightRAG’s dual-level retrieval maps naturally to lecture RAG: entity-level retrieval for specific factual questions; community-level retrieval for broad conceptual questions. The incremental update is critical for a growing lecture corpus. To extend to multi-hop: the high-level community summary could serve as a “meta-document” bridging distant lecture segments.

> **Note on corpus:** LightRAG’s input corpus is plain text documents (news articles, general web text) with no video origin, no timestamps, and no visual component — not video-grounded in any sense, not even in the weak sense that MDKAG is (where video at least contributes entities at build time).

### 6.2 Subgraph-Based RAG with Topology Encoding (GRAG)

Hu et al. (NAACL 2025 Findings) jointly retrieve textual subgraphs and encode their topological structure in the LLM prompt. GRAG significantly outperforms standard RAG on graph reasoning benchmarks via one subgraph retrieval pass. The modular subgraph retriever is swappable for domain-specific implementations.

*Relevance:* GRAG’s topology encoding — representing graph structure in the LLM prompt — is directly applicable to lecture KGs where the structure encodes temporal and conceptual ordering. Extending GRAG to multi-hop: iterating subgraph retrieval from the initial result set would enable chained reasoning across lecture segments.

> **Note on corpus:** GRAG operates on plain text document collections with no video origin. Like LightRAG, there is no video grounding at any stage of the pipeline — no transcripts, no captions, no timestamps.

### 6.3 Gap Analysis for This Section

| Gap | Description |
| --- | --- |
| **Single retrieval pass** | Neither paper extends to iterative multi-hop traversal, limiting performance on compositional questions. |
| **No temporal node attributes** | Nodes represent text entities without temporal coordinates — they cannot return (mm:ss, mm:ss) citations. |
| No video modality | Both systems operate on text corpora only. |

---

## 7\. Overall Gap Analysis

The following table synthesizes the gaps across all five clusters:

| Gap | Clusters Affected | Severity for This Project |
| --- | --- | --- |
| **No video-grounded KG construction** | All clusters | **Critical** — must build lecture KG from ASR transcripts |
| **Temporal segment as KG node** | All clusters | **Critical** — temporal spans (mm:ss to mm:ss) must be KG node attributes |
| **No temporal multi-hop QA evaluation** | All clusters | **High** — multi-hop linking of non-adjacent segments is the core benchmark challenge |
| **No peer-reviewed QA benchmark over educational lecture video** | All clusters | **High** — MDKAG uses educational video as a KG source but releases no QA dataset; EduVidQA (EMNLP 2025) is the only peer-reviewed QA benchmark grounded in educational lecture video with temporal annotations |
| **Noisy ASR transcript handling** | Cluster 1, 2, 3 | **High** — clean KG schema assumptions break on lecture transcripts |
| **Visual content not in KG nodes** | Cluster 3, Separate (Multimodal) | **Medium** — frame captions from Qwen2-VL-7B can be incorporated as node attributes |
| **No temporal ordering in KG edges** | All clusters | **Medium** — “precedes”, “introduces”, “applies” lecture discourse edges are missing |
| **Static corpus assumption** | Cluster 2, Single-hop | **Low** — lecture corpus is fixed after curation |

### Key Observation: The Primary Research Gap

No existing peer-reviewed paper combines (a) knowledge graph construction from *video transcript* content, (b) temporal segment anchoring of KG nodes to (mm:ss, mm:ss) spans, and © multi-hop KG-guided retrieval that predicts temporally-grounded answers. Each component is addressed individually in the literature (VHAKG for video KGs, CoTKR/GNN-RAG for multi-hop KG-RAG, VideoRAG for video RAG), but their integration into a unified pipeline for educational long-lecture video QA is the proposed contribution.

---

## 8\. Comprehensive Comparison Table

| Title | Authors | Venue | Year | Key Contribution | Gap |
| --- | --- | --- | --- | --- | --- |
| CoTKR | Wu et al. | EMNLP 2024 | 2024 | Chain-of-thought knowledge rewriting with PAQAF alignment for complex KGQA | Text-only, clean KG schemas required, no temporal grounding |
| GMeLLo | Chen et al. | EMNLP 2024 Findings | 2024 | LLM-to-KG query translation for multi-hop QA in evolving fact environments | Text-only, no video/temporal modality |
| SG-RAG | Saleh et al. | ICNLSP 2024 | 2024 | Semantic graph question representation + KG path retrieval for multi-hop QA | Text-only, ontology-dependent schemas |
| VHAKG | Egami et al. | CIKM 2024 | 2024 | Multi-modal RDF KG from synchronized multi-view video with SPARQL querying | Controlled simulations only, no RAG pipeline demonstrated |
| VideoRAG *(KG-RAG, long-video)* | Ren et al. | KDD 2026 | 2026 | First KG-RAG system for extremely long-context videos; dual-channel retrieval (textual KG + ImageBind visual); LongerVideos benchmark (134+ hrs, lectures included) | No temporal span prediction; LLM-judge evaluation only (no ground-truth VQA); no explicit multi-hop path chaining |
| AdaVideoRAG | Xue et al. | NeurIPS 2025 | 2025 | Adaptive three-level retrieval (none / dense / graph) for long video; KG built from captions + ASR + OCR; LightRAG-adapted graph layer | Single-pass graph retrieval (implicit multi-hop only); no temporal span prediction; not evaluated on educational lectures |
| Vgent | Shen et al. | NeurIPS 2025 Spotlight | 2025 | Clip-entity graph + two-stage pipeline (graph retrieval → structured query refinement); 8.6% gain over video RAG SOTA on MLVU | Verification refines one candidate batch, not iterative re-querying; no temporal span prediction; expensive LVLM inference per clip |
| GNN-RAG | Mavromatis & Karypis | ACL 2025 Findings | 2025 | GNN subgraph reasoner for efficient dense multi-hop KG path retrieval; matches GPT-4 at 7B scale | KG must be pre-trained, no video/multimodal, Freebase schema required |
| KiRAG | Fang et al. | ACL 2025 Long | 2025 | On-the-fly knowledge triple extraction + iterative gap-filling retrieval without pre-built KG | Text-only, latency from iterative steps, no temporal grounding |
| M³GQA | Peng et al. | ACL 2025 Long | 2025 | Benchmark exposing multi-entity multi-hop failures in current GraphRAG systems | Text KG only, no video or educational content |
| KG2RAG | Zhu et al. | NAACL 2025 Long | 2025 | KG-guided chunk expansion and organization after semantic seed retrieval | Single-hop expansion, no temporal ordering, text-only |
| GRAG | Hu et al. | NAACL 2025 Findings | 2025 | Joint textual subgraph + topology encoding in LLM prompt for graph reasoning | Single retrieval pass, text-only, no temporal attributes |
| Query-Driven Multimodal GraphRAG | Bu et al. | ACL 2025 Findings | 2025 | Dynamic query-conditioned local KG construction from multimodal documents | Image-text domain; no temporal video; no educational evaluation |
| VideoRAG *(non-KG baseline)* | Jeong et al. | ACL 2025 Findings | 2025 | First LVLM-powered RAG over video corpus for visual + textual response generation — dense retrieval baseline, no KG | Dense retrieval only, no KG, no multi-hop, no span prediction |
| LightRAG | Guo et al. | EMNLP 2025 Findings | 2025 | Dual-level (entity + community) KG-based RAG with incremental KG update algorithm | Single-hop per query, no temporal encoding, text-only |
| GraphRAG-FI | Guo et al. | EMNLP 2025 Main | 2025 | Two-stage KG filtering + logits-based intrinsic/external knowledge balancing | Text-domain entity graphs only, no video/multimodal |
| KERAG | Sun et al. | EMNLP 2025 Findings | 2025 | KG subgraph retrieval + noise filtering + CoT reasoning; 10–21% gain over GPT-4o | Requires fine-tuned LLM on KG schemas, text-only |
| BYOKG-RAG | Mavromatis et al. | EMNLP 2025 Main | 2025 | Multi-tool graph retrieval (traversal, entity linking, Cypher) over custom KGs | Requires graph database backend, no video support |
| LLMs Meet KGs for QA | Ma et al. | EMNLP 2025 Main | 2025 | Comprehensive survey of LLM+KG integration patterns; identifies “KG as index” as underexplored | Survey only; video/multimodal KG-RAG not covered |
| MDKAG | Zhao et al. | Applied Sciences 2025 | 2025 | Multimodal disciplinary KG from textbooks + slides + video; relevance-prioritized retrieval | Video treated as text-entity source only, no temporal grounding, Chinese domain |
| KA-RAG | Gao et al. | Applied Sciences 2025 | 2025 | Agentic retrieval that dynamically chooses between KG and dense retrieval for educational QA | Single-hop KG retrieval; curriculum-structured input only |

---

## 9\. Coverage of Core Criteria: KG-RAG × Multi-hop × Video QA

No paper in this review addresses all three criteria simultaneously. The table below shows which criteria each paper satisfies, highlighting the primary research gap this project targets.

| Paper | KG-RAG | Multi-hop | Video QA |
| --- | --- | --- | --- |
| CoTKR, GMeLLo, GNN-RAG, SG-RAG, KiRAG, BYOKG-RAG, M³GQA | ✅ | ✅ | ❌ text only |
| VHAKG | ✅ (KG from video) | ❌ no QA pipeline | ❌ benchmarking only, no RAG |
| VideoRAG — Ren et al. *(KDD 2026)* | ✅ (KG from transcripts) | ⚠️ implicit via KG connectivity, no explicit path chaining | ⚠️ open-ended generation; no ground-truth VQA; no temporal span prediction |
| AdaVideoRAG | ✅ (KG from captions+ASR+OCR) | ⚠️ implicit — LightRAG single-pass graph retrieval | ⚠️ ground-truth VQA benchmarks; no temporal span prediction |
| Vgent | ✅ (clip-entity graph) | ⚠️ implicit + verification step; not iterative re-querying | ✅ ground-truth VQA (MLVU, VideoMME); no temporal span prediction |
| VideoRAG — Jeong et al. *(non-KG baseline)* | ❌ dense retrieval, no KG | ❌ | ✅ |
| MDKAG | ✅ | ❌ | ⚠️ video contributes entities to KG at build time only; retrieved passages are textbook/slide text; no temporal grounding |
| KA-RAG | ✅ | ❌ single-hop | ❌ text/curriculum only |
| LightRAG, GRAG, KG2RAG | ✅ | ❌ single-hop | ❌ |

**The combination of all three criteria — KG-based RAG, multi-hop reasoning, and video QA with temporal grounding — is unaddressed in the peer-reviewed literature as of 2026.** VideoRAG (KDD 2026) is the closest: it achieves KG-RAG over lecture video, but lacks explicit multi-hop path chaining and temporal span prediction. This remaining gap is the contribution space targeted by this project.

---

## 10\. Implications for the Project

Based on the gap analysis, the most promising adaptation strategy combines elements from three papers:

1.  **KiRAG** (ACL 2025): On-the-fly triple construction from lecture transcript chunks — avoids expensive KG pre-build, handles noisy ASR.
2.  **KG2RAG** (NAACL 2025): KG-guided chunk expansion — given a seed chunk retrieved by dense search, expand to linked chunks (the KG neighbor that introduced the concept, the chunk that later applies it).
3.  **LightRAG** (EMNLP 2025): Dual-level retrieval (entity-level for specific concept queries, community-level for broad lecture-section queries) + incremental update for growing lecture corpus.

**Proposed adaptation:**

1.  Build a lecture KG from transcript chunks: nodes = 45-second chunks with temporal attributes (start, end, video\_id); edges = semantic relationships extracted by an LLM (introduces, applies, contrasts, prerequisite\_of).
2.  At inference time, perform dual-level retrieval (KG entity search + ChromaDB dense search).
3.  Expand retrieved seed chunks to their KG neighbors (KiRAG/KG2RAG style).
4.  Generate a temporally-grounded answer with multi-hop citation `[video_id @ mm:ss to mm:ss]`.

This pipeline adds KG-based multi-hop expansion on top of the existing ChromaDB infrastructure, minimizing implementation cost while directly targeting the multi-hop weakness identified in the baseline evaluation.

---

## 11\. References

1.  Wu, Y., Huang, Y., Hu, N., Hua, Y., Qi, G., Chen, J., & Pan, J. Z. (2024). CoTKR: Chain-of-Thought Enhanced Knowledge Rewriting for Complex Knowledge Graph Question Answering. *EMNLP 2024*. [https://aclanthology.org/2024.emnlp-main.205/](https://aclanthology.org/2024.emnlp-main.205/)
    
2.  Chen, R., Jiang, W., Qin, C., Rawal, I. S., Tan, C., Choi, D., Xiong, B., & Ai, B. (2024). LLM-Based Multi-Hop Question Answering with Knowledge Graph Integration in Evolving Environments. *Findings of EMNLP 2024*. [https://aclanthology.org/2024.findings-emnlp.844/](https://aclanthology.org/2024.findings-emnlp.844/)
    
3.  Saleh, A. O. M., Tur, G., & Saygin, Y. (2024). SG-RAG: Multi-Hop Question Answering With Large Language Models Through Knowledge Graphs. *ICNLSP 2024*. [https://aclanthology.org/2024.icnlsp-1.45/](https://aclanthology.org/2024.icnlsp-1.45/)
    
4.  Egami, S., Ugai, T., Htun, S. N. N., & Fukuda, K. (2024). VHAKG: A Multi-modal Knowledge Graph Based on Synchronized Multi-view Videos of Daily Activities. *CIKM 2024*. [https://dl.acm.org/doi/10.1145/3627673.3679175](https://dl.acm.org/doi/10.1145/3627673.3679175)
    
5.  Mavromatis, C., & Karypis, G. (2025). GNN-RAG: Graph Neural Retrieval for Efficient Large Language Model Reasoning on Knowledge Graphs. *Findings of ACL 2025*. [https://aclanthology.org/2025.findings-acl.856/](https://aclanthology.org/2025.findings-acl.856/)
    
6.  Fang, J., Meng, Z., & MacDonald, C. (2025). KiRAG: Knowledge-Driven Iterative Retriever for Enhancing Retrieval-Augmented Generation. *ACL 2025*. [https://aclanthology.org/2025.acl-long.929/](https://aclanthology.org/2025.acl-long.929/)
    
7.  Peng, B., Liu, Y., Bo, X., Guo, J., Zhu, Y., Fan, X., Hong, C., & Zhang, Y. (2025). M³GQA: A Multi-Entity Multi-Hop Multi-Setting Graph Question Answering Benchmark. *ACL 2025*. [https://aclanthology.org/2025.acl-long.1478/](https://aclanthology.org/2025.acl-long.1478/)
    
8.  Zhu, X., Xie, Y., Liu, Y., Li, Y., & Hu, W. (2025). Knowledge Graph-Guided Retrieval Augmented Generation. *NAACL 2025*. [https://aclanthology.org/2025.naacl-long.449/](https://aclanthology.org/2025.naacl-long.449/)
    
9.  Hu, Y., Lei, Z., Zhang, Z., Pan, B., Ling, C., & Zhao, L. (2025). GRAG: Graph Retrieval-Augmented Generation. *Findings of NAACL 2025*. [https://aclanthology.org/2025.findings-naacl.232/](https://aclanthology.org/2025.findings-naacl.232/)
    
10.  Bu, C., Chang, G., Chen, Z., Dang, C., Wu, Z., He, Y., & Wu, X. (2025). Query-Driven Multimodal GraphRAG: Dynamic Local Knowledge Graph Construction for Online Reasoning. *Findings of ACL 2025*. [https://aclanthology.org/2025.findings-acl.1100/](https://aclanthology.org/2025.findings-acl.1100/)
     
11.  Jeong, S., Kim, K., Baek, J., & Hwang, S. J. (2025). VideoRAG: Retrieval-Augmented Generation over Video Corpus. *Findings of ACL 2025*. [https://aclanthology.org/2025.findings-acl.1096/](https://aclanthology.org/2025.findings-acl.1096/)
     
12.  Guo, Z., Xia, L., Yu, Y., Ao, T., & Huang, C. (2025). LightRAG: Simple and Fast Retrieval-Augmented Generation. *Findings of EMNLP 2025*. [https://aclanthology.org/2025.findings-emnlp.568/](https://aclanthology.org/2025.findings-emnlp.568/)
     
13.  Guo, K., Shomer, H., Zeng, S., Han, H., Wang, Y., & Tang, J. (2025). Empowering GraphRAG with Knowledge Filtering and Integration. *EMNLP 2025*. [https://aclanthology.org/2025.emnlp-main.1293/](https://aclanthology.org/2025.emnlp-main.1293/)
     
14.  Sun, Y., Sun, K., Xu, Y. E., Yang, X., Dong, X. L., Tang, N., & Chen, L. (2025). KERAG: Knowledge-Enhanced Retrieval-Augmented Generation for Advanced Question Answering. *Findings of EMNLP 2025*. [https://aclanthology.org/2025.findings-emnlp.329/](https://aclanthology.org/2025.findings-emnlp.329/)
     
15.  Mavromatis, C., Adeshina, S., Ioannidis, V. N., Han, Z., Zhu, Q., Robinson, I., Thompson, B., Rangwala, H., & Karypis, G. (2025). BYOKG-RAG: Multi-Strategy Graph Retrieval for Knowledge Graph Question Answering. *EMNLP 2025*. [https://aclanthology.org/2025.emnlp-main.1417/](https://aclanthology.org/2025.emnlp-main.1417/)
     
16.  Ma, C., Chen, Y., Wu, T., Khan, A., & Wang, H. (2025). Large Language Models Meet Knowledge Graphs for Question Answering: Synthesis and Opportunities. *EMNLP 2025*. [https://aclanthology.org/2025.emnlp-main.1249/](https://aclanthology.org/2025.emnlp-main.1249/)
     
17.  Zhao, X., Wang, G., & Lu, Y. (2025). MDKAG: Retrieval-Augmented Educational QA Powered by a Multimodal Disciplinary Knowledge Graph. *Applied Sciences, MDPI*. [https://www.mdpi.com/2076-3417/15/16/9095](https://www.mdpi.com/2076-3417/15/16/9095)
     
18.  Gao, F., Xu, S., Hao, W., & Lu, T. (2025). KA-RAG: Integrating Knowledge Graphs and Agentic Retrieval-Augmented Generation for an Intelligent Educational Question-Answering Model. *Applied Sciences, MDPI*. [https://www.mdpi.com/2076-3417/15/23/12547](https://www.mdpi.com/2076-3417/15/23/12547)

19.  Ren, X., Xu, L., Xia, L., Wang, S., Yin, D., & Huang, C. (2026). VideoRAG: Retrieval-Augmented Generation with Extreme Long-Context Videos. *32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD 2026)*. [https://dl.acm.org/doi/10.1145/3770854.3783944](https://dl.acm.org/doi/10.1145/3770854.3783944)

20.  Xue, Z., Zhang, J., Xie, X., Cai, Y., Liu, Y., Li, X., & Tao, D. (2025). AdaVideoRAG: Omni-Contextual Adaptive Retrieval-Augmented Efficient Long Video Understanding. *NeurIPS 2025*. [https://arxiv.org/abs/2506.13589](https://arxiv.org/abs/2506.13589)

21.  Shen, X., Zhang, W., Chen, J., & Elhoseiny, M. (2025). Vgent: Graph-based Retrieval-Reasoning-Augmented Generation for Long Video Understanding. *NeurIPS 2025 (Spotlight)*. [https://arxiv.org/abs/2510.14032](https://arxiv.org/abs/2510.14032)