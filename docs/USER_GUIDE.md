# Picky User Guide

[← Back to README](../README.md)

Picky accompanies a **Sleeper NBA fantasy draft**. It reads public draft information, scores available players, and presents roster and research context. You make every pick in Sleeper; Picky cannot draft or change league settings.

## 1. Connect your draft

1. Open the [Picky app](https://satyanthayaparan-sleeper-tracker-app-pmaj1x.streamlit.app).
2. In the sidebar, choose **Settings & Connections**.
3. Paste the Sleeper NBA draft link or draft ID in **Sleeper draft link or ID**. You can use a link of the form `https://sleeper.com/draft/nba/YOUR_DRAFT_ID`.
4. Enter your **Sleeper username or user ID**. If you leave it blank and Sleeper provides a league member list, the Settings screen may offer **Select your team / Sleeper account** instead.
5. Return to **Overview**.

Team selection matters: without it, Picky can show public picks and basic rankings, but cannot reliably personalize your roster, next turn, or turn-based AI Scout. A **League ID override** exists for unusual drafts; normally the league ID is discovered from the draft.

If you see **Cannot connect to Sleeper**, confirm that the ID is an NBA draft, the link is correct, and Sleeper's API is reachable. A private/inaccessible draft or a missing league response may prevent roster or scoring information from loading.

## 2. Follow picks in real time

On **Overview**, review the draft status, number of picks made, current pick, your estimated next pick, and picks until your turn. The **My Team** panel shows drafted players and a display-oriented assignment into eligible starter/utility slots.

Picky refreshes the live fragment while your browser session is active:

| Settings choice | Meaning |
| --- | --- |
| **5 seconds (default)** | Most frequent supported poll; not a guarantee of delivery every five seconds. |
| **10 / 15 / 30 / 60 seconds** | Less frequent checks and potentially fewer network requests. |
| **Check Sleeper now** | Available on **Overview** and **Draft Board**; clears the short-lived draft/picks snapshot and fetches again. |

A normal draft snapshot is cached for about four seconds; **Check Sleeper now** bypasses that snapshot cache. Other API metadata, ADP and news are cached separately. Polling does **not** continue when the browser session is gone or the hosted app is sleeping.

**Automatic AI research is separate from automatic Sleeper checks.** Polling can update rankings without making a billable OpenAI request. Automatic AI is disabled until you unlock Scout and explicitly opt in.

### Where to look

- **Overview:** Featured recommendation, five available player cards, draft-timing notes, manual refresh and recent picks.
- **My Team:** Players drafted, position/slot coverage, bench and utility illustration, NBA-team distribution.
- **Draft Board:** Latest picks, full selection history, and a drafted-player search.
- **Player Rankings:** Available-player table, position filter, ranking source, and **Export available rankings** CSV.
- **Reports & News:** Headlines from ESPN NBA RSS and a Google News NBA-fantasy search feed; open the original story to confirm context.
- **AI Lab:** Observed shortlist survival from your current session, downloadable decision CSV, and retrospective replay using today's ADP.
- **Help:** Brief definitions of ADP, Lock-In, sleeper, fade, roster fit, and projections.

The displayed roster is not a live official Sleeper lineup. Next-pick estimates use draft order and can be wrong when traded picks affect ownership. A player's **wait-risk** label is an explanation based on ADP, estimated next selection and, where available, opponent roster gaps—not a probability.

## 3. Understand the recommendations

Picky removes players already drafted and ranks the remaining player pool using:

- A **Hashtag Basketball ADP blend** by default, matching outside ADP entries to Sleeper NBA player IDs.
- Your own **uploaded projections or rankings** if supplied. These replace the ADP baseline.
- A **Sleeper search-rank fallback** when the normal ADP source cannot be loaded.
- Your team's position eligibility and remaining slots, current injury tags, and headlines where available.
- An optional **Lock-In opportunity estimate**, only when you supplied enough valid data.

**Do not interpret ADP as projected fantasy points.** A smaller ADP indicates that a player is usually drafted earlier. Labels such as sleeper/fade are decision signals, not professional medical or verified injury assessments. Picky's featured choice and Top 5 remain driven by its deterministic ranking engine even after optional AI research.

## 4. Custom projections and Lock-In

Go to **Settings & Connections → Custom projections (optional)** and upload a CSV. You can start from [lockin_projection_template.csv](../lockin_projection_template.csv), which contains the expected header names.

To identify a player, provide one of:

| Column | Description |
| --- | --- |
| `player_id` | Sleeper NBA player ID; most reliable matching option. |
| `player` or `name` | Player name matched to Sleeper's directory. Name mismatches may exclude rows. |

Provide at least one ranking/value column: `projected_fppg`, `fppg`, `projected_points`, or `rank`. Prefer **league-scored per-game fantasy points** via `projected_fppg`. If you import `projected_points`, confirm the units yourself; the app does not assume it means per-game production. A `rank`-only CSV provides rank order, **not** measured points.

For the exploratory Lock-In model, include:

| Column | Meaning |
| --- | --- |
| `projected_fppg` | Expected **per-game** fantasy points using your league's scoring rules. |
| `stdev_fppg` | Estimated game-to-game standard deviation. |
| `floor_fppg`, `upside_fppg` | Alternative to `stdev_fppg` **when both are supplied**; interpreted as approximate 10th/90th percentile game scores. |
| `games_per_week` | Number of scheduled games in a typical matchup week. |
| `availability_pct` | Estimated chance of being available for a game; the code accepts either 0–1 or 0–100 format. |

Advanced CSVs may also include projected per-game stat columns such as `pts`, `reb`, `ast`, `stl`, `blk`, `tov`, `fg3m`, `fgm`, `fga`, `ftm`, `fta`, `oreb`, `dreb`, `pf`, `dd`, and `td`. Where **all applicable league scoring categories** are covered, Picky can calculate league-scored mean points from those stats. Unsupported bonuses or omitted scoring categories must not be presented as a complete projection; if a trustworthy imported league-scored FPPG is available, the model may use that instead.

**How to read the result:** Picky models an optimistic expected *best available game* based on per-game mean, variation, game count, and availability. It does not simulate a real manager's lock-in timing or Sleeper's exact fallback rules. Missing/partial inputs mean the model stays unavailable; Picky does not create fake projections from ADP. For fair rankings, comparable Lock-In distributions must cover the compared players.

Your upload is associated with the current Streamlit session; do not assume it is stored or shared with other visitors.

## 5. AI Scout and Ask Picky

AI functionality requires **your own deployment's** `OPENAI_API_KEY` and `PICKY_AI_SCOUT_ACCESS_CODE`, plus a selected Sleeper account. The application owner should configure those privately; visitors do **not** need to know the API key and must **not** see it.

### Manual research (default)

1. Go to **Overview** and unlock **Picky AI Scout** with the separate Scout access code.
2. Review the deterministic Top 5 shortlist.
3. Click **Research Top 5 with AI**; a progress indicator shows the attempt.
4. Review the updated player-card summaries, source chips, and **View details** dialog (scouting overview, reports & sources, draft context). Some cards may have no reliable outside sources.
5. Only click **Refresh AI research** when another paid research run is warranted.

For up to five candidates, a single run may start **five web-search calls plus five analysis calls**. Failures may leave a player with a clear unverified or unavailable state instead of invented research. Retrieved links provide provenance; they do not independently establish that an AI summary is correct.

### Optional automatic on-clock research

After unlocking Scout on **Overview**, enable **Automatically research when I'm on the clock**. While that screen is open, Picky checks Sleeper on the configured timer. Once Sleeper identifies an active draft and confirms the selected account has the current pick, the app attempts one research run for that owned pick. Failed attempts are **not** automatically repeated. You may still choose to retry manually, which may cost money.

The opt-in can also refresh an earlier manually researched shortlist when your turn starts; it is not a blanket ban on all further manual AI requests. Turning off the toggle returns to manual-only behavior. On-clock research is **not** a push notification or server-side autonomous agent.

### Ask Picky and comparisons

Under Overview, open **Ask Picky · AI Copilot and player comparisons** after unlocking Scout. Select two available shortlisted players and click **Compare these players**, or enter a question and click **Ask Picky**. Each submission sends a new paid model request and uses current shortlist/roster context and prior report findings if present. It performs **no new web search** and can lack recent evidence.

AI requests are optional, and there are no in-app billing limits. Set budgets with your OpenAI provider. Reports, the opt-in and conversations live in the current browser session; reopening a session does not restore them.

## 6. AI Lab and exports

When you are on the clock and **Overview** is open, Picky can save the current Top 5 shortlist in session state. After subsequent Sleeper selections, **AI Lab** checks which candidates were taken before your next estimated selection. Export these observed outcomes with **Export observed decisions CSV**.

**Retrospective ADP replay** applies the current ADP table to already-made draft picks. This is a proxy with potential hindsight bias, not a historical replay of original projections or actual NBA fantasy-point outcomes. Its CSV is also exportable.

## 7. Common problems

| Symptom | What to check |
| --- | --- |
| **Cannot connect to Sleeper** | Check draft URL/ID, NBA sport, Sleeper API availability, and league visibility. |
| **My Team is empty / no turn detected** | Select the correct Sleeper username, user ID, or team in Settings. Confirm Sleeper has draft-order/team ownership data. |
| **Rankings seem thin or no ADP appears** | External ADP may be unavailable or players may fail name matching; upload your own CSV or use the fallback search order. |
| **CSV upload fails or rows disappear** | Use the supported identifier/value headers, valid numeric cells, and IDs/names matching Sleeper players. |
| **Lock-In model inactive** | Supply league-scored FPPG, variation, games per week, and availability for compared players. ADP alone is insufficient. |
| **No AI controls / research errors** | Confirm the owner set both secrets, you selected a team, and you unlocked Scout. Check OpenAI quota and connectivity. |
| **Research has no cited findings** | Treat the card as unverified. Follow source links manually; retrying research may create another charge. |
| **App is sleeping or appears stale** | Wake the Streamlit deployment, keep the tab active, and use **Check Sleeper now** on Overview/Draft Board. |
| **Player portrait missing** | Sleeper's external image CDN might lack an image; Picky should show initials as the fallback. |

For deployment, source modules, cache durations, and test commands, see the [Developer Guide](DEVELOPER_GUIDE.md).
