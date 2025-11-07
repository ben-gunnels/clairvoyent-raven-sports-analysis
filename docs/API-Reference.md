# API Reference Manual

This section describes how to interact with the API for various sources of NFL data.

---

## NFL Data Sources

---

## Sports Data IO (Discovery Lab)

**Description**

Provides live play-by-play data, seasonal statistics, and player feeds. Includes fantasy information and a *Discovery Lab* environment for personal projects. The previous season’s data is available for free for prototyping and testing.

---

### Argument Conventions

| Argument    | Type  | Description                                                                                                                  |
| ----------- | ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| **season**  | `str` | In `"YYYYTYPE"` format, where `TYPE` is one of: <br>• `REG` – Regular season<br>• `PRE` – Preseason<br>• `POST` – Postseason |
| **week**    | `int` | Depends on the season type:<br>• Preseason: `0–4`<br>• Regular season: `1–17`<br>• Postseason: `1–4`                         |
| **scoreid** | `str` | The `ScoreID` of an NFL game. ScoreIDs can be found in the **Scores API**.                                                   |

---

## API Namespaces and Methods

### `SportsDataIO.core`

| Method                       | Returns        | Description                                                                    |
| ---------------------------- | -------------- | ------------------------------------------------------------------------------ |
| `get_bye_weeks(season)`      | `pd.DataFrame` | Get each team’s bye weeks for the specified season.                            |
| `get_player_details(typeof)` | `pd.DataFrame` | Retrieve details for players. `typeof` can be `"available"` or `"free-agent"`. |
| `get_rookie_details(season)` | `pd.DataFrame` | Get details for rookie players by season.                                      |
| `get_standings(season)`      | `pd.DataFrame` | Get league standings for a given season.                                       |
| `get_teams()`                | `pd.DataFrame` | Get details of all active teams.                                               |
| `get_timeframes(typeof)`     | `pd.DataFrame` | Get detailed information about past, present, and future timeframes.           |

---

### `SportsDataIO.fantasy`

| Method                                           | Returns        | Description                                                      |
| ------------------------------------------------ | -------------- | ---------------------------------------------------------------- |
| `get_dfs_slates_by_date(date)`                   | `pd.DataFrame` | Get daily fantasy sports (DFS) slates for a specific date.       |
| `get_dfs_slates_by_week(season, week)`           | `pd.DataFrame` | Get DFS slates for a specific season and week.                   |
| `get_defense_game_stats(season, week)`           | `pd.DataFrame` | Get a team’s defensive game stats for the given season and week. |
| `get_defense_season_stats(season)`               | `pd.DataFrame` | Get a team’s defensive season stats.                             |
| `get_player_game_stats(season, week)`            | `pd.DataFrame` | Get individual player game stats for the given season and week.  |
| `get_player_season_stats(season)`                | `pd.DataFrame` | Get individual player season stats.                              |
| `get_projected_defense_game_stats(season, week)` | `pd.DataFrame` | Get projected defensive game stats for a team.                   |
| `get_projected_defense_season_stats(season)`     | `pd.DataFrame` | Get projected defensive season stats for a team.                 |
| `get_projected_player_game_stats(season, week)`  | `pd.DataFrame` | Get projected player game stats.                                 |
| `get_projected_player_season_stats(season)`      | `pd.DataFrame` | Get projected player season stats.                               |

---

### `SportsDataIO.odds`

| Method                                    | Returns        | Description                                              |
| ----------------------------------------- | -------------- | -------------------------------------------------------- |
| `get_pregame_odds(season, week)`          | `pd.DataFrame` | Get pregame betting odds for games in a season and week. |
| `get_pregame_odds_line_movement(scoreid)` | `pd.DataFrame` | Get betting line movement prior to a specific game.      |
| `get_scores(season, week)`                | `pd.DataFrame` | Get game scores for a season and week.                   |
| `get_stadiums()`                          | `pd.DataFrame` | Get information on current NFL stadiums.                 |
| `get_team_game_stats(season, week)`       | `pd.DataFrame` | Get team stats for a specific season and week.           |
| `get_team_season_stats(season)`           | `pd.DataFrame` | Get team stats for an entire season.                     |


@TODO ADD EXAMPLE USAGE SECTION
---

### Notes

