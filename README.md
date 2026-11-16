# Sleeper Tracker

Streamlit draft copilot for Sleeper NBA fantasy leagues — live pick tracking, projections, and pick recommendations.

## Features

- Connect to a Sleeper draft by ID or URL
- Auto-refresh picks while the browser session is open
- Import custom projection CSVs (FPPG, upside/floor, availability)
- Recommendation engine that accounts for roster needs, ADP, injury tags, and news headlines
- Lock-In-friendly projection template included

## Tech stack

- Python 3.10+
- Streamlit
- Sleeper public API (read-only)

## Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the app:

```bash
python -m streamlit run app.py
```

4. Open the Streamlit URL (usually `http://localhost:8501`).
5. Select your Sleeper username and import a projections CSV if desired.

## Usage

- Enter a draft ID/URL, or use the configured draft already in the app.
- Provide a CSV with `player,projected_fppg` or `player_id,projected_fppg` (optional: `upside_fppg`, `floor_fppg`, `games_per_week`, `availability_pct`).
- Use `lockin_projection_template.csv` as a starting template.
- The app never makes picks for you; it only reads league/draft data.

## Project structure

```text
sleeper-tracker/
├── app.py                          # Streamlit UI
├── recommend.py                    # recommendation logic
├── adp.py                          # ADP helpers
├── lockin_projection_template.csv  # projection CSV template
└── requirements.txt
```

## Notes

- No Sleeper password or API key is required for read-only draft polling.
- News headlines are signals, not confirmed facts.
- Projection quality depends on the CSV you supply matching your league’s scoring.
