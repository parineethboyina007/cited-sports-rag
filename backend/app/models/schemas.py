"""
Pydantic data models for the Cited Sports Encyclopedia.

Defines the canonical PlayerRecord shape, citation/verification types,
and API request/response schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Core domain models ──────────────────────────────────────────


class Performance(BaseModel):
    """A single Olympic performance: one medal at one Games."""
    medal: str      # "Gold", "Silver", "Bronze", "No medal (4th)"
    games: str      # "Tokyo 2020", "Paris 2024", etc.


class PlayerRecord(BaseModel):
    """
    Canonical representation of one row from either dataset.

    IDs follow the pattern CRI-001…CRI-129 / OLY-001…OLY-022.
    `excel_row` is the 1-indexed row number the user would see in Excel.
    `fields` stores every original column as a flat dict.
    `performances` is populated only for Olympic athletes (may have 0-N entries).
    `search_text` concatenates all fields for embedding & verification matching.
    """
    id: str = Field(..., pattern=r"^(CRI|OLY)-\d{3}$")
    dataset: str    # "World_Cricketers" | "Indian_Olympic_Players"
    category: str   # "Cricketer" | "Olympic Athlete"
    excel_row: int  # dataframe_index + 2
    name: str
    fields: dict[str, str]
    performances: list[Performance] = Field(default_factory=list)
    search_text: str = ""
    embedding: list[float] | None = None


# ── Retrieval result models ─────────────────────────────────────


class MatchResult(BaseModel):
    """Result of the entity-matching step."""
    matched_players: list[PlayerRecord] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    collision_detected: bool = False
    collision_tokens: list[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    """Unified output from the hybrid retriever."""
    candidates: list[PlayerRecord] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    collision_detected: bool = False
    collision_tokens: list[str] = Field(default_factory=list)
    method: str = "hybrid"  # "entity_match" | "semantic" | "hybrid"


# ── Relevance gate / refusal models ────────────────────────────


class RefusalType:
    ENTITY_NOT_FOUND = "entity_not_found"
    ATTRIBUTE_ABSENT = "attribute_absent"


class GateDecision(BaseModel):
    """Output of the Corrective RAG relevance gate."""
    should_refuse: bool = False
    refusal_type: str | None = None   # RefusalType value
    refusal_message: str | None = None
    passed_candidates: list[PlayerRecord] = Field(default_factory=list)
    query_complexity: str = "simple"  # "simple" | "complex"


# ── Generation / verification models ───────────────────────────


class VerificationFlag(BaseModel):
    """A single issue found during post-generation citation verification."""
    sentence: str
    flag_type: str   # "uncited" | "wrong_entity" | "unverified_fact"
    details: str
    citation_id: str | None = None


class VerifiedAnswer(BaseModel):
    """Final verified answer ready for the user."""
    answer: str
    citations: list[str] = Field(default_factory=list)       # e.g. ["CRI-006", "CRI-015"]
    source_cards: list[dict] = Field(default_factory=list)    # [{id, dataset, excel_row, name, fields}]
    flags_raised: list[VerificationFlag] = Field(default_factory=list)
    flags_repaired: list[VerificationFlag] = Field(default_factory=list)
    fell_back_to_template: bool = False
    method: str = "template"  # "template" | "generative" | "refusal"


# ── API schemas ─────────────────────────────────────────────────


class QueryRequest(BaseModel):
    """Incoming question from the frontend."""
    query: str = Field(..., min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    """Response sent to the frontend."""
    answer: str
    citations: list[str] = Field(default_factory=list)
    source_cards: list[dict] = Field(default_factory=list)
    method: str = "template"
    collision_detected: bool = False
    collision_tokens: list[str] = Field(default_factory=list)


class PlayerSummary(BaseModel):
    """Lightweight player info for the dataset browser."""
    id: str
    name: str
    dataset: str
    category: str
    excel_row: int
    fields: dict[str, str]
    performances: list[Performance] = Field(default_factory=list)
