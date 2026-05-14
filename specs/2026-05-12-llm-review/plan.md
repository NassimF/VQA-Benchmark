# Phase 7.3 — LLM Review: Plan

> **Approval gate:** Before starting any task group, present the group's tasks to the user
> and wait for explicit approval before writing any code or files. Do not proceed to the
> next group without confirmation, even if the previous group completed cleanly.

---

## Group 1 — Branch and Spec Setup

1.1 Create branch `feat/phase-7-llm-review` (done when this spec is written)
1.2 Create `specs/2026-05-12-llm-review/` with `requirements.md`, `plan.md`, `validation.md`
1.3 Update `specs/tech-stack.md` to mark the Phase 7.3 open decision as resolved (LLM-only)
1.4 Run `/changelog` and commit spec files to `feat/phase-7-llm-review`

---

## Group 1.5 — Literature Review Sign-off

> Walk through all 6 Q&A answers with the user and get explicit confirmation on each.
> Any answer that is revised must update both `literature-review/phase_7.3/literature_review_report.md`
> and `specs/2026-05-12-llm-review/requirements.md` before Group 2 starts.
> Group 2 does not begin until all 6 are confirmed.

1.5.1 Confirm Q1: Same-model review accepted (Claude Sonnet 4.6, structured checklist)
1.5.2 Confirm Q2: Binary PASS/FAIL per criterion; G-Eval form-filling rubric
1.5.3 Confirm Q3: Multi-hop adjacency threshold ≥70s (≥2 chunk strides)
1.5.4 Confirm Q4: Answer correctness via atomic fact check against chunk text + frame captions
1.5.5 Confirm Q5: Rejection policy — floor ≥10, 1 retry with failure-aware constraints, discard if <8
1.5.6 Confirm Q6: Span tightening not required; tIoU@0.3 as primary metric

---

## Group 2 — Reviewer Prompt Design

2.1 Write two prompt templates:
    a) Claude primary prompt — G-Eval form-filling rubric for all 3 criteria:
       - C1: instruct reviewer to decompose answer into atomic factual claims and verify
         each claim against cited chunk text individually (D4, FActScore method) — not
         holistic correctness judgment
       - Present each criterion (D2) with explicit chain-of-thought step before PASS/FAIL
       - Include unanswerable-specific path (D5): no-evidence check replaces C1/C2/C3
       - Include visual hop detection instruction (D6): check for `[frame caption: ...]` marker
       - Include multi-hop adjacency check (D3): reject if span gap < 70s
    b) GPT-4o C1 cross-check prompt — C1 only:
       - Simpler prompt scoped to Criterion 1 alone
       - Same atomic fact decomposition instruction as (a)
       - No C2/C3, no unanswerable path, no span gap check
2.2 Define JSON schema for the reviewer response.
    Two schemas required — one per model call (D1: two-call flow for non-unanswerable pairs):
    - Claude primary call (all 3 criteria):
    ```json
    {
      "criterion_1": {"result": "PASS|FAIL", "reason": "..."},
      "criterion_2": {"result": "PASS|FAIL", "reason": "..."},
      "criterion_3": {"result": "PASS|FAIL", "reason": "..."},
      "overall": "ACCEPT|REJECT",
      "rejection_reason": "..."
    }
    ```
    - GPT-4o C1 cross-family call (only when Claude passes C1):
    ```json
    {
      "criterion_1": {"result": "PASS|FAIL", "reason": "..."}
    }
    ```
    If GPT-4o returns FAIL for C1, overall decision is REJECT (knowledge-conflict discard).
2.3 Manually test the prompt on 3 sample raw QA pairs (1 valid, 1 span-gap violation,
    1 type-accuracy failure) and confirm the reviewer returns expected ACCEPT/REJECT.
    Also test the GPT-4o C1 cross-check on the valid pair.

---

## Group 3 — Core Implementation

3.1 Implement `src/qa_reviewer.py`:
    - `review_qa_pair(qa: dict, chunks: dict) -> ReviewResult` — single-pair review
    - `ReviewResult` dataclass: criterion results, overall decision, rejection reason,
      c1_cross_check_result (PASS/FAIL/SKIPPED)
    - Two-call flow (D1): Claude primary for all 3 criteria; if C1 passes, call GPT-4o
      for C1 cross-check via `openai` SDK; if GPT-4o disagrees → REJECT
    - Uses `anthropic` SDK for Claude call; `openai` SDK for GPT-4o C1 call
    - Models from `config.yaml` (`qa_review.primary_model`, `qa_review.c1_crosscheck_model`)
    - Handles unanswerable type with separate prompt path (no C1 cross-check needed)