* All method names are shown exactly as used in the API.
* Ensure correct argument types and valid values (for example, `season="2024REG"`).

## Yahoo Fantasy (Wrapper)

**Description**  
Thin wrapper around `yahoo_fantasy_api` that provides convenient access to Yahoo Fantasy NFL data via three classes: `Game`, `League`, and `Yahoo`. Uses OAuth2 tokens loaded by `yahoo_oauth.OAuth2`. You must authenticate once to create a token file, then reuse it for future sessions.  
See official docs: [Yahoo Fantasy API authentication](https://yahoo-fantasy-api.readthedocs.io/en/latest/authentication.html?utm_source=chatgpt.com)

**Upstream APIs / References**  
- `yahoo_fantasy_api` methods: `game_id()`, `league_ids()`, `player_details()`, `player_stats()`, `positions()`, `stat_categories()`.  
- Yahoo Fantasy Sports API resource model (game, league, player).  
- Yahoo OAuth2 / token flow (client keys, redirect, token exchange).

---

### Authentication

Before using the wrapper, you need to:

1. Register a Yahoo developer app and perform an OAuth flow once to obtain tokens (access & refresh).  
2. Save credentials (consumer key/secret + tokens) in a JSON file.  
3. Set an environment variable like `YAHOO_OAUTH_KEYS_PATH` pointing to that JSON file.  
4. In your wrapper’s constructor, do:

```python
self.sc = OAuth2(None, None, from_file=api_keys)
```

If tokens are valid or refreshable, the session works without further user intervention.

---

### Argument Conventions

| Parameter       | Type                           | Description |
|-----------------|--------------------------------|-------------|
| **code**        | `str`                          | Yahoo sport code (default `"nfl"`) |
| **league_key**  | `str`                          | Identifier for a Yahoo league (e.g. `nfl.l.12345`) |
| **player**      | `str \| int \| list[int]`      | Either a name prefix or one or more Yahoo player IDs |
| **req_type**    | `str`                          | One of: `season`, `average_season`, `lastweek`, `lastmonth`, `date`, `week` for stats queries |

---

## API Namespaces & Methods

### `Yahoo.game`

Wrapper around `yahoo_fantasy_api.game.Game`:

| Method              | Returns          | Description |
|---------------------|------------------|-------------|
| `get_game_id()`     | `int`            | Yahoo game identifier (for that sport + year) |
| `get_league_ids()`  | `list[str]`      | League identifiers accessible by the authorized user |

---

### `Yahoo.league`

Wrapper around `yahoo_fantasy_api.league.League`, returning `pandas.DataFrame` in many cases:

| Method | Returns | Description |
|--------|---------|-------------|
| `get_current_week()` | `int` | Current week number for the league |
| `get_draft_results()` | `pd.DataFrame` | The draft results (rounds, picks, players) |
| `get_end_week()` | `int` | Final week number for the season |
| `get_percent_owned(player_ids)` | `pd.DataFrame` | Percent-owned statistics for specified players |
| `get_player_details(player)` | `pd.DataFrame` | Detailed player metadata (search or ID lookup) |
| `get_player_stats(player_ids, req_type, date=None, week=None, season=None)` | `pd.DataFrame` | Player statistics by request type |
| `get_positions()` | `pd.DataFrame` | List of positions used in the league |
| `get_stat_categories()` | `pd.DataFrame` | Statistical categories definitions for league scoring |

---

### `Yahoo`

High-level facade that initializes the OAuth session, picks a league, and provides direct access:

- **Constructor**:
  ```python
  Yahoo(api_keys=os.getenv("YAHOO_OAUTH_KEYS_PATH"), code="nfl")
  ```
  
- Internally it:
  1. Initializes `OAuth2` session  
  2. Constructs `Game(self.sc, code)`  
  3. Retrieves `league_ids()` and selects one (default logic)  
  4. Builds `League(self.sc, league_key)`

---

## Example Usage

```python
from data_api.Yahoo import Yahoo

y = Yahoo()  # assumes YAHOO_OAUTH_KEYS_PATH is set properly

# Game-level
game_id = y.game.get_game_id()
league_ids = y.game.get_league_ids()

# League-level
current_week = y.league.get_current_week()
draft_df = y.league.get_draft_results()

# Player lookup
df_by_name = y.league.get_player_details("Taylor")
df_by_ids = y.league.get_player_details([12345, 67890])

# Player stats (season / weekly)
season_stats = y.league.get_player_stats([12345], req_type="season", season=2025)
weekly_stats = y.league.get_player_stats(12345, req_type="week", week=3)

positions = y.league.get_positions()
stat_cats = y.league.get_stat_categories()
```

---

### Troubleshooting & Tips

- **FileNotFoundError on OAuth JSON**: Verify that the env var `YAHOO_OAUTH_KEYS_PATH` points to an existing JSON file. Use absolute paths when possible.  
- **Missing `access_token` in JSON**: If the JSON lacks tokens after your first run, the OAuth flow likely failed. Re-run the authorization process so tokens are persisted.  
- **Multiple leagues / selection logic**: The wrapper uses a default choice (last league ID). You may want to adjust logic to pick a specific league.

## Pro Football Reference

**Description**

Provides seasonal data for passing, rushing and receiving, defense, and kicking. Scrapes active players from Pro Football Reference for their most relevant stats. 

---
### Prerequisite

Before using the api, ensure that a data cache json file is set up in the repository. To do this, add pfr_data_cache.json as an empty file in the \data folder. In your environment variables, initialize PFR_DATA_CACHE to the full absolute path to this data cache. 

---

### Argument Conventions

| Argument    | Type  | Description                                                                                                                  |
| ----------- | ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| **name**    | `str` | Player name to be matched. Query will use fuzzy matching to return the best match.                   |
| **season**  | `str  \| int` | In `"YYYY"` format. This will be used to query the available data for that specified season. |

---

## API Namespaces and Methods

### `PFR`

| Method                            | Returns   |    Description                                                                                   |
| ----------------------------      | --------------- | ----------------------------------------------------------------------------------------------|
| `get_player_stats(name, season)`  | `pd.DataFrame`  | Get a player's seasonal stats by name and optionally by season, otherwise return all seasons. |

---

## Example Usage

```python
from data_api.PFR import PFR

pfr_api = PFR() 

# Get the name for a player to query, names text should be sourced from Pro Football Reference
with open(r"C:\Path\To\nfl_player_names.txt", "r") as f:
  names = [line.strip() for line in f.readlines()]

example_player = names[0]

player_total_stats = pfr_api.get_player_stats(name=example_player)
# Good
player_2023_stats = pfr_api.get_player_stats(name=example_player, season=2023)
# Also Good
player_2023_stats = pfr_api.get_player_stats(name=example_player, season='2023')
```

---

# Notes
* This method involves web scraping pro-football-reference.com. The website allows modest scraping efforts but it is imperative when you call this API to self-regulate. According to Pro Football Reference, the server will block requests "more often than ten requests in a minute". source: https://www.sports-reference.com/bot-traffic.html
* Hammering the server will result in a one day suspension from the website. Out of caution, in your functions limit calls using this endpoint to once every 7 seconds. 
* The API is designed to cache results in the pfr_data_cache.json file when player data is scraped. For best use, scrape all the data you need programmatically and safely using the guidance above and then feel free to use the API without timing restrictions. 


---


## NFLDataPy (Wrapper)

**Description**  
Thin wrapper around `nflreadpy` that provides convenient access to nfl-data-py and nflverse data. 
The api defaults to returning a polars dataframe, but this wrapper returns a pandas dataframe.

---

### Argument Conventions

| Parameter       | Type                           | Description |
|-----------------|--------------------------------|-------------|
| **years**       | `YearsLike`                    | Union/[int, str/]. Checks that the year is valid 1999-2025|
| **ranking_type**  | `Literal['draft','week','all']`| Defines the scope for fantasy player ranking|
| **stat_type**  | `Literal['weekly','pbp_pass','pbp_rush']`| Defines the scope for fantasy opportunity stats|

---

## API Namespaces & Methods

### `NFLDataPy`

Wrapper around `nflreaderpy`, returning `pandas.DataFrame` in many cases:

### 🏈 `NFLDataPy` API Reference

| Category                           | Method                                                                                                                                                                       | Returns        | Description                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------- |
| **Play-by-play / Columns**         | `load_play_by_play_data(years: YearsLike \| None = None)`                                                                                                                    | `pd.DataFrame` | Play-by-play (PBP) data for the given seasons. Years can be a single year, range, or iterable. |
| **Weekly Data**                    | `load_player_stats(years: YearsLike \| None = None, summary_level: Literal['week','reg','post','reg+post']="week")`                                                          | `pd.DataFrame` | Player statistics at weekly or seasonal summary levels.                                        |
|                                    | `load_team_stats(years: YearsLike \| None = None, summary_level: Literal['week','reg','post','reg+post']="week")`                                                            | `pd.DataFrame` | Team statistics at weekly or seasonal summary levels.                                          |
| **Rosters / Schedules / Metadata** | `load_schedules(years: YearsLike \| None = None)`                                                                                                                            | `pd.DataFrame` | League schedules by week and season.                                                           |
|                                    | `load_players(years: YearsLike \| None = None)`                                                                                                                              | `pd.DataFrame` | Player metadata and IDs for the given seasons.                                                 |
|                                    | `load_weekly_rosters(years: YearsLike \| None = None)`                                                                                                                       | `pd.DataFrame` | Weekly roster snapshots for each team.                                                         |
|                                    | `load_snap_counts(years: YearsLike \| None = None)`                                                                                                                          | `pd.DataFrame` | Weekly offensive/defensive snap counts.                                                        |
|                                    | `load_nextgen_stats(years: YearsLike \| None = None, stat_type: Literal['passing','receiving','rushing']="passing")`                                                         | `pd.DataFrame` | Next Gen Stats by stat type (passing, receiving, rushing).                                     |
|                                    | `load_ftn_charting(years: YearsLike \| None = None)`                                                                                                                         | `pd.DataFrame` | FTN charting data (route/target-level charting).                                               |
|                                    | `load_participation(years: YearsLike \| None = None)`                                                                                                                        | `pd.DataFrame` | Player participation (active/inactive and play involvement).                                   |
|                                    | `import_draft_picks(years: YearsLike \| None = None)`                                                                                                                        | `pd.DataFrame` |      |
|                                    | `import_draft_values(years: YearsLike \| None = None)`                                                                                                                       | `pd.DataFrame` |                      |
|                                    | `load_injuries(years: YearsLike \| None = None)`                                                                                                                             | `pd.DataFrame` | Player injury reports.                                                                         |
|                                    | `load_contracts()`                                                                                                                                                           | `pd.DataFrame` | Player contract information.                                                                   |
|                                    | `load_officials(years: YearsLike \| None = None)`                                                                                                                            | `pd.DataFrame` | Game officials data.                                                                           |
|                                    | `load_combine(years: YearsLike \| None = None)`                                                                                                                              | `pd.DataFrame` | NFL Combine results.                                                                           |
|                                    | `load_depth_charts(years: YearsLike \| None = None)`                                                                                                                         | `pd.DataFrame` | Team depth charts by week/season.                                                              |
|                                    | `load_trades()`                                                                                                                                                              | `pd.DataFrame` | Historical trades.                                                                             |
| **Fantasy Football Data**          | `load_fantasy_playerids()`                                                                                                                                                   | `pd.DataFrame` | Cross-platform fantasy player ID mapping.                                                      |
|                                    | `load_fantasy_rankings(ranking_type: Literal['draft','week','all']="draft")`                                                                                                 | `pd.DataFrame` | Fantasy rankings by requested type (draft, weekly, all).                                       |
|                                    | `load_fantasy_opportunity(years: YearsLike \| None = None, stat_type: Literal['weekly','pbp_pass','pbp_rush']="weekly", model_version: Literal['latest','v1.0.0']="latest")` | `pd.DataFrame` | Fantasy opportunity metrics (expected stats) for given seasons.                                |
| **Utility Functions**              | `clear_cache(pattern: str \| None = None)`                                                                                                                                   | `Any`          | Clears cached data optionally filtered by pattern.                                             |
|                                    | `get_current_season(roster: bool = False)`                                                                                                                                   | `pd.DataFrame` | Returns current season info (or full roster data if `roster=True`).                            |
|                                    | `get_current_week()`                                                                                                                                                         | `pd.DataFrame` | Returns the current week number for the NFL season.                                            |

---

