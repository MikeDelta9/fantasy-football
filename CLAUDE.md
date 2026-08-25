# CLAUDE.md

Fantasy football league tooling. Python 3.11+, managed with `uv`.

## Commands

```bash
uv sync                  # install
uv run ff --help         # CLI entry point (src/ff/cli.py)
uv run pytest            # tests
uv run ruff check        # lint
```

Never `pip install` here — the environment is uv-managed and `pyproject.toml`
is the source of truth for dependencies.

## The constraint that shapes this project

**Yahoo's Fantasy Sports API cannot write league settings.** Write scopes cover
rosters, add/drops, trades and draft picks only. Scoring categories and point
values are commissioner-UI-only. Any suggestion that ends in "then POST the new
scoring settings to Yahoo" is wrong — the deliverable is a change-list a human
(or browser automation) applies. Sleeper's API is read-only outright.

Direction of travel: **Sleeper is the source of truth, Yahoo is the target.**

## Things that bite

- **Yahoo's JSON is XML-shaped.** Objects come back as `{"0": {...}, "1": {...},
  "count": n}` pseudo-arrays, and one logical record is split across sibling
  single-key dicts. Use `ff.yahoo.client.flatten`, never hand-index the raw
  payload. `flatten` deliberately refuses to merge sibling dicts when a key
  repeats — that case is a real collection and merging would silently keep only
  the last element.
- **Yahoo stat ids are not guaranteed stable across seasons** and the table in
  `ff/scoring/mapping.py` is hardcoded. Run `ff yahoo verify-mapping` against
  Yahoo's own catalogue before trusting any diff in a new season.
- **Yahoo league keys are season-scoped** (`449.l.123456`). Last year's key
  404s. Re-run `ff yahoo leagues` each season.
- **`format=json` is mandatory** on every Yahoo call or you get XML back.
- **Unmapped scoring keys are never dropped silently.** `normalize_*` collects
  anything the mapping table doesn't know into `.unmapped` and the report
  surfaces it. Keep that property when adding categories.
- **Sleeper has scoring concepts Yahoo lacks** (positional PPR premiums,
  yardage-threshold bonuses, forced fumbles). Those get status `unportable`, not
  `missing_in_target` — they need a decision, not an edit. Log the decision in
  `docs/decisions/`.

## Context system

Load the **`ff-context`** skill before working here — it maps where knowledge lives.
The short version:

| Kind of fact | Owner |
|---|---|
| Current status of anything | `seasons/<year>/SEASON_INDEX.md` — **the only place** |
| What happened, in order | `_project/PROGRESS.md` |
| Standing decisions | `_project/DECISIONS.md` |
| Platform traps | `_project/LEARNINGS.md` |
| How scoring travels Sleeper→Yahoo | `_project/threads/scoring-and-settings.md` |
| What this project can do | `_project/operations/REGISTRY.md` |
| Week-by-week decisions | `seasons/<year>/weeks/week-NN.md` |
| Things league members read | `seasons/<year>/deliverables/` |

Rules that keep it from rotting:

- **One place per fact.** If status appears outside the season index, that's a bug.
- **Threads are maps, not stores** — no status in them, ever.
- **Label claims** in threads and learnings: `verified (date)` · `asserted` · `doc`.
  Unlabelled means unverified.
- The scoring table inside `ff-context/SKILL.md` is **generated**. Regenerate with
  `python3 ~/.claude/skills/ff-context/scripts/build_scoring_table.py --write`;
  never hand-edit it.

Save with **`/ffSave`** — it updates the durable files, commits, and flushes the
conversation to `~/fantasy-memory-compiler` (this project's own knowledge base, kept
separate from the ACT client one).

## Conventions

- Snapshots go to `data/snapshots/<source>-<UTC timestamp>.json` and are
  gitignored. `ff diff` uses the newest of each unless given `--live`.
- FantasyPros responses cache to `data/raw/`; the API key is metered, so leave
  caching on unless you're deliberately refreshing.
- Secrets live in `.env` and `.yahoo_token.json`, both gitignored. Never print a
  token or key to the terminal or into a snapshot file.
- Author metadata, where required, is **Michael DeBrey**.
