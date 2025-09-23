from yahoo_oauth import OAuth2
from yahoo_fantasy_api import game, league
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Game:
    def __init__(self, sc, code: str="nfl"):
        self.game = game.Game(sc, code)

    def get_game_id(self):
        """
        Get the game ID.
        """
        return self.game.game_id()
    
    def get_league_ids(self):
        """
        Get the league IDs associated with the game.
        """
        return self.game.league_ids()

class League:
    def __init__(self, sc, league_key: str):
        self.league = league.League(sc, league_key)

    def get_current_week(self):
        """
        Get the current week of the league.
        """
        return self.league.current_week()       
    
    def get_draft_results(self):
        """
        Get the draft results of the league.
        """
        return self.league.draft_results()
    
    def get_end_week(self):
        """
        Get the final week of the league's season.
        """
        return self.league.end_week()
    
    def get_percent_owned(self, player_ids: list[int]):
        """
        Get the percentage of teams that own the specified players.
        """
        return self.league.percent_owned(player_ids)
    
    def get_player_details(self, player: str | int | list[int]):
        """
        Get detailed information about a player or list of players.
        """
        return self.league.player_details(player)

    def get_player_stats(self, player_ids, req_type: str = "season", date: datetime.date = None, week: int = None, season: int = None):
        """
        Get player stats based on the request type.
            req_type: ‘season’, ‘average_season’, ‘lastweek’, ‘lastmonth’, ‘date’, ‘week’
        """
        return self.league.player_stats(player_ids, req_type, date, week, season)
    
    def get_positions(self):
        """
        Get the positions used in the league.
        """
        return self.league.positions()
    
    def get_stat_categories(self):
        """
        Get the statistical categories used in the league.
        """
        return self.league.stat_categories()

class Yahoo:
    def __init__(self, code: str="nfl"):
        # Reuse the tokens saved earlier
        self.sc = OAuth2(None, None, from_file=os.getenv("YAHOO_OAUTH_KEYS_PATH"))
        self.game = Game(self.sc, code)

        league_key = self.game.get_league_ids()[0]  # Assuming we want the first league, it doesn't matter
        self.leagues = League(self.sc, league_key)
        

