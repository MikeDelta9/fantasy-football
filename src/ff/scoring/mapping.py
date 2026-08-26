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
    # Label as it appears in Yahoo's commissioner UI. Set when the category is
    # readable from the settings page, which is currently the only way in --
    # Yahoo gates the Fantasy API behind an approval process. A category with a
    # yahoo_ui label is portable even when `yahoo` (the stat id) is None or
    # unverified, so the diff must not call it unportable.
    yahoo_ui: str | None = None
    # Key in a FantasyPros projection `stats` object. Set only where the mapping
    # is one-to-one: FantasyPros reports a single `2pt_tds` count and a single
    # `ret_tds`, so exactly ONE canonical category may claim each, or scoring
    # would double- or triple-count the same projected event.
    fantasypros: str | None = None


CANON: list[Category] = [
    # ---- passing ----
    Category("pass_yd", "Passing Yards", "passing", "pass_yd", 4, "Passing Yards", fantasypros="pass_yds"),
    Category("pass_td", "Passing TD", "passing", "pass_td", 5, "Passing Touchdowns", fantasypros="pass_tds"),
    Category("pass_int", "Interception Thrown", "passing", "pass_int", 6, "Interceptions", fantasypros="pass_ints"),
    Category("pass_2pt", "Passing 2-Pt Conversion", "passing", "pass_2pt", 16, "2-Point Conversions", fantasypros="2pt_tds"),
    Category("pass_cmp", "Completion", "passing", "pass_cmp", 3, None, fantasypros="pass_cmp"),
    Category("pass_att", "Passing Attempt", "passing", "pass_att", 2, None, fantasypros="pass_att"),
    Category("pass_sack", "Sack Taken", "passing", "pass_sack", 7),
    # ---- rushing ----
    Category("rush_yd", "Rushing Yards", "rushing", "rush_yd", 9, "Rushing Yards", fantasypros="rush_yds"),
    Category("rush_td", "Rushing TD", "rushing", "rush_td", 10, "Rushing Touchdowns", fantasypros="rush_tds"),
    Category("rush_att", "Rushing Attempt", "rushing", "rush_att", 8, None, fantasypros="rush_att"),
    Category("rush_2pt", "Rushing 2-Pt Conversion", "rushing", "rush_2pt", None, "2-Point Conversions"),
    # ---- receiving ----
    Category("rec", "Reception", "receiving", "rec", 11, "Receptions", fantasypros="rec_rec"),
    Category("rec_yd", "Receiving Yards", "receiving", "rec_yd", 12, "Receiving Yards", fantasypros="rec_yds"),
    Category("rec_td", "Receiving TD", "receiving", "rec_td", 13, "Receiving Touchdowns", fantasypros="rec_tds"),
    Category("rec_2pt", "Receiving 2-Pt Conversion", "receiving", "rec_2pt", None, "2-Point Conversions"),
    Category("rec_tgt", "Target", "receiving", "rec_tgt", 78),
    # Sleeper-only positional PPR premiums; Yahoo has no equivalent.
    Category("rec_rb", "Reception (RB premium)", "receiving", "rec_rb", None),
    Category("rec_wr", "Reception (WR premium)", "receiving", "rec_wr", None),
    Category("rec_te", "Reception (TE premium)", "receiving", "rec_te", None),
    Category("bonus_rec_te", "TE Reception Bonus", "receiving", "bonus_rec_te", None),
    # ---- fumbles ----
    Category("fum", "Fumble", "misc", "fum", 17),
    Category("fum_lost", "Fumble Lost", "misc", "fum_lost", 18, "Fumbles Lost", fantasypros="fumbles"),
    Category("fum_rec_td", "Fumble Recovery TD (offense)", "misc", "fum_rec_td", 57, "Offensive Fumble Return TD"),
    # ---- returns ----
    Category("kr_td", "Kick Return TD", "misc", "kr_td", 15),
    Category("pr_td", "Punt Return TD", "misc", "pr_td", 15),
    Category("kr_yd", "Kick Return Yards", "misc", "kr_yd", 14),
    Category("pr_yd", "Punt Return Yards", "misc", "pr_yd", 14),
    # ---- kicking ----
    Category("xpm", "Extra Point Made", "kicking", "xpm", 31, "Point After Attempt Made", fantasypros="xpt"),
    Category("xpmiss", "Extra Point Missed", "kicking", "xpmiss", 32),
    Category("fgm_0_19", "FG Made 0-19", "kicking", "fgm_0_19", 19, "Field Goals 0-19 Yards"),
    Category("fgm_20_29", "FG Made 20-29", "kicking", "fgm_20_29", 20, "Field Goals 20-29 Yards"),
    Category("fgm_30_39", "FG Made 30-39", "kicking", "fgm_30_39", 21, "Field Goals 30-39 Yards"),
    Category("fgm_40_49", "FG Made 40-49", "kicking", "fgm_40_49", 22, "Field Goals 40-49 Yards"),
    Category("fgm_50p", "FG Made 50+", "kicking", "fgm_50p", 23, "Field Goals 50+ Yards"),
    # Sleeper splits the 50+ bucket that Yahoo keeps whole. Both sides are named
    # here so the diff can say which one Yahoo cannot express, instead of
    # dropping them into `unmapped` and calling it a table bug.
    Category("fgm_50_59", "FG Made 50-59", "kicking", "fgm_50_59", None),
    Category("fgm_60p", "FG Made 60+", "kicking", "fgm_60p", None),
    Category("fgmiss", "FG Missed", "kicking", "fgmiss", 30),
    # ---- team defense / special teams ----
    Category("sack", "Sack", "defense", "sack", 34, "Sack", fantasypros="def_sack"),
    Category("int", "Interception", "defense", "int", 35, "Interception", fantasypros="def_int"),
    Category("fum_rec", "Fumble Recovery", "defense", "fum_rec", 36, "Fumble Recovery", fantasypros="def_fr"),
    Category("def_td", "Defensive TD", "defense", "def_td", 37, "Touchdown", fantasypros="def_td"),
    Category("safe", "Safety", "defense", "safe", 38, "Safety", fantasypros="def_safety"),
    Category("blk_kick", "Blocked Kick", "defense", "blk_kick", 39, "Block Kick"),
    Category("def_st_td", "Special Teams TD", "defense", "def_st_td", 41, "Kickoff and Punt Return Touchdowns", fantasypros="def_retd"),
    Category("st_td", "Return TD (ST player)", "misc", "st_td", None, "Return Touchdowns", fantasypros="ret_tds"),
    Category("ff", "Forced Fumble", "defense", "ff", None, None, fantasypros="def_ff"),
    Category("pts_allow_0", "Points Allowed 0", "defense", "pts_allow_0", 50, "Points Allowed 0 points", fantasypros="def_pa_a"),
    Category("pts_allow_1_6", "Points Allowed 1-6", "defense", "pts_allow_1_6", 51, "Points Allowed 1-6 points", fantasypros="def_pa_b"),
    Category("pts_allow_7_13", "Points Allowed 7-13", "defense", "pts_allow_7_13", 52, "Points Allowed 7-13 points", fantasypros="def_pa_c"),
    Category("pts_allow_14_20", "Points Allowed 14-20", "defense", "pts_allow_14_20", 53, "Points Allowed 14-20 points", fantasypros="def_pa_d"),
    Category("pts_allow_21_27", "Points Allowed 21-27", "defense", "pts_allow_21_27", 54, "Points Allowed 21-27 points", fantasypros="def_pa_e"),
    Category("pts_allow_28_34", "Points Allowed 28-34", "defense", "pts_allow_28_34", 55, "Points Allowed 28-34 points", fantasypros="def_pa_f"),
    Category("pts_allow_35p", "Points Allowed 35+", "defense", "pts_allow_35p", 56, "Points Allowed 35+ points", fantasypros="def_pa_g"),
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
