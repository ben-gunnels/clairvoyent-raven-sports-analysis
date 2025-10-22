import os
import sys
import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, r2_score

from dotenv import load_dotenv
load_dotenv()

# -----------------------------------------------------------------------------
# Project path setup
# -----------------------------------------------------------------------------
project_root = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
print(f"Project Root: {project_root}")
print("Sys Path Before:", sys.path)
if project_root not in sys.path:
    print("Inserting project root to sys.path")
    sys.path.insert(0, project_root)

# Now import internal modules
import utils

__all__ = [
    "run_pipeline", 
    "train_and_validate_model"
]

# -----------------------------------------------------------------------------
# Constants / Config
# -----------------------------------------------------------------------------
COLUMN_CATEGORIES = utils.STATISTICAL_COLUMNS_BY_CATEGORY
TARGET_INPUTS = utils.TARGETS_TO_INPUTS

ROLLING_PERIOD = 4

CATEGORIES_POSITIONS = {
    "passing": ["QB"],
    "rushing_and_receiving": ["RB", "WR", "TE", "QB"],
    # (kicking not available)
}

# -----------------------------------------------------------------------------
# Load Persistent DataFrames
# -----------------------------------------------------------------------------
print("Loading base data frames...")
player_stats_path = os.getenv("NFLVERSE_DATA_PATH")
teams_stats_path = os.getenv("NFLVERSE_TEAMS_DATA_PATH")
injuries_path = os.getenv("NFLVERSE_INJURIES_PATH")
depth_path = os.getenv("NFLVERSE_DEPTH_CHART_PATH")

all_players_df = pd.read_excel(rf"{player_stats_path}", engine="openpyxl")
all_teams_df = pd.read_csv(rf"{teams_stats_path}")
injuries_df = pd.read_excel(rf"{injuries_path}", engine="openpyxl")
depth_df = pd.read_excel(rf"{depth_path}", engine="openpyxl")
print("-" * 40)
print("\n")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def encode_and_filter_injuries_data(injuries_df: pd.DataFrame = injuries_df):
    df_inj = injuries_df.copy()
    if "gsis_id" in df_inj.columns:
        df_inj = df_inj.rename({"gsis_id": "player_id"}, axis=1)

    filtered = df_inj[["season", "week", "player_id", "report_status", "practice_status"]].copy()

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_cat = filtered[["report_status", "practice_status"]]
    encoded_data = encoder.fit_transform(X_cat)
    encoded_feature_names = encoder.get_feature_names_out(X_cat.columns)

    encoded_df = pd.DataFrame(encoded_data, columns=encoded_feature_names, index=filtered.index).fillna(0)

    out = pd.concat([filtered[["season", "week", "player_id"]], encoded_df], axis=1)
    return out, encoded_feature_names


def filter_depth_data(depth_df: pd.DataFrame = depth_df):
    # Always start from a concrete base df
    if "gsis_id" in depth_df.columns:
        base = depth_df.rename({"gsis_id": "player_id"}, axis=1).copy()
    else:
        base = depth_df.copy()

    filtered = base[["season", "week", "player_id", "depth_team"]].copy()
    filtered = filtered.dropna(subset=["season", "week"]).reset_index(drop=True)

    filtered["week"] = filtered["week"].astype(int)
    filtered["season"] = filtered["season"].astype(int)

    # Fill NaNs in depth with mean depth (around 1.5/2.0)
    if filtered["depth_team"].isna().any():
        filtered["depth_team"] = filtered["depth_team"].fillna(filtered["depth_team"].mean())

    return filtered


def merge_players_to_depth_and_injury(
    all_players_df: pd.DataFrame,
    filtered_injuries_df: pd.DataFrame,
    filtered_depth_df: pd.DataFrame,
) -> pd.DataFrame:
    df = all_players_df.merge(filtered_injuries_df, how="left", on=["player_id", "season", "week"])
    df = df.merge(filtered_depth_df, how="left", on=["player_id", "season", "week"])
    return df


def filter_by_positional_group(df: pd.DataFrame, category_key_a: str, category_key_b: str = "standard") -> pd.DataFrame:
    new_df = df.loc[:, list(COLUMN_CATEGORIES[category_key_a] | COLUMN_CATEGORIES[category_key_b])].copy()
    new_df = new_df[new_df["position"].isin(CATEGORIES_POSITIONS[category_key_a])]
    return new_df.reset_index(drop=True)


