# Picky

**Picky** is a Streamlit draft board for Sleeper NBA fantasy leagues — live pick tracking, projections, and pick recommendations.

**Live app:** [satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app](https://satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app)

## Features

- Dark 60/30/10 dashboard (emerald accent)
- Sidebar navigation: Overview, My Team, Draft Board, Rankings, Reports, AI Lab, Settings, Help
- Settings & Connections for draft link, projections CSV, and ranking weights
- Live draft metrics, top recommendations, sleeper / fade cards
- Auto-refresh picks while the browser session is open
- Lock-In opportunity estimates from real league scoring inputs + user-supplied player volatility, schedule and availability
- Opt-in AI Scout and contextual Ask Picky / 2-player comparisons; manually paid requests, no additional web search for follow-ups
- AI Lab: per-turn observed shortlist survival, retrospective ADP baseline, CSV export

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
- Provide a CSV with `player,projected_fppg` or `player_id,projected_fppg` (optional: `upside_fppg`, `floor_fppg`, `stdev_fppg`, `games_per_week`, `availability_pct`).
- Use `lockin_projection_template.csv` as a starting template.
- The app never makes picks for you; it only reads league/draft data.

## Project structure

```text
sleeper-tracker/
├── app.py                          # Streamlit UI (Picky)
├── theme.py                        # Dark theme + fixed sidebar CSS
├── assets/picky-icon.jpg           # dice cube icon
├── .streamlit/config.toml          # default Streamlit theme tokens
├── recommend.py                    # recommendation logic
├── adp.py                          # ADP helpers
├── lockin_projection_template.csv  # projection CSV template
└── requirements.txt
```

## Secrets & local test draft

Local secrets stay out of git (`.env` and `.streamlit/secrets.toml` are gitignored).

1. Copy `.env.example` → `.env`
2. Set `OPENAI_API_KEY=...` for ChatGPT helpers
3. Set `PICKY_DEFAULT_DRAFT_URL=...` to your base Sleeper draft (pre-fills Settings for local testing)
4. Or put the same keys in `.streamlit/secrets.toml`
5. On Streamlit Community Cloud, add them under **App settings → Secrets**

`config.py` / `ai.py` load these values. Never commit real keys or a private draft URL.

## Evaluating Picky's AI roadmap

### Lock-In scoring (Phase 3)

A valid imported projection should provide **league-scored per-game FPPG**, either `stdev_fppg` or both `floor_fppg` and `upside_fppg`, `games_per_week`, and `availability_pct`. The `upside_fppg` and `floor_fppg` values are treated as rough 90th and 10th percentile game outcomes; if that assumption does not match your data, provide `stdev_fppg` instead.

When *complete* per-game stat projections are supplied for all applicable Sleeper scoring categories, the model can apply the league's actual scoring settings. Unsupported scoring bonuses are **not silently dropped**: an imported fully league-scored FPPG is required instead. Without the needed inputs, the model reports missing data and **does not convert ADP into fantasy points**.

The estimate is an optimistic *expected best available game* for a matchup week. Actual Sleeper Lock-In requires timely choices after real games and has fallback rules; the number is **not** a guarantee or a validated prediction of your lock decision. When every eligible projected player has comparable model inputs, Picky can incorporate opportunity into its score while preserving the existing injury, news and roster fit adjustments. With incomplete coverage, the ranking remains unchanged.

### Expert reports and cheat-sheet research (Phase 1 enhancement)

Once you unlock AI Scout with your access code, Picky can search the **current Top 5** for expert coverage including ESPN fantasy analysis, Yahoo fantasy draft kits and points-league rankings, NBA.com, RotoWire and other cited sports reports.

- **On any turn:** unlock AI Scout and click **Research Top 5 with AI**. A click deliberately starts a separate web-search retrieval and a no-web AI analysis request for each available candidate (up to five searches plus five analysis calls per button press). The report is cached until you choose to refresh it or the shortlist changes.
- **No automatic paid requests:** draft polling, opening the app and loading a new pick never trigger OpenAI research.
- **Research report:** all shortlisted players get visible concise research summaries, each labeled as source-linked or unverified. Full expert findings, cited articles, source status and failures are tucked into an expandable details section. Existing fantasy-points rank and roster-fit order remain the baseline.
- **Sources:** the retrieval stage collects provider web-search action sources and inline citations; the analysis stage can only cite numbered source IDs from that list. Missing or unsupported IDs remain unverified. Retrieved URLs establish provenance, not independent fact-checking of article claims. Publication dates are **AI-reported, not independently verified from page metadata**; older articles are flagged and unknown dates remain unknown.
- **Rankings:** expert lists are external context, not a replacement for your league's actual scoring settings or draft rank. ESPN/Yahoo points-league rankings do not necessarily value Sleeper Lock-In in the same way. Never infer a player's rank or expert endorsement just because a general draft kit exists.
- **Cost:** clicking Research uses OpenAI web-search/model credits, potentially five web searches and five analysis calls per press, and clicking again does the same. There are no Picky-side credit or attempt limits. Set budgets and billing limits in your OpenAI account. Research is always manual. Results are browser-session scoped.

### Ask Picky (Phase 4)

On Overview, unlock AI Scout with the existing passkey and open **Ask Picky · AI Copilot**. Compare two available candidates or type a question. **Only clicking Ask/Compare incurs a new model request**; follow-ups reuse the existing Scout report (when available), have no new web-search tool, have no Picky-side request cap and are scoped to your current browser session. They can be wrong when relevant evidence is missing or stale.

### AI Lab (Phase 5)

Open **AI Lab** in the sidebar. During your on-clock pick Picky records a shortlist snapshot in your current browser session, then checks whether shortlisted players were actually selected before your next estimated pick. You can export observed outcomes. No snapshot exists for past turns when the app was closed.

The retrospective ADP replay compares **today's** ADP order with the observed pick history. It may contain hindsight bias, is not an unbiased historical backtest, and **cannot validate Lock-In scoring quality**. Use it to find rough selection patterns and design future evaluation experiments; historical scoring and point outcomes require separate reliable game-level archives.

## Notes

- No Sleeper password or API key is required for read-only draft polling.
- News headlines are signals, not confirmed facts.
- Projection quality depends on the CSV you supply matching your league’s scoring.
