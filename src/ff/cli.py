"""`ff` command line. Run `ff --help` for the full list."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from .config import SNAPSHOTS, settings
from .scoring.diff import diff_scoring
from .scoring.mapping import CANON
from .scoring.normalize import normalize_sleeper, normalize_yahoo
from .scoring.report import print_diff, to_markdown

app = typer.Typer(help="Sleeper -> Yahoo league migration and fantasy football tooling.")
sleeper_app = typer.Typer(help="Sleeper (read-only public API).")
yahoo_app = typer.Typer(help="Yahoo Fantasy Sports API (OAuth2).")
app.add_typer(sleeper_app, name="sleeper")
app.add_typer(yahoo_app, name="yahoo")

console = Console()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _save(name: str, payload: object) -> Path:
    path = SNAPSHOTS / f"{name}-{_stamp()}.json"
    path.write_text(json.dumps(payload, indent=2))
    console.print(f"[dim]saved {path}[/dim]")
    return path


def _latest(prefix: str) -> Path:
    matches = sorted(SNAPSHOTS.glob(f"{prefix}-*.json"))
    if not matches:
        raise SystemExit(f"No {prefix} snapshot yet. Run: ff {prefix.split('-')[0]} pull")
    return matches[-1]


# ---------------------------------------------------------------- sleeper
@sleeper_app.command("pull")
def sleeper_pull(league_id: str = typer.Option(None, help="Defaults to SLEEPER_LEAGUE_ID")) -> None:
    """Snapshot the full Sleeper league object."""
    from .sleeper import SleeperClient

    league_id = league_id or settings.sleeper_league_id
    if not league_id:
        raise SystemExit("Set SLEEPER_LEAGUE_ID in .env or pass --league-id")
    with SleeperClient() as c:
        league = c.league(league_id)
    console.print(f"[green]{league.get('name')}[/green]  season {league.get('season')}  "
                  f"{league.get('total_rosters')} teams")
    _save("sleeper-league", league)


@sleeper_app.command("scoring")
def sleeper_scoring(league_id: str = typer.Option(None)) -> None:
    """Print Sleeper scoring settings, normalized."""
    from .sleeper import SleeperClient

    league_id = league_id or settings.sleeper_league_id
    with SleeperClient() as c:
        raw = c.scoring_settings(league_id)
    norm = normalize_sleeper(raw)
    for key, value in sorted(norm.values.items()):
        console.print(f"{key:<20} {value:g}")
    if norm.unmapped:
        console.print(f"\n[yellow]unmapped:[/yellow] {norm.unmapped}")


# ------------------------------------------------------------------ yahoo
@yahoo_app.command("login")
def yahoo_login() -> None:
    """One-time OAuth2 approval; writes .yahoo_token.json."""
    from .yahoo import YahooAuth

    YahooAuth().login()


@yahoo_app.command("leagues")
def yahoo_leagues() -> None:
    """List every Yahoo NFL league on the authenticated account, with its league key."""
    from .yahoo import YahooClient
    from .yahoo.client import flatten

    with YahooClient() as c:
        data = flatten(c.my_leagues())
    _save("yahoo-leagues", data)
    console.print(data)
    console.print("\n[dim]Copy the league_key (e.g. 449.l.123456) into YAHOO_LEAGUE_KEY.[/dim]")


@yahoo_app.command("pull")
def yahoo_pull(league_key: str = typer.Option(None, help="Defaults to YAHOO_LEAGUE_KEY")) -> None:
    """Snapshot the Yahoo league settings payload."""
    from .yahoo import YahooClient

    league_key = league_key or settings.yahoo_league_key
    if not league_key:
        raise SystemExit("Set YAHOO_LEAGUE_KEY in .env (find it with: ff yahoo leagues)")
    with YahooClient() as c:
        payload = c.settings(league_key)
    _save("yahoo-settings", payload)


@yahoo_app.command("verify-mapping")
def yahoo_verify_mapping() -> None:
    """Check ff.scoring.mapping's hardcoded stat ids against Yahoo's own catalogue."""
    from .yahoo import YahooClient
    from .yahoo.client import flatten

    with YahooClient() as c:
        catalogue = flatten(c.stat_categories())

    yahoo_names: dict[int, str] = {}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if "stat_id" in node and "display_name" in node:
                try:
                    yahoo_names[int(node["stat_id"])] = str(node["display_name"])
                except (TypeError, ValueError):
                    pass
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(catalogue)
    if not yahoo_names:
        raise SystemExit("Could not parse stat categories from Yahoo's response.")

    problems = 0
    for cat in CANON:
        if cat.yahoo is None:
            continue
        actual = yahoo_names.get(cat.yahoo)
        if actual is None:
            console.print(f"[red]MISSING[/red] {cat.key}: stat_id {cat.yahoo} not in Yahoo's list")
            problems += 1
        else:
            console.print(f"[dim]{cat.yahoo:>3}[/dim]  {cat.label:<32} -> Yahoo: {actual}")
    console.print(
        f"\n{len(yahoo_names)} stat ids in Yahoo's catalogue, {problems} mapping problems.\n"
        "[dim]Eyeball the right-hand column; a name mismatch means the id moved.[/dim]"
    )


# ------------------------------------------------------------------- diff
@app.command("diff")
def diff_cmd(
    live: bool = typer.Option(False, "--live", help="Pull fresh instead of using snapshots"),
    show_matches: bool = typer.Option(False, "--all", help="Include already-matching categories"),
    out: Path = typer.Option(None, "--out", help="Write the markdown change-list here"),
) -> None:
    """Diff Sleeper (source of truth) against Yahoo (target)."""
    if live:
        from .sleeper import SleeperClient
        from .yahoo import YahooClient

        settings.require("sleeper_league_id", "yahoo_league_key")
        with SleeperClient() as s:
            sleeper_raw = s.scoring_settings(settings.sleeper_league_id)
        with YahooClient() as y:
            yahoo_raw = y.settings(settings.yahoo_league_key)
        _save("sleeper-scoring", sleeper_raw)
        _save("yahoo-settings", yahoo_raw)
    else:
        sleeper_league = json.loads(_latest("sleeper-league").read_text())
        sleeper_raw = sleeper_league.get("scoring_settings", sleeper_league)
        yahoo_raw = json.loads(_latest("yahoo-settings").read_text())

    result = diff_scoring(normalize_sleeper(sleeper_raw), normalize_yahoo(yahoo_raw))
    print_diff(result, show_matches=show_matches)

    if out:
        out.write_text(to_markdown(result))
        console.print(f"\n[green]change-list written to {out}[/green]")


@app.command("status")
def status() -> None:
    """Show which credentials are configured."""
    from .config import TOKEN_FILE

    rows = [
        ("SLEEPER_LEAGUE_ID", settings.sleeper_league_id),
        ("YAHOO_CLIENT_ID", settings.yahoo_client_id),
        ("YAHOO_CLIENT_SECRET", "set" if settings.yahoo_client_secret else None),
        ("YAHOO_LEAGUE_KEY", settings.yahoo_league_key),
        ("Yahoo token", "present" if TOKEN_FILE.exists() else None),
        ("FANTASYPROS_API_KEY", "set" if settings.fantasypros_api_key else None),
    ]
    for name, value in rows:
        mark = "[green]OK[/green]  " if value else "[red]--[/red]  "
        console.print(f"{mark}{name:<22} {value or ''}")


if __name__ == "__main__":
    app()
