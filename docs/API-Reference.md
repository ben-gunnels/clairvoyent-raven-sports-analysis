# API Reference Manual

This section describes how to interact with the API for various sources of NFL data.

---

## NFL Data Sources

### Sports Data IO (Discovery Lab)

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

| Method                       | Description                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------ |
| `get_bye_weeks(season)`      | Get each team’s bye weeks for the specified season.                            |
| `get_player_details(typeof)` | Retrieve details for players. `typeof` can be `"available"` or `"free-agent"`. |
| `get_rookie_details(season)` | Get details for rookie players by season.                                      |
| `get_standings(season)`      | Get league standings for a given season.                                       |
| `get_teams()`                | Get details of all active teams.                                               |
| `get_timeframes(typeof)`     | Get detailed information about past, present, and future timeframes.           |

---

### `SportsDataIO.fantasy`

| Method                                           | Description                                                      |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| `get_dfs_slates_by_date(date)`                   | Get daily fantasy sports (DFS) slates for a specific date.       |
| `get_dfs_slates_by_week(season, week)`           | Get DFS slates for a specific season and week.                   |
| `get_defense_game_stats(season, week)`           | Get a team’s defensive game stats for the given season and week. |
| `get_defense_season_stats(season)`               | Get a team’s defensive season stats.                             |
| `get_player_game_stats(season, week)`            | Get individual player game stats for the given season and week.  |
| `get_player_season_stats(season)`                | Get individual player season stats.                              |
| `get_projected_defense_game_stats(season, week)` | Get projected defensive game stats for a team.                   |
| `get_projected_defense_season_stats(season)`     | Get projected defensive season stats for a team.                 |
| `get_projected_player_game_stats(season, week)`  | Get projected player game stats.                                 |
| `get_projected_player_season_stats(season)`      | Get projected player season stats.                               |

---

### `SportsDataIO.Odds`

| Method                                    | Description                                              |
| ----------------------------------------- | -------------------------------------------------------- |
| `get_pregame_odds(season, week)`          | Get pregame betting odds for games in a season and week. |
| `get_pregame_odds_line_movement(scoreid)` | Get betting line movement prior to a specific game.      |
| `get_scores(season, week)`                | Get game scores for a season and week.                   |
| `get_stadiums()`                          | Get information on current NFL stadiums.                 |
| `get_team_game_stats(season, week)`       | Get team stats for a specific season and week.           |
| `get_team_season_stats(season)`           | Get team stats for an entire season.                     |

---

### Notes

* All method names are shown exactly as used in the API.
* Ensure correct argument types and valid values (for example, `season="2024REG"`).
