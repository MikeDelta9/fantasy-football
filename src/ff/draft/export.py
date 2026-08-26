"""Assemble the draft board dataset the HTML page runs on.

Everything that cannot change during a draft is computed here -- league points,
the consensus baseline, the gap between them, expert rank and spread. Anything
that depends on who is still on the board (replacement level, VORP, tiers,
availability, surplus) is computed in the page itself, because those move every
time a pick comes off.
"""

from __future__ import annotations

import json
from typing import Any

from .score import Player


def to_rows(players: list[Player]) -> list[dict[str, Any]]:
    rows = []
    for p in players:
        if p.league_points <= 0:
            continue
        rows.append(
            {
                "name": p.name,
                "pos": p.position,
                "team": p.team,
                "pts": round(p.league_points, 1),
                "cons": round(p.consensus_points, 1),
                "delta": round(p.delta, 1),
                "ecr": p.ecr,
                "std": p.ecr_std,
                "bye": int(p.bye) if str(p.bye or "").isdigit() else None,
                "note": p.notes[0] if p.notes else None,
            }
        )
    rows.sort(key=lambda r: -r["pts"])
    return rows


def merge_rankings(players: list[Player], rankings: dict[str, Any]) -> int:
    """Attach consensus rank, expert spread and bye week. Returns match count."""
    idx = {r["player_name"]: r for r in rankings.get("players", [])}
    # Defenses are named differently between the two endpoints.
    alt = {r["player_name"].split()[-1]: r for r in rankings.get("players", [])}
    hits = 0
    for p in players:
        r = idx.get(p.name) or alt.get(p.name.split()[-1])
        if not r:
            continue
        hits += 1
        p.ecr = float(r["rank_ecr"]) if r.get("rank_ecr") else None
        p.ecr_std = float(r["rank_std"]) if r.get("rank_std") else None
        p.fp_tier = r.get("tier")
        p.bye = r.get("player_bye_week")
        p.yahoo_id = r.get("player_yahoo_id")
    return hits


def render(rows: list[dict[str, Any]], template: str, meta: dict[str, Any]) -> str:
    payload = json.dumps({"players": rows, "meta": meta}, separators=(",", ":"))
    return template.replace("/*__DATA__*/", payload)
