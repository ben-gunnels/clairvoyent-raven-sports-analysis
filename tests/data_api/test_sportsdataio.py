# tests/data_api/test_sportsdataio.py
import pytest
import pandas as pd
import responses

from src.data_api import SportsDataIO


# ---------- Helpers ----------------------------------------------------------

def add_json_get(url: str, payload, status: int = 200) -> None:
    """
    Register a mocked GET endpoint that returns JSON.
    Using 'json=' is the supported way to provide a JSON body in 'responses'.
    """
    responses.add(
        responses.GET,
        url,
        json=payload,
        status=status,
    )


# ---------- Fixtures ---------------------------------------------------------

@pytest.fixture(autouse=True)
def ensure_env_key(monkeypatch):
    # Ensure constructor can read the API key from the environment.
    monkeypatch.setenv("SPORTS_DATA_IO_API_KEY", "test-key")


@pytest.fixture
def api():
    # Uses the env var set by ensure_env_key
    return SportsDataIO()


# ---------- Core -------------------------------------------------------------

@responses.activate
def test_core_get_bye_weeks_default(api):
    url = "https://api.sportsdata.io/api/nfl/fantasy/json/Byes/2024REG"
    add_json_get(url, [{"Team": "SF", "Week": 9}])

    df = api.core.get_bye_weeks()
    assert isinstance(df, pd.DataFrame)
    assert {"Team", "Week"}.issubset(df.columns)
    # verify header was sent
    sent_headers = responses.calls[0].request.headers
    assert sent_headers.get("Ocp-Apim-Subscription-Key") == "test-key"


@responses.activate
def test_core_get_player_details_available_default(api):
    url = "https://api.sportsdata.io/api/nfl/fantasy/json/Players"
    add_json_get(url, [{"PlayerID": 1}])

    df = api.core.get_player_details()
    assert not df.empty
    assert "PlayerID" in df.columns


def test_core_get_player_details_bad_type(api):
    with pytest.raises(ValueError):
        api.core.get_player_details(typeof="nope")


# ---------- Fantasy ----------------------------------------------------------

@responses.activate
def test_fantasy_get_dfs_slates_by_week_defaults(api):
    url = "https://api.sportsdata.io/api/nfl/fantasy/json/DfsSlatesByWeek/2024REG/1"
    add_json_get(url, [{"SlateID": 123}])

    df = api.fantasy.get_dfs_slates_by_week()  # season="2024REG", week=1
    assert "SlateID" in df.columns


@responses.activate
def test_fantasy_get_player_season_stats_accepts_year_only(api):
    # Your function allows "YYYY" via alternate=True path
    url = "https://api.sportsdata.io/api/nfl/fantasy/json/PlayerSeasonStats/2024"
    add_json_get(url, [{"PlayerID": 5, "Season": 2024}])

    df = api.fantasy.get_player_season_stats(season="2024")
    assert {"PlayerID", "Season"}.issubset(df.columns)


# ---------- Odds -------------------------------------------------------------

@responses.activate
def test_odds_get_pregame_odds_defaults(api):
    url = "https://api.sportsdata.io/api/nfl/odds/json/GameOddsByWeek/2024REG/1"
    add_json_get(url, [{"GameId": 999}])

    df = api.odds.get_pregame_odds()
    assert "GameId" in df.columns


@responses.activate
def test_odds_get_scores_season_only(api):
    url = "https://api.sportsdata.io/api/nfl/odds/json/Scores/2024"
    add_json_get(url, [{"ScoreID": 42}])

    df = api.odds.get_scores(season="2024")
    assert "ScoreID" in df.columns


@responses.activate
def test_odds_get_scores_season_week(api, monkeypatch):
    # Force the by-week code path by making the validator return True.
    # (Otherwise your method might hit the season-only endpoint.)
    import src.utils as utils
    monkeypatch.setattr(utils, "validate_season_week", lambda s, w: True)

    url = "https://api.sportsdata.io/api/nfl/odds/json/ScoresByWeek/2024REG/2"
    add_json_get(url, [{"ScoreID": 77}])

    df = api.odds.get_scores(season="2024REG", week=2)
    assert "ScoreID" in df.columns
