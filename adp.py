"""Hashtag Basketball ADP (Yahoo, ESPN, Fantrax) as a draft baseline."""

import re

import pandas as pd
import requests

from recommend import name_parts

ADP_URL = 'https://hashtagbasketball.com/fantasy-basketball-adp'
ROW_PATTERN = re.compile(
    r"<tr data-madp='([^']*)' data-yadp='([^']*)' data-eadp='([^']*)' data-fadp='([^']*)'>"
    r"\s*<td><a class=\"d-none d-sm-inline\" href='([^']*)'[^>]*>([^<]+)</a>",
    re.IGNORECASE,
)


def _number(value):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return number


def match_key(name):
    parts = name_parts(name)
    collapsed = []
    initials = ''
    for part in parts:
        if len(part) == 1:
            initials += part
            continue
        if initials:
            collapsed.append(initials)
            initials = ''
        collapsed.append(part)
    if initials:
        collapsed.append(initials)
    return ' '.join(collapsed)


def fetch_adp_rows():
    response = requests.get(ADP_URL, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    response.encoding = 'utf-8'
    html = response.text
    updated = ''
    stamp = re.search(r'Updated:\s*(?:</strong>\s*)?([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})', html)
    if stamp:
        updated = stamp.group(1).strip()
    players = []
    for blend, yahoo, espn, fantrax, href, name in ROW_PATTERN.findall(html):
        blend_adp = _number(blend)
        yahoo_adp = _number(yahoo)
        espn_adp = _number(espn)
        fantrax_adp = _number(fantrax)
        if blend_adp is None:
            present = [value for value in (yahoo_adp, espn_adp, fantrax_adp) if value is not None]
            blend_adp = sum(present) / len(present) if present else None
        if blend_adp is None:
            continue
        path = href if href.startswith('http') else f'https://hashtagbasketball.com{href}'
        players.append({
            'name': name.strip(),
            'blend_adp': blend_adp,
            'yahoo_adp': yahoo_adp,
            'espn_adp': espn_adp,
            'fantrax_adp': fantrax_adp,
            'adp_url': path,
        })
    if not players:
        raise ValueError('Hashtag Basketball ADP table was empty.')
    return {'updated': updated, 'source': ADP_URL, 'players': players}


def _player_priority(meta):
    status = str(meta.get('status') or '').upper()
    active = 2 if status in ('ACT', 'ACTIVE') else 1 if meta.get('team') else 0
    try:
        rank = int(meta.get('search_rank'))
    except (TypeError, ValueError):
        rank = 9999
    return (active, -rank)


def _sleeper_index(players):
    best = {}
    by_last = {}
    for pid, meta in (players or {}).items():
        if not isinstance(meta, dict):
            continue
        name = meta.get('full_name') or ' '.join(filter(None, [meta.get('first_name'), meta.get('last_name')]))
        if 'DUPLICATE' in name.upper():
            continue
        key = match_key(name)
        parts = key.split()
        if len(parts) < 2:
            continue
        pid = str(pid)
        current = best.get(key)
        if current is None or _player_priority(meta) > _player_priority(current[1]):
            best[key] = (pid, meta)
        by_last.setdefault(parts[-1], []).append((pid, parts[0], meta))
    return {key: pid for key, (pid, _meta) in best.items()}, by_last


def _loose_id(name, by_last):
    parts = match_key(name).split()
    if len(parts) < 2:
        return None
    first, last = parts[0], parts[-1]
    hits = []
    for pid, sleeper_first, meta in by_last.get(last, []):
        short, long = sorted((sleeper_first, first), key=len)
        if len(short) >= 3 and long.startswith(short):
            hits.append((pid, meta))
    if not hits:
        return None
    hits.sort(key=lambda item: _player_priority(item[1]), reverse=True)
    if len(hits) == 1 or _player_priority(hits[0][1]) > _player_priority(hits[1][1]):
        return hits[0][0]
    return None


def match_adp(adp_players, sleeper_players):
    index, by_last = _sleeper_index(sleeper_players)
    rows = []
    seen = set()
    for player in adp_players or []:
        pid = index.get(match_key(player.get('name'))) or _loose_id(player.get('name'), by_last)
        if not pid or pid in seen:
            continue
        seen.add(pid)
        blend = float(player['blend_adp'])
        rows.append({
            'player_id': pid,
            'base': 1000 - blend,
            'metric_label': 'Hashtag Basketball blend ADP',
            'blend_adp': blend,
            'yahoo_adp': player.get('yahoo_adp'),
            'espn_adp': player.get('espn_adp'),
            'fantrax_adp': player.get('fantrax_adp'),
            'adp_url': player.get('adp_url') or '',
            'upside_fppg': float('nan'),
            'floor_fppg': float('nan'),
            'games_per_week': float('nan'),
            'availability_pct': float('nan'),
        })
    return pd.DataFrame(rows)
