# Yahoo API setup

Commissioner login is not enough on its own — the API authenticates *apps*, and
your login only approves one. Ten minutes, once.

## 1. Register the app

1. Go to <https://developer.yahoo.com/apps/create/> and sign in with the Yahoo
   account that commissions the league.
2. Fill in:
   - **Application Name**: anything (`ff-league-tools`)
   - **Application Type**: Web Application
   - **Redirect URI (Callback Domain)**: `https://localhost:8099/callback`
     Yahoo rejects plain `http://` here. The URL never has to resolve — the flow
     below reads the code out of the address bar after the page fails to load.
   - **OAuth Client Type**: **Confidential Client** — the token exchange in
     `ff.yahoo.auth` sends a client secret, which is what this setting means.
   - **API Permissions**: leave everything unticked. **verified (2026-08-25)** —
     Yahoo no longer offers a Fantasy Sports permission on this page; the only
     options are OpenID Connect and TW Auction. Tick neither. OpenID Connect is
     identity, not fantasy data, and switching it on changes the token flow
     (nonce / `id_token`) in ways `ff yahoo login` does not handle.

     Historic note: this step used to read "tick Fantasy Sports → Read/Write".
     That checkbox is gone. Read/Write never unlocked league-settings writes
     anyway — those don't exist.
3. Create it. Copy the **Client ID (Consumer Key)** and **Client Secret** from the
   app page. Both stay visible on that page afterwards, but there is no rotate
   button — only **Delete App** and start over.

### If Fantasy calls come back 401/403

`YahooAuth.authorize_url()` sends no `scope` parameter, because scope used to come
from the app's permissions — the ones this page no longer lets you set. Yahoo
appears to grant Fantasy read to apps created this way. **asserted** — if
`ff yahoo leagues` returns 401 or 403, append `&scope=fspt-r` to the authorize URL
in `src/ff/yahoo/auth.py` and re-run `ff yahoo login`.

## 2. Put them in .env

```
YAHOO_CLIENT_ID=<consumer key>
YAHOO_CLIENT_SECRET=<consumer secret>
YAHOO_REDIRECT_URI=https://localhost:8099/callback
```

## 3. Authorize

```bash
uv run ff yahoo login
```

Approve in the browser. Yahoo redirects to `https://localhost:8099/callback?code=…`
which **will show a connection error — that is expected**. Copy the value of
`code=` out of the address bar and paste it at the prompt.

The refresh token lands in `.yahoo_token.json` (gitignored, chmod 600) and
renews itself from then on. Yahoo refresh tokens are long-lived but not
permanent; if calls start returning 401, re-run `ff yahoo login`.

## 4. Find the league key

```bash
uv run ff yahoo leagues
```

League keys look like `449.l.123456` — `<game_key>.l.<league_id>`. The game key
changes every NFL season, so a key from last year won't resolve. Put it in
`YAHOO_LEAGUE_KEY`.

## Gotchas

- **Rate limits** aren't published; they're generous for this workload but
  every call here snapshots to `data/snapshots/` so you can re-run the diff
  without re-pulling.
- **`format=json` is mandatory.** The API is XML-first; without it you get XML.
  `YahooClient._get` sets it for you.
- **The JSON is XML in a trenchcoat** — objects arrive as `{"0": {...}, "1": {...},
  "count": 2}` pseudo-arrays and one logical record is often split across
  sibling single-key dicts. `ff.yahoo.client.flatten` untangles both; don't
  hand-index the raw payload.
