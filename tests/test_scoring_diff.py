from ff.scoring.diff import diff_scoring
from ff.scoring.normalize import normalize_sleeper, normalize_yahoo


def _yahoo_payload(pairs):
    """Minimal shape mimicking Yahoo's nested settings response."""
    return {
        "fantasy_content": {
            "league": [
                {"league_key": "449.l.1"},
                {
                    "settings": [
                        {
                            "stat_modifiers": {
                                "stats": [
                                    {"stat": {"stat_id": str(sid), "value": str(val)}}
                                    for sid, val in pairs
                                ]
                            }
                        }
                    ]
                },
            ]
        }
    }


def test_matching_values_report_as_match():
    sleeper = normalize_sleeper({"pass_td": 4, "rec": 1})
    yahoo = normalize_yahoo(_yahoo_payload([(5, 4), (11, 1)]))
    result = diff_scoring(sleeper, yahoo)
    assert result.actionable == []


def test_value_difference_is_flagged():
    sleeper = normalize_sleeper({"pass_td": 6})
    yahoo = normalize_yahoo(_yahoo_payload([(5, 4)]))
    result = diff_scoring(sleeper, yahoo)
    (change,) = result.actionable
    assert change.key == "pass_td"
    assert change.status == "differs"
    assert (change.source_value, change.target_value) == (6.0, 4.0)


def test_category_missing_in_yahoo_is_an_add():
    sleeper = normalize_sleeper({"rec": 0.5})
    yahoo = normalize_yahoo(_yahoo_payload([]))
    (change,) = diff_scoring(sleeper, yahoo).actionable
    assert change.status == "missing_in_target"


def test_sleeper_only_category_is_unportable_not_an_add():
    sleeper = normalize_sleeper({"bonus_rec_te": 0.5})
    yahoo = normalize_yahoo(_yahoo_payload([]))
    (change,) = diff_scoring(sleeper, yahoo).actionable
    assert change.status == "unportable"


def test_unknown_sleeper_key_is_kept_as_unmapped():
    sleeper = normalize_sleeper({"some_new_stat": 3})
    assert sleeper.unmapped == {"some_new_stat": 3.0}
    assert sleeper.values == {}


def test_yahoo_pseudo_array_form_is_flattened():
    """Yahoo really returns {"0": {...}, "1": {...}, "count": n}, not a list."""
    payload = {
        "fantasy_content": {
            "league": {
                "0": {"league_key": "449.l.1"},
                "1": {
                    "settings": {
                        "0": {
                            "stat_modifiers": {
                                "stats": {
                                    "0": {"stat": {"stat_id": "5", "value": "6"}},
                                    "1": {"stat": {"stat_id": "11", "value": "0.5"}},
                                    "count": 2,
                                }
                            }
                        },
                        "count": 1,
                    }
                },
                "count": 2,
            }
        }
    }
    norm = normalize_yahoo(payload)
    assert norm.values == {"pass_td": 6.0, "rec": 0.5}
