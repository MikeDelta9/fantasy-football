# 2026 Season — Index

**Platform:** Yahoo (migrated from Sleeper, preseason 2026)
**League:** _name TBD_ · **Teams:** _TBD_ · **Scoring:** _TBD, see migration/_
**Last updated:** 2026-08-24

> **This file is the single source of truth for status.** Nothing else in the repo
> records whether something is done. If two files disagree, this one wins — and the
> other one is a bug.

---

## Phase status

| Phase | Status | Notes |
|---|---|---|
| Tooling scaffold | ✅ done | `ff` CLI, tests passing, 2026-08-24 |
| Credentials | ⬜ not started | Sleeper league ID, Yahoo dev app, FantasyPros key |
| Sleeper snapshot | ⬜ not started | `ff sleeper pull` — **do this first, it's unrecoverable** |
| Yahoo league created | ⬜ not started | |
| Mapping verified | ⬜ not started | `ff yahoo verify-mapping` |
| Scoring diff produced | ⬜ not started | `ff diff --out seasons/2026/migration/change-list.md` |
| Scoring applied in Yahoo | ⬜ not started | by hand; **must land before week 1** |
| Diff re-run clean | ⬜ not started | zero actionable rows |
| Non-scoring settings ported | ⬜ not started | rosters, waivers, playoffs — see migration/ |
| League informed of changes | ⬜ not started | any unportable rule needs saying out loud |
| Draft | ⬜ not started | |

## Key dates

| Date | What |
|---|---|
| _TBD_ | Draft |
| _TBD_ | NFL week 1 — **Yahoo locks most settings** |
| _TBD_ | Trade deadline |
| _TBD_ | Playoffs start |

## Weeks

| Week | File | Record | Notes |
|---|---|---|---|
| — | | | _add a row when the week's file is created_ |

## Open questions

| Question | Blocks | Raised |
|---|---|---|
| Which Sleeper scoring rules have no Yahoo equivalent, and what replaces them? | scoring apply | 2026-08-24 |

## Resume here

**Next step:** get the Sleeper league ID into `.env` and run `ff sleeper pull`.
Nothing else can be verified until there is a real league object to diff against.
