"""Read league scoring out of Yahoo's commissioner UI.

Yahoo gates the Fantasy Sports API behind an approval process
(<https://sports.yahoo.com/developer/access/>), so until that lands there is no
API payload to snapshot. The settings page renders every value we need, and the
commissioner is already logged in, so we read it from there instead.

This produces a snapshot in the same `data/snapshots/yahoo-settings-*.json`
slot the API path writes to, tagged with `_source` so `normalize` can tell the
two apart. When API access is granted, nothing downstream has to change.

Deliberately *not* done here: inventing Yahoo stat ids. The UI gives labels, not
ids, and `ff/scoring/mapping.py`'s ids cannot be checked without the API
(`ff yahoo verify-mapping` needs it). Matching on label keeps this path honest
rather than confidently wrong.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

# Rows whose value cell reads exactly this are section headers, not categories.
_SECTION_MARKER = "League Value"

# "25 yards per point" -> 0.04
_RATE = re.compile(r"^([\d.]+)\s+yards?\s+per\s+point$", re.IGNORECASE)


def parse_ui_dump(dump: dict[str, Any], league_id: str | None = None) -> dict[str, Any]:
    """Turn a scraped settings page into a snapshot payload."""
    scoring: list[dict[str, Any]] = []
    section = ""
    for row in dump.get("scoring", []):
        label = (row.get("label") or "").strip()
        raw = (row.get("value") or "").strip()
        if not label:
            continue
        if raw == _SECTION_MARKER:
            section = label
            continue
        points = _to_points(raw)
        if points is None:
            continue
        scoring.append(
            {"section": section, "label": _clean_label(label), "raw": raw, "points": points}
        )

    return {
        "_source": "yahoo-commissioner-ui",
        "_league_id": league_id or dump.get("settings", {}).get("League ID#"),
        "_read_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "_why": (
            "Yahoo's Fantasy Sports API requires approved access, which this league "
            "does not have yet. Values read from the commissioner settings page."
        ),
        "settings": dump.get("settings", {}),
        "scoring": scoring,
    }


def _clean_label(label: str) -> str:
    """Yahoo appends 'Yahoo Default' to rows overridden from the default."""
    return re.sub(r"\s*Yahoo Default\s*$", "", label).strip()


def _to_points(raw: str) -> float | None:
    """A Yahoo value is either a number or a 'N yards per point' rate."""
    rate = _RATE.match(raw)
    if rate:
        per = float(rate.group(1))
        return round(1.0 / per, 6) if per else None
    try:
        return float(raw)
    except ValueError:
        return None
