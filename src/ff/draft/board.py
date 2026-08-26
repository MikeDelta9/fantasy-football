"""Turn scored projections into a draft board that makes a recommendation.

The board answers one question at pick time: *who should I take right now?*
Everything else -- tiers, deltas, availability -- exists to justify that answer
in a sentence you can read in ten seconds.

Deliberately NOT a re-implementation of FantasyPros' Draft Assistant. That tool
already ranks best-available under consensus. This one exists for the places
where consensus is wrong for this league, so its headline number is *surplus
over what you could still get next time*, not raw projected points.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

from .score import Player

TEAMS = 12
# One team's starting lineup. FLEX is filled from RB/WR/TE.
STARTERS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "K": 1, "DEF": 1}
FLEX_SLOTS = 1
FLEX_POSITIONS = ("RB", "WR", "TE")
BENCH = 7


@dataclass
class Candidate:
    player: Player
    vorp: float = 0.0
    tier: int = 0
    tier_last: bool = False          # last player in this tier at this position
    tier_drop: float = 0.0           # points lost by waiting for the next tier
    p_available_next: float = 1.0    # chance of surviving to your next pick
    surplus: float = 0.0             # vorp now minus expected vorp next turn
    reasons: list[str] = field(default_factory=list)


def replacement_levels(players: list[Player]) -> dict[str, float]:
    """Points of the first player at each position who will NOT start anywhere.

    Flex demand is allocated by who actually fills flex slots rather than by a
    fixed assumption, so a league where tight ends never flex gets a tight-end
    replacement level that reflects that.
    """
    by_pos: dict[str, list[Player]] = {}
    for p in players:
        by_pos.setdefault(p.position, []).append(p)
    for lst in by_pos.values():
        lst.sort(key=lambda p: -p.league_points)

    demand = {pos: n * TEAMS for pos, n in STARTERS.items()}

    # Everyone past their position's dedicated starters competes for flex.
    pool: list[Player] = []
    for pos in FLEX_POSITIONS:
        pool.extend(by_pos.get(pos, [])[demand.get(pos, 0):])
    pool.sort(key=lambda p: -p.league_points)
    for p in pool[: FLEX_SLOTS * TEAMS]:
        demand[p.position] = demand.get(p.position, 0) + 1

    levels: dict[str, float] = {}
    for pos, lst in by_pos.items():
        idx = min(demand.get(pos, len(lst)), len(lst) - 1)
        levels[pos] = lst[idx].league_points if lst else 0.0
    return levels


def assign_tiers(cands: list[Candidate]) -> None:
    """Break a position into tiers wherever the drop between players is unusual.

    Tier breaks are the fastest signal on a draft clock: 'last one before a
    16-point cliff' decides a pick faster than any ranking does.
    """
    for pos in {c.player.position for c in cands}:
        group = sorted(
            [c for c in cands if c.player.position == pos], key=lambda c: -c.vorp
        )
        if len(group) < 3:
            for i, c in enumerate(group):
                c.tier = 1
            continue

        gaps = [group[i].vorp - group[i + 1].vorp for i in range(len(group) - 1)]
        cutoff = statistics.mean(gaps) + statistics.pstdev(gaps)
        tier = 1
        for i, c in enumerate(group):
            c.tier = tier
            if i < len(gaps) and gaps[i] >= cutoff and gaps[i] > 0:
                c.tier_last = True
                c.tier_drop = gaps[i]
                tier += 1
        # the final player of each tier that did not trigger a break
        for i in range(len(group) - 1):
            if group[i].tier != group[i + 1].tier and not group[i].tier_last:
                group[i].tier_last = True
                group[i].tier_drop = group[i].vorp - group[i + 1].vorp


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def availability(player: Player, next_pick: int, default_std: float = 12.0) -> float:
    """P(this player is still there at `next_pick`), from expert rank spread.

    Uses the consensus rank as the centre and the disagreement among experts as
    the spread. Wide disagreement means a genuinely uncertain draft slot, which
    is exactly when 'he'll probably last' goes wrong.
    """
    if player.ecr is None:
        return 0.5
    std = player.ecr_std if player.ecr_std and player.ecr_std > 0 else default_std
    std = max(float(std) * 3.0, 4.0)  # rank_std is per-expert; draft spread is wider
    return 1.0 - _phi((next_pick - float(player.ecr)) / std)


def build(
    players: list[Player],
    drafted: set[str],
    my_roster: list[Player],
    current_pick: int,
    next_pick: int,
) -> list[Candidate]:
    levels = replacement_levels(players)
    cands = [
        Candidate(player=p, vorp=p.league_points - levels.get(p.position, 0.0))
        for p in players
        if p.name not in drafted
    ]
    assign_tiers(cands)

    need = roster_need(my_roster)
    by_pos: dict[str, list[Candidate]] = {}
    for c in cands:
        by_pos.setdefault(c.player.position, []).append(c)
    for lst in by_pos.values():
        lst.sort(key=lambda c: -c.vorp)

    # Availability must be computed for EVERY candidate before any surplus is,
    # because surplus reads its peers' availability. Doing both in one pass
    # leaves later peers holding the default 1.0 and wildly overstates what
    # waiting would yield.
    for c in cands:
        c.p_available_next = availability(c.player, next_pick)

    for c in cands:
        # What this position is expected to yield if you wait one turn.
        peers = by_pos[c.player.position]
        expected_next = 0.0
        survival = 1.0
        for peer in peers[:14]:
            p_here = peer.p_available_next if peer is not c else 0.0
            expected_next += survival * p_here * peer.vorp
            survival *= 1.0 - p_here
        c.surplus = c.vorp - expected_next
        if need.get(c.player.position, 0) <= 0:
            c.surplus -= 25.0  # already covered; needs to be clearly better to justify
            c.reasons.append("position already covered")
        if c.tier_last and c.tier_drop > 0:
            c.surplus += min(c.tier_drop, 20.0) * 0.5
            c.reasons.append(f"last in tier - next is {c.tier_drop:.0f} pts lower")
        if c.player.delta > 12:
            c.reasons.append(f"worth {c.player.delta:+.0f} pts vs consensus in our scoring")
        elif c.player.delta < -8:
            c.reasons.append(f"consensus overrates him by {-c.player.delta:.0f} pts here")
        if c.p_available_next < 0.25:
            c.reasons.append(f"{c.p_available_next * 100:.0f}% to last to pick {next_pick}")

    cands.sort(key=lambda c: -c.surplus)
    return cands


def roster_need(my_roster: list[Player]) -> dict[str, int]:
    """Starting slots still unfilled, counting flex against RB/WR/TE."""
    have: dict[str, int] = {}
    for p in my_roster:
        have[p.position] = have.get(p.position, 0) + 1
    need = {pos: n - have.get(pos, 0) for pos, n in STARTERS.items()}
    spare = sum(max(0, -need[pos]) for pos in FLEX_POSITIONS if pos in need)
    if spare < FLEX_SLOTS:
        for pos in FLEX_POSITIONS:
            need[pos] = need.get(pos, 0) + 1
    return need
