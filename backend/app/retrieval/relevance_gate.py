from __future__ import annotations

import re

from app.config import ABSENT_ATTRIBUTES, RELEVANCE_SCORE_THRESHOLD
from app.models.schemas import GateDecision, PlayerRecord, RefusalType, RetrievalResult


class RelevanceGate:
    def evaluate(self, query: str, retrieval_result: RetrievalResult) -> GateDecision:
        query_lower = query.lower()
        
        # 1. Attribute Absent Filter — check BEFORE entity matching
        for attr in ABSENT_ATTRIBUTES:
            if attr in query_lower:
                # Try to find a matching entity to cite in the refusal
                best_candidate = None
                if retrieval_result.candidates:
                    best_candidate = retrieval_result.candidates[0]

                if best_candidate:
                    refusal_msg = (
                        f"The datasets don't record {attr}. "
                        f"{best_candidate.name} [{best_candidate.id}] is in the database, "
                        f"but that attribute is not tracked."
                    )
                else:
                    refusal_msg = f"I don't have information about {attr}."

                return GateDecision(
                    should_refuse=True,
                    refusal_type=RefusalType.ATTRIBUTE_ABSENT,
                    refusal_message=refusal_msg,
                    passed_candidates=[],
                    query_complexity="simple"
                )
                
        # 2. Entity Not Found Filter
        passed_candidates = []
        for p, s in zip(retrieval_result.candidates, retrieval_result.scores):
            if s >= RELEVANCE_SCORE_THRESHOLD:
                passed_candidates.append(p)
                
        if not passed_candidates:
            return GateDecision(
                should_refuse=True,
                refusal_type=RefusalType.ENTITY_NOT_FOUND,
                refusal_message="I don't have any player matching your query in the datasets.",
                passed_candidates=[],
                query_complexity="simple"
            )
            
        # 3. Determine complexity
        # Complex if: collision detected, multiple candidates, or comparative query
        is_comparative = any(word in query_lower for word in ["compare", "vs", "versus", "and", "both", "difference"])
        query_complexity = "complex" if (
            retrieval_result.collision_detected 
            or len(passed_candidates) > 1 
            or is_comparative
        ) else "simple"

        return GateDecision(
            should_refuse=False,
            refusal_type=None,
            refusal_message=None,
            passed_candidates=passed_candidates,
            query_complexity=query_complexity
        )
