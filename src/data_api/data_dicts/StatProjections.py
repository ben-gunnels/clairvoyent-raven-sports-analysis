"""Lays out the data framework for what stats are needed to make a player fantasy points projection 
for the following positions:
    POSITION_PLAYER_STAT_PROJECTION_DATA_DICT: QB, RB, WR, TE

The data is laid out so that each key (statistic projection) maps to a dictionary which contains a placeholder for the projection
created by the model, and the weight assigned for fantasy points. Feel free to tweak the weights according to your own purposes
by changing the code here, or updating the weights when the object is used.

The standard point system will follow for the following stat categories:
 * rushing_yards: 0.1 points per yard
 * rushing_tds: 6 points
 * receiving_yards: 0.1 points per yard
 * receiving_tds: 6 points
 * receptions: 0.5 points per receptions
 * passing_yards: 0.04 points per yard
 * passing_tds: 4 points per td completion
 * rsh_fumbles: -2 points per fumble
 * rc_fumbles: -2 points per fumble
 * interceptions: -2 points per interception

The preferred usage for this object is to import it and mutate the 'projection' values while assigning an object to each player for
a given week. Only mutate the stat projection for stats of interest based on the position of the player being assessed, 
i.e. running backs probably don't need to be projected for passing yards, but quarterbacks should be assessed for rushing yards. 
"""

POSITION_PLAYER_STAT_PROJECTION_DATA_DICT = {
    "rushing_yards": {"projection": 0.00, "weight": 0.1},
    "rushing_tds": {"projection": 0.00, "weight": 6},
    "receiving_yards": {"projection": 0.00, "weight": 0.1},
    "receiving_tds": {"projection": 0.00, "weight": 6},
    "receptions": {"projection": 0.00, "weight": 0.5},
    "passing_yards": {"projection": 0.00, "weight": 0.04},
    "passing_tds": {"projection": 0.00, "weight": 4},
    "rushing_fumbles_lost": {"projection": 0.00, "weight": -2},
    "receiving_fumbles_lost": {"projection": 0.00, "weight": -2},
    "passing_interceptions": {"projection": 0.00, "weight": -2},
}