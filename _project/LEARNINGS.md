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

## Sleeper API

- **Public and unauthenticated**, and read-only outright — there is no write path at
  all, in either direction. *doc, 2026-08-24.*
- **No history.** A deleted league is gone and the API cannot recover it. Snapshot
  before making changes. *asserted.*

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

## FantasyPros

- **The key is metered**, so responses cache to `data/raw/`. Leave caching on unless
  deliberately refreshing. *doc.*

## This repo

- **`ff diff` reads the newest snapshot of each kind** unless given `--live`. If a
  diff looks stale, check the timestamps in `data/snapshots/` before debugging logic.
- **Unmapped scoring keys are never dropped silently** — `normalize_*` collects them
  into `.unmapped` and the report surfaces them. Preserve that property when adding
  categories.
