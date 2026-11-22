# Picky — Sleeper NBA Draft Copilot

**Picky** is a read-only, Streamlit-powered NBA fantasy draft companion for Sleeper. It follows your draft, removes selected players from consideration, estimates roster needs, and explains which available players may be worth drafting now versus waiting for your next pick. Picky is designed with **Sleeper NBA Lock-In** leagues in mind; imported projections must match your league's scoring to support meaningful points estimates.

**Live app:** https://satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app

> Picky never submits a selection. Make all actual picks in Sleeper. Recommendations, reported injuries, ADP, AI summaries, and projected Lock-In opportunities are decision aids—not guarantees.

## Start using Picky

1. Open the live app. If Streamlit has put it to sleep, use its wake-up control and allow the app to start.
2. Open **Settings & Connections** and paste a Sleeper NBA draft URL or draft ID. No Sleeper password or API token is needed for read-only draft access.
3. Enter your Sleeper username/user ID, or select your team when league users are available. This enables roster-aware recommendations and turn detection.
4. Return to **Overview** for the current pick, your roster, a featured recommendation, and the **Top 5 available options**. Use **View details** on a player for scouting, sources, and draft-timing context.
5. Keep the app open during the draft. Picky checks picks every **5 seconds by default** (adjustable to 10, 15, 30, or 60 seconds under Settings). **Check Sleeper now** on Overview or Draft Board requests a fresh snapshot immediately.

The 5-second timer runs while an active browser session is open; it is **not** a background server job or a 24/7 monitor. Sleeper response time and network availability may delay updates.

For a step-by-step walkthrough, see [User Guide](docs/USER_GUIDE.md).

## Features and pages

| Page | What you can do |
| --- | --- |
| **Overview** | See pick count, your estimated next turn, team depth, featured and Top 5 recommendations, draft-timing notes, optional AI Scout, and recent picks. |
| **My Team** | Review drafted players, eligible starter/utility assignments, open slots, and NBA-team distribution. These assignments are illustrations, not Sleeper's official lineup. |
| **Draft Board** | Follow the latest picks, search the full pick history, and manually refresh Sleeper. |
| **Player Rankings** | Explore available players, filter by position, compare ADP/projection baselines, and export a CSV. |
| **Reports & News** | Review ESPN/Google News RSS headlines associated with available players. A headline is not an independently verified injury report. |
| **AI Lab** | Evaluate session-recorded shortlist survival and export observations; inspect a retrospective *current-ADP* replay. This is **not** a validated historical fantasy-point backtest. |
| **Settings & Connections** | Configure draft, team, refresh interval, optional projections, and ranking weights. |
| **Help** | Get a short in-app explanation of setup and fantasy terminology. |

### Ranking inputs and Lock-In estimates

- Without a CSV, Picky tries a **Hashtag Basketball blended ADP** baseline (ESPN/Yahoo/Fantrax values). If unavailable, it falls back to Sleeper player search rank. **ADP measures typical draft order, not fantasy points.**
- Optionally upload a CSV with a `player_id`, `player`, or `name` column and at least one of `projected_fppg`, `fppg`, `projected_points`, or `rank`. Uploading it replaces the ADP baseline for scoring candidates.
- For the exploratory Lock-In opportunity model, use league-scored per-game `projected_fppg`, `games_per_week`, `availability_pct`, and either `stdev_fppg` or both `floor_fppg` and `upside_fppg`. See [the projection template](lockin_projection_template.csv).
- The model estimates an optimistic expected best available game, **not** the score a manager will actually lock. Picky does not substitute ADP for missing points, or apply incomplete stat-category scoring silently. Ranking incorporates the Lock-In estimate only when compared players have adequate, comparable inputs.
- Position fit, injuries/news signals, opponent roster gaps, and pick-wait risk inform the suggestions, but Picky does **not** output calibrated probabilities of a player still being available.

