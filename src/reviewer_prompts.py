"""Prompt templates for Phase 7.3 LLM review pass."""

from __future__ import annotations


CLAUDE_PRIMARY_SYSTEM = """\
You are a rigorous QA benchmark reviewer for LectureBench, an academic benchmark of \
video lecture question-answer pairs. Your task is to evaluate whether a QA pair meets \
the quality criteria for inclusion in the benchmark.

You will be given:
- A QA pair (question, answer, question_type, ground_truth_spans, source_chunk_ids)
- The chunk text for each cited source chunk (may include [frame caption: ...] markers \
for visual content)

Evaluate the QA pair against three criteria. For each criterion, reason step by step \
before stating PASS or FAIL. Be strict: when in doubt, FAIL.
"""


CLAUDE_PRIMARY_TEMPLATE = """\
## QA Pair

- **qa_id:** {qa_id}
- **question_type:** {question_type}
- **question:** {question}
- **answer:** {answer}
- **ground_truth_spans:** {spans}
- **source_chunk_ids:** {chunk_ids}

## Source Chunks

{chunks_text}

---

## Review Instructions

{unanswerable_or_standard}

---

## Response Format

Return a JSON object exactly matching this schema — no extra keys, no markdown fences:

{{
  "criterion_1": {{"result": "PASS or FAIL", "reason": "one or two sentences"}},
  "criterion_2": {{"result": "PASS or FAIL", "reason": "one or two sentences"}},
  "criterion_3": {{"result": "PASS or FAIL", "reason": "one or two sentences"}},
  "overall": "ACCEPT or REJECT",
  "rejection_reason": "empty string if ACCEPT, else brief reason citing which criterion failed"
}}
"""


_STANDARD_CRITERIA = """\
### Criterion 1 — Answer Correctness

Decompose the answer into its individual atomic factual claims — the smallest \
indivisible assertions. For each claim, check whether it is explicitly supported \
by the cited chunk text (including any [frame caption: ...] content). A claim is \
supported only if the chunk text contains evidence for it; do not use outside \
knowledge. If any claim is unsupported or contradicted by the chunk text, FAIL.

Think step by step: list each atomic claim, then verdict per claim, then overall \
PASS or FAIL for Criterion 1.

### Criterion 2 — Span Plausibility

Check two things:
a) Do the ground_truth_spans start/end times align with the chunk boundaries of \
the cited source_chunk_ids? (Each chunk covers a 45-second window; spans should \
fall within ±15s of a chunk boundary.)
b) For multi-hop and multi-hop-visual questions: is the temporal gap between hops \
≥ 70 seconds? Compute |start_A - start_B| for every pair of hops. If any pair has \
a gap < 70s, FAIL — the hops are too close and can be retrieved in a single step, \
making this single-hop in disguise.

For visual and text questions: only check (a). PASS if spans are plausible.

Think step by step: check each span against its chunk, then compute inter-hop gaps \
if applicable, then PASS or FAIL.

### Criterion 3 — Question Type Accuracy

Verify that the question genuinely requires the claimed question_type:
- **multi-hop-visual**: requires ≥ 2 non-adjacent spans AND ≥ 1 source_chunk_id \
whose chunk text contains a [frame caption: ...] marker. Both conditions must hold.
- **multi-hop**: requires ≥ 2 non-adjacent spans. No frame caption required.
- **visual**: requires exactly 1 span AND ≥ 1 source_chunk_id with a \
[frame caption: ...] marker.
- **text**: requires exactly 1 span. No frame caption required.
- **unanswerable**: handled separately (see unanswerable path).

FAIL if the question could be answered from a single span when multi-hop is claimed, \
or if the type claims visual evidence but no [frame caption: ...] marker is present \
in any cited chunk.

Think step by step: verify type requirements against the actual chunks, then PASS or FAIL.

### Overall Decision

ACCEPT only if Criterion 1, Criterion 2, and Criterion 3 all PASS. Otherwise REJECT \
and state which criterion(a) failed.\
"""


