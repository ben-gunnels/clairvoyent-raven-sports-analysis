from __future__ import annotations

from typing import Iterable, Optional, Sequence, Union, Any, Literal
import pandas as pd
import nflreadpy as nfl


YearLike = Union[int, str]
YearsLike = Union[YearLike, Iterable[YearLike], range]

def _cap_year(year):
    """Ensure the year is between 1999-2025, the range of the available data.
    """
    return min(max(int(year), 1999), 2025)

def _normalize_years(years: YearsLike | None) -> Optional[list[YearLike]]:
    """
    Accepts a single year (int/str), an iterable of years, a range, or None.
    Returns a list or None.
    """
    if years is None:
        return None
    if isinstance(years, (int, str)):
        return [min(max(int(years), 1999), 2025)]
    if isinstance(years, range):
        _start_range = max(min(years), 1999)
        _end_range = min(max(years), 2025)
        return range(_start_range, _end_range)

    # Assume iterable
    return [_cap_year(int(year)) for year in years]


class NFLDataPy:
    """
    Thin convenience wrapper over nfl_data_py functions.

    Notes:
    - Methods primarily pass through to nfl_data_py.* while normalizing input.
    - Years can be int/str, range, or any iterable of int/str.
    - You can safely rename/alias methods later to match your workflow.
    """

    # -------------------------
    # Play-by-play / columns
    # -------------------------
    def load_play_by_play_data(
        self,
        years: YearsLike | None = None,
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_pbp(yrs).to_pandas()

    # -------------------------
    # Weekly data
    # -------------------------
    def load_player_stats(
        self,
        years: YearsLike | None = None,
        summary_level: Literal['week', 'reg', 'post', 'reg+post']="week"
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_player_stats(yrs, summary_level=summary_level).to_pandas()
    
    
    def load_team_stats(
        self,
        years: YearsLike | None = None,
        summary_level: Literal['week', 'reg', 'post', 'reg+post']="week"
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_team_stats(yrs, summary_level=summary_level).to_pandas()


    # -------------------------
    # Rosters / schedules / ids / metadata
    # -------------------------
    def load_schedules(
        self,
        years: YearsLike | None = None,
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        # nfl_data_py uses s_type argument name
        return nfl.load_schedules(yrs).to_pandas()
    

    def load_players(
        self,
        years: YearsLike | None = None,
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_players(yrs).to_pandas()
    

    def load_weekly_rosters(
        self,
        years: YearsLike | None = None,
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_rosters_weekly(yrs).to_pandas()


    def load_snap_counts(
        self, 
        years: YearsLike | None = None, 
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_snap_counts(yrs).to_pandas()


    def load_nextgen_stats(
        self, 
        years: YearsLike | None = None,
        stat_type: Literal['passing', 'receiving', 'rushing'] = "passing"
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_nextgen_stats(yrs, stat_type=stat_type).to_pandas()


    def load_ftn_charting(
        self, 
        years: YearsLike | None = None 
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_ftn_charting(yrs).to_pandas()
    

    def load_participation(
        self, 
        years: YearsLike | None = None 
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_participation(yrs).to_pandas()
    

    def import_draft_picks(self, years: YearsLike | None = None) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_draft_picks(yrs).to_pandas()

    def import_draft_values(self, years: YearsLike | None = None) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_draft_values(yrs).to_pandas()


    def load_injuries(
        self,
        years: YearsLike | None = None
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_injuries(yrs).to_pandas()


    def load_contracts(
        self,
    ) -> pd.DataFrame:
        return nfl.load_contracts().to_pandas()


    def load_officials(
        self,
        years: YearsLike | None = None
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_officials(yrs).to_pandas()


    def load_combine(
        self, 
        years: YearsLike | None = None 
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_combine(yrs).to_pandas()

    def load_depth_charts(
        self, 
        years: YearsLike | None = None
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_depth_charts(yrs).to_pandas()


    def load_trades(self) -> pd.DataFrame:
        return nfl.load_trades().to_pandas()

    # -------------------------
    # Fantasy football data
    # -------------------------
    def load_fantasy_playerids(self) -> pd.DataFrame:
        return nfl.load_ff_playerids().to_pandas()
    

    def load_fantasy_rankings(
        self,
        ranking_type: Literal['draft', 'week', 'all'] = "draft"
    ) -> pd.DataFrame:
        return nfl.load_ff_rankings(ranking_type).to_pandas()
    

    def load_fantasy_opportunity(
        self,
        years: YearsLike | None = None,
        stat_type: Literal['weekly', 'pbp_pass', 'pbp_rush'] = "weekly",
        model_version: Literal['latest', 'v1.0.0'] = "latest"
    ) -> pd.DataFrame:
        yrs = _normalize_years(years)
        return nfl.load_ff_opportunity(yrs, stat_type=stat_type, model_version=model_version).to_pandas()


    # -------------------------
    # Utility functions
    # -------------------------
    def clear_cache(
        self,
        pattern: str | None = None
    ):
        return nfl.clear_cache(pattern)

    
    def get_current_week(self) -> int:
        return nfl.get_current_week()

    def get_current_season(self, roster: bool = False) -> int | pd.DataFrame:
        result = nfl.get_current_season(roster)
        return result if isinstance(result, int) else result.to_pandas()
