"""Score FantasyPros projections under *this* league's rules.

FantasyPros publishes `points_half` against a generic half-PPR profile: 4-point
passing touchdowns, -1 interceptions, and a forced-fumble credit for defenses.
This league pays 6 and -2 and has no forced-fumble category at all, so the
consensus number is wrong here in a way that scales with passing volume. The
gap between the two is the whole point of this module.

Kickers are the one position we cannot reprice: FantasyPros projects a single
`fg` count with no distance split, while the league pays 3/3/3/4/5 by distance.
See KICKER_FG_VALUE.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..scoring.mapping import CANON

# Blended value of a made field goal, weighted by a typical NFL distance
# distribution (~20% under 30, ~28% 30-39, ~30% 40-49, ~22% 50+) against this
# league's 3/3/3/4/5 tiers. An approximation, and flagged as one: kicker values
# carry no custom-scoring edge and should not drive a draft decision.
KICKER_FG_VALUE = 3.74

_SCORED = [c for c in CANON if c.fantasypros]

POSITIONS = ["QB", "RB", "WR", "TE", "K", "DST"]


@dataclass
class Player:
    name: str
    position: str
    team: str
    fp_id: int
    stats: dict[str, float]
    league_points: float = 0.0
    consensus_points: float = 0.0
    # filled in from the rankings endpoint
    ecr: float | None = None
    ecr_std: float | None = None
    fp_tier: int | None = None
    bye: int | None = None
    yahoo_id: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def delta(self) -> float:
        """Points this league pays that consensus scoring does not (or vice versa)."""
        return self.league_points - self.consensus_points


def league_points(stats: dict[str, Any], position: str, scoring: dict[str, float]) -> float:
    """Apply the league's scoring table to one FantasyPros projection."""
    if position == "K":
        return (
            float(stats.get("xpt", 0) or 0) * scoring.get("xpm", 1.0)
            + float(stats.get("fg", 0) or 0) * KICKER_FG_VALUE
        )

    total = 0.0
    for cat in _SCORED:
        value = scoring.get(cat.key)
        if not value:
            continue
        raw = stats.get(cat.fantasypros)
        if raw in (None, ""):
            continue
        total += float(raw) * value
    return total


def load_projections(client: Any, season: int, scoring: dict[str, float]) -> list[Player]:
    """Pull every position, score each player twice: league rules and consensus."""
    out: list[Player] = []
    for pos in POSITIONS:
        payload = client.projections(season, week="draft", position=pos, scoring="HALF")
        for row in payload.get("players", []):
            stats = row.get("stats") or {}
            p = Player(
                name=row.get("name", "?"),
                position=pos if pos != "DST" else "DEF",
                team=row.get("team_id", ""),
                fp_id=row.get("fpid") or row.get("mflid") or 0,
                stats=stats,
                consensus_points=float(stats.get("points_half") or 0),
            )
            p.league_points = league_points(stats, pos, scoring)
            if pos == "K":
                p.notes.append("kicker scoring approximated - no distance split available")
            out.append(p)
    return out


def load_league_scoring(snapshot: Path | None = None) -> dict[str, float]:
    """Canonical {category: points} for this league.

    Yahoo is the platform of record for 2026 and wins where the two disagree --
    interceptions are -2 here, not Sleeper's -1 (see _project/DECISIONS.md). So
    the Yahoo snapshot is the default source; scoring off Sleeper would silently
    misprice every quarterback.
    """
    from ..config import SNAPSHOTS
    from ..scoring.normalize import normalize_sleeper, normalize_yahoo_any

    if snapshot is None:
        yahoo = sorted(SNAPSHOTS.glob("yahoo-settings-*.json"))
        if not yahoo:
            raise SystemExit(
                "No Yahoo settings snapshot. Run: ff yahoo import-ui <scraped.json>"
            )
        snapshot = yahoo[-1]

    data = json.loads(snapshot.read_text())
    if "yahoo" in snapshot.name:
        return dict(normalize_yahoo_any(data).values)
    return dict(normalize_sleeper(data.get("scoring_settings", data)).values)
