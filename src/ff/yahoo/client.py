"""Yahoo Fantasy Sports API client.

Scope note: the Fantasy Sports API is READ-ONLY for league settings. Its write
endpoints cover roster/lineup changes, add/drops, trades and draft picks only.
There is no endpoint that sets a league's stat categories or point values, so
scoring changes are applied by a human (or by browser automation) in the Yahoo
commissioner UI. See docs/league-migration.md.
"""

from __future__ import annotations

from typing import Any

import httpx

from .auth import YahooAuth

BASE = "https://fantasysports.yahooapis.com/fantasy/v2"


class YahooClient:
    def __init__(self, auth: YahooAuth | None = None, timeout: float = 30.0) -> None:
        self.auth = auth or YahooAuth()
        self._http = httpx.Client(base_url=BASE, timeout=timeout)

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        params.setdefault("format", "json")
        r = self._http.get(
            path,
            params=params,
            headers={"Authorization": f"Bearer {self.auth.access_token()}"},
        )
        r.raise_for_status()
        return r.json()

    # ---- discovery -----------------------------------------------------
    def my_leagues(self, game_key: str = "nfl") -> dict[str, Any]:
        """Every league the authenticated user is in, for the given game."""
        return self._get(f"/users;use_login=1/games;game_keys={game_key}/leagues")

    # ---- league --------------------------------------------------------
    def league(self, league_key: str) -> dict[str, Any]:
        return self._get(f"/league/{league_key}")

    def settings(self, league_key: str) -> dict[str, Any]:
        """Raw settings payload, including stat_categories and stat_modifiers."""
        return self._get(f"/league/{league_key}/settings")

    def stat_categories(self, game_key: str = "nfl") -> dict[str, Any]:
        """Game-level stat id -> name catalogue. Use this to VERIFY the mapping
        table in ff.scoring.mapping rather than trusting hardcoded ids."""
        return self._get(f"/game/{game_key}/stat_categories")

    def teams(self, league_key: str) -> dict[str, Any]:
        return self._get(f"/league/{league_key}/teams")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "YahooClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


# --- Yahoo's JSON is XML-shaped: numeric string keys + "count". ----------
def flatten(node: Any) -> Any:
    """Collapse Yahoo's {"0": {...}, "1": {...}, "count": n} pseudo-arrays into
    real lists, recursively. Makes the settings payload navigable."""
    if isinstance(node, dict):
        keys = set(node) - {"count"}
        if keys and all(k.isdigit() for k in keys):
            return [flatten(node[k]) for k in sorted(keys, key=int)]
        return {k: flatten(v) for k, v in node.items() if k != "count"}
    if isinstance(node, list):
        items = [flatten(x) for x in node]
        items = [i for i in items if i not in ([], {})]
        dicts = [i for i in items if isinstance(i, dict)]
        # Yahoo splits one logical object across sibling single-key dicts. Merge
        # those, but only when no key repeats -- a repeat means it is a real
        # collection (several <stat> entries) and merging would drop all but one.
        if dicts and len(dicts) == len(items):
            merged: dict[str, Any] = {}
            collision = False
            for d in dicts:
                if any(k in merged for k in d):
                    collision = True
                    break
                merged.update(d)
            if not collision:
                return merged
        return items
    return node
