"""Reduce each platform's scoring payload to {canonical_key: points}.

Anything the mapping table doesn't cover is kept aside as `unmapped` so the
diff report can surface it instead of quietly losing a scoring rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..yahoo.client import flatten
from .mapping import CANON, by_sleeper_key, by_yahoo_id


@dataclass
class NormalizedScoring:
    platform: str
    values: dict[str, float] = field(default_factory=dict)
    unmapped: dict[str, float] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)


def normalize_sleeper(scoring_settings: dict[str, Any]) -> NormalizedScoring:
    out = NormalizedScoring(platform="sleeper", source=dict(scoring_settings))
    for key, value in scoring_settings.items():
        try:
            points = float(value)
        except (TypeError, ValueError):
            continue
        cat = by_sleeper_key(key)
        if cat:
            out.values[cat.key] = points
        else:
            out.unmapped[key] = points
    return out


def normalize_yahoo(settings_payload: dict[str, Any]) -> NormalizedScoring:
    """Accepts the raw JSON from YahooClient.settings()."""
    flat = flatten(settings_payload)
    modifiers = _find_stat_modifiers(flat)
    out = NormalizedScoring(platform="yahoo", source={"stat_modifiers": modifiers})
    for entry in modifiers:
        stat = entry.get("stat") if isinstance(entry, dict) else None
        if not isinstance(stat, dict):
            continue
        try:
            stat_id = int(stat["stat_id"])
            points = float(stat["value"])
        except (KeyError, TypeError, ValueError):
            continue
        cat = by_yahoo_id(stat_id)
        if cat:
            out.values[cat.key] = points
        else:
            out.unmapped[f"stat_id:{stat_id}"] = points
    return out


# Yahoo's UI labels are not unique on their own -- "Interception" is a thrown
# pick under Offense and a defensive takeaway under Defense/Special Teams -- so
# the lookup is keyed on the label plus the section it appeared under.
_BY_UI_LABEL: dict[str, list[str]] = {}
for _c in CANON:
    if _c.yahoo_ui:
        _BY_UI_LABEL.setdefault(_c.yahoo_ui, []).append(_c.key)

_SECTION_GROUPS = {
    "Offense": {"passing", "rushing", "receiving", "misc"},
    "Kickers": {"kicking"},
    "Defense/Special Teams": {"defense"},
}
_GROUP_OF = {c.key: c.group for c in CANON}


def normalize_yahoo_ui(payload: dict[str, Any]) -> NormalizedScoring:
    """Accepts a snapshot written by ff.yahoo.ui_import.parse_ui_dump()."""
    out = NormalizedScoring(platform="yahoo", source={"_source": payload.get("_source")})
    for row in payload.get("scoring", []):
        label = row.get("label")
        section = row.get("section", "")
        try:
            points = float(row["points"])
        except (KeyError, TypeError, ValueError):
            continue

        candidates = _BY_UI_LABEL.get(label, [])
        allowed = _SECTION_GROUPS.get(section)
        if allowed:
            candidates = [k for k in candidates if _GROUP_OF.get(k) in allowed] or candidates

        if candidates:
            # One Yahoo row can legitimately feed several canonical keys: the
            # single 2-Point Conversions category covers Sleeper's separate
            # pass/rush/rec keys. Every candidate gets the same value.
            for key in candidates:
                out.values[key] = points
        else:
            out.unmapped[f"{section}: {label}" if section else label] = points
    return out


def normalize_yahoo_any(payload: dict[str, Any]) -> NormalizedScoring:
    """Dispatch on how the snapshot was obtained: commissioner UI or the API."""
    if payload.get("_source") == "yahoo-commissioner-ui":
        return normalize_yahoo_ui(payload)
    return normalize_yahoo(payload)


def _find_stat_modifiers(node: Any) -> list[Any]:
    """Yahoo nests settings several pseudo-array levels deep; walk for the key."""
    if isinstance(node, dict):
        if "stat_modifiers" in node:
            mods = node["stat_modifiers"]
            if isinstance(mods, dict):
                mods = mods.get("stats", mods)
            return mods if isinstance(mods, list) else [mods]
        for value in node.values():
            found = _find_stat_modifiers(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_stat_modifiers(item)
            if found:
                return found
    return []
