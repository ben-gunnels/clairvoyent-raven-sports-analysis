# Project Roadmap & Tasks

EXAMPLE TODO DOC
MAY USE THIS IN THE FUTURE
FOR NOW, REFER TO Sports Analysis Project: Planning Document | Team Responsibilities and Tasks Table

## 🚧 In Progress

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Implement Yahoo wrapper’s `get_player_stats` overloads | NULL | In Progress | Need to handle `req_type="week"` |
| Add tests for edge cases (invalid IDs) | NULL | Pending | Use pytest parametrize |

## ✅ Completed

- Set up project structure (`/src`, `/notebooks`, `/tests`)
- Created basic SportsDataIO wrapper
- Configured pytest and CI pipeline

## 💡 Backlog / Ideas

- Allow specifying which Yahoo league instead of defaulting to last one  
- Add simulation-based fantasy point projections  
- Support roster & matchup endpoints from Yahoo  
- Cache API results locally & version snapshots  
- Build UI to show projections & trends  

## 🐛 Known Issues / Bugs

| Issue | Description | Priority / Impact |
|-------|-------------|--------------------|
| OAuth JSON not found in notebook | Notebook run path may differ, breaking file lookup | High |
| Duplicate player IDs in merged searches | Need unique filtering in player list builder | Medium |
| Inconsistent API responses | Some endpoints return dicts vs lists | High |
