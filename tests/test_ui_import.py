"""The commissioner-UI path carries the whole diff while API access is pending,
so the parts that could silently produce a wrong number are pinned here."""

from ff.scoring.diff import diff_scoring
from ff.scoring.normalize import NormalizedScoring, normalize_yahoo_ui
from ff.yahoo.ui_import import parse_ui_dump


def _dump(rows):
    return {"settings": {}, "scoring": [dict(zip(("label", "value"), r)) for r in rows]}


def test_yards_per_point_becomes_points_per_yard():
    out = parse_ui_dump(_dump([("Passing Yards", "25 yards per point")]))
    assert out["scoring"][0]["points"] == 0.04


def test_yahoo_default_suffix_is_stripped_from_overridden_rows():
    out = parse_ui_dump(_dump([("Passing Touchdowns Yahoo Default", "6")]))
    assert out["scoring"][0]["label"] == "Passing Touchdowns"


def test_section_disambiguates_a_label_yahoo_reuses():
    """'Interception' is a thrown pick on offense and a takeaway on defense."""
    dump = {
        "settings": {},
        "scoring": [
            {"label": "Offense", "value": "League Value"},
            {"label": "Interceptions", "value": "-2"},
            {"label": "Defense/Special Teams", "value": "League Value"},
            {"label": "Interception", "value": "2"},
        ],
    }
    norm = normalize_yahoo_ui(parse_ui_dump(dump))
    assert norm.values["pass_int"] == -2
    assert norm.values["int"] == 2


def test_one_yahoo_row_can_feed_several_sleeper_keys():
    dump = {"settings": {}, "scoring": [{"label": "2-Point Conversions", "value": "2"}]}
    norm = normalize_yahoo_ui(parse_ui_dump(dump))
    assert norm.values["pass_2pt"] == norm.values["rush_2pt"] == norm.values["rec_2pt"] == 2


def test_unrecognised_label_is_surfaced_not_dropped():
    dump = {"settings": {}, "scoring": [{"label": "Some New Yahoo Thing", "value": "3"}]}
    norm = normalize_yahoo_ui(parse_ui_dump(dump))
    assert not norm.values
    assert norm.unmapped["Some New Yahoo Thing"] == 3


def test_zero_on_one_side_and_absent_on_the_other_is_not_a_work_item():
    source = NormalizedScoring(platform="sleeper", values={"fgmiss": 0.0})
    target = NormalizedScoring(platform="yahoo", values={})
    result = diff_scoring(source, target)
    assert result.changes[0].status == "no_effect"
    assert not result.actionable


def test_a_ui_readable_category_is_not_called_unportable():
    """Portability is about the category, not about lacking a verified stat id."""
    source = NormalizedScoring(platform="sleeper", values={"st_td": 6.0})
    target = NormalizedScoring(platform="yahoo", values={"st_td": 6.0})
    assert diff_scoring(source, target).changes[0].status == "match"
