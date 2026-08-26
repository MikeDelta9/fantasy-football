# fantasy-football

League tooling for moving a dynasty/redraft league off Sleeper and onto Yahoo,
plus FantasyPros projection work once the league is live.

## Quick start

```bash
cd ~/projects/fantasy-football
cp .env.example .env          # fill in as you go
uv sync
uv run ff status              # shows what's still missing
```

## The migration, end to end

```bash
uv run ff sleeper pull                     # snapshot the Sleeper league
uv run ff yahoo login                      # one-time OAuth (see docs/yahoo-setup.md)
uv run ff yahoo leagues                    # find your YAHOO_LEAGUE_KEY
uv run ff yahoo verify-mapping             # sanity-check stat ids for this season
uv run ff yahoo pull                       # snapshot Yahoo league settings
uv run ff diff --out docs/change-list.md   # what to change in Yahoo
```

### If Yahoo has not granted you API access

Yahoo gates the Fantasy Sports API behind an approval process
(<https://sports.yahoo.com/developer/access/>). Without it, `ff yahoo pull` and
`verify-mapping` cannot run: the authorize call returns `invalid_scope`.

The settings are still readable from the commissioner UI. Scrape the scoring and
settings tables off the league's *Scoring & Settings* page into JSON, then:

```bash
uv run ff yahoo import-ui scraped.json --league-id <your league id>
uv run ff diff --out change-list.md
```

`import-ui` writes into the same snapshot slot `ff yahoo pull` uses, so the API
path drops in unchanged if access is ever granted. It matches on **Yahoo's UI
labels, not stat ids** — the ids in `ff/scoring/mapping.py` cannot be verified
without the API, so nothing depends on them.

`ff diff` reads the newest snapshots in `data/snapshots/`; add `--live` to pull
fresh from both platforms instead.

## Why the last step is manual

Yahoo's Fantasy Sports API is **read-only for league settings**. Its write
scopes cover rosters, add/drops, trades and draft picks — nothing that sets
stat categories or point values. `ff diff --out` therefore produces an ordered
change-list you apply in *League Settings → Edit League Settings → Modify Stat
Categories*. See `docs/league-migration.md` for the browser-automation option.

## Layout

```
src/ff/
  config.py            .env-backed settings, paths
  cli.py               the `ff` command
  sleeper/client.py    public read-only API
  yahoo/auth.py        OAuth2 + token refresh
  yahoo/client.py      Fantasy Sports API + JSON flattener
  fantasypros/client.py  projections/rankings, cached to data/raw
  scoring/mapping.py   canonical categories <-> Sleeper keys <-> Yahoo stat ids
  scoring/normalize.py both platforms -> {canonical_key: points}
  scoring/diff.py      comparison, with an "unportable" status
  scoring/report.py    terminal table + markdown change-list
data/snapshots/        timestamped API pulls (gitignored)
data/raw/              FantasyPros response cache (gitignored)
docs/                  setup guides and runbooks
_project/              durable knowledge — context, progress, decisions,
                       learnings, threads, operations registry
seasons/2026/          season work: migration, draft, weeks, deliverables
```

See `CLAUDE.md` or the `ff-context` skill for which file owns which kind of fact.

## Tests

```bash
uv run pytest
uv run ruff check
```
