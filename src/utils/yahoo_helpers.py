import os 
import sys
import pandas as pd
from datetime import datetime
# Get the path to the project root (assuming notebooks/ and src/ are siblings)
project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_api import Yahoo
from pathlib import Path
from typing import List, Optional
import logging

def get_all_players(
    file_path: Optional[str] = None,
    *,
    allow_duplicates: bool = True,
    min_len: int = 2,
    encoding: str = "utf-8",
) -> List[str]:
    """
    Load NFL player names from a text file (one per line).

    Error tolerance / quality-of-life:
      - If file_path is None, tries a few sensible locations (env var, cwd/data/, module data/, your original path).
      - Returns [] instead of raising on missing/locked/undecodable files.
      - Ignores blank lines and comment lines starting with '#'.
      - Normalizes internal whitespace (e.g., '  Tom   Brady ' -> 'Tom Brady').
      - Deduplicates while preserving order unless allow_duplicates=True.
      - Skips very short tokens (len < min_len).

    Args:
        file_path: Optional explicit path to the players file.
        allow_duplicates: Keep duplicate names if True.
        min_len: Minimum length for a cleaned name to be kept.
        encoding: File encoding used to read the file.

    Returns:
        List[str]: Cleaned player names. Empty list on error.
    """
    # Candidate paths (in order):
    candidates = []
    if file_path:
        candidates.append(Path(file_path))
    # Allow override via env var
    env_path = os.getenv("PLAYER_NAMES_PATH")
    if env_path:
        candidates.append(Path(env_path))

    # Common project locations
    candidates.extend([
        Path.cwd() / "data" / "nfl_players.txt",
        Path(__file__).resolve().parent / "data" / "nfl_players.txt",
        # Your original absolute path as a fallback:
        Path(r"C:\Users\bengu\Documents\Sports Analysis Project\clairvoyent-raven-sports-analysis\data\nfl_players.txt"),
    ])

    chosen: Optional[Path] = next((p for p in candidates if p and p.exists()), None)
    if not chosen:
        logging.warning("Player file not found in any expected location; returning empty list.")
        return []

    names: List[str] = []
    seen = set()

    try:
        with chosen.open("r", encoding=encoding, errors="replace") as f:
            for line_no, raw in enumerate(f, 1):
                name = raw.strip()
                if not name or name.startswith("#"):
                    continue
                # Collapse internal whitespace
                name = " ".join(name.split())
                if len(name) < min_len:
                    logging.debug("Skipping short token on line %d: %r", line_no, raw)
                    continue
                if allow_duplicates:
                    names.append(name)
                else:
                    if name not in seen:
                        names.append(name)
                        seen.add(name)
    except FileNotFoundError:
        logging.warning("Player file %s not found; returning empty list.", chosen)
        return []
    except PermissionError:
        logging.error("No permission to read %s; returning empty list.", chosen)
        return []
    except Exception as e:
        logging.exception("Unexpected error reading %s: %s", chosen, e)
        return []

    return names


def get_player_details(yahoo_api: Yahoo, player_names: list[str]) -> list[pd.DataFrame | None] | None:
    """
    Fetch player details using the Yahoo API.
    Returns a list of player details or None if not found.
    """
    player_details = []
    for name in player_names:
        try:
            details = yahoo_api.league.get_player_details(name)
            if details is not None and not details.empty:
                player_details.append(details.iloc[0])
        except Exception as e:
            print(f"Error fetching details for {name}: {e}")        
    return player_details if player_details else None
    
def get_player_stats(yahoo_api: Yahoo,
                        player_ids: list[str | int], 
                        req_type: str = "season", 
                        date: datetime.date = None, 
                        week: int = None, 
                        season: int = None) -> pd.DataFrame | None:
    """
    Fetch player stats using the Yahoo API.
    Returns a DataFrame of player stats or None if not found.
    """
    stats_df = pd.DataFrame()
    for player_id in player_ids:
        try:
            stats = yahoo_api.league.get_player_stats(player_id, req_type, date, week, season)
            stats_df = pd.concat([stats_df, stats], ignore_index=True) if stats is not None else stats_df
        except Exception as e:
            print(f"Error fetching stats for player ID {player_id}: {e}")
            return None
        
    return stats_df if not stats_df.empty else None

