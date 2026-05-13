"""Phase 7.3 LLM review pass for raw QA pairs.

Two-call flow per non-unanswerable pair (D1):
  1. Claude Sonnet primary: evaluates C1, C2, C3.
  2. GPT-4o cross-check: re-evaluates C1 only if Claude passed it.
     Disagreement on C1 → REJECT with reason "c1_knowledge_conflict".
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Literal

import anthropic
import openai

from src.config import QAReviewConfig
from src.reviewer_prompts import build_claude_prompt, build_gpt4o_c1_prompt

logger = logging.getLogger(__name__)

C1CrossCheckResult = Literal["PASS", "FAIL", "SKIPPED"]


@dataclass
class CriterionResult:
    result: Literal["PASS", "FAIL"]
    reason: str


@dataclass
class ReviewResult:
    qa_id: str
    overall: Literal["ACCEPT", "REJECT"]
    criterion_1: CriterionResult
    criterion_2: CriterionResult
    criterion_3: CriterionResult
    rejection_reason: str
    c1_cross_check_result: C1CrossCheckResult
    c1_cross_check_reason: str = ""


class QAReviewer:
    def __init__(self, cfg: QAReviewConfig) -> None:
        self._cfg = cfg
        self._anthropic = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._openai = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def review_qa_pair(self, qa: dict, chunks: dict[str, str]) -> ReviewResult:
        """Run the full two-call review for a single QA pair.

        Args:
            qa: Raw QA pair dict.
            chunks: Mapping of chunk_id → augmented chunk text.
        """
        is_unanswerable = qa.get("question_type") == "unanswerable"
        system_p, user_p = build_claude_prompt(qa, chunks)
        claude_raw = self._call_claude(system_p, user_p)
        parsed = self._parse_claude_response(claude_raw, qa["qa_id"])

        c1_cross = "SKIPPED"
        c1_cross_reason = ""

        if not is_unanswerable and parsed.criterion_1.result == "PASS" and parsed.overall == "ACCEPT":
            sys_g, user_g = build_gpt4o_c1_prompt(qa, chunks)
            gpt_raw = self._call_gpt4o_c1(sys_g, user_g)
            gpt_result, gpt_reason = self._parse_gpt4o_c1_response(gpt_raw, qa["qa_id"])
            c1_cross = gpt_result
            c1_cross_reason = gpt_reason

            if gpt_result == "FAIL":
                parsed.overall = "REJECT"
                parsed.rejection_reason = "c1_knowledge_conflict"

        parsed.c1_cross_check_result = c1_cross
        parsed.c1_cross_check_reason = c1_cross_reason
        return parsed

    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        response = self._anthropic.messages.create(
            model=self._cfg.primary_model,
            max_tokens=1024,
            temperature=self._cfg.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    def _call_gpt4o_c1(self, system_prompt: str, user_prompt: str) -> str:
        response = self._openai.chat.completions.create(
            model=self._cfg.c1_crosscheck_model,
            temperature=self._cfg.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    def _parse_claude_response(self, raw: str, qa_id: str) -> ReviewResult:
        data = _extract_json(raw, qa_id, context="Claude primary")
        return ReviewResult(
            qa_id=qa_id,
            overall=data.get("overall", "REJECT"),
            criterion_1=CriterionResult(**data.get("criterion_1", {"result": "FAIL", "reason": "parse error"})),
            criterion_2=CriterionResult(**data.get("criterion_2", {"result": "FAIL", "reason": "parse error"})),
            criterion_3=CriterionResult(**data.get("criterion_3", {"result": "FAIL", "reason": "parse error"})),
            rejection_reason=data.get("rejection_reason", ""),
            c1_cross_check_result="SKIPPED",
        )

    def _parse_gpt4o_c1_response(self, raw: str, qa_id: str) -> tuple[C1CrossCheckResult, str]:
        data = _extract_json(raw, qa_id, context="GPT-4o C1 cross-check")
        c1 = data.get("criterion_1", {})
        result = c1.get("result", "FAIL")
        reason = c1.get("reason", "parse error")
        if result not in ("PASS", "FAIL"):
            logger.warning(f"{qa_id}: unexpected GPT-4o C1 result '{result}', treating as FAIL")
            result = "FAIL"
        return result, reason  # type: ignore[return-value]


def _extract_json(raw: str, qa_id: str, context: str) -> dict:
    """Extract the first JSON object from a model response string."""
    raw = raw.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        logger.error(f"{qa_id} [{context}]: no JSON object found in response")
        return {}
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError as exc:
        logger.error(f"{qa_id} [{context}]: JSON parse error — {exc}")
        return {}
