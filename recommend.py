"""Best-pick scoring from roster need, available players, and headline tone."""

import re
import unicodedata

import pandas as pd

HARD_STATUS = {'OUT', 'DOUBTFUL', 'IR', 'INJURED', 'SUSPENDED'}
SOFT_STATUS = {'QUESTIONABLE', 'GTD', 'DTD'}
FLEX_SLOTS = {'UTIL', 'UTILITY', 'FLEX', 'BN', 'BENCH'}
BROAD_SLOTS = {'G', 'F'}
ROLES = ('PG', 'SG', 'SF', 'PF', 'C')
SUFFIXES = {'jr', 'sr', 'ii', 'iii', 'iv', 'v'}
PRECEDING_OK = {
    'the', 'and', 'but', 'for', 'with', 'from', 'after', 'before', 'over', 'into',
    'vs', 'at', 'in', 'on', 'to', 'a', 'of', 'out', 'ruled', 'remains', 'listed',
    'warriors', 'lakers', 'celtics', 'nets', 'knicks', 'sixers', 'raptors', 'bulls',
    'cavaliers', 'cavs', 'pistons', 'pacers', 'bucks', 'hawks', 'hornets', 'heat',
    'magic', 'wizards', 'nuggets', 'timberwolves', 'wolves', 'thunder', 'blazers',
    'jazz', 'suns', 'kings', 'clippers', 'mavericks', 'mavs', 'rockets', 'grizzlies',
    'pelicans', 'spurs', 'nba', 'espn',
}

NEG_PHRASES = (
    'ruled out', 'out indefinitely', 'season ending', 'will not play', 'wont play',
    'will miss', 'sidelined', 'torn', 'surgery', 'fractured', 'fracture',
    'suspended', 'not starting', 'remains out', 'listed out', 'is out', 'sits out',
    'sit out', 'healthy scratch', 'out for the season', 'acl', 'achilles',
    'to miss', 'misses', 'downgraded to out',
)
CAUTION_PHRASES = (
    'questionable', 'day to day', 'game time decision', 'gtd', 'doubtful',
    'minutes restriction', 'load management', 'probable', 'resting', 'will rest',
    'limited minutes',
)
POS_PHRASES = (
    'cleared', 'will play', 'expected to play', 'available to play', 'will start',
    'named starter', 'in the starting lineup', 'activated', 'full participant',
    'no injury', 'healthy',
)
TONE_RANK = {'negative': 0, 'caution': 1, 'positive': 2, 'neutral': 3}
TONE_LABEL = {
    'negative': 'Negative headline',
    'caution': 'Caution headline',
    'positive': 'Positive headline',
    'neutral': 'Mentioned',
    'none': '—',
}


