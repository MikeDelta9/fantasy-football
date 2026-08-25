"""Compare two NormalizedScoring objects and describe what must change."""

from __future__ import annotations

from dataclasses import dataclass, field

from .mapping import CANON
from .normalize import NormalizedScoring

_LABELS = {c.key: c for c in CANON}


@dataclass
class Change:
    key: str
    label: str
    group: str
    source_value: float | None
    target_value: float | None
    status: str  # match | differs | missing_in_target | missing_in_source | unportable

    @property
    def needs_action(self) -> bool:
        return self.status != "match"


@dataclass
class ScoringDiff:
    source_platform: str
    target_platform: str
    changes: list[Change] = field(default_factory=list)
    source_only_unmapped: dict[str, float] = field(default_factory=dict)
    target_only_unmapped: dict[str, float] = field(default_factory=dict)

    @property
    def actionable(self) -> list[Change]:
        return [c for c in self.changes if c.needs_action]

    def by_status(self, status: str) -> list[Change]:
        return [c for c in self.changes if c.status == status]


def diff_scoring(source: NormalizedScoring, target: NormalizedScoring) -> ScoringDiff:
    """source is the platform of record (Sleeper); target is what gets changed."""
    result = ScoringDiff(source.platform, target.platform)
    keys = sorted(set(source.values) | set(target.values), key=_order)

    for key in keys:
        cat = _LABELS.get(key)
        sv = source.values.get(key)
        tv = target.values.get(key)

        if cat and cat.yahoo is None and target.platform == "yahoo" and sv is not None:
            status = "unportable"
        elif sv is not None and tv is not None:
            status = "match" if abs(sv - tv) < 1e-9 else "differs"
        elif sv is not None:
            status = "missing_in_target"
        else:
            status = "missing_in_source"

        result.changes.append(
            Change(
                key=key,
                label=cat.label if cat else key,
                group=cat.group if cat else "misc",
                source_value=sv,
                target_value=tv,
                status=status,
            )
        )

    result.source_only_unmapped = dict(source.unmapped)
    result.target_only_unmapped = dict(target.unmapped)
    return result


_GROUP_ORDER = ["passing", "rushing", "receiving", "kicking", "defense", "misc"]


def _order(key: str) -> tuple[int, int]:
    cat = _LABELS.get(key)
    if not cat:
        return (len(_GROUP_ORDER), 0)
    return (_GROUP_ORDER.index(cat.group), [c.key for c in CANON].index(cat.key))
