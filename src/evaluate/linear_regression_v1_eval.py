import os
import sys
import numpy as np
import pandas as pd

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
from pipelines import linear_regression_pipeline_v1 as pipeline

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
all_teams_df = pd.read_excel(rf"{teams_stats_path}", engine="openpyxl")
injuries_df = pd.read_excel(rf"{injuries_path}", engine="openpyxl")
depth_df = pd.read_excel(rf"{depth_path}", engine="openpyxl")
print("-" * 40)
print("\n")

# ----------------------------------------------------------------------------
# Filter dfs to 2025 season
# ----------------------------------------------------------------------------
print("Filtering data to current season...")
all_players_df = all_players_df[all_players_df["season"] == 2025]
all_teams_df = all_teams_df[all_teams_df["season"] == 2025]
injuries_df = injuries_df[injuries_df["season"] == 2025]
depth_df = depth_df[depth_df["season"] == 2025]
print("-" * 40)

# ----------------------------------------------------------------------------
# Apply pipeline to filtered data.
# ----------------------------------------------------------------------------
print("Running data pipeline...")
test_data_struct, test_input_cols = pipeline.run_pipeline(all_players_df, all_teams_df, injuries_df, depth_df)
print("-" * 40)
# ----------------------------------------------------------------------------
# Apply model
# ----------------------------------------------------------------------------
model_results, trues, predictions = pipeline.test_model(test_data_struct, test_input_cols, rf"{os.getenv('SAVED_WEIGHTS_PATH')}")
print(model_results)
