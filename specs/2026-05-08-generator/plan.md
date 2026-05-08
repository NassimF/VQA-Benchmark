# Phase 6 — Generator: Plan

## Task Groups

### 1. Define `GeneratorResult` dataclass

File: `src/generator.py`

- Define `@dataclass class GeneratorResult` with fields: `question`, `answer`, `citations`,
  `cited_chunks`, `predicted_start`, `predicted_end`, `mode`, `raw_llm_response`
- All timestamps in seconds (float); no frames, no milliseconds

---

### 2. Implement prompt builder

File: `src/generator.py`

- `_build_prompt(question: str, chunks: list[dict]) -> str`
- Renders each chunk as:
  ```
  [N] {video_id} @ mm:ss to mm:ss
  {text}
  ```
- Formats `start_time` / `end_time` (seconds float) → `mm:ss` string
- Returns complete user message string with the question appended

---

### 3. Implement citation formatter

File: `src/generator.py`

- `_format_citation(chunk: dict, metadata: dict) -> str`
- Reads `youtube_id` from `metadata[video_id]` (loaded from `data/raw/metadata.json`)
- Returns `[video_id @ mm:ss to mm:ss](https://youtu.be/{youtube_id}?t={int(start)})`

---

### 4. Implement span aggregator

File: `src/generator.py`

- `_union_span(chunks: list[dict]) -> tuple[float, float]`
- Returns `(min(start_times), max(end_times))` across cited chunks
- Used to populate `predicted_start` / `predicted_end` in `GeneratorResult`

---

### 5. Implement LLM caller

File: `src/generator.py`

- `_call_llm(system_prompt: str, user_prompt: str, cfg) -> str`
- Uses `openai.OpenAI()` client with `cfg.generator.model`, `cfg.generator.temperature`,
  `cfg.generator.max_tokens`
- Returns raw response string
- No retries — raises immediately on API error

---

### 6. Implement output parser

File: `src/generator.py`

- `_parse_llm_output(raw: str, chunks: list[dict]) -> tuple[str, list[int]]`
- Parses `{"answer": "...", "citations": [1, 3]}` from raw string
- Raises `ValueError(f"Malformed LLM output: {raw!r}")` if JSON missing, unparseable,
  or citations field absent / wrong type
- Citation indices are 1-based (as shown in prompt); converts to 0-based for chunk lookup

---

### 7. Implement `generate()` entry point

File: `src/generator.py`

- `generate(question: str, chunks: list[dict], mode: str) -> GeneratorResult`
- Loads metadata once per call from `data/raw/metadata.json`
- Orchestrates: build prompt → call LLM → parse output → format citations → union span
- Returns fully populated `GeneratorResult`

---

### 8. Unit tests

File: `tests/test_generator.py`

- Fixture: 3 synthetic chunks (no real models loaded)
- Test `_build_prompt` — check excerpt numbering and `mm:ss` formatting
- Test `_parse_llm_output` — valid JSON, malformed JSON (raises), missing citations (raises)
- Test `_union_span` — single chunk, multiple chunks, unsorted start times
- Test `_format_citation` — deep link format, `t=` param equals `int(start_time)`
- Test `generate()` — mock `_call_llm` to return valid JSON; assert `GeneratorResult` fields

---

### 9. Git checkpoint

```
feat: generator module (Phase 6)
```

Update `specs/roadmap.md`: mark Phase 6.1 ✅.
