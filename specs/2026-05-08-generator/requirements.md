# Phase 6 — Generator: Requirements

## Scope

Implement `src/generator.py`: a stateless module that accepts a question and a list of
retrieved chunks, calls an LLM to produce a grounded answer with temporal citations, and
returns a structured result object.

This is the final RAG step between retrieval and evaluation. It must work with both
retrieval modes (`transcript_only`, `transcript_plus_frames`) and feed directly into
`run_part1.py` and `run_part2.py`.

---

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Public interface | Module-level `generate()` function | Stateless; no persistent state needed; simpler to call from run scripts |
| Return type | `GeneratorResult` dataclass | Typed, inspectable, easy to serialize for evaluation |
| LLM backend | `gpt-4o-mini` (primary) | Cost-effective, reliable structured JSON output; config-driven so model is swappable |
| Output format | Structured JSON `{"answer": "...", "citations": [1, 3]}` | More reliable than regex-parsing bracket citations; allows strict schema validation |
| Error handling | Raise `ValueError` immediately on malformed output | Fail fast; no silent failures that would corrupt evaluation results |
| Span aggregation | Union of all cited chunk time-ranges | Standard for multi-chunk answers; required by Phase 8 evaluator |
| Citation format | `[video_id @ mm:ss to mm:ss](https://youtu.be/VIDEO_ID?t=SECONDS)` | Prescribed by assignment |

---

## Inputs

`generate(question: str, chunks: list[dict], mode: str) -> GeneratorResult`

Each chunk dict is the raw output from `Retriever.query()`:
```python
{
    "chunk_id": "mit_6046_lec10_chunk_009",
    "video_id": "mit_6046_lec10",
    "start_time": 315.0,   # seconds (float)
    "end_time": 360.0,     # seconds (float)
    "text": "...",
    "score": 0.87
}
```

`mode` is passed through to `GeneratorResult` for downstream logging; it does not change
prompt construction (both modes use the same prompt template).

---

## Outputs

```python
@dataclass
class GeneratorResult:
    question: str
    answer: str
    citations: list[str]          # formatted citation strings
    cited_chunks: list[dict]      # subset of input chunks that were cited
    predicted_start: float        # union span start (seconds)
    predicted_end: float          # union span end (seconds)
    mode: str                     # "transcript_only" | "transcript_plus_frames"
    raw_llm_response: str         # full LLM response string, for debugging
```

---

## Prompt Template

Each chunk is rendered as a numbered excerpt:
```
[1] mit_6046_lec10 @ 05:15 to 06:00
<chunk text here>

[2] mit_6046_lec10 @ 12:30 to 13:15
<chunk text here>
...
```

System prompt instructs the LLM to:
- Answer only from the provided excerpts
- Cite by excerpt number(s) in `"citations"` field
- Return strict JSON: `{"answer": "...", "citations": [1, 3]}`
- Keep answer concise (1–3 sentences)

---

## YouTube Deep Link Formula

```
https://youtu.be/{youtube_id}?t={seconds}
```

`youtube_id` is resolved from `data/raw/metadata.json` via `video_id`.
`seconds` = `int(predicted_start)` (truncated, not rounded).

---

## Config Keys Used

```yaml
generator:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 512
```

All keys read from `cfg.generator` via `src/config.py`. No hardcoded values in the module.

---

## Out of Scope

- Streaming / async LLM calls
- Multi-turn conversation / chat history
- Fallback to a second model on failure (raise immediately)
- Any QA generation logic (that is Phase 7: `src/qa_generator.py`)
