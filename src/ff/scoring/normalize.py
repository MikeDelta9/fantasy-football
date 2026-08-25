"""Reduce each platform's scoring payload to {canonical_key: points}.

Anything the mapping table doesn't cover is kept aside as `unmapped` so the
diff report can surface it instead of quietly losing a scoring rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..yahoo.client import flatten
from .mapping import by_sleeper_key, by_yahoo_id


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
