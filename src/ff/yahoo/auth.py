"""Yahoo OAuth2 (authorization code) with on-disk token refresh.

Yahoo requires an https redirect URI, so the local callback listener is not
usable without a cert. The flow below prints the authorize URL, you approve it
in the browser, and paste the `code=` value back in. Tokens live in
.yahoo_token.json (gitignored) and refresh automatically after that.
"""

from __future__ import annotations

import json
import time
import webbrowser
from typing import Any

import httpx

from ..config import TOKEN_FILE, settings

AUTHORIZE_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"


class YahooAuth:
    def __init__(self) -> None:
        settings.require("yahoo_client_id", "yahoo_client_secret")
        self.client_id = settings.yahoo_client_id
        self.client_secret = settings.yahoo_client_secret
        self.redirect_uri = settings.yahoo_redirect_uri

    # ---- token storage -------------------------------------------------
    def _load(self) -> dict[str, Any] | None:
        if TOKEN_FILE.exists():
            return json.loads(TOKEN_FILE.read_text())
        return None

    def _save(self, token: dict[str, Any]) -> None:
        token["expires_at"] = time.time() + int(token.get("expires_in", 3600)) - 60
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
        TOKEN_FILE.chmod(0o600)

    # ---- flows ---------------------------------------------------------
    def authorize_url(self) -> str:
        return (
            f"{AUTHORIZE_URL}?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}&response_type=code&language=en-us"
        )

    def login(self, open_browser: bool = True) -> dict[str, Any]:
        url = self.authorize_url()
        print("\n1. Approve access here:\n   " + url)
        if open_browser:
            webbrowser.open(url)
        print(
            "\n2. Yahoo redirects to a localhost URL that will fail to load. "
            "That is expected.\n   Copy the `code=` value out of the address bar."
        )
        code = input("\nPaste the code: ").strip()
        token = self._exchange(code)
        self._save(token)
        print(f"\nToken saved to {TOKEN_FILE}")
        return token

    def _exchange(self, code: str) -> dict[str, Any]:
        r = httpx.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def _refresh(self, refresh_token: str) -> dict[str, Any]:
        r = httpx.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def access_token(self) -> str:
        token = self._load()
        if not token:
            raise SystemExit("No Yahoo token. Run: ff yahoo login")
        if token.get("expires_at", 0) < time.time():
            token = self._refresh(token["refresh_token"])
            self._save(token)
        return token["access_token"]
