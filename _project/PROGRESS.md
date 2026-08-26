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

## 2026-08-25 — Yahoo target read, scoring diff closed

- Learned the league's real history: **Yahoo → ESPN → Sleeper → Yahoo**, with scoring
  hand-matched to the Yahoo original at every hop. Reframed the migration from a port
  to a **drift check** and recorded it in `PROJECT_CONTEXT.md`.
- Registered the Yahoo dev app and wired OAuth. Then hit the real blocker:
  **Yahoo now gates the Fantasy Sports API behind an approval process.** The app page
  no longer offers a Fantasy Sports permission, and `scope=fspt-r` returns
  `invalid_scope`. Not applied for yet.
- Worked around it: read the settings straight out of the commissioner UI. New
  `ff yahoo import-ui` writes a snapshot into the same slot `ff yahoo pull` uses, so
  the API path drops in unchanged if access is ever granted. Matching is by **label,
  not stat id** — the hardcoded ids stay unverifiable without the API, so nothing
  depends on them.
- Also added: `yahoo_ui` labels in the mapping table, `normalize_yahoo_ui`, a
  `no_effect` diff status (a 0-value category absent on the other side is not work),
  and 7 tests. 13 pass.
- **Result: 31 of 36 categories match exactly.** One real difference (interceptions
  thrown, -1 vs -2) and three unportable rules. All resolved in Yahoo's favour, so
  **there is nothing to apply before the draft.** See `DECISIONS.md`.
- Non-scoring settings compared too. Rosters, waivers, playoffs, trades all match.
  **Open: Sleeper allowed 1 keeper, Yahoo has no keeper setting** — needs an answer
  before Sun Aug 30.
- Drafted the league announcement: `seasons/2026/deliverables/scoring-changes-2026.md`.

## 2026-08-25 (cont.) — settings audit closed

- Compared every remaining league setting against Sleeper: season length, playoffs,
  trades, waivers, roster rules, and per-slot roster counts. **Roster is an exact
  match** (9 starters / 7 bench / 1 IR, flex confirmed `W/R/T`, no IDP, no superflex).
- Commissioner applied three changes, since verified on the edit form: veto votes
  Default → **6**, postponed-game injury status No → **Yes**, trade deadline
  Nov 28 → **Nov 21** (week 11, matching Sleeper).
- `lock_benched_players` left at No on purpose — matches Sleeper's `bench_lock: 0`
  and the league's unlimited-acquisitions setup.
- Yahoo settings were read via the **edit-settings and roster-position forms**, which
  expose true selected values where the summary page only renders a string.
- Still no Fantasy API access — everything above was browser automation against the
  commissioner UI, not the API.
