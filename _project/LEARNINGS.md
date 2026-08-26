# Fantasy Football — Learnings

Platform traps and patterns discovered by doing. Check here before troubleshooting.

Every entry carries a confidence label — **verified (date)** · **asserted** · **doc**.
An unlabelled claim is unverified.

---

## Yahoo Fantasy API

- **The API cannot write league settings.** Write scopes cover rosters, add/drops,
  trades and draft picks. Stat categories and point values are commissioner-UI-only,
  and Yahoo locks most settings once the regular season starts — make every scoring
  change before week 1. *doc, 2026-08-24.*
- **Commissioner login is not API access.** You need a registered app at
  developer.yahoo.com for the consumer key/secret; your login only approves it. *doc.*
- **The redirect URI must be `https://`.** Yahoo rejects `http://`. The URL never has
  to resolve — the flow reads the `code=` out of the failed page's address bar. *doc.*
- **`format=json` is mandatory** or the API returns XML. *doc.*
- **The JSON is XML in a trenchcoat.** Objects arrive as `{"0": {...}, "1": {...},
  "count": n}` pseudo-arrays, and one logical record is split across sibling
  single-key dicts. Use `ff.yahoo.client.flatten`. Its merge deliberately refuses to
  combine siblings when a key repeats — a repeat means a real collection, and merging
  would silently keep only the last element. *verified 2026-08-24 (caught by a test).*
- **League keys are season-scoped** (`449.l.123456`). Last season's key does not
  resolve. *doc.*

- **Yahoo's app-creation page no longer offers a Fantasy Sports permission.** The only
  API Permissions on `developer.yahoo.com/apps/create` are OpenID Connect and TW
  Auction; the old "Fantasy Sports → Read/Write" checkbox is gone. Create the app with
  both unticked. *verified 2026-08-25 (observed on the page).*
- **The Fantasy Sports API is gated behind an approval application.** This is the
  reason the permission checkbox is gone. Apply at
  <https://sports.yahoo.com/developer/access/> — product description, data needed,
  estimated user count. Read-only by default; write needs justification. No published
  turnaround, and Yahoo says thin submissions are closed without correspondence.
  *verified 2026-08-25 (read the access page).* **Applied 2026-08-25** requesting
  read/write, justified as single-league and self-directed; outcome unknown.
- **Without that approval the OAuth flow fails in two different ways, neither obvious.**
  With no `scope` parameter the consent screen auto-approves, issues a token with
  `scope: null`, and every fantasy call 401s. With `scope=fspt-r` the authorize
  redirect returns `error=invalid_scope` before any token is issued. The second
  failure is the honest one, so `ff/yahoo/auth.py` now always sends `SCOPE = "fspt-r"`
  — a loud failure beats a token that looks valid and isn't.
  *verified 2026-08-25 (observed both).*
- **Choose Confidential Client**, not Public — `ff.yahoo.auth` exchanges the code with
  a client secret. *verified 2026-08-25 (read the source).*
- **There is no secret-rotation button.** The app page shows the Client Secret
  permanently but offers only Delete App. *verified 2026-08-25 (observed).*

- **The Yahoo draft room does not exist before draft day.** `/f1/<id>/draftclient`
  404s and `/f1/<id>/draftresults` serves an empty shell, so a pick-polling parser
  cannot be written or tested ahead of time except against a **mock draft**
  (`/f1/<id>/mock_lobby`). Yahoo's bot-only Instant Mock is behind Yahoo Plus.
  *verified 2026-08-25.*

## Sleeper API

- **Public and unauthenticated**, and read-only outright — there is no write path at
  all, in either direction. *doc, 2026-08-24.*
- **No history.** A deleted league is gone and the API cannot recover it. Snapshot
  before making changes. *asserted.*
- **`settings` is a flat int map with undocumented enums.** `waiver_type`,
  `waiver_day_of_week`, `playoff_type` and friends come back as bare integers with no
  labels. Guessing them is how a migration silently ports the wrong waiver system —
  read the value off the Sleeper UI instead. *verified 2026-08-25 (snapshot).*