def calculate_rolling_data(
    df: pd.DataFrame,
    sort_values: list,
    input_ref: str,
    groupby: list,
    rolling_period: int = 3,
    min_periods: int = 1,
    shift: int = 1,
) -> pd.DataFrame:
    df = df.sort_values(sort_values)
    cols = TARGET_INPUTS[input_ref]
    df[[f"{c}_roll{rolling_period}_shift" for c in cols]] = (
        df.groupby(groupby)[cols]
          .transform(lambda x: x.rolling(rolling_period, min_periods=min_periods).mean().shift(shift))
    )
    return df


def calculate_cumulative_data(
    df: pd.DataFrame,
    sort_values: list,
    input_ref: str,
    groupby: list,
    prefix: str = "",
    shift: int = 1
) -> pd.DataFrame:
    df = df.sort_values(sort_values)
    cols = TARGET_INPUTS[input_ref]
    # mean
    df[[f"{prefix}{c}_cum_avg" for c in cols]] = (
        df.groupby(groupby)[cols]
          .transform(lambda x: x.expanding().mean().shift(shift))
    )
    # std (sample std by default); adjust min_periods/ddof if you prefer
    df[[f"{prefix}{c}_cum_std" for c in cols]] = (
        df.groupby(groupby)[cols]
          .transform(lambda x: x.expanding().std().shift(shift))
    )
    return df


def get_standard_input_cols(target: str, encoded_feature_names) -> list[str]:
    rolling_cols = [col + f"_roll{ROLLING_PERIOD}_shift" for col in TARGET_INPUTS[target]]
    avg_cum_cols = [col + "_cum_avg" for col in TARGET_INPUTS[target]]
    std_cum_cols = [col + "_cum_std" for col in TARGET_INPUTS[target]]
    opp_avg_cum_cols = ["vs_opponent_" + col + "_cum_avg" for col in TARGET_INPUTS[target]]
    opp_std_cum_cols = ["vs_opponent_" + col + "_cum_std" for col in TARGET_INPUTS[target]]

    return (
        rolling_cols
        + avg_cum_cols
        + std_cum_cols
        + opp_avg_cum_cols
        + opp_std_cum_cols
        + ["depth_team"]
        + list(encoded_feature_names)
    )


def scale_inplace(df: pd.DataFrame, cols: list[str], name: str, scalers: dict | None = None):
    if scalers is None:
        scalers = {}
    scaler = StandardScaler()
    df.loc[:, cols] = scaler.fit_transform(df[cols])
    scalers[name] = scaler
    return df, scalers


def handle_merge(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    how: str = "left",
    left_on: list = ["opponent_team", "season", "week"],
    right_on: list = ["team", "season", "week"],
) -> pd.DataFrame:
    return left_df.merge(right_df, how=how, left_on=left_on, right_on=right_on)