For required columns, units, and interpretation, see [User Guide — Custom projections](docs/USER_GUIDE.md#custom-projections-and-lock-in).

### AI Scout is optional and may cost money

Basic draft tracking, recommendations, news, and rankings **do not require OpenAI**.

To enable paid AI features on your own deployment, configure **both** `OPENAI_API_KEY` and `PICKY_AI_SCOUT_ACCESS_CODE` as private environment variables or Streamlit secrets. Select a Sleeper account, then enter the access code on Overview.

- **Manual (default):** **Research Top 5 with AI** researches the current shortlist using player-specific web searches and subsequent analysis. A run may make **up to five paid web-search requests and five paid analysis requests**, depending on candidate count and failures. **Refresh AI research** is another paid run.
- **Automatic (opt-in):** After unlocking, turn on **Automatically research when I'm on the clock**. While **Overview remains open**, Picky checks Sleeper at your selected interval and attempts research **once per confirmed owned pick**. The attempt is recorded before any API call so errors do not trigger automatic retry loops. Manual research remains available; clicking it again may incur additional charges.
- **Ask Picky:** Once unlocked, manually ask a question or compare two shortlisted players. Each click makes a **paid model call**, but no new web-search call; it uses the current draft context and previously retrieved report when available.
- **Provenance:** AI Scout displays retrieved sources and labels unsupported/retrieval-only findings. Linked articles and model-reported dates are not independently fact-checked by Picky. AI text can be incorrect or stale. The deterministic Top 5 order is not secretly replaced by AI recommendations.

There is no Picky-enforced spending cap; control costs through your OpenAI account. Auto-research settings, reports, evaluation snapshots and conversations are **per browser session**, not synced across users.

For detailed behavior and safe configuration, see [User Guide — AI Scout](docs/USER_GUIDE.md#ai-scout-and-ask-picky) and [Developer Guide](docs/DEVELOPER_GUIDE.md).

## Local setup

Requires **Python 3.10+**.

~~~bash
git clone https://github.com/SatyanThayaparan/sleeper-tracker.git
cd sleeper-tracker
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

Open the local Streamlit URL (normally `http://localhost:8501`). The app works without OpenAI credentials for its non-AI features.

To prefill a draft and/or enable AI locally, copy `.env.example` to `.env` and replace placeholders. The supported settings are:

| Variable | Purpose |
| --- | --- |
| `PICKY_DEFAULT_DRAFT_URL` | Optional starting draft URL for local testing/deployment; prepopulates Settings. |
| `OPENAI_API_KEY` | Optional for basic use; **required** for paid AI research and follow-ups. |
| `PICKY_AI_SCOUT_ACCESS_CODE` | A separate private phrase needed to unlock paid AI features, even when the API key exists. |

Never commit `.env`, `.streamlit/secrets.toml`, real keys, access codes, or private draft settings. The repo's ignore rules exclude the two secret files.

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io) with GitHub.
2. Deploy repository `SatyanThayaparan/sleeper-tracker`, branch `main`, main file `app.py`.
3. Under **App settings → Secrets**, add optional credentials if you want AI access. Restrict who receives the Scout access code: the application itself is **public** if deployed publicly.
4. Share the app URL. Visitors can open it and wake a sleeping Community Cloud app, but uptime is **not guaranteed** and it may hibernate after inactivity. A sleeping app does not keep polling Sleeper or running AI tasks.

[Direct deploy link](https://share.streamlit.io/deploy?repository=SatyanThayaparan/sleeper-tracker&branch=main&mainModule=app.py)

No Sleeper API key is needed. A public Streamlit URL does not make your private OpenAI key visible, but **any visitor who knows the separately configured Scout access code could initiate billable requests**. Do not publish it.

## Project map

| Files | Responsibility |
| --- | --- |
| `app.py`, `theme.py`, `page_style.py` | Streamlit screens, live refresh, shared dark/emerald UI. |
| `scout_design.py`, `scout_style.py` | Responsive featured/Top 5 cards, details dialog, Sleeper CDN headshots with initials fallback. |
| `recommend.py`, `adp.py`, `lockin.py` | Candidate ranking, ADP matching, optional league-aware Lock-In model. |
| `roster.py`, `draft_strategy.py`, `opponent_draft.py`, `nba_teams.py` | Roster presentation, next-pick estimates, opponent demand, NBA-team distribution. |
| `ai.py`, `scout.py`, `research_pipeline.py`, `expert_research.py`, `copilot.py` | Protected, opt-in AI research and manual follow-ups. |
| `evaluation.py` | Session-scoped decision observations and retrospective ADP replay. |
| `config.py`, `.env.example`, `.streamlit/config.toml` | Local/deployment settings and app theme tokens. |
| `assets/picky-logo.png` | **Current browser tab/sidebar icon**. `assets/picky-icon.jpg` is an older asset. |
| `lockin_projection_template.csv` | Header-only CSV example for projection imports. |
| `tests/`, `.github/workflows/picky-checks.yml` | Unit tests and compile/test checks on pull requests and pushes to `main`. |

## Developer commands

~~~bash
python -m unittest discover -s tests -v
python -m compileall -q app.py theme.py recommend.py roster.py scout.py ai.py draft_strategy.py opponent_draft.py nba_teams.py lockin.py copilot.py evaluation.py expert_research.py research_pipeline.py scout_design.py scout_style.py page_style.py
~~~

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for architecture, cache/refresh behavior, GitHub Codespaces, AI safety/cost guards, test workflow, and troubleshooting.

## Limitations and external data

Picky depends on Sleeper's public API, Hashtag Basketball ADP, outside news feeds, an optional Sleeper image CDN, and optional OpenAI services. Any may be unavailable, stale, or changed independently. Missing portraits fall back to initials. Turn estimates can be imperfect when picks are traded. Session data is not a durable database, and Picky is neither an auto-drafter nor a promise of winning a fantasy league.
