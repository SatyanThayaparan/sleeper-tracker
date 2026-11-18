# Hanko

**Hanko** is a Streamlit draft board for Sleeper NBA fantasy leagues — live pick tracking, projections, and pick recommendations. The name nods to a Japanese seal stamp: your pick, marked.

**Live app:** [satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app](https://satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app)

## Features

- Fantasy draft UI with a swipe theme toggle (60-30-10):
  - **Washi & Sumi** — cream paper, charcoal ink, vermilion accents (same Sora typography as dark)
  - **Midnight Shibuya** — aizome indigo, slate panels, matcha / gold accents
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

1. Clone the repo and enter the project folder:

```bash
git clone https://github.com/SatyanThayaparan/sleeper-tracker.git
cd sleeper-tracker
```

2. Install [Python 3.10+](https://www.python.org/downloads/).
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run the app:

```bash
python -m streamlit run app.py
```

5. Open the Streamlit URL (usually `http://localhost:8501`).
6. Select your Sleeper username and import a projections CSV if desired.

## Deploy (Streamlit Community Cloud — free)

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with **GitHub**.
2. **Create app** (or use a deploy link) with:
   - Repository: `SatyanThayaparan/sleeper-tracker`
   - Branch: `main`
   - Main file: `app.py`
3. Deploy — current public URL:

https://satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app

Direct deploy link (after GitHub auth):

https://share.streamlit.io/deploy?repository=SatyanThayaparan/sleeper-tracker&branch=main&mainModule=app.py

No API keys are required for read-only Sleeper draft polling. Apps on Community Cloud may sleep after ~12 hours without traffic.

## Usage

- Enter a draft ID/URL, or use the configured draft already in the app.
- Provide a CSV with `player,projected_fppg` or `player_id,projected_fppg` (optional: `upside_fppg`, `floor_fppg`, `games_per_week`, `availability_pct`).
- Use `lockin_projection_template.csv` as a starting template.
- The app never makes picks for you; it only reads league/draft data.

## Project structure

```text
sleeper-tracker/
├── app.py                          # Streamlit UI (Hanko)
├── theme.py                        # Washi / Midnight themes + hero
├── assets/hanko-icon.jpg           # app icon
├── .streamlit/config.toml          # default Streamlit theme tokens
├── recommend.py                    # recommendation logic
├── adp.py                          # ADP helpers
├── lockin_projection_template.csv  # projection CSV template
└── requirements.txt
```

## Notes

- No Sleeper password or API key is required for read-only draft polling.
- News headlines are signals, not confirmed facts.
- Projection quality depends on the CSV you supply matching your league’s scoring.
