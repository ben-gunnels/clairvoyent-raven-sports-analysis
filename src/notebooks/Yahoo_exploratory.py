import os 
import sys
# Get the path to the project root (assuming notebooks/ and src/ are siblings)
project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_api import Yahoo

# Initialize the Yahoo API wrapper
yahoo_api = Yahoo()
game = yahoo_api.game
leagues = yahoo_api.leagues

# Example usage
game_id = game.get_game_id()
league_ids = game.get_league_ids()
current_week = leagues.get_current_week()
draft_results = leagues.get_draft_results()
end_week = leagues.get_end_week()
print(f"Game ID: {game_id}")
print(f"League IDs: {league_ids}")
print(f"Current Week: {current_week}")
print(f"Draft Results: {draft_results}")
print(f"End Week: {end_week}")

player_stats = leagues.get_player_stats(player_ids=[12345, 67890], req_type="season", season=2023)
print(f"Player Stats: {player_stats}")
