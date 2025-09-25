## Fantasy Football Player Projections: How They’re Built & What They Use

### 🎯 What a Projection Tries to Do  
A player projection aims to estimate a player’s **future fantasy points** (weekly or season total). The goal is not just a point estimate, but often a **distribution** (floor, ceiling, percentile) plus a ranking relative to other players.

To do this well, models must combine:

- A player’s baseline performance and usage  
- Team / offense context (pace, coaching tendencies)  
- Matchup / opponent defenses  
- Game script (how the game is expected to flow)  
- Injury / roster shifts / volatility  
- Uncertainty modeling  

---

### Key Data & Features Used

| Category | Example Features | Purpose |
|---|---|---|
| **Player historical performance** | Past fantasy points, per-game stats (yards, touchdowns, receptions), usage (snap share, target share) | Provides the baseline “expected” level of play |
| **Efficiency / advanced metrics** | Yards per route, yards after catch, target depth, success rate | Adjusts for the *quality* of opportunity, not just quantity |
| **Team / offense context** | Offensive line strength, pace (plays/game), pass/run balance, coaching tendencies | Influences how many opportunities a player might see |
| **Matchup / defensive context** | Opponent pass defense, rush defense, coverage strength vs position | Allows up/down adjustment by opponent weakness/strength |
| **Game script / environment** | Implied point totals, win probability, expected pass/run tilt, possession share | Predicts whether a team will be in pass-heavy or run-heavy mode |
| **Roster / injury dynamics** | Injuries, depth chart changes, bye weeks | Can change opportunity share dramatically |
| **Variance / stability** | Past volatility, consistency measures (standard deviation week-to-week) | To estimate how “risky” a player’s projection is |
| **External adjustments** | Weather, match conditions, late news, coaching changes | Minor tweaks / overrides in some systems |

Many high-end systems also **simulate entire games or seasons repeatedly** (Monte Carlo) to derive distributions of possible outcomes.

---

### Common Modeling Techniques & Approaches

- **Regression / GLM / regularized linear models** — interpretable, good baseline  
- **Tree-based methods** (Random Forest, XGBoost, LightGBM) — capture nonlinear interactions well  
- **Ensembles / stacking / blending** — combining multiple models for robustness  
- **Bayesian / hierarchical models** — introduce priors, shrink extreme predictions, pool data by group  
- **Similarity / comparable-player methods** — find “players like this one” historically and borrow their future trajectories  
- **Simulations / Monte Carlo** — simulate distinct plausible future paths (usage, game script) and average  
- **Neural networks / deep learning** — for highly nonlinear relationships or integrating alternate data (e.g. news)  
- **Rule-based or human tweaks on top** — to override when domain knowledge is strong  

---

### Workflow / Pipeline Outline

1. **Ingest & clean data** — historical stats, fantasy scoring, injuries, opponent metrics  
2. **Feature engineering** — rolling averages, matchup deltas, usage changes, trend features  
3. **Train / validation splits** — e.g. train on years 1…N-1, test on year N; cross-validation  
4. **Regularization / shrinkage / calibration** — to avoid overconfident outliers  
5. **(Optional) Simulation** — run many game/season simulations to derive distributions  
6. **Post-processing / human tweaking** — adjust for late news, known biases  
7. **Backtest & evaluate** — compare predictions to real results, measure error, refine  
8. **Output** — point estimate + floor/ceiling + rank + percentile + volatility metrics  

---

### Criteria & Tradeoffs

- **Rank accuracy over absolute error** — getting ordering right matters more than precise score  
- **Bias vs variance** — better to underpredict wild extremes than produce wildly erratic forecasts  
- **Stability / consistency** — projections shouldn’t swing massively week to week  
- **Handling sparse data / rookies** — often require shrinkage or borrowing from similar players  
- **Timeliness / updates** — must react to injury news, matchups changing, etc.  
- **Interpretability** — many systems prefer components you can explain (usage × efficiency vs black box)  
- **Providing distributions, not just points** — floor, ceiling, percentiles help users understand risk  

---

### How You Might Build a Simple Prototype

1. Start with baseline: e.g. weighted average of last 2–3 seasons of fantasy points  
2. Add recency bias: higher weight on recent games  
3. Add matchup adjustment based on opponent defense to that position  
4. Add usage predictor: target share change, route share, pace, projected offense volume  
5. Shrink toward mean for volatile players  
6. (Optionally) simulate usage and performance distributions to derive a range  
7. Output expected points + standard deviation + percentile  

You could begin with a **Gradient Boosting Model** (XGBoost / LightGBM) using features like:

- Historical fantasy points (lag, moving avg)  
- Usage volume (carries, targets, route share)  
- Efficiency (yards per target, yards per carry, touchdowns per attempt)  
- Matchup strength vs opponent  
- Team pace / pass percent  
- Injury or usage change flags  

Train by position (RB, WR, TE) separately, tune hyperparameters, calibrate errors, and you’ll have a working projection engine.

---
