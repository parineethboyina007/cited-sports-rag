from __future__ import annotations

import json
import re
import logging

from app.generation.prompts import format_player_block
from app.llm.client import LLMClient
from app.models.schemas import PlayerRecord, VerificationFlag, VerifiedAnswer

logger = logging.getLogger(__name__)

VERIFICATION_SYSTEM_PROMPT = """You are a strict fact-checker.
You are given a set of <PLAYER> profiles and an ANSWER containing claims with citations (e.g., [CRI-001]).

For every claim in the ANSWER, verify it is strictly supported by the cited <PLAYER> profile.
Return ONLY a JSON array of issues. If there are no issues, return [].
Each issue must be an object with:
- "sentence": the sentence containing the issue
- "flag_type": "uncited" | "wrong_entity" | "unverified_fact"
- "details": why it is wrong
- "citation_id": the cited ID in question (e.g. "CRI-001")
"""

def build_verification_prompt(answer: str, candidates: list[PlayerRecord]) -> str:
    blocks = [format_player_block(p) for p in candidates]
    context = "\n\n".join(blocks)
    return f"Context:\n{context}\n\nAnswer to verify:\n{answer}\n\nOutput JSON array:"

class CitationVerifier:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def verify(self, raw_answer: str, candidates: list[PlayerRecord]) -> VerifiedAnswer:
        prompt = build_verification_prompt(raw_answer, candidates)
        json_output = self.llm_client.generate(prompt, system_prompt=VERIFICATION_SYSTEM_PROMPT)
        
        flags_raised = []
        try:
            match = re.search(r"\[.*\]", json_output, re.DOTALL)
            if match:
                issues = json.loads(match.group(0))
                for issue in issues:
                    flags_raised.append(
                        VerificationFlag(
                            sentence=issue.get("sentence", ""),
                            flag_type=issue.get("flag_type", "unverified_fact"),
                            details=issue.get("details", ""),
                            citation_id=issue.get("citation_id")
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to parse verification JSON: {e}")

        fell_back = False
        final_answer = raw_answer
        
        if flags_raised:
            fell_back = True
            from app.generation.template_answers import TemplateAnswerGenerator
            template_gen = TemplateAnswerGenerator()
            safe_verified = template_gen.generate(candidates)
            final_answer = safe_verified.answer
            
        citations = list(set(re.findall(r"\[(CRI-\d{3}|OLY-\d{3})\]", final_answer)))
        
        return VerifiedAnswer(
            answer=final_answer,
            citations=citations,
            source_cards=[p.model_dump() for p in candidates],
            flags_raised=flags_raised,
            flags_repaired=flags_raised if fell_back else [],
            fell_back_to_template=fell_back,
            method="template" if fell_back else "generative"
        )