_UNANSWERABLE_CRITERIA = """\
This QA pair has question_type = "unanswerable".

### Criterion 1 — No-Evidence Check (replaces standard Criterion 1)

A question is unanswerable if and only if no chunk in the provided source chunks \
contains text that could serve as a supporting answer. Scan every chunk below. \
If any chunk provides even partial evidence that could answer the question, FAIL. \
PASS only if no chunk contains relevant supporting evidence.

Think step by step: check each chunk for relevant evidence, then PASS or FAIL.

### Criterion 2 — Not Applicable

Set result to "PASS" and reason to "Not applicable for unanswerable questions."

### Criterion 3 — Not Applicable

Set result to "PASS" and reason to "Not applicable for unanswerable questions."

### Overall Decision

ACCEPT if Criterion 1 PASS (no supporting evidence found). REJECT if any evidence found.\
"""


def build_claude_prompt(
    qa: dict,
    chunks: dict[str, str],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the Claude primary review call.

    Args:
        qa: Raw QA pair dict.
        chunks: Mapping of chunk_id → chunk text (with frame captions embedded).
    """
    chunks_text = "\n\n".join(
        f"**{cid}**\n{chunks.get(cid, '[chunk text not found]')}"
        for cid in qa["source_chunk_ids"]
    )

    spans_str = "; ".join(
        f"hop {s['hop']}: {s['start']}s–{s['end']}s" for s in qa["ground_truth_spans"]
    )

    is_unanswerable = qa.get("question_type") == "unanswerable"
    criteria_block = _UNANSWERABLE_CRITERIA if is_unanswerable else _STANDARD_CRITERIA

    user_prompt = CLAUDE_PRIMARY_TEMPLATE.format(
        qa_id=qa["qa_id"],
        question_type=qa["question_type"],
        question=qa["question"],
        answer=qa["answer"],
        spans=spans_str,
        chunk_ids=", ".join(qa["source_chunk_ids"]),
        chunks_text=chunks_text,
        unanswerable_or_standard=criteria_block,
    )

    return CLAUDE_PRIMARY_SYSTEM, user_prompt


# ---------------------------------------------------------------------------
# GPT-4o C1 cross-family check
# ---------------------------------------------------------------------------

GPT4O_C1_SYSTEM = """\
You are a strict factual accuracy reviewer. Your task is to verify whether every \
factual claim in a given answer is explicitly supported by the provided source text. \
Do not use outside knowledge — only the source text matters.
"""


GPT4O_C1_TEMPLATE = """\
## Question

{question}

## Answer to Verify

{answer}

## Source Text

{chunks_text}

---

## Instructions

Decompose the answer into its individual atomic factual claims — the smallest \
indivisible assertions. For each claim, determine whether it is explicitly supported \
by the source text above. A claim is supported only if the source text contains \
direct evidence for it. Do not accept claims that rely on inference, background \
knowledge, or information absent from the source text.

Think step by step: list each atomic claim, check it against the source text, \
then give an overall verdict.

If every claim is supported: PASS.
If any claim is unsupported or contradicted: FAIL.

Return a JSON object exactly matching this schema — no extra keys, no markdown fences:

{{
  "criterion_1": {{"result": "PASS or FAIL", "reason": "one or two sentences citing specific supported or unsupported claims"}}
}}
"""


def build_gpt4o_c1_prompt(
    qa: dict,
    chunks: dict[str, str],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the GPT-4o C1 cross-check call.

    Only called when Claude primary returned PASS for Criterion 1.

    Args:
        qa: Raw QA pair dict.
        chunks: Mapping of chunk_id → chunk text (with frame captions embedded).
    """
    chunks_text = "\n\n".join(
        f"[{cid}]\n{chunks.get(cid, '[chunk text not found]')}"
        for cid in qa["source_chunk_ids"]
    )

    user_prompt = GPT4O_C1_TEMPLATE.format(
        question=qa["question"],
        answer=qa["answer"],
        chunks_text=chunks_text,
    )

    return GPT4O_C1_SYSTEM, user_prompt
