"""FantasyPros API client.

Auth is a plain `x-api-key` header on a paid key from
https://www.fantasypros.com/api/. Responses are cached under data/raw so
repeated analysis runs don't burn quota.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from ..config import RAW, settings

BASE = "https://api.fantasypros.com/public/v2/json"


class FantasyProsClient:
    def __init__(self, api_key: str | None = None, cache: bool = True) -> None:
        self.api_key = api_key or settings.fantasypros_api_key
        if not self.api_key:
            raise SystemExit("Missing FANTASYPROS_API_KEY in .env")
        self.cache = cache
        self._http = httpx.Client(
            base_url=BASE, timeout=30.0, headers={"x-api-key": self.api_key}
        )

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        slug = (path.strip("/").replace("/", "_") + "_" +
                "_".join(f"{k}-{v}" for k, v in sorted(params.items())))
        cache_file = RAW / f"fantasypros_{slug}.json"
        if self.cache and cache_file.exists():
            return json.loads(cache_file.read_text())

        r = self._http.get(path, params=params)
        r.raise_for_status()
        data = r.json()
        if self.cache:
            cache_file.write_text(json.dumps(data, indent=2))
        return data

    def projections(
        self, season: int, week: int | str = "draft", position: str = "ALL", scoring: str = "PPR"
    ) -> dict[str, Any]:
        """week='draft' for preseason full-season projections, else 1-18."""
        return self._get(
            f"/nfl/{season}/projections", position=position, week=week, scoring=scoring
        )

    def rankings(
        self, season: int, week: int | str = "draft", position: str = "ALL", scoring: str = "PPR"
    ) -> dict[str, Any]:
        return self._get(
            f"/nfl/{season}/consensus-rankings", position=position, week=week, scoring=scoring
        )

    def players(self, season: int) -> dict[str, Any]:
        return self._get(f"/nfl/{season}/players")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "FantasyProsClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
