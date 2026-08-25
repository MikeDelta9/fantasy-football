"""Canonical scoring categories, mapped to Sleeper keys and Yahoo stat ids.

The Yahoo stat ids below are the standard NFL set. Do NOT trust them blind --
`ff yahoo verify-mapping` pulls /game/nfl/stat_categories and reports any id
whose Yahoo-side name disagrees with the label here. Run it once per season;
Yahoo has added ids over time.

A category present on one platform only (Sleeper's per-position reception
bonuses, Yahoo's separate FG-missed buckets) has None on the other side and is
reported as UNMAPPED rather than silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    key: str          # canonical name used throughout this project
    label: str        # human label for reports
    group: str        # passing | rushing | receiving | kicking | defense | misc
    sleeper: str | None
    yahoo: int | None


CANON: list[Category] = [
    # ---- passing ----
    Category("pass_yd", "Passing Yards", "passing", "pass_yd", 4),
    Category("pass_td", "Passing TD", "passing", "pass_td", 5),
    Category("pass_int", "Interception Thrown", "passing", "pass_int", 6),
    Category("pass_2pt", "Passing 2-Pt Conversion", "passing", "pass_2pt", 16),
    Category("pass_cmp", "Completion", "passing", "pass_cmp", 3),
    Category("pass_att", "Passing Attempt", "passing", "pass_att", 2),
    Category("pass_sack", "Sack Taken", "passing", "pass_sack", 7),
    # ---- rushing ----
    Category("rush_yd", "Rushing Yards", "rushing", "rush_yd", 9),
    Category("rush_td", "Rushing TD", "rushing", "rush_td", 10),
    Category("rush_att", "Rushing Attempt", "rushing", "rush_att", 8),
    Category("rush_2pt", "Rushing 2-Pt Conversion", "rushing", "rush_2pt", None),
    # ---- receiving ----
    Category("rec", "Reception", "receiving", "rec", 11),
    Category("rec_yd", "Receiving Yards", "receiving", "rec_yd", 12),
    Category("rec_td", "Receiving TD", "receiving", "rec_td", 13),
    Category("rec_2pt", "Receiving 2-Pt Conversion", "receiving", "rec_2pt", None),
    Category("rec_tgt", "Target", "receiving", "rec_tgt", 78),
    # Sleeper-only positional PPR premiums; Yahoo has no equivalent.
    Category("rec_rb", "Reception (RB premium)", "receiving", "rec_rb", None),
    Category("rec_wr", "Reception (WR premium)", "receiving", "rec_wr", None),
    Category("rec_te", "Reception (TE premium)", "receiving", "rec_te", None),
    Category("bonus_rec_te", "TE Reception Bonus", "receiving", "bonus_rec_te", None),
    # ---- fumbles ----
    Category("fum", "Fumble", "misc", "fum", 17),
    Category("fum_lost", "Fumble Lost", "misc", "fum_lost", 18),
    Category("fum_rec_td", "Fumble Recovery TD (offense)", "misc", "fum_rec_td", 57),
    # ---- returns ----
    Category("kr_td", "Kick Return TD", "misc", "kr_td", 15),
    Category("pr_td", "Punt Return TD", "misc", "pr_td", 15),
    Category("kr_yd", "Kick Return Yards", "misc", "kr_yd", 14),
    Category("pr_yd", "Punt Return Yards", "misc", "pr_yd", 14),
    # ---- kicking ----
    Category("xpm", "Extra Point Made", "kicking", "xpm", 31),
    Category("xpmiss", "Extra Point Missed", "kicking", "xpmiss", 32),
    Category("fgm_0_19", "FG Made 0-19", "kicking", "fgm_0_19", 19),
    Category("fgm_20_29", "FG Made 20-29", "kicking", "fgm_20_29", 20),
    Category("fgm_30_39", "FG Made 30-39", "kicking", "fgm_30_39", 21),
    Category("fgm_40_49", "FG Made 40-49", "kicking", "fgm_40_49", 22),
    Category("fgm_50p", "FG Made 50+", "kicking", "fgm_50p", 23),
    Category("fgmiss", "FG Missed", "kicking", "fgmiss", 30),
    # ---- team defense / special teams ----
    Category("sack", "Sack", "defense", "sack", 34),
    Category("int", "Interception", "defense", "int", 35),
    Category("fum_rec", "Fumble Recovery", "defense", "fum_rec", 36),
    Category("def_td", "Defensive TD", "defense", "def_td", 37),
    Category("safe", "Safety", "defense", "safe", 38),
    Category("blk_kick", "Blocked Kick", "defense", "blk_kick", 39),
    Category("def_st_td", "Special Teams TD", "defense", "def_st_td", 41),
    Category("ff", "Forced Fumble", "defense", "ff", None),
    Category("pts_allow_0", "Points Allowed 0", "defense", "pts_allow_0", 50),
    Category("pts_allow_1_6", "Points Allowed 1-6", "defense", "pts_allow_1_6", 51),
    Category("pts_allow_7_13", "Points Allowed 7-13", "defense", "pts_allow_7_13", 52),
    Category("pts_allow_14_20", "Points Allowed 14-20", "defense", "pts_allow_14_20", 53),
    Category("pts_allow_21_27", "Points Allowed 21-27", "defense", "pts_allow_21_27", 54),
    Category("pts_allow_28_34", "Points Allowed 28-34", "defense", "pts_allow_28_34", 55),
    Category("pts_allow_35p", "Points Allowed 35+", "defense", "pts_allow_35p", 56),
]

_BY_SLEEPER = {c.sleeper: c for c in CANON if c.sleeper}
_BY_YAHOO: dict[int, Category] = {}
for _c in CANON:
    if _c.yahoo is not None:
        _BY_YAHOO.setdefault(_c.yahoo, _c)


def by_sleeper_key(key: str) -> Category | None:
    return _BY_SLEEPER.get(key)


def by_yahoo_id(stat_id: int) -> Category | None:
    return _BY_YAHOO.get(stat_id)
