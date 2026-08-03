from __future__ import annotations

from app.models.schemas import PlayerRecord

SYSTEM_PROMPT = """You are the Cited Sports Encyclopedia Assistant.
Your task is to answer user queries using ONLY the provided <PLAYER> profiles.

Rules for your response:
1. Base your answer strictly on the facts provided in the <PLAYER> profiles.
2. You MUST cite your claims using the player ID in square brackets, e.g., [CRI-001] or [OLY-005].
3. Do not include external information or hallucinate facts.
4. Keep the answer concise and direct.
5. If the provided profiles do not contain enough information to answer the query fully, state that the information is unavailable.
"""

def format_player_block(player: PlayerRecord) -> str:
    """
    Format a PlayerRecord into the expected <PLAYER> XML-like block.
    """
    lines = [f'<PLAYER id="{player.id}">']
    lines.append(f"Name: {player.name}")
    
    # Append all dataset-specific fields
    for k, v in player.fields.items():
        if k != "Name":
            lines.append(f"{k}: {v}")
            
    # Append Olympic performances if any
    if player.performances:
        lines.append("Performances:")
        for perf in player.performances:
            lines.append(f"  - {perf.medal} at {perf.games}")
            
    lines.append("</PLAYER>")
    return "\n".join(lines)

def build_generation_prompt(query: str, candidates: list[PlayerRecord]) -> str:
    """Build the final prompt for the LLM."""
    blocks = [format_player_block(p) for p in candidates]
    context = "\n\n".join(blocks)
    
    return f"Context:\n{context}\n\nUser Query: {query}\n\nAnswer:"
