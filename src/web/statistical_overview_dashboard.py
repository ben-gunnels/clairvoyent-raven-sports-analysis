import os
import sys
import matplotlib
import numpy as np
import pandas as pd
from functools import reduce
from shiny import App, reactive, render, ui



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
from data_api import NFLDataPy

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

SAVED_WEIGHTS_PATH = os.getenv("SAVED_WEIGHTS_PATH")
COMBINED_DF_PATH = os.getenv("COMBINED_DATA_FRAME_PATH")

# -----------------------------------------------------------------------------
# Define functions
# -----------------------------------------------------------------------------

def assemble_combined_df(
    target_data_struct: dict[str, pd.DataFrame],
    trues: dict[str, pd.Series | pd.DataFrame],
    predictions: dict[str, pd.Series | pd.DataFrame],
) -> pd.DataFrame:
    """
    Build one wide table with per-target True/Projected columns.
    - Merges on keys (prefers ['player_id','season','week'] if present, else just 'player_id')
    - Keeps player_name and position (joined from a meta table)
    - Fills NA in metric columns with 0 (does not touch text/meta)
    """
    # Collect metric frames (only keys + 2 metric columns per target)
    metric_frames: list[pd.DataFrame] = []
    # Collect meta (to attach player_name/position once at the end)
    meta_frames: list[pd.DataFrame] = []

    for target, df in target_data_struct.items():
        if target == "def" or df is None or not isinstance(df, pd.DataFrame):
            continue

        # Determine merge keys available in this df
        preferred_keys = ["player_id", "season", "week"]
        keys = [k for k in preferred_keys if k in df.columns]
        if not keys:  # Fallback to player_id only if absolutely necessary
            if "player_id" in df.columns:
                keys = ["player_id"]
            else:
                # Can't merge without an id; skip this target
                print(f"[assemble] Skipping '{target}' (no merge key present).")
                continue

        # Build a small frame with keys and per-target metrics
        tmp = df[keys].copy()

        # Align trues/preds to df rows (works if Series indexed like df or just reindexes)
        true_series = trues.get(target, pd.Series(index=df.index, dtype="float64"))
        pred_series = predictions.get(target, pd.Series(index=df.index, dtype="float64"))

        # If they are DataFrames with a single column, squeeze to Series
        if isinstance(true_series, pd.DataFrame) and true_series.shape[1] == 1:
            true_series = true_series.iloc[:, 0]
        if isinstance(pred_series, pd.DataFrame) and pred_series.shape[1] == 1:
            pred_series = pred_series.iloc[:, 0]

        tmp[f"True {utils.TARGET_TRANSLATION[target]}"] = pd.Series(true_series).reindex(df.index).to_numpy()
        tmp[f"Projected {utils.TARGET_TRANSLATION[target]}"] = pd.Series(pred_series).reindex(df.index).to_numpy()
        tmp[f"Average {utils.TARGET_TRANSLATION[target]}"] = df[f"{utils.TARGET_TRANSLATION[target]}_cum_avg_copy"]
        tmp[f"STD {utils.TARGET_TRANSLATION[target]}"] = df[f"{utils.TARGET_TRANSLATION[target]}_cum_std_copy"]

        metric_frames.append(tmp)

        # Stash meta once per df (we’ll dedupe later)
        keep_meta = [c for c in ["player_id", "season", "week", "player_display_name", "position"] if c in df.columns]
        if keep_meta:
            meta_frames.append(df[keep_meta].copy())

    if not metric_frames:
        return pd.DataFrame(columns=["player_id", "season", "week", "player_display_name", "position"])

    # Merge all metric frames with an outer join on the available keys
    def _merge(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
        # Intersect on keys both frames share (at least player_id)
        shared_keys = [k for k in ["player_id", "season", "week"] if k in left.columns and k in right.columns]
        if not shared_keys and "player_id" in left.columns and "player_id" in right.columns:
            shared_keys = ["player_id"]
        return left.merge(right, on=shared_keys, how="outer")

    combined_metrics = reduce(_merge, metric_frames)

    # Build a meta table and join it on keys (prefer season/week if present)
    if meta_frames:
        meta = pd.concat(meta_frames, ignore_index=True).drop_duplicates()
        # Keep only one row per key combo, preferring non-null player_name/position
        key_order = [k for k in ["player_id", "season", "week"] if k in meta.columns]
        if not key_order:
            key_order = ["player_id"]
        meta = (meta
                .sort_values(key_order)  # stable
                .groupby(key_order, as_index=False)
                .agg({
                    "player_display_name": "first" if "player_display_name" in meta.columns else "first",
                    "position": "first" if "position" in meta.columns else "first"
                })
               ) if any(c in meta.columns for c in ["player_display_name", "position"]) else meta

        # Determine merge keys between combined_metrics and meta
        shared_keys = [k for k in ["player_id", "season", "week"] if k in combined_metrics.columns and k in meta.columns]
        if not shared_keys and "player_id" in combined_metrics.columns and "player_id" in meta.columns:
            shared_keys = ["player_id"]

        combined = combined_metrics.merge(meta, on=shared_keys, how="left")
    else:
        combined = combined_metrics

    # Fill NA only in metric columns (leave text/meta alone)
    def _metric_conditions(column: str):
        return column.startswith("True ") or column.startswith("Projected ") or column.startswith("Average ") or column.startswith("STD ")
    
    metric_cols = [c for c in combined.columns if _metric_conditions(c)]
    combined[metric_cols] = combined[metric_cols].fillna(0)

    # Optional: order columns
    front = [c for c in ["player_id", "season", "week", "player_display_name", "position"] if c in combined.columns]
    rest = [c for c in combined.columns if c not in front]
    combined = combined[front + rest]

    combined = combined.drop_duplicates(subset=["season", "week", "player_display_name"])

    return combined.reset_index(drop=True)

# -----------------------------------------------------------------------------
# Load Persistent DataFrames
# -----------------------------------------------------------------------------
df_cached = False

if COMBINED_DF_PATH:
    try:
        combined_df = pd.read_csv(COMBINED_DF_PATH)
        df_cached = True

    except:
        print("Dataframe is not cached or is not cached correctly, or the path is not set.")

if not df_cached:
    print("Loading base data frames...")
    nfl_data = NFLDataPy()
    years = [2024]
    all_players_df = nfl_data.load_player_stats(years)
    all_teams_df = nfl_data.load_team_stats(years)
    injuries_df = nfl_data.load_injuries(years)
    depth_df = nfl_data.load_depth_charts(years)
    print("-" * 40)
    print("\n")

    print("Running data pipeline...")
    target_data_struct, target_input_cols = pipeline.run_pipeline(all_players_df, all_teams_df, injuries_df, depth_df)
    print("-" * 40)

    results, trues, predictions = pipeline.test_model(target_data_struct, target_input_cols, SAVED_WEIGHTS_PATH)

    combined_df = assemble_combined_df(target_data_struct, trues, predictions)
    combined_df.to_csv("combined_data_frame.csv")

# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------
app_ui = ui.page_fluid(
    ui.h2("2024 NFL Weekly Player Stats with Projections"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_selectize(
                "week_filter",
                "Select week(s)",
                choices=sorted(combined_df["week"].unique().tolist()),
                multiple=True,
            ),
            ui.input_selectize(
                "position_filter",
                "Select position(s)",
                choices=sorted(combined_df["position"].unique().tolist()),
                multiple=True,
            ),
            ui.input_numeric("min_rsh_yards", "Minimum rushing yards", 0),
            ui.input_numeric("min_rc_yards", "Minimum receiving yards", 0),
            ui.input_numeric("min_p_yards", "Minimum passing yards", 0),
            ui.input_select(
                "sort_by",
                "Sort by column",
                choices=["True rushing_yards", "Projected rushing_yards", "True receiving_yards", "Projected receiving_yards", "True passing_yards", "Projected passing_yards"],
                selected="True rushing_yards"
            ),
            ui.input_radio_buttons(
                "sort_order",
                "Sort order",
                choices=["Descending", "Ascending"],
                selected="Descending"
            ),
        ),
        ui.card(
            ui.card_header("Colorized (by z-score)"),
            ui.output_ui("styled_table"),
        ),
        # ui.card(
        #     ui.card_header("Raw grid"),
        #     ui.output_data_frame("filtered_table"),
        # ),
    )
)

