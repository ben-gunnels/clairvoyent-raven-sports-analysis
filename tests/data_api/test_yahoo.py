# tests/yahoo/test_yahoo_wrappers.py
import pytest
from datetime import date

# === Adjust this import to match your project ===
# e.g., if your file is src/data_api/yahoo_wrappers.py:
from src.data_api.Yahoo import Game, League, Yahoo


# -----------------------------
# Test doubles for 3rd-party API
# -----------------------------

class FakeYFA_Game:
    def __init__(self, sc):
        self._sc = sc

    def game_id(self):
        return "nfl"

    def league_ids(self):
        return ["nfl.l.12345", "nfl.l.67890"]


class FakeYFA_League:
    def __init__(self, sc, league_key: str):
        self._sc = sc
        self._league_key = league_key

    def current_week(self):
        return 6

    def draft_results(self):
        # per docs, typically a list of picks / player IDs :contentReference[oaicite:2]{index=2}
        return [{"round": 1, "pick": 1, "player_id": 12345, "cost": 42}]

    def end_week(self):
        return 17

    def percent_owned(self, player_ids):
        return {pid: 0.76 for pid in player_ids}

    def player_details(self, player):
        # Library supports string name, single id, list of ids (your wrapper forwards) :contentReference[oaicite:3]{index=3}
        if isinstance(player, str):
            return [{"player_id": 22222, "name": player, "pos": "RB"}]
        if isinstance(player, int):
            return [{"player_id": player, "name": "Test Player", "pos": "WR"}]
        # list[int]
        return [{"player_id": pid, "name": f"Player {pid}", "pos": "QB"} for pid in player]

    def player_stats(self, player_ids, req_type="season", date=None, week=None, season=None):
        # Return simple fake stats keyed by player id
        return {
            pid: {"req_type": req_type, "week": week, "season": season, "pts": 10.5}
            for pid in (player_ids if isinstance(player_ids, list) else [player_ids])
        }

    def positions(self):
        return ["QB", "RB", "WR", "TE", "K", "DEF"]

    def stat_categories(self):
        # trimmed example
        return [{"stat": "PTS"}, {"stat": "YDS"}, {"stat": "TD"}]


class FakeOAuth2:
    def __init__(self, *_args, **_kwargs):
        # minimal stub; real lib exposes token helpers & session, but we don't need them here
        self.token = {"access_token": "fake"}
    def token_is_valid(self):
        return True
    def refresh_access_token(self):
        return None


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def patch_yahoo_oauth(monkeypatch):
    # Stub out yahoo_oauth.OAuth2 used by your Yahoo() class
    import yahoo_oauth
    monkeypatch.setattr(yahoo_oauth, "OAuth2", FakeOAuth2)
    return FakeOAuth2()


@pytest.fixture
def patch_yfa_game(monkeypatch):
    # Replace yahoo_fantasy_api.game.Game with our fake
    import yahoo_fantasy_api.game as yfa_game
    monkeypatch.setattr(yfa_game, "Game", FakeYFA_Game)
    return FakeYFA_Game


@pytest.fixture
def patch_yfa_league(monkeypatch):
    # Replace yahoo_fantasy_api.league.League with our fake
    import yahoo_fantasy_api.league as yfa_league
    monkeypatch.setattr(yfa_league, "League", FakeYFA_League)
    return FakeYFA_League


# -----------------------------
# Game wrapper tests
# -----------------------------

def test_game_getters_use_underlying_yfa_game(patch_yfa_game):
    sc = object()
    g = Game(sc)
    assert g.get_game_id() == "nfl"
    assert g.get_league_ids() == ["nfl.l.12345", "nfl.l.67890"]


# -----------------------------
# League wrapper tests
# -----------------------------

def test_league_basic_getters(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")
    assert lg.get_current_week() == 6
    assert lg.get_end_week() == 17

def test_league_draft_results(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")
    res = lg.get_draft_results()
    assert isinstance(res, list)
    assert {"round", "pick", "player_id"}.issubset(res[0].keys())

def test_league_percent_owned(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")
    po = lg.get_percent_owned([101, 202])
    assert po == {101: 0.76, 202: 0.76}

def test_league_player_details_accepts_name_id_and_list(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")

    by_name = lg.get_player_details("Taylor")
    assert by_name and by_name[0]["name"] == "Taylor"

    by_id = lg.get_player_details(777)
    assert by_id and by_id[0]["player_id"] == 777

    by_list = lg.get_player_details([1, 2, 3])
    assert len(by_list) == 3 and {r["player_id"] for r in by_list} == {1, 2, 3}

def test_league_player_stats_variants(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")

    season_stats = lg.get_player_stats([10, 20], req_type="season", season=2025)
    assert season_stats[10]["season"] == 2025 and season_stats[20]["req_type"] == "season"

    week_stats = lg.get_player_stats(10, req_type="week", week=3)
    assert week_stats[10]["week"] == 3 and week_stats[10]["req_type"] == "week"

    date_stats = lg.get_player_stats([10], req_type="date", date=date(2025, 9, 1))
    assert date_stats[10]["req_type"] == "date"

def test_league_positions_and_stat_categories(patch_yfa_league):
    sc = object()
    lg = League(sc, "nfl.l.12345")
    assert "QB" in lg.get_positions()
    cats = lg.get_stat_categories()
    assert {"stat"} <= set(cats[0].keys())


# -----------------------------
# Yahoo facade tests
# -----------------------------

def test_yahoo_facade_constructs_game_and_league(patch_yahoo_oauth, monkeypatch, patch_yfa_game, patch_yfa_league):
    """
    Ensures Yahoo() uses OAuth2 (stubbed), builds Game, reads league_ids, and selects first
    to construct a League wrapper.
    """
    # We want the Yahoo() ctor to see our Game wrapper's get_league_ids() return value.
    # Easiest: monkeypatch our wrapper Game.get_league_ids directly.
    monkeypatch.setattr(Game, "get_league_ids", lambda self: ["nfl.l.55555", "nfl.l.66666"])

    y = Yahoo()
    # Confirm the selected league key became the League wrapper's internal league key
    assert isinstance(y.game, Game)
    assert isinstance(y.leagues, League)
    # quick smoke checks through the league wrapper we created
    assert y.leagues.get_current_week() == 6
