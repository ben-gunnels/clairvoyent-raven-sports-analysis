import requests
import os
import pandas as pd
import numpy as np
import typing

from src.utils import validate_date, validate_season, validate_season_week

from dotenv import load_dotenv
load_dotenv()

class Core:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_bye_weeks(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch bye weeks for all teams in a given season.
        """
        if not validate_season(season) and not validate_season(season, alternate=True):
            raise ValueError("Season must be in the format 'YYYY', 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/Byes/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_player_details(self, typeof: str = "available") -> pd.DataFrame:
        """
            Fetch player details based on the type specified. Default to the available players.
        """
        allowed_types = {"available", "free-agent"}
        if typeof not in allowed_types:
            raise ValueError(f"'typeof' must be one of {allowed_types}")

        if typeof == "available":
            url = f"{self.base_url}/Players"
        elif typeof == "free-agent":
            url = f"{self.base_url}/FreeAgents"

        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return pd.DataFrame(response.json())
    
    def get_rookie_details(self, season: str = "2024") -> pd.DataFrame:
        """
            Fetch rookie player details for a given season.
        """
        if not validate_season(season, alternate=True):
            raise ValueError("Season must be in the format 'YYYY'.")
        
        url = f"{self.base_url}/Rookies/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_standings(self, season: int = "2024REG") -> pd.DataFrame:
        """
            Fetch team standings for a given season.
        """
        if not validate_season(season):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/Standings/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_teams(self) -> pd.DataFrame:
        """
            Fetch details of all active teams.
        """
        url = f"{self.base_url}/Teams"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_timeframes(self, typeof: str = "current") -> pd.DataFrame:
        """
            Fetch timeframes based on the type specified. Default to current timeframes.
        """
        allowed_types = {"current", "upcoming", "completed", "recent", "all"}
        if typeof not in allowed_types:
            raise ValueError(f"'type' must be one of {allowed_types}")

        url = f"{self.base_url}/Timeframes/{typeof}"

        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return pd.DataFrame(response.json()) 
    
class Fantasy:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_dfs_slates_by_date(self, date: str) -> pd.DataFrame:
        """
            Fetch DFS slates for a specific date.
        """
        if not validate_date(date):
            raise ValueError("Date must be in the format 'YYYY-MM-DD' or 'YYYY-MONTH-DD'.")
        
        url = f"{self.base_url}/DfsSlatesByDate/{date}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_dfs_slates_by_week(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch DFS slates for a specific week in a given season.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
            
        url = f"{self.base_url}/DfsSlatesByWeek/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_defense_game_stats(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch defensive game stats for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
       
        url = f"{self.base_url}/FantasyDefenseByGame/{season}/{week}"
        
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_defense_season_stats(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch defensive season stats for a given season.
        """
        if not validate_season(season):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/FantasyDefenseBySeason/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_player_game_stats(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch player game stats for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        url = f"{self.base_url}/PlayerGameStatsByWeek/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_player_season_stats(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch player season stats for a given season.
        """
        if not validate_season(season) and not validate_season(season, alternate=True):
            raise ValueError("Season must be in the format 'YYYY', 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/PlayerSeasonStats/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_projected_defense_game_stats(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch projected defensive game stats for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        url = f"{self.base_url}/FantasyDefenseProjectionsByGame/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_projected_defense_season_stats(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch projected defensive season stats for a given season.
        """
        if not validate_season(season):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/FantasyDefenseProjectionsBySeason/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())  
    
    def get_projected_player_game_stats(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch projected player game stats for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        url = f"{self.base_url}/PlayerGameProjectionStatsByWeek/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_projected_player_season_stats(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch projected player season stats for a given season.
        """
        if not validate_season(season):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/PlayerSeasonProjectionStats/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
class Odds:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url   

    def get_pregame_odds(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch pregame odds for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        url = f"{self.base_url}/GameOddsByWeek/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_pregame_odds_line_movement(self, scoreid: int) -> pd.DataFrame:
        """
            Fetch pregame odds line movement for a given season and week.
        """
        url = f"{self.base_url}/GameOddsLineMovement/{scoreid}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_scores(self, season: str = "2024REG", week: typing.Optional[int] = None) -> pd.DataFrame:
        """
            Fetch scores for a given season and week.
        """
        if not validate_season(season, alternate=True) and not validate_season(season):
            raise ValueError("Season must be in the format 'YYYY', 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        if week is not None:
            if not validate_season_week(season, week):
                raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
            url = f"{self.base_url}/ScoresByWeek/{season}/{week}"
        else:
            url = f"{self.base_url}/Scores/{season}"

        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_stadiums(self) -> pd.DataFrame:
        """
            Fetch details of all active stadiums.
        """
        url = f"{self.base_url}/Stadiums"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_team_game_stats(self, season: str = "2024REG", week: int = 1) -> pd.DataFrame:
        """
            Fetch team game stats for a given season and week.
        """
        if not validate_season_week(season, week):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'. Season and week must be valid.")
        
        url = f"{self.base_url}/TeamGameStatsByWeek/{season}/{week}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_team_season_stats(self, season: str = "2024REG") -> pd.DataFrame:
        """
            Fetch team season stats for a given season.
        """
        if not validate_season(season):
            raise ValueError("Season must be in the format 'YYYYREG', 'YYYYPRE', or 'YYYYPOST'.")
        
        url = f"{self.base_url}/TeamSeasonStats/{season}"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json())

class SportsDataIO:
    def __init__(self, api_key: str=None):
        self.api_key = api_key or os.getenv('SPORTS_DATA_IO_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or through the SPORTS_DATA_API_KEY environment variable.")

        self.core = Core(self.api_key, "https://api.sportsdata.io/api/nfl/fantasy/json")
        self.fantasy = Fantasy(self.api_key, "https://api.sportsdata.io/api/nfl/fantasy/json")
        self.odds = Odds(self.api_key, "https://api.sportsdata.io/api/nfl/odds/json")
    
    
