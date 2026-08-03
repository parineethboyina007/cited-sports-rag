"""
Index builder: embeddings + FAISS vector index + collision index.

Run after load_datasets.py to produce:
  - data/processed/faiss.index      (FAISS flat L2 index, 151 vectors)
  - data/processed/collision_index.json  (token → list of matching player ids)
  - Updated data/processed/players.json  (with embeddings added)
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import (
    COLLISION_INDEX_JSON,
    DATA_PROCESSED_DIR,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    FAISS_INDEX_FILE,
    PLAYERS_JSON,
)
from app.models.schemas import PlayerRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ── Collision index builder ─────────────────────────────────────


def build_collision_index(players: list[PlayerRecord]) -> dict[str, list[dict]]:
    """
    Build a collision index: group every (dataset, id, name) by each
    whitespace-split token in `name` (case-insensitive, strip punctuation).

    Any token mapping to 2+ ids is a collision token.

    Returns:
        Dict mapping collision tokens to lists of
        {"id": "CRI-040", "name": "Zaheer Khan", "dataset": "World_Cricketers"}
    """
    token_map: dict[str, list[dict]] = {}

    for p in players:
        # Split name into tokens, lowercase, strip punctuation
        tokens = re.findall(r"[a-zA-Z]+", p.name.lower())
        # Also keep original-case tokens for display
        original_tokens = re.findall(r"[a-zA-Z]+", p.name)

        seen_tokens = set()  # avoid adding same player twice for repeated tokens
        for token_lower, token_orig in zip(tokens, original_tokens):
            if token_lower in seen_tokens:
                continue
            seen_tokens.add(token_lower)

            if token_lower not in token_map:
                token_map[token_lower] = []

            token_map[token_lower].append({
                "id": p.id,
                "name": p.name,
                "dataset": p.dataset,
                "category": p.category,
            })

    # Filter to only tokens with 2+ players (actual collisions)
    collision_index = {
        token: entries
        for token, entries in token_map.items()
        if len(entries) >= 2
    }

    logger.info(f"Built collision index: {len(collision_index)} collision tokens found")
    return collision_index


# ── Embedding + FAISS builder ───────────────────────────────────


def build_embeddings_and_index(players: list[PlayerRecord]) -> list[PlayerRecord]:
    """
    Generate embeddings for all players using sentence-transformers,
    build a FAISS flat index, and return updated PlayerRecords with embeddings.
    """
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        logger.error(f"Missing dependency: {e}. Install sentence-transformers and faiss-cpu.")
        raise

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Generate embeddings from search_text
    texts = [p.search_text for p in players]
    logger.info(f"Generating embeddings for {len(texts)} players...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    logger.info(f"Embedding shape: {embeddings.shape}")
    assert embeddings.shape == (len(players), EMBEDDING_DIM), (
        f"Expected ({len(players)}, {EMBEDDING_DIM}), got {embeddings.shape}"
    )

    # Update player records with embeddings
    for i, player in enumerate(players):
        player.embedding = embeddings[i].tolist()

    # Build FAISS index
    logger.info("Building FAISS flat index...")
    index = faiss.IndexFlatIP(EMBEDDING_DIM)  # Inner product (cosine sim for normalized vectors)
    index.add(embeddings)
    logger.info(f"FAISS index contains {index.ntotal} vectors")

    # Save FAISS index
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_FILE))
    logger.info(f"Saved FAISS index to {FAISS_INDEX_FILE}")

    return players


# ── Persistence ─────────────────────────────────────────────────


def save_collision_index(collision_index: dict[str, list[dict]]) -> None:
    """Save collision index to JSON."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(COLLISION_INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(collision_index, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved collision index to {COLLISION_INDEX_JSON}")


def save_players_with_embeddings(players: list[PlayerRecord]) -> None:
    """Save PlayerRecords (now with embeddings) to JSON."""
    records_dicts = [p.model_dump() for p in players]
    with open(PLAYERS_JSON, "w", encoding="utf-8") as f:
        json.dump(records_dicts, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(players)} players (with embeddings) to {PLAYERS_JSON}")