3.2 Implement `scripts/review_qa.py`:
    - CLI: `--video_id <id>` or `--all`
    - Loads raw QA from `data/qa_pairs/raw/`
    - Loads augmented chunk text from `data/chunks/{video_id}_chunks_augmented.json`
      (must use augmented file — contains [frame caption: ...] markers required for
      C1 atomic check and C3 visual hop detection)
    - Writes accepted pairs to `data/qa_pairs/reviewed/{video_id}_qa_reviewed.json`
    - Writes full review log to `data/qa_pairs/review_log/{video_id}_review_log.json`
3.3a Implement review statistics report:
    - After review pass completes, print per-lecture summary: accepted count, rejected count,
      rejection breakdown by criterion (C1/C2/C3/c1_knowledge_conflict), rejection breakdown
      by question type
    - Print corpus-wide totals: overall rejection rate, lectures below floor, lectures at risk
      of discard, count of knowledge-conflict discards (c1_knowledge_conflict) separately
    - Save report to `data/qa_pairs/review_log/review_summary.json`

    > **Approval gate:** Present the statistics report to the user before proceeding to 3.3b.
    > User decides regeneration strategy (type-targeted vs. full regeneration) based on
    > actual failure distribution. Do not implement regeneration until strategy is confirmed.

3.3b Implement regeneration (strategy decided after 3.3a):
    - Build regeneration prompt with failure-aware constraints carried forward (D8)
    - Run regeneration for the chosen scope (type-targeted or full)
    - Re-run reviewer on regenerated pairs; merge with accepted set
    - If still < 8 after regeneration: write discard flag; log lecture as excluded
3.4 Add `qa_review` section to `config.yaml`:
    ```yaml
    qa_review:
      primary_model: "claude-sonnet-4-6"
      c1_crosscheck_model: "gpt-4o"
      temperature: 0.0
      floor_accepted: 10
      discard_threshold: 8
      max_retries: 1
      min_span_gap_seconds: 70
    ```

---

## Group 4 — Tests

4.1 Write `tests/test_qa_reviewer.py` with synthetic fixtures:
    - Test C1 FAIL: answer claim not in chunk text
    - Test C2 FAIL: span gap < 70s on multi-hop question
    - Test C3 FAIL: multi-hop-visual with no frame caption marker in cited chunks
    - Test unanswerable PASS: no chunk contains supporting evidence
    - Test unanswerable FAIL: one chunk does contain supporting evidence
    - Test overall ACCEPT: all criteria pass, GPT-4o C1 cross-check also passes
    - Test knowledge-conflict discard: Claude passes C1, GPT-4o returns FAIL →
      REJECT with rejection_reason = "c1_knowledge_conflict"
    - Test unanswerable skips GPT-4o: c1_cross_check_result = "SKIPPED"
    - Use `pytest.approx` for any float comparisons (span gap arithmetic)
    - Never load real models — mock both `anthropic.Anthropic` and `openai.OpenAI`
      clients in fixtures (both SDKs are used in the two-call flow)

---

## Group 5 — Full Run and Validation

5.1 Run `python scripts/review_qa.py --all` on all 60 lectures (live Claude + GPT-4o calls)

    > **Approval gate (3.3a):** Review `data/qa_pairs/review_log/review_summary.json`.
    > Confirm regeneration strategy before proceeding to 5.2.

5.2 Run regeneration for lectures below floor (3.3b):
    - Build regeneration prompt with failure-aware constraints (D8)
    - Re-run reviewer on regenerated pairs; merge with accepted set
    - If a lecture is still < 8 after regeneration: write discard flag; log as excluded

5.3 Validate output files and counts:
    - `data/qa_pairs/reviewed/` has exactly 60 files (or 60 − discarded)
    - `data/qa_pairs/review_log/` has exactly 60 files
    - Total accepted ≥ 720; every lecture has ≥ 10 accepted pairs
    - Every lecture has ≥ 1 unanswerable pair and ≥ 60% visual-type pairs

5.4 Validate D1 cross-check logging:
    - Every non-unanswerable pair where Claude passed C1 has `c1_cross_check_result`
      logged as PASS or FAIL in the review log
    - Any knowledge-conflict discard has `rejection_reason = "c1_knowledge_conflict"`

5.5 Validate quality checks:
    - No accepted `multi-hop*` pair has span gap < 70s
    - All accepted `multi-hop-visual` pairs cite ≥ 1 chunk with `[frame caption:]` marker
    - No accepted pair has `answer` length < 10 words
    - All `qa_id` values are unique and follow `{video_id}_q{index:03d}`

5.6 If any lecture is at floor (10–11 accepted), add a footnote to
    `overleaf/assets/sections/results.tex` disclosing the per-lecture distribution

5.7 Run `/changelog`, commit results, push branch, open PR against `main`
