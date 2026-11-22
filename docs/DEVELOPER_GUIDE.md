# Picky Developer Guide

[← Back to README](../README.md) · [User Guide](USER_GUIDE.md)

This guide describes the **implemented** Sleeper NBA draft copilot, not a proposed future system. The codebase is a single Python/Streamlit application with modular recommendation, scouting, style, and evaluation helpers. There is **no database, background worker, auto-draft integration, or Sleeper login**.

## Run locally

**Prerequisites:** Python 3.10+ and access to the external services you want to use. CI currently uses Python 3.12.

~~~bash
git clone https://github.com/SatyanThayaparan/sleeper-tracker.git
cd sleeper-tracker
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

With no configuration, enter a Sleeper NBA draft in the UI. OpenAI is **not** needed for the core app.

For private configuration, copy `.env.example` to an ignored `.env` file and replace its placeholders:

~~~dotenv
# Optional: prefill Settings with a draft for local testing
PICKY_DEFAULT_DRAFT_URL=https://sleeper.com/draft/nba/YOUR_DRAFT_ID

# Optional for basic operation; required for AI Scout/Ask Picky
OPENAI_API_KEY=replace-with-your-private-openai-key
PICKY_AI_SCOUT_ACCESS_CODE=replace-with-a-long-private-passphrase
~~~

The same three values can be set in local ignored `.streamlit/secrets.toml` or **Streamlit Community Cloud → App settings → Secrets**. `config.py` and `ai.py` read environment variables first and Streamlit secrets second. The Scout access code is a separate spend-control gate: an API key alone does not unlock the public app's paid controls.

Do not log, commit, screenshot, or share real keys/passphrases. Treat an exposed code as compromised and rotate it. Do not set a private test draft URL in tracked files.

## Runtime data flow

~~~text
Sleeper public NBA draft + league + player endpoints
           │
           ▼
app.py: session settings, current draft, live picks, selected account
           ├── adp.py: Hashtag Basketball blended ADP (or imported CSV)
           ├── roster.py: user selections and slot presentation
           ├── recommend.py + lockin.py: eligible candidates and scored rankings
           ├── draft_strategy.py + opponent_draft.py: why draft now / wait
           ├── news_feed(): ESPN / Google News RSS headlines
           └── Streamlit screens: Overview, Team, Board, Rankings, Reports, Lab
                          │
                          └── OPTIONAL, passcode-unlocked user action or opt-in
                                ai.py → scout.py → research_pipeline.py
                                      → OpenAI web search + analysis
                                copilot.py → manual no-web follow-up
~~~

### Module ownership

| Module | Responsibilities |
| --- | --- |
| `app.py` | Streamlit routing, Settings widgets, Sleeper requests, fragment refresh, CSV parsing, page assembly and UI actions. |
| `theme.py`, `page_style.py` | Shared brand tokens, sidebar, general metrics/tables/responsive styling. |
| `scout_design.py`, `scout_style.py` | Escaped HTML for featured and Top 5 cards, details dialog presentation, adaptive layout; use `assets/picky-logo.png` for browser tab/sidebar brand. |
| `recommend.py`, `adp.py` | Candidate selection, weighted ranking, ADP retrieval/matching, roster/health/news adjustments. |
| `lockin.py` | Explicit-input expected best-game opportunity model for Sleeper Lock-In; rejects incomplete/incomparable inputs. |
| `roster.py`, `nba_teams.py` | Roster-slot mapping and per-NBA-team breakdown. |
| `draft_strategy.py`, `opponent_draft.py` | Timing/fit and upcoming opposing draft-slot need signals; no invented availability probabilities. |
| `ai.py`, `config.py` | OpenAI client, secret/passcode validation, optional default draft URL. |
| `scout.py`, `research_pipeline.py`, `expert_research.py` | Paid, optional player research, retrieval/source linkage, caching, error handling and once-per-turn guard. |
| `copilot.py` | User-clicked Q&A/comparison using current context and cached evidence, without web search. |
| `evaluation.py` | Session-only shortlist snapshots, observed pick-survival metrics, current-ADP retrospective replay, CSV generation. |
| `tests/` | Standard-library unittest suite covering ranking/scout logic, style contracts, draft strategy, Lock-In, research, opponents, and other helpers. |

