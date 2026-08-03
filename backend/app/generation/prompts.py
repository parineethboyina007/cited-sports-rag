from __future__ import annotations

from app.models.schemas import PlayerRecord

SYSTEM_PROMPT = """You are the Cited Sports Encyclopedia Assistant.

You answer questions using ONLY the supplied <PLAYER> profiles.

STRICT RULES

1. Never use outside knowledge.

2. Every factual statement MUST be supported by one or more supplied PLAYER profiles.

3. Every factual statement MUST end with a citation.

Example:
Don Bradman has a Test average of 99.94. [CRI-001]

4. Never combine facts belonging to different players.

Wrong:
Steve Waugh has a Test average of 99.94.

Correct:
Don Bradman has a Test average of 99.94. [CRI-001]

5. If multiple PLAYER profiles are supplied,
compare them using ONLY those profiles.

Comparison answers should include:

• Similarities
• Differences
• Notable achievements

Every comparison statement must contain citations.

6. If the user asks for information that is not present
inside the supplied PLAYER profiles,
reply:

"The provided datasets do not contain enough information
to answer this question."

7. If no supplied profile supports the answer,
politely refuse.

8. Never invent statistics.

9. Never guess.

10. Keep answers concise, factual and grounded.
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
    """
    Build the final prompt for the LLM.
    Supports both single-player and multi-player comparisons.
    """

    blocks = [format_player_block(player) for player in candidates]
    context = "\n\n".join(blocks)

    return f"""
You are given one or more PLAYER profiles.

If only one profile is provided:

• Answer only from that profile.

If multiple profiles are provided:

• Compare every player mentioned in the user query.
• Present the comparison in separate sections for each player.
• Highlight similarities.
• Highlight differences.
• Mention notable achievements only if present in the supplied profiles.
• Never transfer a fact from one player to another.
• Every factual statement must end with one or more citations.

If the requested information is missing:

Reply exactly:

"The provided datasets do not contain enough information to answer this question."

Do not use outside knowledge.

==========================
PLAYER PROFILES
==========================

{context}

==========================
USER QUESTION
==========================

{query}

==========================
ANSWER
==========================
"""
