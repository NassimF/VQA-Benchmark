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

## Group 2 — Reviewer Prompt Design

2.1 Write the reviewer prompt template implementing the G-Eval form-filling rubric:
    - Present each criterion (D2) with explicit chain-of-thought step before PASS/FAIL
    - Include unanswerable-specific path (D5): no-evidence check replaces C1/C2/C3
    - Include visual hop detection instruction (D6): check for `[frame caption: ...]` marker
    - Include multi-hop adjacency check (D3): reject if span gap < 70s
2.2 Define JSON schema for the reviewer response:
    ```json
    {
      "criterion_1": {"result": "PASS|FAIL", "reason": "..."},
      "criterion_2": {"result": "PASS|FAIL", "reason": "..."},
      "criterion_3": {"result": "PASS|FAIL", "reason": "..."},
      "overall": "ACCEPT|REJECT",
      "rejection_reason": "..."
    }
    ```
2.3 Manually test the prompt on 3 sample raw QA pairs (1 valid, 1 span-gap violation,
    1 type-accuracy failure) and confirm the reviewer returns expected ACCEPT/REJECT

---

## Group 3 — Core Implementation

3.1 Implement `src/qa_reviewer.py`:
    - `review_qa_pair(qa: dict, chunks: dict) -> ReviewResult` — single-pair review
    - `ReviewResult` dataclass: criterion results, overall decision, rejection reason
    - Uses `anthropic` SDK; model from `config.yaml` (add `qa_review.model` key)
    - Handles unanswerable type with separate prompt path
3.2 Implement `scripts/review_qa.py`:
    - CLI: `--video_id <id>` or `--all`
    - Loads raw QA from `data/qa_pairs/raw/`
    - Loads chunk text from `data/chunks/` for reviewer context
    - Writes accepted pairs to `data/qa_pairs/reviewed/{video_id}_qa_reviewed.json`
    - Writes full review log to `data/qa_pairs/review_log/{video_id}_review_log.json`
3.3 Implement failure-aware regeneration (D8):
    - After first review pass, identify under-floor lectures (< 10 accepted)
    - Build type-targeted regeneration prompt with failure constraint carried forward
    - Call `qa_generator.py` logic for the missing types only
    - Re-run reviewer on regenerated pairs; merge with accepted set
    - If still < 8 after retry: write discard flag; log lecture as excluded
3.4 Add `qa_review` section to `config.yaml`:
    ```yaml
    qa_review:
      model: "claude-sonnet-4-6"
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
    - Test overall ACCEPT: all criteria pass
    - Use `pytest.approx` for any float comparisons (span gap arithmetic)
    - Never load real models — mock `anthropic.Anthropic` client in fixtures

---

## Group 5 — Full Run and Validation

5.1 Run `python scripts/review_qa.py --all` on all 60 lectures
5.2 Run `python scripts/validate_benchmark.py` readiness pre-check (counts, types, spans)
5.3 Check: every lecture has ≥ 10 accepted pairs; total ≥ 720
5.4 Flag any lecture at floor (10–11 accepted) in the review log for paper footnote
5.5 Run `/changelog`, commit results, push branch