`assets/picky-icon.jpg` remains in the repository as an older asset; **`assets/picky-logo.png` is the active icon** according to `theme.ICON_PATH`.

## Sleeper, ADP, news, and caching

- **Sleeper API:** `https://api.sleeper.app/v1`; requests are read-only. Draft/picks endpoints include `draft/{id}` and `draft/{id}/picks`. League and member/roster endpoints supply scoring, positions, team identity and draft order. `players/nba` supplies metadata. Traded-pick data is used when available rather than silently inventing ownership.
- **User input:** the URL parser accepts a Sleeper NBA draft link or numeric ID; a league ID override is optional. User/team identity enables ownership and on-clock detection. Draft-status checks distinguish active, completed and unavailable states.
- **Rank source:** `adp.py` parses [Hashtag Basketball ADP](https://hashtagbasketball.com/fantasy-basketball-adp) and matches names to Sleeper IDs. CSV uploads replace the ADP baseline. A Sleeper search-rank fallback applies if needed. ADP must not be converted into fantasy-point projections.
- **News:** ESPN NBA RSS and a Google News search RSS feed supply headline context. Links and headlines are not independently verified injury diagnoses.
- **Player photos:** `scout_design.py` generates a numeric-ID URL under the public Sleeper NBA image CDN. CSS image loading occurs in the browser; the Streamlit server does not fetch these headshots. Initials remain the visible fallback for missing/invalid images.

The current explicit Streamlit data-cache settings in `app.py` are:

| Function | Cache TTL | Notes |
| --- | --- | --- |
| `live_draft_snapshot(draft_id)` | **4 seconds** | Draft/picks tuple. **Check Sleeper now** clears this entry and reruns the fragment. |
| `api_get(path)` | **25 seconds** | General draft/league/user requests; separate from the live picks snapshot. |
| `player_map()` | **24 hours** | Sleeper NBA player directory. |
| `cached_adp_rows()` | **6 hours** | Hashtag Basketball ADP page. |
| `news_feed()` | **10 minutes** | External RSS feeds. |

The `@st.fragment(run_every=f"{refresh}s")` live dashboard runs on an active session with **5 seconds by default**; Settings offers 5, 10, 15, 30 and 60 seconds. **Do not interpret this as a guaranteed poll cadence or a background scheduler.** Network latency, browser/session state, Streamlit hosting, and cache TTL can all affect freshness. Only the specific live snapshot is cleared on a manual refresh.

## AI request lifecycle and spend protection

Picky's deterministic ranking is computed independently of OpenAI. Basic pages and the five-second Sleeper poll **must not** trigger paid AI requests.

1. The deployment owner provides `OPENAI_API_KEY` and `PICKY_AI_SCOUT_ACCESS_CODE`; the visitor selects an account and unlocks Scout with the passphrase.
2. **Manual:** the user clicks **Research Top 5 with AI** or **Refresh AI research**. **Optional automatic:** only after an explicit toggle is enabled and the Overview page confirms the user's turn in an active draft.
3. `scout.py` uses `turn_research_key(draft_id, user_id, pick_number)` and a per-session auto-attempt set. An auto attempt is recorded **before** the external API call so failures do not create repeated charges on later polling ticks. Manual retries remain possible and billable.
4. For a normal shortlist of up to five players, `research_pipeline.py` performs a **web-search retrieval** and a separate **no-web structured analysis** for each player (up to five of each per click/turn). Failed analysis may preserve a retrieval-only state, but must not be labeled as verified player evidence.
5. Report/source metadata are stored in the **current Streamlit session**, keyed to the turn and validated against the current shortlist. Turn-scoped entries stay associated with that turn; their appearance on new shortlists is guarded rather than silently reused.
6. `copilot.py` sends a **new paid model completion only on explicit Ask/Compare clicks**, with no web tool. Its answers can be stale if the source report is incomplete.

`scout.py` and the research pipeline use `gpt-4.1-mini` as their configured default, and `copilot.py` uses the same model for manual follow-ups. Provider model and web-search pricing may change; no Picky-side spending limit exists. Keep account-level budgets/quotas set.

**Source quality:** a URL found during web search shows retrieval provenance, not independent article verification. The analysis must refer to retrieved source IDs where available. Missing links, unsupported references, model-reported publication dates and AI interpretation may be wrong and must remain labeled accordingly. Preserve fallback states for unavailable/partial research.

## State, persistence, and security

- Streamlit **session state** holds draft/team preferences for navigation, uploaded CSV, AI unlock/auto-toggle, research history, Q&A turns and evaluation snapshots. It is **not a durable database**, and data is not synchronized between browser sessions.
- Draft data is fetched from Sleeper via public/read-only endpoints. Picky does **not** ask for a Sleeper password or submit picks.
- A publicly hosted Streamlit app can be viewed by anyone who can access the URL; a sleeping Community Cloud instance may be woken by a visitor. It does **not** continuously check picks while asleep. Public reachability is different from guaranteed uptime.
- Keep `.env` and `.streamlit/secrets.toml` ignored. Do not expose secrets in an HTML card, app log, test fixture, support screenshot or pull request. Scout access code disclosure allows visitors to use the owner's paid OpenAI quota.
- External assets and APIs are best effort. Verify claims using original Sleeper/league settings and source articles before drafting.

### GitHub Codespaces

The repository contains `.devcontainer/devcontainer.json` that installs requirements, starts Streamlit after attach, and forwards port **8501**. This supports browser-based coding, including mobile browsers.

**Security warning:** the current development-container command disables Streamlit CORS and XSRF protection for its preview. That is a **development-only convenience**, not a recommended public production configuration. Keep forwarded ports appropriately restricted and do not reuse those flags in public deployment.

## Checks and release process

The tracked GitHub Actions workflow `.github/workflows/picky-checks.yml` runs on pull requests and pushes to `main`, installs `requirements.txt` under Python 3.12, compiles the application modules, and runs the unittest suite.

Run locally before changing code:

~~~bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q app.py theme.py recommend.py roster.py scout.py ai.py draft_strategy.py opponent_draft.py nba_teams.py lockin.py copilot.py evaluation.py expert_research.py research_pipeline.py scout_design.py scout_style.py page_style.py
~~~

For documentation-only edits, check relative links, command names, file paths and UI labels against `app.py` / `theme.py`. If changing polling, paid-request behavior, CSV rules, public-access handling or active branding, update **README + User Guide + Developer Guide** together. Avoid claiming deployments, availability or paid requests were live-tested unless they were.

Deploy via **Streamlit Community Cloud** with branch `main` and entrypoint `app.py`. Production secrets belong in Cloud's secret settings, not Git. The public URL and deploy instructions are in the [README](../README.md#deploy-on-streamlit-community-cloud).

## Troubleshooting contributors

- **Requirements file not found:** execute commands from the repository root (the folder that actually contains `requirements.txt`), not a parent directory.
- **App reports an invalid draft:** verify NBA draft URL/ID, upstream API health and league metadata.
- **Unit tests don't run:** verify dependencies were installed and use `python -m unittest discover -s tests -v` from the root.
- **AI not visible:** both required secrets and a selected account are needed. The Scout code is independent of the API key.
- **Repeated AI cost concerns:** review opt-in state and explicit manual clicks; do not wire `use_scout` or `ask_copilot` into unconditional fragment refresh.
- **ADP or news empty:** check external provider availability and parser changes before modifying fallback behavior.
