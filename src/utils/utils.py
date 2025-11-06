import pandas as pd
import json
import logging
from pathlib import Path
from typing import Any, Optional
from .data_descriptions.StatProjections import POSITION_PLAYER_STAT_PROJECTION_DATA_DICT

def safe_json_load(path: str | Path, default: Optional[Any] = None) -> Any:
    """
    Safely load JSON from a file.
    
    Returns:
        - Parsed JSON (dict, list, etc.)
        - `None` or the `default` you specify if the file is missing,
          empty, invalid JSON, or contains just whitespace.
    """
    try:
        path = Path(path)
        if not path.exists():
            logging.warning("File not found: %s", path)
            return default
        
        if path.stat().st_size == 0:
            logging.warning("File empty: %s", path)
            return default
        
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning("Invalid JSON in file: %s", path)
        return default
    except Exception as e:
        logging.error("Unexpected error reading %s: %s", path, e)
        return default

def validate_season(season: str, alternate: bool=False) -> bool:
    """
    Validate the season format. It should be in the format 'YYYYREG' or 'YYYYPRE' or 'YYYYPOST' for regular
    or 'YYYY' for alternate.
    """
    import re
    if alternate:
        pattern = r"^\d{4}$"
        return bool(re.match(pattern, season))
    pattern = r"^\d{4}(REG|PRE|POST)$"
    return bool(re.match(pattern, season))

def validate_date(s: str) -> bool:
    """
    Validate that `s` is either:
      - 'YYYY-MMM-DD' (e.g. '2017-SEP-25'), or
      - 'YYYY-MM-DD'  (e.g. '2017-09-25'),
    and that it represents a real calendar date.
    """
    import re
    from datetime import datetime
    # Acceptable regex patterns
    patterns = [
        r'^\d{4}-[A-Z]{3}-\d{2}$',  # e.g. 2017-SEP-25
        r'^\d{4}-\d{2}-\d{2}$'      # e.g. 2017-09-25
    ]
    s_up = s.upper()
    if not any(re.fullmatch(p, s_up) for p in patterns):
        return False

    # Try to parse with either style
    for fmt in ("%Y-%b-%d", "%Y-%m-%d"):
        try:
            datetime.strptime(s_up, fmt)
            return True
        except ValueError:
            continue
    return False

def validate_season_week(season: str, week: int) -> bool:
    """
    Validate that the season and week are in acceptable ranges.
    """
    if not validate_season(season):
        return False
    match (season[-3:]):
        case "PRE":
            return 0 <= week <= 4
        case "REG":
            return 1 <= week <= 17        
        case "POST":
            return 1 <= week <= 4
        case _:
            return False    

def describe_endpoint(name, df):
    """Formats the DataFrame info string for writing."""
    buf = []
    buf.append(f"Endpoint: {name}")
    buf.append("-" * 50)
    # Capture the output of df.info()
    from io import StringIO
    s = StringIO()
    if type(df) is pd.DataFrame:
        df.info(buf=s, verbose=True)
    else:
        buf.append(f"Type: {type(df)}")
        buf.append("Not a DataFrame.")
    s.seek(0)
    buf.append(s.read().rstrip())
    buf.append("-"*50)
    buf.append("\n")  # blank line between endpoints
    return "\n".join(buf)

def compile_player_points_and_projections(df: pd.DataFrame) -> pd.DataFrame:
    """Takes a dataframe with projected stats and adds a column for projected fantasy points.
    """
    projection_cols = [f"Projected {col}" for col in POSITION_PLAYER_STAT_PROJECTION_DATA_DICT.keys()]
    for col in projection_cols:
        if col not in df.columns:
            raise KeyError(f"Key: {col} not in the dataframe's columns.")
    
    weights_proj = pd.Series(
        [val["weight"] for val in POSITION_PLAYER_STAT_PROJECTION_DATA_DICT.values()],
        index=[f"Projected {key}" for key in POSITION_PLAYER_STAT_PROJECTION_DATA_DICT.keys()]
    )

    weights_true = pd.Series(
        [val["weight"] for val in POSITION_PLAYER_STAT_PROJECTION_DATA_DICT.values()],
        index=[f"True {key}" for key in POSITION_PLAYER_STAT_PROJECTION_DATA_DICT.keys()]
    )

    df["Projected Points"] = df[weights_proj.index].mul(weights_proj, axis=1).sum(axis=1)
    df["True Points"] = df[weights_true.index].mul(weights_true, axis=1).sum(axis=1)
    return df

