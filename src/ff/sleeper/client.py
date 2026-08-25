"""Sleeper read-only API client.

Sleeper's v1 API is public and unauthenticated; it is also read-only, which is
why the migration writes land on the Yahoo side.
"""

from __future__ import annotations

from typing import Any

import httpx

BASE = "https://api.sleeper.app/v1"


class SleeperClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self._http = httpx.Client(base_url=BASE, timeout=timeout)

    def _get(self, path: str) -> Any:
        r = self._http.get(path)
        r.raise_for_status()
        return r.json()

    def league(self, league_id: str) -> dict[str, Any]:
        """Full league object: settings, scoring_settings, roster_positions."""
        return self._get(f"/league/{league_id}")

    def scoring_settings(self, league_id: str) -> dict[str, float]:
        return self.league(league_id).get("scoring_settings") or {}

    def roster_positions(self, league_id: str) -> list[str]:
        return self.league(league_id).get("roster_positions") or []

    def rosters(self, league_id: str) -> list[dict[str, Any]]:
        return self._get(f"/league/{league_id}/rosters")

    def users(self, league_id: str) -> list[dict[str, Any]]:
        return self._get(f"/league/{league_id}/users")

    def drafts(self, league_id: str) -> list[dict[str, Any]]:
        return self._get(f"/league/{league_id}/drafts")

    def previous_league_id(self, league_id: str) -> str | None:
        return self.league(league_id).get("previous_league_id")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SleeperClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
