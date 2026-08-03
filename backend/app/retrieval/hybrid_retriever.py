from __future__ import annotations

from app.models.schemas import PlayerRecord, RetrievalResult
from app.retrieval.entity_matcher import EntityMatcher
from app.retrieval.semantic_search import SemanticSearcher


class HybridRetriever:
    def __init__(self, entity_matcher: EntityMatcher, semantic_searcher: SemanticSearcher):
        self.entity_matcher = entity_matcher
        self.semantic_searcher = semantic_searcher

    def retrieve(self, query: str) -> RetrievalResult:
        match_result = self.entity_matcher.match(query)
        sem_candidates, sem_scores = self.semantic_searcher.search(query)
        
        combined_scores: dict[str, float] = {}
        combined_players: dict[str, PlayerRecord] = {}

        # Add semantic scores
        for p, s in zip(sem_candidates, sem_scores):
            combined_players[p.id] = p
            combined_scores[p.id] = s

        # Add entity scores (which may include boost for exact matches)
        for p, s in zip(match_result.matched_players, match_result.scores):
            combined_players[p.id] = p
            if p.id in combined_scores:
                combined_scores[p.id] = max(combined_scores[p.id], s)
            else:
                combined_scores[p.id] = s
                
        # Sort by score descending
        sorted_pairs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_candidates = [combined_players[pid] for pid, _ in sorted_pairs]
        final_scores = [score for _, score in sorted_pairs]
        
        return RetrievalResult(
            candidates=final_candidates,
            scores=final_scores,
            collision_detected=match_result.collision_detected,
            collision_tokens=match_result.collision_tokens,
            method="hybrid"
        )
