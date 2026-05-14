# Phase 7.3 — LLM Review: Requirements

## Scope

Filter 900 raw LLM-drafted QA pairs (15/lecture × 60 lectures) into a final reviewed
set of 720 accepted pairs (12/lecture × 60 lectures) using an automated Claude Sonnet 4.6
reviewer. No span tightening. Note: a human spot-check (D8b) is documented as optional
future validation but is not planned for the current submission.

**Input:** `data/qa_pairs/raw/{video_id}_qa_raw.json`
**Output:** `data/qa_pairs/reviewed/{video_id}_qa_reviewed.json`
**Rejection log:** `data/qa_pairs/review_log/{video_id}_review_log.json`

---

## Locked Decisions

All decisions below are backed by the Phase 7.3 literature review
(`literature-review/phase_7.3/literature_review_report.md`).

### D1 — Reviewer model: Claude Sonnet 4.6 primary + GPT-4o cross-family check for C1

Primary review: Claude Sonnet 4.6, structured G-Eval rubric, all three criteria.
Cross-family verification: GPT-4o reruns Criterion 1 only for pairs where Claude passes C1.
If GPT-4o disagrees on C1, the pair is discarded. C2 and C3: Claude only, no second check.
No human review of any kind.

**Backing:** Ho et al. (2025) shows same-model judging has no SPB for structured QA tasks
(0.85 correlation with human). Yang et al. (2026) structured prompting reduces SPB 31.5% —
so C2 and C3 need no second check. Lee et al. (2026) identifies a concrete systematic
failure mode for C1 specifically: when chunk text conflicts with Claude's parametric
knowledge (as may occur in cutting-edge MIT/Stanford/NYU ML lectures), Claude overrides the
reference text rather than the chunk. A cross-family judge (GPT-4o) is less likely to share
the same parametric bias, making disagreement a reliable signal of knowledge-conflict
failure. C2's ≥70s deterministic threshold (D3) reduces ambiguity enough that a second run
adds little value. Cost: ~$1–3 extra on top of base ~$3–8 (~1.2× total).

**Update 2026-05-13:** Changed from Option B (single-judge) to simplified Option C
(cross-family C1 only). Rationale: knowledge-conflict failure is systematic and silent —
the judge confidently passes C1 while ignoring the source text. Cross-family check is the
only method that catches this. C2 double-run skipped because the ≥70s threshold makes C2
near-deterministic. See lit review Practical Recommendation.

### D2 — Rubric: Binary PASS/FAIL per criterion, G-Eval form-filling

Three criteria evaluated independently; overall ACCEPT only if all three PASS.

```
Criterion 1 — Answer Correctness
Criterion 2 — Span Plausibility
Criterion 3 — Question Type Accuracy
```

**Backing:** G-Eval (Liu et al., 2023) — decomposing evaluation into named criteria with
step-by-step chain-of-thought before scoring achieves Spearman 0.514 with human judgments
vs BLEU/ROUGE. Prometheus (Kim et al., ICLR 2024) — task-specific rubrics achieve Pearson
0.897 with human evaluators, matching GPT-4. Binary PASS/FAIL (rather than 1–5 scale) is
sufficient because Phase 7.3 output is an accept/reject decision, not a quality ranking.

### D3 — Multi-hop adjacency: ≥70s span gap required
> **Relationship to D2:** D3 provides the specific threshold that D2's Criterion 2 (Span Plausibility) requires to be fully specified. D2 defines the rubric structure; D3 provides the parameter value.


Reject multi-hop questions where `|start_A - start_B| < 70s` (i.e., < 2 chunk strides).

**Backing:** Min et al. (2019) demonstrated that 67% of HotpotQA "multi-hop" questions
are answerable by a single-hop BERT model — the root cause being adjacent or redundant
evidence. For LectureBench's chunk structure (45s window, 35s stride), two chunks are
adjacent when their indices differ by ≤1 (they share a 10s overlap). A threshold of 2
strides (70s) ensures the retriever must make at least two genuinely separate decisions.
Xiang et al. (2026) corroborates this: step-level evaluation (span coverage) is needed to
detect single-hop shortcuts hidden under compositional phrasing.