# -------------------------------------------------------------------
# Server
# -------------------------------------------------------------------
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        d = combined_df.copy().round(2)

        if input.week_filter():
            d = d[d["week"].isin([int(wk) for wk in input.week_filter()])]
        if input.position_filter():
            d = d[d["position"].isin(input.position_filter())]

        d = d[d["True rushing_yards"]   >= input.min_rsh_yards()]
        d = d[d["True receiving_yards"] >= input.min_rc_yards()]
        d = d[d["True passing_yards"]   >= input.min_p_yards()]

        sort_col = input.sort_by()
        if sort_col not in d.columns:
            for c in ["True rushing_yards", "Projected rushing_yards"]:
                if c in d.columns: sort_col = c; break
        d = d.sort_values(by=sort_col, ascending=(input.sort_order()=="Ascending"))
        return d.reset_index(drop=True)

    # helper: returns a list of "background-color: #hex" per cell in the column
    def _bg_from_z(zvals: pd.Series) -> list[str]:
        vmax = np.nanmax(np.abs(zvals.values)) if len(zvals) else 1.0
        if not np.isfinite(vmax) or vmax == 0:
            vmax = 1.0
        norm = (zvals.values + vmax) / (2 * vmax)          # [-vmax, vmax] -> [0, 1]
        cmap = matplotlib.cm.get_cmap("RdYlGn")
        colors = [matplotlib.colors.to_hex(cmap(float(x))) if np.isfinite(x) else "#ffffff" for x in norm]
        return [f"background-color: {c}" for c in colors]

    @output
    @render.ui
    def styled_table():
        if not input.week_filter():
            return 
        
        if not input.position_filter():
            return
        
        d = filtered_data()

        z_suffix = "_z-score"
        z_cols   = [c for c in d.columns if c.endswith(z_suffix)]
        base_cols = [c[:-len(z_suffix)] for c in z_cols if c[:-len(z_suffix)] in d.columns]

        # we will show the table WITHOUT z-score columns
        d_no_z = d.drop(columns=z_cols, errors="ignore")

        sty = d_no_z.style.hide(axis="index")

        # apply PER-COLUMN styles from its z-score series (aligned by index)
        def color_by_z(series: pd.Series, z: pd.Series) -> list[str]:
            return _bg_from_z(z.reindex(series.index))

        for base in base_cols:
            zcol = f"{base}{z_suffix}"
            if zcol not in d.columns:
                continue
            z = d.loc[d_no_z.index, zcol]             # align to the displayed rows
            # IMPORTANT: axis=0 (column-wise) and a proper subset to avoid row broadcast
            sty = sty.apply(color_by_z, axis=0, subset=pd.IndexSlice[:, [base]], z=z)

        sty = sty.format(precision=2)
        return ui.HTML(sty.to_html())

    # keep your raw grid too if you want
    @output
    @render.data_frame
    def filtered_table():
        return render.DataGrid(filtered_data(), filters=True)

# -------------------------------------------------------------------
# App entrypoint
# -------------------------------------------------------------------
app = App(app_ui, server)