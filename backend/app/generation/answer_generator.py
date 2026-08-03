from __future__ import annotations

from app.generation.prompts import SYSTEM_PROMPT, build_generation_prompt
from app.generation.template_answers import TemplateAnswerGenerator
from app.llm.client import LLMClient
from app.models.schemas import GateDecision, VerifiedAnswer
from app.verification.citation_verifier import CitationVerifier


class AnswerGenerator:
    def __init__(self, llm_client: LLMClient, verifier: CitationVerifier):
        self.llm_client = llm_client
        self.verifier = verifier
        self.template_generator = TemplateAnswerGenerator()

    def generate_answer(self, query: str, gate_decision: GateDecision) -> VerifiedAnswer:
        # 1. Refusal check (Path 3d)
        if gate_decision.should_refuse:
            return VerifiedAnswer(
                answer=gate_decision.refusal_message or "I cannot answer this query.",
                citations=[],
                source_cards=[],
                method="refusal"
            )

        # 2. Template routing (Path 3d - simple)
        if gate_decision.query_complexity == "simple":
            return self.template_generator.generate(gate_decision.passed_candidates)

        # 3. Generative path (Path 3f)
        prompt = build_generation_prompt(query, gate_decision.passed_candidates)
        raw_answer = self.llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)

        # 4. Self-RAG verification (Path 3g)
        verified_answer = self.verifier.verify(raw_answer, gate_decision.passed_candidates)
        
        return verified_answer
