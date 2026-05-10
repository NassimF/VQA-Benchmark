# Phase 7.1–7.2 — QA Generation: Requirements

## Scope

Implement draft QA generation for the benchmark:

- `src/qa_generator.py` — module that generates 15 draft QA pairs per lecture via Claude
- `scripts/generate_qa.py` — CLI wrapper that reads augmented chunks and saves raw output

**Review method:** LLM-only review (no human review). Ground truth spans are LLM-estimated
from chunk boundaries (~±15–30s precision). This is a known limitation to be disclosed in
the paper's limitations section — it means temporal IoU measures retrieval at chunk
granularity rather than exact-second precision, which is acceptable for 45s windows.

**Stop at Phase 7.3** for `build_benchmark.py` and `validate_benchmark.py` until the
review pipeline is implemented.

---

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Generation model | `claude-sonnet-4-6` | Configured in `config.yaml`; strong multi-hop question design, cost-effective |
| Source material | Augmented chunks (`data/chunks/{video_id}_chunks_augmented.json`) | Includes Qwen2-VL frame captions — required to generate visual-dependent questions |
| Output path | `data/qa_pairs/raw/{video_id}_qa_raw.json` | Matches project directory structure; separate from reviewed output |
| Output format | Structured JSON (list of QA dicts) | Matches the standard QA schema; 2-space indentation per project convention |
| Run strategy | Pilot 3 lectures, inspect, then `--all` | Cheap to catch prompt issues before spending on 60 × API calls |

---

## Question Mix (per lecture)

Target: 15 raw drafts → 12 accepted after LLM review.

The distribution is designed to demonstrate the effect of visual context on retrieval
performance. Visual questions (`multi-hop-visual` + `visual`) account for 60% of questions —
sufficient statistical power across 60 lectures (~540 visual questions total) to support
the paper's central claim. Text-only questions serve as a control group to isolate the
visual contribution from general retrieval quality differences.

| `question_type` value | Count | Role | Notes |
|---|---|---|---|
| `"multi-hop-visual"` | 7 | Primary | ≥2 non-adjacent spans, ≥1 hop requires frame caption; hardest type; serves both multi-hop and visual contributions |
| `"visual"` | 2 | Primary | Single-hop; answer requires frame caption content |
| `"multi-hop"` | 3 | Control | ≥2 non-adjacent spans, transcript-only; isolates visual gain from multi-hop difficulty |
| `"text"` | 2 | Control | Single-hop transcript-only; must be lecture-specific (not answerable from LLM training data alone) |
| `"unanswerable"` | 1 | Required | Plausible question not answerable from any chunk in this lecture |
| **Total** | **15** | | 10 multi-hop (67%) / 9 visual (60%) / 2 text / 1 unanswerable |

Reject (per `specs/roadmap.md` Common Pitfalls): any question where the answer is < 10 words
or is verbatim in the question. `"text"` questions must be lecture-specific — reject any that
could be answered correctly by a general-purpose LLM without retrieval.

---

## Standard QA Schema

Each item in the output JSON list must conform to:

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
  "question_type": "multi-hop-visual",
  "difficulty": "hard",
  "answerable": true,
  "key_concepts": ["memoization", "optimal substructure"],
  "reviewed_by": "llm_draft",
  "review_date": "2026-05-10"
}
```

### Field rules

- `question_type`: must be one of `"multi-hop-visual"` | `"multi-hop"` | `"visual"` | `"text"` | `"unanswerable"`
- `num_hops`: `1` for `visual`, `text`, `unanswerable`; `2+` for `multi-hop` and `multi-hop-visual`
- `ground_truth_spans`: LLM-estimated from chunk boundaries (~±15–30s); not human-tightened — disclosed as limitation in paper
- `reviewed_by`: always `"llm_draft"` for raw output
- `answerable`: `false` + `ground_truth_spans: []` for `"unanswerable"` questions
- `difficulty`: `"easy"` | `"medium"` | `"hard"` — set by the generating LLM; `multi-hop-visual` should default to `"hard"`

### Derived field (evaluator only — not stored in JSON)

```python
VISUAL_TYPES = {"visual", "multi-hop-visual"}
MULTIHOP_TYPES = {"multi-hop", "multi-hop-visual"}
requires_visual = item["question_type"] in VISUAL_TYPES
is_multihop = item["question_type"] in MULTIHOP_TYPES
```

`requires_visual` is computed at evaluation time from `question_type`. It is **not** a stored field — the question type vocabulary makes it redundant.

---

## Prompt Design

The prompt sent to Claude must:

1. Supply all chunks as numbered excerpts: `[N] chunk_id (start–end)\n{text}\n[frame caption: ...]`
2. Instruct the model to produce exactly 15 QA pairs as a JSON array
3. Specify the required question type mix explicitly
4. Require `ground_truth_spans` with `description` per hop
5. Require `source_chunk_ids` matched to actual chunk IDs from the input
6. Include rejection criteria: answer < 10 words, answer verbatim in question, answer spans only a single word

---

## Config Reference

`config.yaml` fields used by this phase:

```yaml
qa_generation:
  model: "claude-sonnet-4-6"
  questions_per_lecture: 15
  target_accepted: 12
```

The `qa_generator` reads these via `src/config.py` (`cfg.qa_generation`).

---

## Pilot Lectures

Run on these 3 first (diverse subject matter and video length):

| Video ID | Course | Duration |
|----------|--------|----------|
| `mit_6046_lec10` | MIT 6.046 Algorithms | ~80 min |
| `mit_18065_lec06` | MIT 18.065 Linear Algebra | ~54 min |
| `nyu_dl_week6` | NYU Deep Learning | ~89 min |
