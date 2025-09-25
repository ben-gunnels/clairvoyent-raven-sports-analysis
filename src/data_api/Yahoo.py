import os
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import game, league
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Game:
    def __init__(self, sc, code: str="nfl"):
        self.game = game.Game(sc, code)

    def get_game_id(self) -> int:
        """
        Get the game ID.
        """
        return self.game.game_id()
    
    def get_league_ids(self) -> pd.DataFrame:
        """
        Get the league IDs associated with the game.
        """
        return self.game.league_ids()

class League:
    def __init__(self, sc, league_key: str):
        self.league = league.League(sc, league_key)

    def get_current_week(self) -> int:
        """
        Get the current week of the league.
        """
        return self.league.current_week()       
    
    def get_draft_results(self) -> pd.DataFrame:
        """
        Get the draft results of the league.
        """
        return pd.DataFrame(self.league.draft_results())
    
    def get_end_week(self) -> int:
        """
        Get the final week of the league's season.
        """
        return self.league.end_week()
    
    def get_percent_owned(self, player_ids: list[int]):
        """
        Get the percentage of teams that own the specified players.
        """
        return pd.DataFrame(self.league.percent_owned(player_ids))
    
    def get_player_details(self, player: str | int | list[int]) -> pd.DataFrame:
        """
        Get detailed information about a player or list of players.
        """
        return pd.DataFrame(self.league.player_details(player))

    def get_player_stats(self, 
                         player_ids, 
                         req_type: str = "season", 
                         date: datetime.date = None, 
                         week: int = None, 
                         season: int = None) -> pd.DataFrame:
        """
        Get player stats based on the request type.
            req_type: ‘season’, ‘average_season’, ‘lastweek’, ‘lastmonth’, ‘date’, ‘week’
        """
        return pd.DataFrame(self.league.player_stats(player_ids, req_type, date, week, season))
    
    def get_positions(self) -> pd.DataFrame:
        """
        Get the positions used in the league.
        """
        return pd.DataFrame(self.league.positions())
    
    def get_stat_categories(self) -> pd.DataFrame:
        """
        Get the statistical categories used in the league.
        """
        return pd.DataFrame(self.league.stat_categories())

class Yahoo:
    def __init__(self, api_keys=os.getenv("YAHOO_OAUTH_KEYS_PATH"), code: str="nfl"):
        # Reuse the tokens saved earlier
        self.sc = OAuth2(None, None, from_file=api_keys)
        self.game = Game(self.sc, code)
        print("Getting league key")
        league_key = self.game.get_league_ids()[-1]  # Assuming we want the most recent league, it doesn't matter
        print(f"League key: {league_key}")
        self.league = League(self.sc, league_key)
        