def generate_target_dataframe_struct(
    encoded_feature_names,
    rushing_and_receiving_df: pd.DataFrame,
    passing_df: pd.DataFrame,
    all_teams_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    standard_inputs = [
        "season", "week", "player_id", "position",
        "player_name", "team", "opponent_team", "depth_team",
    ]
    enc = list(encoded_feature_names)

    target_data_struct: dict[str, pd.DataFrame] = {}

    rushing_cats = ["rsh_yd", "rsh_td", "rc_yd", "rc_td", "rc"]
    passing_cats = ["p_yd", "p_td", "intcpt"]
    both_cats = ["rsh_fmbls", "rc_fmbls"]

    for target in TARGET_INPUTS:
        if target in rushing_cats:
            target_data_struct[target] = rushing_and_receiving_df[TARGET_INPUTS[target] + standard_inputs + enc].copy()
        elif target in passing_cats:
            target_data_struct[target] = passing_df[TARGET_INPUTS[target] + standard_inputs + enc].copy()
        elif target in both_cats:
            both = pd.concat([rushing_and_receiving_df, passing_df], ignore_index=True)
            target_data_struct[target] = both[TARGET_INPUTS[target] + standard_inputs + enc].copy()

    # Defensive (opponent) stats handled separately
    target_data_struct["def"] = all_teams_df[TARGET_INPUTS["def"] + ["season", "week", "team"]].copy()

    return target_data_struct


def get_input_cols_by_target(target_data_struct: dict[str, pd.DataFrame], encoded_feature_names) -> dict[str, list[str]]:
    input_cols_by_target: dict[str, list[str]] = {}
    for target in target_data_struct:
        if target == "def":
            input_cols_by_target[target] = [col + f"_roll{ROLLING_PERIOD}_shift" for col in TARGET_INPUTS[target]]
        else:
            input_cols_by_target[target] = get_standard_input_cols(target, encoded_feature_names)
    return input_cols_by_target


def calculate_rolling_and_cumulative_data(
    target_data_struct: dict[str, pd.DataFrame],
    rolling_period: int = ROLLING_PERIOD,
) -> dict[str, pd.DataFrame]:
    for target, df in target_data_struct.items():
        if target == "def":
            tmp = calculate_rolling_data(df, ["season", "week", "team"], target, ["season", "team"], rolling_period=rolling_period)
            tmp = calculate_cumulative_data(tmp, ["season", "week", "team"], target, ["season", "team"])
            target_data_struct[target] = tmp
        else:
            tmp = calculate_rolling_data(df, ["season", "week", "player_id"], target, ["season", "player_id"], rolling_period=rolling_period)
            tmp = calculate_cumulative_data(tmp, ["season", "week", "player_id"], target, ["season", "player_id"])
            tmp = calculate_cumulative_data(tmp, ["season", "week", "player_id"], target, ["opponent_team", "player_id"], prefix="vs_opponent_")
            target_data_struct[target] = tmp
    return target_data_struct


def scale_target_data(target_data_struct: dict[str, pd.DataFrame], target_input_cols: dict[str, list[str]]) -> dict[str, pd.DataFrame]:
    for target, df in target_data_struct.items():
        cols = target_input_cols.get(target, [])
        if not cols:
            continue
        target_data_struct[target], _ = scale_inplace(df, cols, target)  # discard scalers for now
    return target_data_struct


def merge_target_data_to_defense(target_data_struct: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    # merge 'def' onto each offensive df
    def_df = target_data_struct["def"]
    for target, df in target_data_struct.items():
        if target == "def":
            continue
        target_data_struct[target] = handle_merge(df, def_df)
    return target_data_struct


target_translation = {
           "rsh_yd": "rushing_yards", 
           "rsh_td": "rushing_tds", 
           "rc_yd": "receiving_yards", 
           "rc_td": "receiving_tds", 
           "rc": "receptions", 
           "p_yd": "passing_yards", 
           "p_td": "passing_tds", 
           "intcpt": "passing_interceptions", 
           "rsh_fmbls": "rushing_fumbles_lost", 
           "rc_fmbls": "receiving_fumbles_lost"
}

def train_and_validate_model(
    target_data_struct: dict[str, pd.DataFrame],
    target_input_cols: dict[str, list[str]],
    season_holdout: int = 2024,
):
    model_results: dict[str, dict] = {}
    models: dict[str, LinearRegression] = {}
    predictions: dict[str, np.array] = {}
    trues: dict[str, np.array] = {}

    for target, df in target_data_struct.items():
        if target == "def":
            continue  # no target variable for defense

        input_cols = target_input_cols[target]
        def_input_cols = target_input_cols["def"]

        # hold out a season for validation split (and avoid leakage)
        mask = df["season"] != season_holdout

        # Build a single feature matrix with aligned rows, then dropna once
        feature_cols = input_cols + def_input_cols
        XY = df.loc[mask, feature_cols + [target_translation[target]]].fillna(0) #.dropna().reset_index(drop=True)

        if XY.empty:
            model_results[target] = {"validation_rmse": "nan", "r2": "nan"}
            continue

        X = XY[feature_cols].values
        y = XY[target_translation[target]].values

        X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

        reg = LinearRegression().fit(X_train, y_train)
        preds = reg.predict(X_valid)

        rmse = root_mean_squared_error(y_valid, preds)
        r2 = r2_score(y_valid, preds)

        model_results[target] = {"validation_rmse": f"{rmse:.4f}", "r2": f"{r2:.3f}"}
        models[target] = reg
        predictions[target] = preds
        trues[target] = y_valid

    return models, model_results, trues, predictions


def _restore_weights(
        model_path: str
) -> LinearRegression:
    # --- later: restore ---
    data = np.load(model_path, allow_pickle=True)
    restored = LinearRegression()
    restored.coef_ = data["coef"]
    restored.intercept_ = data["intercept"]
    restored.n_features_in_ = int(data["n_features_in_"])
    # Optional but useful if you trained with a DataFrame and rely on column order:
    fni = data["feature_names_in_"]
    if fni is not None and fni.size > 0:
        restored.feature_names_in_ = fni
    return restored

def _get_model_paths(
        target_names: list,
        linear_regression_weights_path: str
):
    model_paths = {}

    for target_name in target_names:
        model_paths[target_name] = os.path.join(linear_regression_weights_path, f"{target_name}_linreg_weights.npz")
    return model_paths


def test_model(
    test_data_struct: dict[str, pd.DataFrame],
    test_input_cols: dict[str, list[str]],
    linear_regression_weights_path: str
):
    model_results: dict[str, dict] = {}
    models: dict[str, LinearRegression] = {}
    predictions: dict[str, dict] = {}
    trues: dict[str, dict] = {}

    model_paths = _get_model_paths(list(test_data_struct.keys()), linear_regression_weights_path)

    for target, df in test_data_struct.items():
        reg = _restore_weights(model_paths[target])
        if target == "def":
            continue  # no target variable for defense

        input_cols = test_input_cols[target]
        def_input_cols = test_input_cols["def"]

        # Build a single feature matrix with aligned rows, then dropna once
        feature_cols = input_cols + def_input_cols
        XY = df.loc[:, feature_cols + [target_translation[target]]].fillna(0) #.dropna().reset_index(drop=True)

        if XY.empty:
            model_results[target] = {"validation_rmse": "nan", "r2": "nan"}
            continue

        X = XY[feature_cols].values
        y = XY[target].values

        preds = reg.predict(X)

        rmse = root_mean_squared_error(y, preds)
        r2 = r2_score(y, preds)

        model_results[target] = {"validation_rmse": f"{rmse:.4f}", "r2": f"{r2:.3f}"}
        models[target] = reg
        trues[target] = y
        predictions[target] = preds
    
    return model_results, trues, predictions


def save_and_store_model_weights(models: dict, path: str = "models"):
    """Save the coefficients and intercept for the linear regression models to models/ folder."""
    os.makedirs(path, exist_ok=True)

    for name, lr in models.items():
        np.savez(
            os.path.join(path, f"{name}_linreg_weights.npz"),
            coef=lr.coef_,
            intercept=lr.intercept_,
            n_features_in_=lr.n_features_in_,
            feature_names_in_=getattr(lr, "feature_names_in_", None),
        )


def run_pipeline(
        players_df: pd.DataFrame = all_players_df,
        teams_df:  pd.DataFrame = all_teams_df,
        injuries_df: pd.DataFrame = injuries_df, 
        depth_df: pd.DataFrame = depth_df
) -> dict[str, pd.DataFrame]:
    """Runs the data preprocessing pipeline for inputs of all_players_df, injuries_df, and depth_df.
    If no arguments are given, it will default to the dataframes of the same name in this file. 
    Returns a data structure containing the processed dataframes for each target.
    """
    # 1) Prepare injuries/depth and merge with players first
    print("Filtering and merging injuries and depth charts...")
    filtered_injuries_df, encoded_feature_names = encode_and_filter_injuries_data(injuries_df)
    filtered_depth_df = filter_depth_data(depth_df)
    merged_players = merge_players_to_depth_and_injury(players_df, filtered_injuries_df, filtered_depth_df)
    print("-" * 40)
    print("\n")

    # 2) Build positional dataframes FROM the merged players df
    print("Generating positional dataframes...")
    passing_df = filter_by_positional_group(merged_players, "passing")
    rushing_and_receiving_df = filter_by_positional_group(merged_players, "rushing_and_receiving")
    print(f"Generated positional dataframes with {passing_df.size} rows and {rushing_and_receiving_df.size} rows")
    print("-" * 40)
    print("\n")

    # Optional: quick null check utility (add .alias only if used)
    passing_df.alias = "passing_df"
    rushing_and_receiving_df.alias = "rushing_and_receiving_df"

    # 3) Create per-target dataframes
    print("Generating target data structure and input columns by statistical category...")
    target_data_struct = generate_target_dataframe_struct(
        encoded_feature_names, rushing_and_receiving_df, passing_df, teams_df
    )
    target_input_cols = get_input_cols_by_target(target_data_struct, encoded_feature_names)
    print("-" * 40)
    print("\n")

    # 4) Feature engineering: rolling / cumulative (season & vs-opponent), then scale, then merge defense
    print("Engineering features for cumulative and rolling data...")
    target_data_struct = calculate_rolling_and_cumulative_data(target_data_struct)
    target_data_struct = scale_target_data(target_data_struct, target_input_cols)
    target_data_struct = merge_target_data_to_defense(target_data_struct)
    print("-" * 40)
    print("\n")
    return target_data_struct, target_input_cols


def main():
    target_data_struct, target_input_cols = run_pipeline()

    # 5) Train & validate models
    print("Training and validating model...")
    models, model_results = train_and_validate_model(target_data_struct, target_input_cols)
    print("-" * 40) 
    print("\n")

    # 6) Report
    print("\nMODEL RESULTS:")
    for target, metrics in model_results.items():
        print(f"{target}: {metrics}")
    print("-" * 40)

    print("Saving model weights...")
    save_and_store_model_weights(models)
    print("Model weights saved!")

if __name__ == "__main__":
    main()
