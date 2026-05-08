# Phase 6 — Generator: Validation

Phase 6.1 is complete and ready to merge when **all** of the following pass.

---

## 1. Unit tests — all passing

```bash
conda run -n vqa-benchmark pytest tests/test_generator.py -v
```

Expected: all tests green, no skips.

Covers:
- `_build_prompt`: correct excerpt format (`[N] video_id @ mm:ss to mm:ss`)
- `_parse_llm_output`: valid JSON → correct answer + citation indices
- `_parse_llm_output`: malformed JSON → raises `ValueError`
- `_parse_llm_output`: missing `citations` field → raises `ValueError`
- `_union_span`: single chunk, multi-chunk, unsorted times
- `_format_citation`: deep link uses `int(start_time)` for `?t=`
- `generate()`: end-to-end with mocked `_call_llm`

---

## 2. Smoke test — live API call

Run against one real lecture with both retrieval modes:

```bash
conda run -n vqa-benchmark python - <<'EOF'
from src.retriever import Retriever
from src.generator import generate

q = "What is dynamic programming?"
r = Retriever(mode="transcript_only")
chunks = r.query(q, top_k=4)
result = generate(q, chunks, mode="transcript_only")
print(result.answer)
print(result.citations)
print(f"Span: {result.predicted_start:.1f}s – {result.predicted_end:.1f}s")
EOF
```

Pass criteria:
- `result.answer` is a non-empty string (≥10 words)
- `result.citations` is a non-empty list; each string matches `[video_id @ mm:ss to mm:ss](...)`
- `result.predicted_start < result.predicted_end`
- No exception raised

---

## 3. Config-driven — no hardcoded values

```bash
grep -n "gpt-4o-mini\|temperature\|max_tokens" src/generator.py
```

Expected: zero matches. All LLM parameters read exclusively from `cfg.generator.*`.

---

## 4. Citation format compliance

Manually inspect one citation string from the smoke test.

Expected format:
```
[mit_6046_lec10 @ 05:15 to 06:00](https://youtu.be/Tw1k46ywN6E?t=315)
```

Check:
- `?t=` value equals `int(predicted_start)` for the earliest cited chunk
- YouTube video ID matches `data/raw/metadata.json` entry for the `video_id`

---

## 5. Error handling — malformed output raises

```bash
conda run -n vqa-benchmark python - <<'EOF'
from src.generator import _parse_llm_output
try:
    _parse_llm_output("not json at all", [])
    print("FAIL — should have raised")
except ValueError as e:
    print(f"PASS — raised ValueError: {e}")
EOF
```

Expected output: `PASS — raised ValueError: ...`

---

## 6. Roadmap updated

`specs/roadmap.md` Phase 6.1 status must be `✅` before merging.

---

## Merge checklist

- [ ] `pytest tests/test_generator.py` — all green
- [ ] Smoke test passes with live API call
- [ ] No hardcoded model names or hyperparameters in `src/generator.py`
- [ ] Citation string format verified manually
- [ ] `ValueError` raised on malformed LLM output (confirmed)
- [ ] `specs/roadmap.md` Phase 6.1 marked ✅
- [ ] Git commit: `feat: generator module (Phase 6)`
