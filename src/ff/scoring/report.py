"""Render a ScoringDiff as a terminal table and as a markdown change-list.

The markdown output is the thing you actually work from: Yahoo's API cannot
write league scoring, so the deliverable is an ordered checklist to apply in
League Settings -> Edit League Settings -> Modify Stat Categories.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .diff import Change, ScoringDiff

_STYLE = {
    "match": "dim",
    "no_effect": "dim",
    "differs": "yellow",
    "missing_in_target": "red",
    "missing_in_source": "cyan",
    "unportable": "magenta",
}

_HUMAN = {
    "match": "OK",
    "no_effect": "NO EFFECT (0)",
    "differs": "CHANGE",
    "missing_in_target": "ADD",
    "missing_in_source": "REMOVE?",
    "unportable": "NO YAHOO EQUIV",
}


def print_diff(diff: ScoringDiff, show_matches: bool = False) -> None:
    console = Console()
    table = Table(
        title=f"Scoring diff: {diff.source_platform} (source) -> {diff.target_platform} (target)"
    )
    table.add_column("Group")
    table.add_column("Category")
    table.add_column(diff.source_platform, justify="right")
    table.add_column(diff.target_platform, justify="right")
    table.add_column("Action")

    for c in diff.changes:
        if c.status == "match" and not show_matches:
            continue
        table.add_row(
            c.group,
            c.label,
            _fmt(c.source_value),
            _fmt(c.target_value),
            _HUMAN[c.status],
            style=_STYLE[c.status],
        )

    console.print(table)

    matched = len(diff.by_status("match")) + len(diff.by_status("no_effect"))
    console.print(
        f"[dim]{matched} categories already match. "
        f"{len(diff.actionable)} need attention.[/dim]"
    )

    if diff.source_only_unmapped:
        console.print(
            f"\n[yellow]Unmapped on {diff.source_platform}[/yellow] "
            "(not in ff.scoring.mapping -- review by hand): "
            + ", ".join(f"{k}={v}" for k, v in sorted(diff.source_only_unmapped.items()))
        )
    if diff.target_only_unmapped:
        console.print(
            f"[yellow]Unmapped on {diff.target_platform}[/yellow]: "
            + ", ".join(f"{k}={v}" for k, v in sorted(diff.target_only_unmapped.items()))
        )


def to_markdown(diff: ScoringDiff) -> str:
    lines = [
        f"# Scoring change-list: {diff.source_platform} -> {diff.target_platform}",
        "",
        "Yahoo's Fantasy Sports API is read-only for league settings, so apply these",
        "by hand in **League Settings -> Edit League Settings -> Modify Stat Categories**",
        "(commissioner only, and locked once the season starts).",
        "",
    ]

    buckets: list[tuple[str, str, list[Change]]] = [
        ("Change these values", "differs", diff.by_status("differs")),
        ("Add / enable these categories", "missing_in_target", diff.by_status("missing_in_target")),
        (
            "Present in Yahoo but not in Sleeper -- confirm or zero out",
            "missing_in_source",
            diff.by_status("missing_in_source"),
        ),
        (
            "No Yahoo equivalent -- decide on a substitute",
            "unportable",
            diff.by_status("unportable"),
        ),
    ]

    for title, _status, changes in buckets:
        if not changes:
            continue
        lines += [f"## {title}", "", "| Category | Sleeper | Yahoo |", "|---|---|---|"]
        lines += [
            f"| {c.label} | {_fmt(c.source_value)} | {_fmt(c.target_value)} |" for c in changes
        ]
        lines.append("")

    zeros = diff.by_status("no_effect")
    if zeros:
        lines += [
            f"## Scored zero on one side, absent on the other -- no action ({len(zeros)})",
            "",
            "These score identically whether or not Yahoo lists the category.",
            "",
            ", ".join(c.label for c in zeros),
            "",
        ]

    matched = diff.by_status("match")
    if matched:
        lines += [
            f"## Already matching ({len(matched)})",
            "",
            ", ".join(c.label for c in matched),
            "",
        ]

    if diff.source_only_unmapped or diff.target_only_unmapped:
        lines += ["## Unmapped -- review by hand", ""]
        for label, data in (
            (diff.source_platform, diff.source_only_unmapped),
            (diff.target_platform, diff.target_only_unmapped),
        ):
            for k, v in sorted(data.items()):
                lines.append(f"- `{label}` **{k}** = {v}")
        lines.append("")

    return "\n".join(lines)


def _fmt(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:g}"
