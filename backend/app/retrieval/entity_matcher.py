from __future__ import annotations

import re
from typing import Any

from rapidfuzz import fuzz, process

from app.config import ENTITY_EXACT_BOOST, FUZZY_MATCH_THRESHOLD
from app.models.schemas import MatchResult, PlayerRecord


class EntityMatcher:
    def __init__(self, players: list[PlayerRecord], collision_index: dict[str, list[dict[str, Any]]]):
        self.players = {p.id: p for p in players}
        self.player_names = {p.id: p.name for p in players}
        self.collision_index = collision_index

    def match(self, query: str) -> MatchResult:
        query_lower = query.lower()
        query_tokens = set(re.findall(r"[a-zA-Z]+", query_lower))

        collision_detected = False
        collision_tokens = []
        collision_player_ids: set[str] = set()

        for token in query_tokens:
            if token in self.collision_index:
                collision_detected = True
                collision_tokens.append(token)
                # Inject ALL members of this collision group
                for entry in self.collision_index[token]:
                    collision_player_ids.add(entry["id"])

        # fuzzy matching
        matches = process.extract(
            query,
            self.player_names,
            scorer=fuzz.WRatio,
            limit=10
        )

        matched_ids: set[str] = set()
        matched_players = []
        scores = []

        # First add fuzzy matches
        for name, score, pid in matches:
            if score >= FUZZY_MATCH_THRESHOLD:
                final_score = float(score)
                # Boost if exact name is mentioned in the query
                if name.lower() in query_lower or query_lower == name.lower():
                    final_score += ENTITY_EXACT_BOOST
                
                matched_players.append(self.players[pid])
                scores.append(final_score)
                matched_ids.add(pid)

        # Then inject all collision group members that weren't already matched
        for pid in collision_player_ids:
            if pid not in matched_ids and pid in self.players:
                matched_players.append(self.players[pid])
                scores.append(ENTITY_EXACT_BOOST)  # Give them high score since they're collision members
                matched_ids.add(pid)

        return MatchResult(
            matched_players=matched_players,
            scores=scores,
            collision_detected=collision_detected,
            collision_tokens=collision_tokens
        )