### D4 — Answer correctness: atomic fact verification against chunk text

Reviewer decomposes each answer into its main factual claims and checks each against the
cited chunk text (including frame captions). Reject if any claim is unsupported.

**Backing:** FActScore (Min et al., 2023) — breaking answers into atomic facts and
checking each against a source achieves <2% error vs human annotation. Whole-answer
correctness is too coarse; an answer may be mostly correct but contain one hallucinated
detail. Ho et al. (2025) confirms that LLM judges achieve 0.85 correlation with human
correctness assessments for structured QA when working from source text. Frame captions
(Qwen2-VL-7B) are appended to chunk text, so visual content is available in text form —
no video access required.

### D5 — Unanswerable question verification: no-evidence check

For `question_type = "unanswerable"`: PASS Criterion 1 only if no chunk in the lecture's
retrieved context contains text that could serve as a supporting answer. FAIL if any chunk
provides even partial evidence. Criterion 2 and 3 are not applicable.

**Backing:** SQuAD 2.0 (Rajpurkar et al., 2018) established the canonical protocol for
unanswerable questions: a question is unanswerable if and only if no supporting passage
exists. Applied here: the reviewer scans the top-5 chunks for the lecture; if none contain
evidence for the posed question, the unanswerable label is valid. This inverts the
FActScore atomic-verification procedure: instead of confirming each claim IS supported,
confirm that NO claim is supported.

### D6 — Visual hop detection: structural marker check

A hop is classified as "visual" if and only if the cited `source_chunk_id`'s text contains
a `[frame caption: ...]` marker. This is a deterministic structural check, not a model
inference task.

**Backing:** Tech-stack.md Approach A design: frame captions are appended as
`[frame caption: ...]` to the chunk text before embedding. This marker is present in
both `transcript_plus_frames` chunks and in the `context_text` field of raw QA pairs
generated against augmented chunks. Checking for this marker is a zero-cost, zero-error
detection method that requires no additional model call.

### D7 — Span tightening: not required

Ground-truth spans remain at chunk-level precision (±15–30s). No tightening pass.

**Backing:** EduVidQA (EMNLP 2025) — accepted at EMNLP with ±35.4s auto-generated
timestamps without tightening, using a 4-minute fixed context window to compensate.
LectureBench's ±15–30s is better than this accepted baseline. Temporal IoU@0.3 is robust
to ±20s span errors (a ±20s error on a 45s chunk span still yields IoU ≈ 0.4–0.6).
VideoZeroBench (2026) uses tIoU@0.3 as the primary threshold at Level 4. Report tIoU@0.3
as primary; tIoU@0.5 as secondary with limitation footnote; do not report tIoU@0.7.

### D8 — Regeneration: 1 retry with failure-aware constraint carry-forward

**Update 2026-05-13:** After the full run (398/900 accepted, 56% rejection rate, 53 lectures
below floor), type-targeted regeneration was replaced by **full regeneration** — regenerate
all 15 pairs fresh per lecture below floor. The broad failure distribution across all question
types and lectures makes type-targeted regeneration impractical. Failure-aware constraint
carry-forward remains in effect.

**Update 2026-05-14:** Root-cause analysis of first-run failures identified 6 fixes applied
before regeneration. Key finding: 208/900 (23.1%) rejections were reviewer parse errors caused
by `max_tokens=1024` truncating Claude's JSON response on complex multi-hop questions (now 4096).
Additional generator fixes: span gap formula corrected to start-to-start ≥70s, frame caption
marker pre-check added, answer atomicity rule added. Regeneration uses temperature=0.9 and
qa_id offset q016–q030 to avoid collision with accepted first-run pairs.

When a lecture falls below the floor after first review, regenerate all 15 pairs fresh
with failure-specific constraints appended to the prompt. Constraints injected when the
criterion accounts for ≥30% of that lecture's rejections.

