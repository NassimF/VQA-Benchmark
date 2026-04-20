"""Parse YouTube VTT caption files into transcript JSON for the chunker.

YouTube auto-captions use a "rolling" two-line format: each cue block alternates
between a ~2s "word-timing" cue (containing inline <c> tags) and a ~10ms "display"
cue (plain text, no tags). The display cue holds one clean subtitle line — the
complete phrase just spoken. We collect those display cues to build the transcript.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")
_TS_RE = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})")


@dataclass
class Segment:
    start: float
    end: float
    text: str


def _ts_to_seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _strip_tags(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


def _parse_cues(vtt_text: str) -> list[tuple[float, float, str]]:
    """Return (start, end, text) for every cue block that has non-empty text."""
    cues: list[tuple[float, float, str]] = []
    blocks = re.split(r"\n{2,}", vtt_text.strip())

    for block in blocks:
        lines = block.strip().splitlines()
        ts_match = None
        ts_idx = 0
        for i, line in enumerate(lines):
            m = _TS_RE.search(line)
            if m:
                ts_match = m
                ts_idx = i
                break
        if ts_match is None:
            continue

        start = _ts_to_seconds(ts_match.group(1))
        end = _ts_to_seconds(ts_match.group(2))

        text_lines = [_strip_tags(l) for l in lines[ts_idx + 1:] if _strip_tags(l)]
        if not text_lines:
            continue

        cues.append((start, end, text_lines))

    return cues


def parse_vtt(vtt_path: Path) -> list[Segment]:
    """Parse a YouTube VTT file into clean time-stamped segments.

    Strategy: collect the ~10ms "display" cues (duration < 0.1s) — each holds
    one clean subtitle line. Assign each phrase a duration based on the gap to
    the next display cue. De-duplicate identical consecutive phrases, then merge
    phrases with gaps < 3s into cohesive segments for the chunker.
    """
    vtt_text = vtt_path.read_text(encoding="utf-8")
    all_cues = _parse_cues(vtt_text)

    # Collect display cues: duration < 0.1s, first text line = clean phrase
    display: list[tuple[float, str]] = []
    for start, end, text_lines in all_cues:
        if end - start < 0.1:
            phrase = text_lines[0]
            if phrase:
                display.append((start, phrase))

    if not display:
        # Fallback: use all cues, take last text line (new content in rolling format)
        logger.warning(f"No display cues found in {vtt_path.name}; falling back to all cues")
        for start, end, text_lines in all_cues:
            phrase = text_lines[-1]
            if phrase:
                display.append((start, phrase))

    # Assign end times: each phrase ends when the next one begins
    phrases: list[tuple[float, float, str]] = []
    for i, (start, text) in enumerate(display):
        end = display[i + 1][0] if i + 1 < len(display) else start + 3.0
        phrases.append((start, end, text))

    # De-duplicate consecutive identical phrases
    deduped: list[tuple[float, float, str]] = []
    prev = ""
    for start, end, text in phrases:
        if text != prev:
            deduped.append((start, end, text))
            prev = text

    # Each phrase becomes its own segment — the chunker handles 45s window grouping
    return [Segment(start=start, end=end, text=text) for start, end, text in deduped]


def vtt_to_transcript_json(video_id: str, vtt_path: Path, output_path: Path) -> dict:
    """Parse VTT and write transcript JSON consumed by the chunker."""
    segments = parse_vtt(vtt_path)
    transcript = {
        "video_id": video_id,
        "source": "youtube_auto_captions",
        "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in segments],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(transcript, indent=2, ensure_ascii=False))
    logger.info(f"{video_id}: wrote {len(segments)} segments to {output_path}")
    return transcript
