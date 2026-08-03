"""
Dataset loader: xlsx → canonical PlayerRecord objects.

Handles both World_Cricketers.xlsx and Indian_Olympic_Players.xlsx.
Implements the three-case performances parsing rule for Olympic athletes:
  (a) 1 medal, 1 Games → single performance
  (b) N medals, N Games → positional zip
  (c) N medals, 1 Games → all medals at that single Games
  Anything else → data-quality warning logged, not silently guessed.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pandas as pd

# Add parent paths so we can import config/models when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import (
    CRICKETERS_FILE,
    CRICKETERS_SHEET_NAME,
    OLYMPIC_FILE,
    OLYMPIC_SHEET_NAME,
    DATA_PROCESSED_DIR,
    PLAYERS_JSON,
    REGISTRY_JSON,
)
from app.models.schemas import Performance, PlayerRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ── Performance parsing ─────────────────────────────────────────


def parse_performances(medals_raw: str, games_raw: str, player_name: str) -> list[Performance]:
    """
    Parse the Olympic Medal(s) and Games (Year) columns into a list of
    Performance objects, handling all three specified cases.
    """
    medals = [m.strip() for m in str(medals_raw).split(";") if m.strip()]
    games = [g.strip() for g in str(games_raw).split(";") if g.strip()]

    n_medals = len(medals)
    n_games = len(games)

    # Case (a): 1 medal, 1 Games → trivial single performance
    if n_medals == 1 and n_games == 1:
        return [Performance(medal=medals[0], games=games[0])]

    # Case (b): N medals, N Games → positional zip
    if n_medals == n_games and n_medals > 1:
        return [Performance(medal=m, games=g) for m, g in zip(medals, games)]

    # Case (c): N medals (N>1), exactly 1 Games → ALL medals at that single Games
    # This is the Manu Bhaker case: "Bronze; Bronze" with "Paris 2024"
    if n_medals > 1 and n_games == 1:
        logger.info(
            f"  [{player_name}] Case (c): {n_medals} medals at 1 Games "
            f"({games[0]}). Each medal assigned to that Games."
        )
        return [Performance(medal=m, games=games[0]) for m in medals]

    # Unexpected pattern — log a data-quality warning, don't guess
    logger.warning(
        f"  [{player_name}] UNEXPECTED pairing: {n_medals} medal(s) vs "
        f"{n_games} Games entry/entries. Medals={medals_raw!r}, "
        f"Games={games_raw!r}. Storing as best-effort zip (may lose data)."
    )
    # Best-effort: zip as many as we can, but warn
    results = []
    for i in range(max(n_medals, n_games)):
        m = medals[i] if i < n_medals else "UNKNOWN"
        g = games[i] if i < n_games else "UNKNOWN"
        results.append(Performance(medal=m, games=g))
    return results


# ── Cricket dataset loader ──────────────────────────────────────


def load_cricketers() -> list[PlayerRecord]:
    """Load World_Cricketers.xlsx and convert to PlayerRecord list."""
    logger.info(f"Loading cricketers from {CRICKETERS_FILE}")
    df = pd.read_excel(CRICKETERS_FILE, sheet_name=CRICKETERS_SHEET_NAME)
    logger.info(f"  Rows: {len(df)}, Columns: {list(df.columns)}")

    # Verify no nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.warning(f"  Null values found:\n{null_counts[null_counts > 0]}")

    records = []
    for idx, row in df.iterrows():
        player_id = f"CRI-{idx + 1:03d}"
        excel_row = idx + 2  # header row + 1-indexing

        fields = {col: str(row[col]) for col in df.columns}

        search_text = " ".join([
            str(row["Name"]),
            str(row["Country"]),
            str(row["Role"]),
            str(row.get("Batting/Bowling Style", "")),
            str(row.get("Era", "")),
            str(row.get("Notable Achievements", "")),
            str(row.get("Background", "")),
        ])

        record = PlayerRecord(
            id=player_id,
            dataset="World_Cricketers",
            category="Cricketer",
            excel_row=excel_row,
            name=str(row["Name"]),
            fields=fields,
            performances=[],
            search_text=search_text,
        )
        records.append(record)

    logger.info(f"  Loaded {len(records)} cricketers")
    return records


# ── Olympic dataset loader ──────────────────────────────────────


def load_olympic_athletes() -> list[PlayerRecord]:
    """Load Indian_Olympic_Players.xlsx and convert to PlayerRecord list."""
    logger.info(f"Loading Olympic athletes from {OLYMPIC_FILE}")
    df = pd.read_excel(OLYMPIC_FILE, sheet_name=OLYMPIC_SHEET_NAME)
    logger.info(f"  Rows: {len(df)}, Columns: {list(df.columns)}")

    # Verify no nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        logger.warning(f"  Null values found:\n{null_counts[null_counts > 0]}")

    records = []
    for idx, row in df.iterrows():
        player_id = f"OLY-{idx + 1:03d}"
        excel_row = idx + 2

        fields = {col: str(row[col]) for col in df.columns}

        # Parse performances using the three-case rule
        performances = parse_performances(
            medals_raw=str(row["Olympic Medal(s)"]),
            games_raw=str(row["Games (Year)"]),
            player_name=str(row["Name"]),
        )

        # Build search text including parsed performances
        perf_text = " ".join(
            f"{p.medal} {p.games}" for p in performances
        )
        search_text = " ".join([
            str(row["Name"]),
            str(row["Sport"]),
            str(row["Event"]),
            perf_text,
            str(row.get("Home State", "")),
            str(row.get("Born", "")),
            str(row.get("Background", "")),
        ])

        record = PlayerRecord(
            id=player_id,
            dataset="Indian_Olympic_Players",
            category="Olympic Athlete",
            excel_row=excel_row,
            name=str(row["Name"]),
            fields=fields,
            performances=performances,
            search_text=search_text,
        )
        records.append(record)

    logger.info(f"  Loaded {len(records)} Olympic athletes")
    return records


# ── Combined loader + persistence ───────────────────────────────


def load_all_players() -> list[PlayerRecord]:
    """Load both datasets and return the combined list."""
    cricketers = load_cricketers()
    athletes = load_olympic_athletes()
    all_players = cricketers + athletes
    logger.info(f"Total players loaded: {len(all_players)}")
    return all_players


def save_players(players: list[PlayerRecord]) -> None:
    """Persist PlayerRecords to JSON (without embeddings, to keep size small)."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save full player records (embeddings added later by build_index)
    records_dicts = [p.model_dump(exclude={"embedding"}) for p in players]
    with open(PLAYERS_JSON, "w", encoding="utf-8") as f:
        json.dump(records_dicts, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(players)} players to {PLAYERS_JSON}")

    # Save id ↔ row mapping as registry
    registry = {
        p.id: {
            "name": p.name,
            "dataset": p.dataset,
            "excel_row": p.excel_row,
            "category": p.category,
        }
        for p in players
    }
    with open(REGISTRY_JSON, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved registry ({len(registry)} entries) to {REGISTRY_JSON}")


def load_players_from_json() -> list[PlayerRecord]:
    """Load previously-persisted PlayerRecords from JSON."""
    with open(PLAYERS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [PlayerRecord(**d) for d in data]


# ── CLI entry point ─────────────────────────────────────────────


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load datasets into canonical PlayerRecords")
    parser.add_argument("--validate", action="store_true", help="Run validation checks after loading")
    args = parser.parse_args()

    players = load_all_players()
    save_players(players)

    if args.validate:
        cricketers = [p for p in players if p.dataset == "World_Cricketers"]
        athletes = [p for p in players if p.dataset == "Indian_Olympic_Players"]

        print(f"\n{'='*60}")
        print(f"VALIDATION RESULTS")
        print(f"{'='*60}")
        print(f"Cricketers: {len(cricketers)} (expected 129)")
        print(f"Olympic athletes: {len(athletes)} (expected 22)")
        print(f"Total: {len(players)} (expected 151)")

        # Check for duplicate names within each dataset
        cri_names = [p.name for p in cricketers]
        oly_names = [p.name for p in athletes]
        cri_dupes = [n for n in cri_names if cri_names.count(n) > 1]
        oly_dupes = [n for n in oly_names if oly_names.count(n) > 1]
        print(f"Duplicate names (cricket): {set(cri_dupes) or 'None'}")
        print(f"Duplicate names (olympic): {set(oly_dupes) or 'None'}")

        # Show specific checkpoint records
        for target_id in ["OLY-004", "OLY-006"]:
            rec = next((p for p in players if p.id == target_id), None)
            if rec:
                print(f"\n--- {target_id}: {rec.name} ---")
                print(json.dumps(rec.model_dump(exclude={"embedding", "search_text"}), indent=2))
            else:
                print(f"\n!!! {target_id} NOT FOUND !!!")

        # Assertions
        assert len(cricketers) == 129, f"Expected 129 cricketers, got {len(cricketers)}"
        assert len(athletes) == 22, f"Expected 22 athletes, got {len(athletes)}"
        assert not cri_dupes, f"Duplicate cricket names: {set(cri_dupes)}"
        assert not oly_dupes, f"Duplicate olympic names: {set(oly_dupes)}"

        # Verify Manu Bhaker has 2 performances
        manu = next(p for p in players if p.id == "OLY-004")
        assert len(manu.performances) == 2, (
            f"Manu Bhaker should have 2 performances, got {len(manu.performances)}"
        )
        assert all(perf.games == "Paris 2024" for perf in manu.performances), (
            "Both of Manu Bhaker's medals should be at Paris 2024"
        )
        assert all(perf.medal == "Bronze" for perf in manu.performances), (
            "Both of Manu Bhaker's medals should be Bronze"
        )

        # Verify Sushil Kumar has 2 performances with correct pairing
        sushil = next(p for p in players if p.id == "OLY-006")
        assert len(sushil.performances) == 2
        assert sushil.performances[0].medal == "Bronze"
        assert sushil.performances[0].games == "Beijing 2008"
        assert sushil.performances[1].medal == "Silver"
        assert sushil.performances[1].games == "London 2012"

        print(f"\n[OK] ALL VALIDATIONS PASSED")