def news_text(value):
    value = unicodedata.normalize('NFKD', str(value or ''))
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace('’', "'")
    value = re.sub(r"['’]", '', value)
    value = re.sub(r'[-–—/]', ' ', value)
    value = re.sub(r'[^a-z0-9 ]', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def phrase_in(text, phrase):
    return f' {news_text(phrase)} ' in f' {text} '


def classify_headline(title):
    text = news_text(title)
    if any(phrase_in(text, phrase) for phrase in NEG_PHRASES):
        return 'negative'
    non_injury_caution = tuple(phrase for phrase in CAUTION_PHRASES if phrase not in ('injury', 'injured'))
    if any(phrase_in(text, phrase) for phrase in non_injury_caution):
        return 'caution'
    if phrase_in(text, 'no injury'):
        return 'positive'
    if phrase_in(text, 'injury') or phrase_in(text, 'injured'):
        return 'caution'
    if any(phrase_in(text, phrase) for phrase in POS_PHRASES):
        return 'positive'
    return 'neutral'


def name_parts(name):
    return [part for part in news_text(name).split() if part and part not in SUFFIXES]


def unique_last_names(names):
    counts = {}
    for name in names:
        parts = name_parts(name)
        if len(parts) < 2:
            continue
        counts[parts[-1]] = counts.get(parts[-1], 0) + 1
    return {last for last, count in counts.items() if count == 1 and len(last) >= 5}


def title_mentions(title, name, unique_last=()):
    parts = name_parts(name)
    if len(parts) < 2:
        return False
    text = news_text(title)
    words = set(text.split())
    full = ' '.join(parts)
    if full in text:
        return True
    if parts[0] in words and parts[-1] in words:
        return True
    if parts[-1] not in unique_last:
        return False
    tokens = text.split()
    for index, token in enumerate(tokens):
        if token != parts[-1]:
            continue
        previous = tokens[index - 1] if index else ''
        if not previous or previous == parts[0] or previous in PRECEDING_OK:
            return True
    return False


def headline_clauses(title):
    parts = re.split(r'\s*(?:;|\||,|\band\b)\s*', str(title or ''), flags=re.IGNORECASE)
    parts = [part.strip() for part in parts if part and part.strip()]
    return parts or [str(title or '')]


def tone_for_player(title, name, unique_last=()):
    if not title_mentions(title, name, unique_last):
        return None
    mentioned = [clause for clause in headline_clauses(title) if title_mentions(clause, name, unique_last)]
    if mentioned:
        tones = [classify_headline(clause) for clause in mentioned]
        best = min(tones, key=lambda tone: TONE_RANK[tone])
        if best != 'neutral':
            return best
    if not re.search(r',|\band\b', str(title or ''), flags=re.IGNORECASE):
        return classify_headline(title)
    return 'neutral'


def summarize_news(name, articles, unique_last=()):
    hits = []
    seen = set()
    for article in articles or []:
        title = article.get('title', '')
        tone = tone_for_player(title, name, unique_last)
        if tone is None:
            continue
        key = news_text(title)[:90]
        if key in seen:
            continue
        seen.add(key)
        hits.append({
            'title': title,
            'link': article.get('link', ''),
            'source': article.get('source', ''),
            'published': article.get('published', ''),
            'tone': tone,
        })
    if not hits:
        return 'none', []
    tones = [hit['tone'] for hit in hits]
    if 'negative' in tones:
        tone = 'negative'
    elif 'caution' in tones:
        tone = 'caution'
    elif 'positive' in tones:
        tone = 'positive'
    else:
        tone = 'neutral'
    return tone, hits


def positions_of(meta):
    if not isinstance(meta, dict):
        return []
    return meta.get('fantasy_positions') or ([meta.get('position')] if meta.get('position') else [])


def slot_compatible(slot, positions):
    slot_name = str(slot).upper()
    owned = {str(pos).upper() for pos in positions}
    if slot_name in FLEX_SLOTS:
        return True
    if slot_name == 'G':
        return bool(owned & {'PG', 'SG', 'G'})
    if slot_name == 'F':
        return bool(owned & {'SF', 'PF', 'F'})
    return slot_name in owned


def remaining_slots(roster_ids, players, slots):
    remaining = list(slots)
    ordered = sorted(
        [str(pid) for pid in roster_ids],
        key=lambda pid: sum(slot_compatible(slot, positions_of(players.get(pid, {}))) for slot in slots),
    )
    for pid in ordered:
        pos = positions_of(players.get(pid, {}))
        options = [(index, slot) for index, slot in enumerate(remaining) if slot_compatible(slot, pos)]
        if not options:
            continue
        index, _slot = min(
            options,
            key=lambda item: (str(item[1]).upper() in FLEX_SLOTS, str(item[1]).upper() in BROAD_SLOTS),
        )
        remaining.pop(index)
    return remaining


def specific_roles(positions):
    return [str(pos).upper() for pos in positions if str(pos).upper() in ROLES]


def role_counts(roster_ids, players):
    counts = {role: 0 for role in ROLES}
    for pid in roster_ids:
        roles = specific_roles(positions_of(players.get(str(pid), {})))
        if roles:
            counts[roles[0]] += 1
    return counts


def role_targets(slots):
    targets = {role: 0 for role in ROLES}
    for slot in slots:
        name = str(slot).upper()
        if name in targets:
            targets[name] += 1
        elif name == 'G':
            targets['PG'] += 0.5
            targets['SG'] += 0.5
        elif name == 'F':
            targets['SF'] += 0.5
            targets['PF'] += 0.5
    return targets


def scarcest_role(roles, counts, targets):
    def scarcity(role):
        return counts.get(role, 0) / max(targets.get(role, 0), 1)
    return min(roles, key=scarcity)


def need_rank_delta(roles, counts, targets, has_user):
    if not has_user or not roles:
        return 0
    role = scarcest_role(roles, counts, targets)
    ratio = counts.get(role, 0) / max(targets.get(role, 0), 1)
    if ratio == 0:
        return -18
    if ratio < 0.75:
        return -12
    if ratio < 1:
        return -6
    if ratio < 1.5:
        return 6
    return 12


def need_score_multiplier(roles, counts, targets, has_user, category, fit_bonus):
    if not has_user:
        return roster_penalty(category, 'projection', fit_bonus)
    if not roles:
        return 1.0
    role = scarcest_role(roles, counts, targets)
    ratio = counts.get(role, 0) / max(targets.get(role, 0), 1)
    if ratio == 0:
        return 1 + fit_bonus / 100 * 2
    if ratio < 1:
        return 1 + fit_bonus / 100
    if ratio < 1.5:
        return 1.0
    return 0.9


def need_note(roles, counts, targets, has_user, fallback):
    if not has_user or not roles:
        return fallback
    role = scarcest_role(roles, counts, targets)
    have = int(counts.get(role, 0))
    target = targets.get(role, 0)
    if have == 0:
        return f'You have no {role} yet.'
    if target and have < target:
        return f'You have {have} {role}, and that role is not full.'
    return f'You already have {have} {role}. Thinner roles rank higher.'


def fit_category(pid, roster_ids, players, slots, has_user):
    if not has_user:
        return 'unknown', 'Select your Sleeper account in the sidebar so your roster can change the pick.'
    remaining = remaining_slots(roster_ids, players, slots)
    pos = positions_of(players.get(str(pid), {}))
    matching = [slot for slot in remaining if slot_compatible(slot, pos)]
    specific = [slot for slot in matching if str(slot).upper() not in FLEX_SLOTS and str(slot).upper() not in BROAD_SLOTS]
    broad = [slot for slot in matching if str(slot).upper() in BROAD_SLOTS]
    flex = [slot for slot in matching if str(slot).upper() in FLEX_SLOTS]
    if specific:
        return 'specific', f'Fills your open {specific[0]} slot.'
    if broad:
        return 'broad', f'Fills your open {broad[0]} slot.'
    if flex:
        return 'flex', 'Only a utility slot is open for this position.'
    if not pos:
        return 'none', 'No position is listed for this player.'
    return 'none', 'Your starter slots for this position are already filled.'


def search_rank_pool(players, picked_ids):
    rows = []
    for pid, meta in (players or {}).items():
        if not isinstance(meta, dict):
            continue
        pid = str(pid)
        if pid in picked_ids:
            continue
        if str(meta.get('status') or '').lower() == 'retired':
            continue
        if meta.get('active') is False and not meta.get('team'):
            continue
        try:
            rank = int(meta.get('search_rank'))
        except (TypeError, ValueError):
            continue
        if rank <= 0 or rank > 400:
            continue
        name = meta.get('full_name') or ' '.join(filter(None, [meta.get('first_name'), meta.get('last_name')]))
        if not name:
            continue
        rows.append({
            'player_id': pid,
            'base': float(1000 - rank),
            'metric_label': 'Sleeper search rank',
            'search_rank': rank,
            'upside_fppg': float('nan'),
            'floor_fppg': float('nan'),
            'games_per_week': float('nan'),
            'availability_pct': float('nan'),
        })
    return pd.DataFrame(rows)


def projection_base(row, upside_weight, safety_weight):
    base = float(row.base)
    label = str(row.metric_label)
    has_range = pd.notna(row.upside_fppg) and pd.notna(row.floor_fppg)
    if has_range and label not in ('Rank proxy (not points)', 'Sleeper search rank'):
        upside = upside_weight / 100
        safety = safety_weight / 100
        base = (1 - upside - safety) * base + upside * float(row.upside_fppg) + safety * float(row.floor_fppg)
    if pd.notna(row.availability_pct):
        base *= max(0, min(1, float(row.availability_pct) / 100))
    if pd.notna(row.games_per_week):
        base *= 1 + 0.03 * max(-2, min(3, float(row.games_per_week) - 3))
    return base


def news_penalty(tone, hits, origin):
    count = sum(1 for hit in hits if hit['tone'] == tone)
    if origin in ('search_rank', 'adp'):
        if tone == 'negative':
            return 50 + (20 if count > 1 else 0)
        if tone == 'caution':
            return 18 + (8 if count > 1 else 0)
        if tone == 'positive':
            return -10
        return 0
    if tone == 'negative':
        return 0.74 if count > 1 else 0.82
    if tone == 'caution':
        return 0.90 if count > 1 else 0.93
    if tone == 'positive':
        return 1.04
    return 1.0


def roster_penalty(category, origin, fit_bonus):
    if origin in ('search_rank', 'adp'):
        return {'specific': -15, 'broad': -8, 'flex': -4}.get(category, 0)
    if category == 'specific':
        return 1 + fit_bonus / 100
    if category == 'broad':
        return 1 + fit_bonus / 100 * 0.7
    if category == 'flex':
        return 1 + fit_bonus / 100 * 0.4
    return 1.0


def optional_number(row, name):
    value = getattr(row, name, None)
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def source_display(row, origin):
    if origin == 'adp':
        return round(float(row.blend_adp), 1)
    if origin == 'search_rank':
        return int(row.search_rank)
    return round(float(row.base), 2)


def player_name_from(pid, meta):
    if not isinstance(meta, dict):
        return str(pid)
    return meta.get('full_name') or ' '.join(filter(None, [meta.get('first_name'), meta.get('last_name')])) or str(pid)


def candidate_rows(ranking, players, picked_ids, adp_frame=None):
    if ranking is not None and not ranking.empty:
        frame = ranking[~ranking.player_id.astype(str).isin(picked_ids)].copy()
        return frame, 'projection'
    if adp_frame is not None and not adp_frame.empty:
        frame = adp_frame[~adp_frame.player_id.astype(str).isin(picked_ids)].copy()
        return frame, 'adp'
    return search_rank_pool(players, picked_ids), 'search_rank'


def score_candidates(frame, origin, players, roster_ids, slots, articles, has_user, upside_weight, safety_weight, risk_weight, fit_bonus):
    prepared = []
    for row in frame.itertuples(index=False):
        pid = str(row.player_id)
        meta = players.get(pid, {}) if isinstance(players, dict) else {}
        prepared.append((row, pid, meta, player_name_from(pid, meta)))
    unique_last = unique_last_names(name for _row, _pid, _meta, name in prepared)
    counts = role_counts(roster_ids, players) if has_user else {role: 0 for role in ROLES}
    targets = role_targets(slots)
    scored = []
    for row, pid, meta, name in prepared:
        injury = str(meta.get('injury_status') or '').upper()
        roles = specific_roles(positions_of(meta))
        category, roster_note = fit_category(pid, roster_ids, players, slots, has_user)
        roster_note = need_note(roles, counts, targets, has_user, roster_note)
        tone, hits = summarize_news(name, articles, unique_last)
        hard = injury in HARD_STATUS or tone == 'negative'
        if origin in ('search_rank', 'adp'):
            rank_delta = 0
            if injury in HARD_STATUS:
                rank_delta += 40
            elif injury in SOFT_STATUS:
                rank_delta += 12
            rank_delta += news_penalty(tone, hits, origin)
            rank_delta += need_rank_delta(roles, counts, targets, has_user)
            score = float(row.base) - rank_delta
        else:
            score = projection_base(row, upside_weight, safety_weight)
            if injury in HARD_STATUS:
                score *= 1 - risk_weight / 100
            elif injury in SOFT_STATUS:
                score *= 1 - risk_weight / 200
            score *= news_penalty(tone, hits, origin)
            score *= need_score_multiplier(roles, counts, targets, has_user, category, fit_bonus)
        scored.append({
            'player_id': pid,
            'player': name,
            'position': ', '.join(positions_of(meta)),
            'team': meta.get('team') or '',
            'injury': injury or '—',
            'injury_hard': injury in HARD_STATUS,
            'baseline': source_display(row, origin),
            'metric_label': row.metric_label,
            'roster': roster_note,
            'fit': category,
            'media': TONE_LABEL.get(tone, '—'),
            'tone': tone,
            'hits': hits,
            'hard_negative': hard,
            'score': score,
            'blend_adp': optional_number(row, 'blend_adp'),
            'yahoo_adp': optional_number(row, 'yahoo_adp'),
            'espn_adp': optional_number(row, 'espn_adp'),
            'fantrax_adp': optional_number(row, 'fantrax_adp'),
            'adp_url': getattr(row, 'adp_url', '') or '',
            'roles': roles,
            'role_have': dict(counts) if has_user else {},
        })
    scored.sort(key=lambda item: item['score'], reverse=True)
    return scored


def select_recommendation(rows, limit=5):
    if not rows:
        return None, [], []
    eligible = [row for row in rows if not row['hard_negative']] or rows

    def talent(row):
        adp = row.get('blend_adp')
        if adp is not None:
            return adp
        return 1000 - row['score']

    pool = sorted(eligible, key=talent)[:50]
    role_have = pool[0].get('role_have') or {}
    present = [role for role in ROLES if any(role in row.get('roles', []) for row in pool)]

    def best_at(role, used):
        matches = [row for row in pool if role in row.get('roles', []) and row['player_id'] not in used]
        return max(matches, key=lambda row: row['score']) if matches else None

    def role_sort(role):
        best = best_at(role, set())
        return (role_have.get(role, 0), -(best['score'] if best else 0))

    present.sort(key=role_sort)
    options = []
    used = set()
    for _pass in range(3):
        if len(options) >= limit:
            break
        thinnest = role_have.get(present[0], 0) if present else 0
        for role in present:
            if len(options) >= limit:
                break
            if _pass and role_have.get(role, 0) > thinnest:
                continue
            match = best_at(role, used)
            if not match:
                continue
            options.append({**match, 'variety_role': role})
            used.add(match['player_id'])
    if not options:
        options = [rows[0]]
    chosen = options[0]
    skipped = [row for row in rows if row['score'] > chosen['score'] and row['player_id'] != chosen['player_id']][:3]
    return chosen, options, skipped


def adp_summary(row):
    parts = []
    if row.get('blend_adp') is not None:
        parts.append(f"blend {row['blend_adp']:.1f}")
    for label, key in (('ESPN', 'espn_adp'), ('Yahoo', 'yahoo_adp'), ('Fantrax', 'fantrax_adp')):
        if row.get(key) is not None:
            parts.append(f'{label} {row[key]:.1f}')
    return ', '.join(parts)


def value_reason(row, origin):
    if origin == 'adp':
        return (
            f"Still available. Baseline is Hashtag Basketball ADP ({adp_summary(row)}). "
            'Lower ADP means drafters take the player earlier. The blend averages Yahoo, ESPN, and Fantrax.'
        )
    if origin == 'search_rank':
        return (
            f"Still available. Baseline is Sleeper search rank #{row['baseline']} "
            '(a lower rank means the player is more relevant). This is not a fantasy-point forecast.'
        )
    if row['metric_label'] == 'Rank proxy (not points)':
        return f"Still available. Baseline is your imported rank list (source value {row['baseline']})."
    return (
        f"Still available. Baseline projection is {row['baseline']} fantasy points per game, "
        f"adjusted to {row['score']:.1f} after roster fit, injury status, and headlines."
    )


def media_reason(row, articles_loaded):
    if not articles_loaded:
        return 'News feeds did not load, so headlines did not change this pick.'
    if row['tone'] == 'none':
        return 'No current ESPN or Google News headline names this player, so media did not move them.'
    if row['tone'] == 'negative':
        return 'Headlines describe this player as out or seriously limited, which lowered them.'
    if row['tone'] == 'caution':
        return 'Headlines urge caution (questionable, limited, or day-to-day), which lowered them slightly.'
    if row['tone'] == 'positive':
        return 'Headlines lean positive (healthy, starting, or cleared), which raised them slightly.'
    return 'Headlines mention this player, but they do not clearly say the player is out, limited, or confirmed to play.'


def injury_reason(row):
    if row['injury'] == '—':
        return ''
    if row['injury_hard']:
        return f"Sleeper lists this player as {row['injury']}."
    if row['injury'] in SOFT_STATUS:
        return f"Sleeper lists this player as {row['injury']}, so the score includes a smaller injury penalty."
    return f"Sleeper injury tag: {row['injury']}."


def with_reasons(row, origin, articles):
    reasons = [value_reason(row, origin), row['roster'], media_reason(row, bool(articles))]
    injury = injury_reason(row)
    if injury:
        reasons.append(injury)
    return {**row, 'reasons': reasons}


def pick_sleeper(rows, teams):
    healthy = [row for row in rows if not row['hard_negative']]
    if not healthy:
        return None
    adps = [row['blend_adp'] for row in healthy if row.get('blend_adp') is not None]
    if not adps:
        return None
    best_adp = min(adps)
    later_than = max(best_adp + max(teams, 1), max(teams, 1) * 4)
    ceiling = later_than + max(teams, 1) * 6
    ranked = []
    for row in healthy:
        blend = row.get('blend_adp')
        if blend is None or blend < later_than or blend > ceiling:
            continue
        platform_adps = []
        for label, key in (('ESPN', 'espn_adp'), ('Yahoo', 'yahoo_adp'), ('Fantrax', 'fantrax_adp')):
            value = row.get(key)
            if value is not None:
                platform_adps.append((label, value))
        edge, source, source_adp = 0, '', None
        if len(platform_adps) >= 2 and max(value for _label, value in platform_adps) - min(value for _label, value in platform_adps) <= 50:
            source, source_adp = min(platform_adps, key=lambda item: item[1])
            edge = blend - source_adp
        positive = row['tone'] == 'positive'
        if not positive and edge < 8:
            continue
        fit_bonus = {'specific': 15, 'broad': 8, 'flex': 4}.get(row['fit'], 0)
        sleeper_score = edge + (25 if positive else 0) + fit_bonus - (blend - later_than) * 0.2
        ranked.append((sleeper_score, edge, source, source_adp, row))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0], reverse=True)
    _score, edge, source, source_adp, row = ranked[0]
    reasons = [
        f"Blend ADP {row['blend_adp']:.1f} is later than the best player still available, inside the next six rounds of sleeper range.",
    ]
    if row['tone'] == 'positive':
        reasons.append('Headlines lean positive (healthy, starting, or cleared).')
    if edge >= 8 and source_adp is not None:
        reasons.append(
            f"{source} ADP {source_adp:.1f} is {edge:.0f} spots earlier than the Yahoo/ESPN/Fantrax blend."
        )
    reasons.append(row['roster'])
    return {**row, 'reasons': reasons, 'espn_edge': edge}


