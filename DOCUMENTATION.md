# Sleeper Tracker — Documentation

## What this project is

A Streamlit “NBA Draft Copilot” for Sleeper fantasy drafts. It watches a live draft, blends your projection sheet with ADP and news signals, and ranks who you might want next. It is read-only advice—it does not make picks for you.

## Tech stack

| Layer | Choice | Why it’s used |
| --- | --- | --- |
| App framework | Streamlit | Fast interactive dashboard in Python |
| Data wrangling | pandas | Normalize projection CSVs and rank tables |
| HTTP | requests | Call Sleeper’s public API and fetch ADP/news pages |
| Feeds | feedparser | Read ESPN / Google News RSS for injury and buzz signals |
| Input | Custom projection CSV template | Bring your own player valuations |

## How the logic works

1. **Identify the draft** — You enter a Sleeper draft ID or URL (a Lock-In draft can be prefilled as a default).
2. **Pull live draft state** — The app calls `api.sleeper.app` for draft metadata, league context, player directory, and picks already made.
3. **Import projections** — An optional CSV of your rankings/projections is normalized into a consistent table.
4. **Add market + news context** — ADP is pulled from Hashtag Basketball; RSS headlines add injury/news tone.
5. **Score available players** — `recommend.py` ranks remaining players using projection strength, roster need, ADP baseline, and headline tone.
6. **Refresh while open** — Streamlit keeps polling so the board updates as the draft progresses.

## Project map

Flat Python app—each file is a lane of responsibility.

| Path | Role |
| --- | --- |
| `app.py` | Streamlit UI: draft ID input, Sleeper API polling, CSV upload/normalize, news feed intake, display of recommendations |
| `recommend.py` | Pure ranking logic: score available players using projections, roster need, ADP, and headline tone |
| `adp.py` | Fetches/normalizes Average Draft Position data (Hashtag Basketball) so rankings have a market baseline |
| `lockin_projection_template.csv` | Example projection sheet showing the columns the app expects |
| `requirements.txt` | Python dependencies (`streamlit`, `pandas`, `requests`, `feedparser`, …) |
| `README.md` / `DOCUMENTATION.md` | How to run + this overview |

### How the files talk to each other
`app.py` gathers live draft state and inputs, then asks `recommend.py` (and `adp.py` for market context) to produce the shortlist shown in the UI.

## Mental model

Imagine a **draft room sticky-note board that updates itself**: Sleeper tells you who’s gone, your CSV says who you value, ADP/news nudge the ranking, and Streamlit shows the shortlist. You still click the actual pick in Sleeper.