| Criterion failed | Constraint to add in regeneration prompt |
|---|---|
| Criterion 1 — Correctness | Atomicity constraint: every claim must trace to specific chunk text |
| Criterion 2 — Span plausibility | "ground_truth_spans must be ≥70s apart (start-to-start)" |
| Criterion 3 — Type accuracy | Explicit type reminder + frame caption marker check |

Maximum 1 retry per lecture. If still below floor after retry, discard the lecture.

**Backing:** Min et al. (2019) quality-over-quantity principle — a smaller set of genuinely
valid multi-hop questions is more valuable than inflating counts with borderline pairs.
Cost analysis in Phase 7.3 lit review: 900 review calls at ~$0.003 each ≈ $3–8 total;
a second retry round doubles cost for affected lectures only.

### D8b — Optional: Claude C2/C3 reliability check (Cohen's Kappa)

**Update 2026-05-13:** The original D8b condition "Kappa < 0.7 → escalate to GPT-4o" is
superseded — GPT-4o cross-family check for C1 is now unconditional (D1). D8b now applies
only to C2 and C3 reliability.

Run the Claude reviewer twice on C2 and C3 with different prompt seeds; compute Cohen's
Kappa between the two runs. Report Kappa in the paper's Phase 7.3 methodology section.

- Kappa > 0.8 → C2/C3 single-run is well-justified
- Kappa 0.7–0.8 → acceptable; note as a limitation
- Kappa < 0.7 → flag as a paper limitation; C2 near-deterministic (D3 threshold) so
  low Kappa here would indicate a prompt design issue to fix before full run

**This is optional** — it adds cost only for the C2/C3 second-run (~$1–4 extra).

**Backing:** Wei et al. (2024) found LLM judges disagree with themselves 15–25% of the
time under prompt variation. Reporting Kappa directly addresses this concern. PCFJudge
(Huang et al., 2026) confirms permutation consensus is effective for factuality evaluation.

### D9 — Count targets (locked)

| Stage | Count |
|---|---|
| Drafted per lecture | 15 |
| Target accepted | 12 |
| Floor (acceptable shortfall) | 10 |
| Discard threshold | None — all 60 lectures included regardless of count |

**Backing:** Mission.md target: ~720 QA pairs (12 × 60). All 60 lectures must appear in
the benchmark — no lecture is discarded regardless of accepted pair count.
Full corpus coverage is enforced by `scripts/check_coverage.py`:
- Pass 1: any lecture with 0 accepted pairs gets one additional retry.
- Pass 2: if total accepted < 500 or visual pairs < 300 after Pass 1, the script reports
  the lowest-count lectures and asks the user whether to run another pass manually.

**Paper reminder — if final accepted count < 500:** Strengthen the count justification in
`overleaf/assets/sections/benchmark.tex`. Add: our pairs-per-video density exceeds
LongVidSearch (6.7/video), and the high curation cost of multi-hop temporally grounded
visual annotation makes each pair more diagnostic than single-hop pairs in larger benchmarks
(EduVidQA: 5,252 pairs, no multi-hop, no temporal span evaluation). Minimum acceptable for
BMVC: ~500 pairs with ≥300 visual-dependent pairs to preserve the Config 1 vs Config 2
statistical comparison.

---

## Out of Scope

- Automated human review in the curation loop (D8b spot-check is post-hoc validation, not part of the accept/reject gate)
- Span tightening (deferred to future work per Q6)
- Phase 7.5 span precision audit (separate phase, runs after 7.4)
- Phase 8 evaluation (separate phase)

---

## Question Type Mix Per Lecture (target)

| `question_type` | Target drafted | Minimum accepted |
|---|---|---|
| `multi-hop-visual` | 7 | 4 |
| `visual` | 2 | 1 |
| `multi-hop` | 3 | 2 |
| `text` | 2 | 1 |
| `unanswerable` | 1 | 1 |
| **Total** | **15** | **≥10** |

Visual-type (multi-hop-visual + visual) ≥ 60% of accepted pairs, preserved per lecture
to support the paper's Config 1 vs Config 2 comparison.
