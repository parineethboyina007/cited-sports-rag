"""
Application configuration.

All paths, thresholds, and external service settings.
Reads sensitive values from environment variables / .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")


# ── Paths ───────────────────────────────────────────────────────

PROJECT_ROOT = _backend_dir.parent            # sports-rag-encyclopedia/
BACKEND_DIR = _backend_dir                     # backend/
DATA_RAW_DIR = _backend_dir / "data" / "raw"
DATA_PROCESSED_DIR = _backend_dir / "data" / "processed"

CRICKETERS_FILE = DATA_RAW_DIR / "World_Cricketers.xlsx"
OLYMPIC_FILE = DATA_RAW_DIR / "Indian_Olympic_Players.xlsx"

PLAYERS_JSON = DATA_PROCESSED_DIR / "players.json"
REGISTRY_JSON = DATA_PROCESSED_DIR / "registry.json"
COLLISION_INDEX_JSON = DATA_PROCESSED_DIR / "collision_index.json"
FAISS_INDEX_FILE = DATA_PROCESSED_DIR / "faiss.index"
VERIFICATION_LOG = DATA_PROCESSED_DIR / "verification_log.json"

CRICKETERS_SHEET_NAME = "World Cricketers"
OLYMPIC_SHEET_NAME = "Olympic Players"


# ── LLM ─────────────────────────────────────────────────────────

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048


# ── Embeddings ──────────────────────────────────────────────────

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # dimension of all-MiniLM-L6-v2


# ── Retrieval thresholds ────────────────────────────────────────

FUZZY_MATCH_THRESHOLD = 80        # rapidfuzz score (0–100)
SEMANTIC_TOP_K = 10               # number of vectors to retrieve
RELEVANCE_SCORE_THRESHOLD = 0.35  # minimum score to pass the relevance gate
ENTITY_EXACT_BOOST = 100.0        # score boost for exact name matches


# ── Attribute-absence detection ─────────────────────────────────

# Query keywords that request information NOT present in either dataset schema
ABSENT_ATTRIBUTES = {
    "net worth", "salary", "income", "earnings", "wealth",
    "highest score", "highest individual", "batting average",
    "bowling average", "strike rate", "economy rate",
    "test score", "odi score", "t20 score",
    "ranking", "rank", "icc ranking",
    "records", "statistics", "stats",
    "centuries", "wickets",     # these are aggregated stats, not in the data
    "runs", "catches",
    "height", "weight", "age",
    "family", "wife", "husband", "children",
    "controversy", "scandal",
    "social media", "instagram", "twitter",
}

# Fields that ARE present in the cricket dataset
CRICKET_FIELDS = {"Name", "Country", "Role", "Batting/Bowling Style", "Era",
                  "Notable Achievements", "Background"}

# Fields that ARE present in the Olympic dataset
OLYMPIC_FIELDS = {"Name", "Sport", "Event", "Olympic Medal(s)", "Games (Year)",
                  "Home State", "Born", "Background"}


# ── Server ──────────────────────────────────────────────────────

API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
