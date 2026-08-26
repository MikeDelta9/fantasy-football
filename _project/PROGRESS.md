# Fantasy Football — Progress Log

**Log started:** 2026-08-24

Session-by-session narrative: what happened, in order. Standing decisions belong in
`DECISIONS.md`; reusable gotchas belong in `LEARNINGS.md`; current status belongs in
the season index. This file is the story, not the state.

---

## Session Log

### 2026-08-24 — Project created; tooling scaffolded; context system built

**What came out of it**

1. **Scaffolded the repo** — Python + uv, `ff` CLI, read-only clients for Sleeper and
   Yahoo, a canonical scoring mapping, and normalize → diff → report. 6 tests passing.

2. **Established the hard constraint.** The Yahoo Fantasy Sports API has no endpoint
   for league scoring settings; its write scopes cover rosters, add/drops, trades and
   draft picks only. The migration therefore ends in a markdown change-list applied in
   the commissioner UI, not an API write. *verified 2026-08-24 (Yahoo API docs).*

3. **Split the knowledge base from ACT's.** A second compiler instance at
   `~/fantasy-memory-compiler`, selected by a router hook at
   `~/.claude/hooks/memory_router.py`. Personal and client work no longer mix in
   either direction.

4. **Built this context system** — `_project/` durable layer, `seasons/2026/` work
   units, the `ff-context` skill, and `/ffSave`.

**Open**

- No credentials yet: Sleeper league ID, Yahoo dev app, FantasyPros key.
- Nothing pulled from either platform, so the scoring mapping is unverified against
  a real league.

### 2026-08-25 — Sleeper baseline captured; league scoring is mostly portable

**What came out of it**

1. **Snapshotted the Sleeper league** — `DeBrey's League`, 12 teams, `pre_draft`,
   continuing from `previous_league_id` 1257434478813392896. This was the one
   irreversible step in the migration and it is now done:
   `data/snapshots/sleeper-league-20260826-003127.json`.

2. **Read the scoring.** 44 raw keys — 36 land on canonical categories, 8 do not.
   0.5 PPR, 6-pt passing TD, 1pt/25 pass yds, 1pt/10 rush+rec yds, standard DST
   point-allowed tiers.

3. **The expensive unportables don't apply.** No positional reception premiums
   (`rec_te`/`rec_wr`/`rec_rb` all absent) and no yardage-threshold bonuses. Those are
   the two categories that usually force a league-visible rule change, and this league
   has neither.

4. **Found a likely mapping gap rather than a rule problem.** `fgm_50_59` (5) and
   `fgm_60p` (6) come back unmapped. Yahoo is believed to have a 50+ FG category, which
   would make this a `mapping.py` omission, not an unportable rule — unconfirmed until
   `ff yahoo verify-mapping` runs against a live catalogue.

5. **Wrote the non-scoring port checklist** —
   `seasons/2026/migration/non-scoring-checklist.md`. Several Sleeper enum values
   (`waiver_type`, `waiver_day_of_week`, `playoff_type`) are recorded as raw ints with
   their interpretation explicitly marked unconfirmed, rather than guessed.

**Open**

- Yahoo dev app not registered; Yahoo league not created. Everything downstream blocks
  on the target existing.
- Forced fumbles (`ff`, 1 pt) still needs a decision — Yahoo scores recoveries only.
- Six special-teams/defense keys unmapped: `st_ff`, `st_fum_rec`, `st_td`,
  `def_st_ff`, `def_st_fum_rec`, `def_2pt`.
- `draft_rounds` = 3 against a 16-slot roster looks misconfigured on Sleeper.