def pick_fade(rows, skipped):
    row = None
    if skipped:
        row = skipped[0]
    else:
        healthy = [item for item in rows if not item['hard_negative'] and item.get('blend_adp') is not None]
        if not healthy:
            return None
        best_adp = min(item['blend_adp'] for item in healthy)
        flagged = [
            item for item in rows
            if item['hard_negative'] and item.get('blend_adp') is not None and item['blend_adp'] <= best_adp + 8
        ]
        if not flagged:
            return None
        flagged.sort(key=lambda item: item['blend_adp'])
        row = flagged[0]
    reasons = []
    if row.get('blend_adp') is not None:
        reasons.append(f"Consensus blend ADP is {row['blend_adp']:.1f}, so this name is still near the top of the available board.")
    if row.get('injury_hard'):
        reasons.append(f"Sleeper lists this player as {row['injury']}.")
    if row['tone'] == 'negative':
        reasons.append('A headline says this player is out or seriously limited.')
    elif row['tone'] == 'caution':
        reasons.append('Headlines urge caution, so this is a worse click than the ADP alone suggests.')
    elif not row.get('injury_hard'):
        reasons.append('Injury status or a headline makes this a player to pass on for now.')
    reasons.append(row['roster'])
    return {**row, 'reasons': reasons}


def build_recommendations(ranking, players, picked_ids, roster_ids, slots, articles, has_user, upside_weight, safety_weight, risk_weight, fit_bonus, adp_frame=None, teams=12):
    frame, origin = candidate_rows(ranking, players, picked_ids, adp_frame)
    open_slots = [str(slot) for slot in remaining_slots(roster_ids, players, slots)] if has_user else []
    empty = {
        'rows': [],
        'recommended': None,
        'options': [],
        'sleeper': None,
        'fade': None,
        'skipped': [],
        'origin': origin,
        'open_slots': open_slots,
        'reluctant': False,
        'articles_loaded': bool(articles),
    }
    if frame is None or frame.empty:
        return empty
    rows = score_candidates(
        frame, origin, players, roster_ids, slots, articles, has_user,
        upside_weight, safety_weight, risk_weight, fit_bonus,
    )
    chosen, options, skipped = select_recommendation(rows)
    sleeper = pick_sleeper(rows, teams or 12) if origin == 'adp' else None
    fade = pick_fade(rows, skipped) if origin == 'adp' else None
    if sleeper and fade and sleeper['player_id'] == fade['player_id']:
        sleeper = None
    if sleeper and chosen and sleeper['player_id'] == chosen['player_id']:
        sleeper = None
    if chosen:
        chosen = with_reasons(chosen, origin, articles)
    return {
        'rows': rows,
        'recommended': chosen,
        'options': options,
        'sleeper': sleeper,
        'fade': fade,
        'skipped': skipped,
        'origin': origin,
        'open_slots': open_slots,
        'reluctant': bool(chosen and chosen['hard_negative']),
        'articles_loaded': bool(articles),
    }