def load_collision_index() -> dict[str, list[dict]]:
    """Load previously-built collision index from JSON."""
    with open(COLLISION_INDEX_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Verification ────────────────────────────────────────────────


EXPECTED_COLLISIONS = {
    "khan": {"CRI-040", "CRI-063", "CRI-070", "CRI-126"},
    "singh": {"CRI-037", "CRI-041", "CRI-042", "OLY-019", "OLY-022"},
    "kumar": {"CRI-080", "OLY-006", "OLY-012", "OLY-015"},
    "waugh": {"CRI-006", "CRI-015"},
    "chappell": {"CRI-016", "CRI-017"},
    "afridi": {"CRI-068", "CRI-078"},
    "zaheer": {"CRI-040", "CRI-073"},
    "michael": {"CRI-014", "CRI-023", "CRI-054"},
    "smith": {"CRI-009", "CRI-107"},
    "taylor": {"CRI-019", "CRI-121"},
    "richards": {"CRI-046", "CRI-113"},
    "mohammad": {"CRI-071", "CRI-077", "CRI-127"},
}


def verify_collision_index(collision_index: dict[str, list[dict]]) -> bool:
    """
    Verify the collision index reproduces every expected collision group.
    Returns True if all match exactly.
    """
    all_passed = True

    for token, expected_ids in EXPECTED_COLLISIONS.items():
        if token not in collision_index:
            logger.error(f"  MISSING collision token: '{token}'")
            all_passed = False
            continue

        actual_ids = {entry["id"] for entry in collision_index[token]}
        if actual_ids != expected_ids:
            logger.error(
                f"  MISMATCH for '{token}': expected {sorted(expected_ids)}, "
                f"got {sorted(actual_ids)}"
            )
            all_passed = False
        else:
            names = [entry["name"] for entry in collision_index[token]]
            logger.info(f"  ✓ '{token}' ({len(expected_ids)}): {', '.join(names)}")

    # Check for unexpected collisions (informational, not a failure)
    extra = set(collision_index.keys()) - set(EXPECTED_COLLISIONS.keys())
    if extra:
        logger.info(f"\n  Additional collision tokens not in expected list: {sorted(extra)}")
        for token in sorted(extra):
            names = [f"{e['name']} [{e['id']}]" for e in collision_index[token]]
            logger.info(f"    '{token}' ({len(collision_index[token])}): {', '.join(names)}")

    return all_passed


# ── CLI entry point ─────────────────────────────────────────────


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build embeddings, FAISS index, and collision index")
    parser.add_argument("--verify-collisions", action="store_true",
                        help="Verify collision index against expected groups")
    parser.add_argument("--skip-embeddings", action="store_true",
                        help="Skip embedding generation (collision index only)")
    args = parser.parse_args()

    from app.ingestion.load_datasets import load_players_from_json

    logger.info("Loading players from JSON...")
    players = load_players_from_json()
    logger.info(f"Loaded {len(players)} players")

    # Build collision index
    collision_index = build_collision_index(players)
    save_collision_index(collision_index)

    if args.verify_collisions:
        print(f"\n{'='*60}")
        print("COLLISION INDEX VERIFICATION")
        print(f"{'='*60}")
        passed = verify_collision_index(collision_index)
        if passed:
            print(f"\n[OK] ALL {len(EXPECTED_COLLISIONS)} EXPECTED COLLISION GROUPS VERIFIED")
        else:
            print(f"\n[FAIL] SOME COLLISION GROUPS FAILED VERIFICATION")
            sys.exit(1)

    if not args.skip_embeddings:
        players = build_embeddings_and_index(players)
        save_players_with_embeddings(players)
    else:
        logger.info("Skipping embedding generation (--skip-embeddings)")

    print("\n[OK] Index build complete")
