from __future__ import annotations

from app.models.schemas import PlayerRecord, VerifiedAnswer


class TemplateAnswerGenerator:
    """
    Handles simple queries where an LLM is not needed (Deterministic path 3e).
    Now handles both single-player and multi-player (collision) templates.
    """
    def generate(self, candidates: list[PlayerRecord]) -> VerifiedAnswer:
        if not candidates:
            return VerifiedAnswer(
                answer="No relevant information found.",
                citations=[],
                source_cards=[],
                method="template"
            )

        # If only one candidate, use single-player template
        if len(candidates) == 1:
            return self._single_player(candidates[0], candidates)

        # Multiple candidates — list them all distinctly
        return self._multi_player(candidates)

    def _single_player(self, player: PlayerRecord, all_candidates: list[PlayerRecord]) -> VerifiedAnswer:
        lines = [f"{player.name} is a {player.category}."]
        
        for k, v in player.fields.items():
            if k != "Name":
                lines.append(f"- {k}: {v}")
                
        if player.performances:
            lines.append("- Performances:")
            for perf in player.performances:
                lines.append(f"  * {perf.medal} at {perf.games}")
                
        answer_text = "\n".join(lines) + f" [{player.id}]"
        
        return VerifiedAnswer(
            answer=answer_text,
            citations=[player.id],
            source_cards=[p.model_dump() for p in all_candidates],
            method="template"
        )

    def _multi_player(self, candidates: list[PlayerRecord]) -> VerifiedAnswer:
        all_citations = []
        sections = []

        for player in candidates:
            lines = [f"**{player.name}** [{player.id}]:"]
            for k, v in player.fields.items():
                if k != "Name":
                    lines.append(f"  - {k}: {v}")
            if player.performances:
                lines.append("  - Performances:")
                for perf in player.performances:
                    lines.append(f"    * {perf.medal} at {perf.games}")
            sections.append("\n".join(lines))
            all_citations.append(player.id)

        answer_text = "\n\n".join(sections)

        return VerifiedAnswer(
            answer=answer_text,
            citations=all_citations,
            source_cards=[p.model_dump() for p in candidates],
            method="template"
        )
