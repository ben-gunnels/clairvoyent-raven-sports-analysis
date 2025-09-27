import os 
import sys
import pandas as pd
from datetime import datetime
# Get the path to the project root (assuming notebooks/ and src/ are siblings)
project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_api import Yahoo

def get_all_players():
    """
    Fetch all players from the Yahoo API.
    Returns a DataFrame of all players.
    """
    # Populate player names from the text file
    with open(r"C:\Users\bengu\Documents\Sports Analysis Project\clairvoyent-raven-sports-analysis\data\nfl_players.txt", "r") as f:
        player_names = [line.strip() for line in f]
    return player_names

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

