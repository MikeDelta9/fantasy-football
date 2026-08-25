# Fantasy Football — Project Context

**Type:** Personal (not a client engagement — kept deliberately separate from ACT)
**Owner / commissioner:** Michael DeBrey
**Repo:** `~/projects/fantasy-football` (git-backed)
**Knowledge base:** `~/fantasy-memory-compiler` — its own instance, isolated from the ACT KB

---

## What this project is

Two things that share a codebase:

1. **The migration** — moving the league off Sleeper and onto Yahoo, with scoring
   settings carried across faithfully. One-time, 2026 preseason.
2. **Ongoing league operations** — FantasyPros-driven analysis, draft prep, in-season
   decisions, and commissioner admin. Open-ended by design; see
   `_project/operations/REGISTRY.md`.

## Platforms

| Platform | Auth | Read | Write |
|---|---|---|---|
| Sleeper | none (public API) | full league object, scoring, rosters, users, drafts | **none** |
| Yahoo Fantasy | OAuth2, registered dev app | league settings, teams, rosters, transactions | rosters, add/drops, trades, draft picks — **never league settings** |
| FantasyPros | `x-api-key` (paid) | projections, consensus rankings, players | n/a |

**Direction of travel: Sleeper is the source of truth, Yahoo is the target.**

The constraint that shapes everything: Yahoo's API cannot write league scoring.
Any plan ending in "POST the settings to Yahoo" is wrong. The migration
terminates in a change-list a human applies in the commissioner UI.

## Roles

Michael is commissioner on both platforms, so nothing here is blocked on another
person's access. League members are an **audience** — anything they read is a
deliverable and lives in `seasons/<year>/deliverables/`.

## Where things live

| What | Where |
|---|---|
| Durable, slow-changing knowledge | `_project/` |
| Cross-cutting maps | `_project/threads/` |
| Bespoke operations catalogue | `_project/operations/REGISTRY.md` |
| Season status — one place per fact | `seasons/<year>/SEASON_INDEX.md` |
| Weekly work record | `seasons/<year>/weeks/week-NN.md` |
| Things league members see | `seasons/<year>/deliverables/` |
| Throwaway | `seasons/<year>/scratch/` |
| Tool/setup docs | `docs/` |
| API snapshots | `data/snapshots/` (gitignored) |

## Conventions

- **Never list Claude as author** — use Michael DeBrey.
- **One place per fact.** Status lives in `SEASON_INDEX.md` and nowhere else.
  Threads are maps, not stores.
- **Label every claim** in threads and learnings: **verified (date)** — observed on
  the platform · **asserted** — reasoned, untested · **doc** — from platform
  documentation, may not match reality. An unlabelled claim is treated as
  unverified, so forgetting a label degrades safely.
- **Snapshot before you change anything.** Sleeper leagues can be deleted and the
  API has no history; Yahoo locks settings once the season starts.
- Save a session with **`/ffSave`**.
