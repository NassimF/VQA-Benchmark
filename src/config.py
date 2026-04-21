"""Loads config.yaml and exposes a validated Config dataclass."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class DataConfig:
    raw_dir: Path
    videos_dir: Path
    transcripts_dir: Path
    chunks_dir: Path
    frame_captions_dir: Path
    qa_pairs_dir: Path
    benchmark_dir: Path
    metadata_file: Path


@dataclass
class EmbeddingConfig:
    model: str
    device: str


@dataclass
class RetrievalConfig:
    top_k: int
    k_values: list[int]
    distance_metric: str
    iou_threshold: float


@dataclass
class VectorDBConfig:
    path: Path
    transcript_only_collection: str
    transcript_frames_collection: str


@dataclass
class ChunkingConfig:
    window_seconds: float
    overlap_seconds: float

    @property
    def stride_seconds(self) -> float:
        return self.window_seconds - self.overlap_seconds


@dataclass
class FrameExtractionConfig:
    interval_seconds: float


@dataclass
class FrameCaptionerConfig:
    model: str
    device: str
    max_new_tokens: int


@dataclass
class GeneratorConfig:
    model: str
    temperature: float
    max_tokens: int
    citation_format: str


@dataclass
class QAGenerationConfig:
    questions_per_lecture: int
    target_accepted: int


@dataclass
class Config:
    data: DataConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    vector_db: VectorDBConfig
    chunking: ChunkingConfig
    frame_extraction: FrameExtractionConfig
    frame_captioner: FrameCaptionerConfig
    generator: GeneratorConfig
    qa_generation: QAGenerationConfig


def load_config(config_path: Path | None = None) -> Config:
    """Load and validate config.yaml, resolving all paths relative to project root."""
    if config_path is None:
        config_path = _PROJECT_ROOT / "config.yaml"

    with config_path.open() as f:
        raw = yaml.safe_load(f)

    def p(rel: str) -> Path:
        return _PROJECT_ROOT / rel

    d = raw["data"]
    data = DataConfig(
        raw_dir=p(d["raw_dir"]),
        videos_dir=p(d["videos_dir"]),
        transcripts_dir=p(d["transcripts_dir"]),
        chunks_dir=p(d["chunks_dir"]),
        frame_captions_dir=p(d["frame_captions_dir"]),
        qa_pairs_dir=p(d["qa_pairs_dir"]),
        benchmark_dir=p(d["benchmark_dir"]),
        metadata_file=p(d["metadata_file"]),
    )

    e = raw["embedding"]
    embedding = EmbeddingConfig(model=e["model"], device=e["device"])

    r = raw["retrieval"]
    retrieval = RetrievalConfig(
        top_k=r["top_k"],
        k_values=r["k_values"],
        distance_metric=r["distance_metric"],
        iou_threshold=r["iou_threshold"],
    )

    v = raw["vector_db"]
    vector_db = VectorDBConfig(
        path=p(v["path"]),
        transcript_only_collection=v["transcript_only_collection"],
        transcript_frames_collection=v["transcript_frames_collection"],
    )

    c = raw["chunking"]
    chunking = ChunkingConfig(
        window_seconds=float(c["window_seconds"]),
        overlap_seconds=float(c["overlap_seconds"]),
    )

    fe = raw["frame_extraction"]
    frame_extraction = FrameExtractionConfig(interval_seconds=float(fe["interval_seconds"]))

    fc_raw = raw["frame_captioner"]
    frame_captioner = FrameCaptionerConfig(
        model=fc_raw["model"],
        device=fc_raw["device"],
        max_new_tokens=int(fc_raw["max_new_tokens"]),
    )

    g = raw["generator"]
    generator = GeneratorConfig(
        model=g["model"],
        temperature=float(g["temperature"]),
        max_tokens=int(g["max_tokens"]),
        citation_format=g["citation_format"],
    )

    qa = raw["qa_generation"]
    qa_generation = QAGenerationConfig(
        questions_per_lecture=int(qa["questions_per_lecture"]),
        target_accepted=int(qa["target_accepted"]),
    )

    cfg = Config(
        data=data,
        embedding=embedding,
        retrieval=retrieval,
        vector_db=vector_db,
        chunking=chunking,
        frame_extraction=frame_extraction,
        frame_captioner=frame_captioner,
        generator=generator,
        qa_generation=qa_generation,
    )
    logger.debug(f"Config loaded from {config_path}")
    return cfg
