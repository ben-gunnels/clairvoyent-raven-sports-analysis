from yahoo_oauth import OAuth2
from yahoo_fantasy_api import game

# Reuse the tokens saved earlier
sc = OAuth2(None, None, from_file="../utils/oauth2.json")

# NFL game handle (use "nfl")
gm = game.Game(sc, "nfl")      # docs: Game(sc, code)
league_ids = gm.league_ids()   # leagues you can access with this account
print("Your NFL league IDs:", league_ids)

# Pick a league (if you have multiple)
lg = gm.to_league(league_ids[0])   # construct a League object from Game
print("Current week:", lg.current_week())

# -------------- Players: lookup & stats --------------
# 1) Search players by name (returns list of dicts with player details)
players_named_taylor = lg.player_details("Taylor")
print(players_named_taylor[:2])