- **The league object carries `previous_league_id`.** A returning league chains
  backwards through it; prior-season history lives there and does not migrate.
  *verified 2026-08-25 (snapshot).*

## Scoring translation

- **Yahoo stat ids are not guaranteed stable across seasons.** The table in
  `ff/scoring/mapping.py` is hardcoded; run `ff yahoo verify-mapping` against Yahoo's
  own catalogue each season before trusting a diff. *asserted — the failure mode is
  a silently wrong diff, which is worse than an error.*
- **Sleeper has scoring concepts Yahoo simply lacks**: positional reception premiums
  (`rec_te`/`rec_rb`/`rec_wr`), yardage-threshold bonuses, forced fumbles. These get
  status `unportable` in the diff — they need a decision, not an edit. *doc.*
- **2-point conversions are one combined category in Yahoo** (stat id 16) where
  Sleeper splits pass/rush/rec. One Yahoo value has to cover all three. *doc.*
- **The split-category collapse is only lossy if the values differ.** Check the Sleeper
  values before treating a collapse as a rule change — in this league all three 2-pt
  values are 2, so the combined Yahoo category is exact and there is nothing to tell
  the league. *verified 2026-08-25 (snapshot).*
- **`unmapped` is a claim about our table, not about Yahoo.** `fgm_50_59` and
  `fgm_60p` surfaced as unmapped on the first real pull, but Yahoo is believed to have
  a 50+ FG category — that makes it a `mapping.py` omission, not an unportable rule.
  Check Yahoo's catalogue before recording anything unmapped as a lost rule.
  *asserted 2026-08-25 — the Yahoo side is unconfirmed until `verify-mapping` runs.*
- **`verify-mapping` only checks the ids we already have.** It cannot tell you about
  Yahoo categories absent from `CANON`, so it will not catch an omission like the 50+
  FG bucket. Coverage in the other direction needs eyeballing the catalogue.
  *verified 2026-08-25 (read the command's source).*

## FantasyPros

- **The key is metered**, so responses cache to `data/raw/`. Leave caching on unless
  deliberately refreshing. *doc.*
- **Projections come back as component stats, not just fantasy points** — `pass_yds`,
  `pass_tds`, `pass_ints`, `rec_rec`, and so on, alongside a `points_half` baseline.
  This is what makes custom scoring possible; if it were pre-scored only, the whole
  custom-valuation idea would collapse. *verified 2026-08-25.*
- **Premium limits are 1 request/second and 500/day.** Enough for analysis, nowhere
  near enough to poll during a live draft. Anything live has to come from the browser,
  not this API. *doc — stated on the key page.*
- **There is no ADP endpoint on this plan** (`/nfl/{season}/adp` returns 403). The
  consensus-rankings endpoint carries `rank_ecr` plus `rank_min`/`max`/`ave`/`std`,
  and the spread is arguably better than ADP for judging whether a player survives to
  your next pick. *verified 2026-08-25.*
- **The rankings endpoint also carries `player_yahoo_id`**, which is the bridge to
  Yahoo rosters if API access is ever granted. *verified 2026-08-25.*
- **Kickers cannot be custom-scored.** FantasyPros projects one `fg` total with no
  distance split, so a 3/3/3/4/5 tier structure cannot be applied. `ff/draft/score.py`
  uses a blended value and flags it. *verified 2026-08-25.*
- **Their terms forbid redistribution.** Data stays in gitignored `data/raw/`, and the
  published draft board must stay private. *doc.*

## This repo

- **`ff diff` reads the newest snapshot of each kind** unless given `--live`. If a
  diff looks stale, check the timestamps in `data/snapshots/` before debugging logic.
- **Unmapped scoring keys are never dropped silently** — `normalize_*` collects them
  into `.unmapped` and the report surfaces them. Preserve that property when adding
  categories.
