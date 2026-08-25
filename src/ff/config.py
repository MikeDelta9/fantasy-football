"""Environment-backed settings. Everything optional so partial setup still runs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
SNAPSHOTS = DATA / "snapshots"
TOKEN_FILE = ROOT / ".yahoo_token.json"

load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    sleeper_league_id: str | None = os.getenv("SLEEPER_LEAGUE_ID") or None
    yahoo_client_id: str | None = os.getenv("YAHOO_CLIENT_ID") or None
    yahoo_client_secret: str | None = os.getenv("YAHOO_CLIENT_SECRET") or None
    yahoo_redirect_uri: str = os.getenv("YAHOO_REDIRECT_URI", "https://localhost:8099/callback")
    yahoo_league_key: str | None = os.getenv("YAHOO_LEAGUE_KEY") or None
    fantasypros_api_key: str | None = os.getenv("FANTASYPROS_API_KEY") or None

    def require(self, *names: str) -> None:
        missing = [n for n in names if not getattr(self, n)]
        if missing:
            raise SystemExit(
                "Missing required settings in .env: "
                + ", ".join(n.upper() for n in missing)
                + "\nSee .env.example and docs/yahoo-setup.md"
            )


settings = Settings()

for _d in (RAW, SNAPSHOTS):
    _d.mkdir(parents=True, exist_ok=True)
