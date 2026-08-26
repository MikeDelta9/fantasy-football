# 2026 Season — Index

**Platform:** Yahoo (migrated from Sleeper, preseason 2026)
**League:** DeBrey's League · **Teams:** 12 · **Scoring:** 0.5 PPR, 6-pt pass TD (see migration/)
**Last updated:** 2026-08-25

> **This file is the single source of truth for status.** Nothing else in the repo
> records whether something is done. If two files disagree, this one wins — and the
> other one is a bug.

---

## Phase status

| Phase | Status | Notes |
|---|---|---|
| Tooling scaffold | ✅ done | `ff` CLI, tests passing, 2026-08-24 |
| Credentials | 🟡 partial | Sleeper ID set; Yahoo dev app + FantasyPros key outstanding |
| Sleeper snapshot | ✅ done | `sleeper-league-20260826-003127.json`, 2026-08-25 |
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
| 2-pt conversions: Yahoo has one combined category, Sleeper splits pass/rush/rec (all =2) | scoring apply | 2026-08-25 |
| Forced fumbles (1 pt) have no Yahoo equivalent — drop, or absorb into another category? | scoring apply | 2026-08-25 |
| `fgm_50_59`/`fgm_60p` unmapped — Yahoo bug in `mapping.py` or genuinely absent? | scoring diff | 2026-08-25 |
| `draft_rounds` is 3 against a 16-slot roster — misconfigured on Sleeper? | draft | 2026-08-25 |

## Resume here

**Next step:** register the Yahoo dev app (`docs/yahoo-setup.md`), create the 2026
Yahoo league in the UI, then `ff yahoo login` → `ff yahoo leagues` → `ff yahoo pull`.
The Sleeper side is captured and safe; everything now blocks on the Yahoo target existing.
