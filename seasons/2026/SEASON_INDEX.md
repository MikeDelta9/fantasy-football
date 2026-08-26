# 2026 Season — Index

**Platform:** Yahoo (reactivating the league's original Yahoo home, preseason 2026)
**Path travelled:** Yahoo (original) → ESPN → Sleeper → Yahoo. Scoring was re-entered by
hand at each hop to match the Yahoo original, so this diff is a **drift check**, not a port.
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
| Credentials | 🟡 partial | Dev app + OAuth wired. **Yahoo API access applied for 2026-08-25** — awaiting their decision, no published turnaround. Requested read/write (`fspt-w`). Not blocking: the UI-import path covers the migration. FantasyPros key outstanding |
| Sleeper snapshot | ✅ done | `sleeper-league-20260826-003127.json`, 2026-08-25 |
| Yahoo league reactivated | ✅ done | already renewed: **ID# <league-id>**, auto-renew on, 12 teams, settings carried forward |
| Mapping verified | ⚪ n/a for now | needs the API. The UI path matches on labels, not stat ids, so no unverified id is trusted |
| Scoring diff produced | ✅ done | 2026-08-25 — 31 exact matches, 1 real difference, 3 accepted exceptions |
| Scoring applied in Yahoo | ✅ nothing to apply | all three disagreements resolved in Yahoo's favour — the league is already configured correctly |
| Diff re-run clean | ✅ as clean as it gets | the 5 remaining rows are the accepted exceptions in DECISIONS.md, not work |
| Non-scoring settings compared | ✅ done | **all settings compared 2026-08-25** — scoring, season/playoffs, trades, waivers, roster slots. Roster is an exact match. All settings changes applied and verified 2026-08-25 (veto votes 6, postponed-game status Yes, trade deadline wk 11). Open decision: Can't Cut List |
| League informed of changes | ⬜ not started | 3 real changes to announce: INT -1→-2, 60+ FG 6→5, forced fumbles gone |
| Draft | ⬜ not started | |

## Key dates

| Date | What |
|---|---|
| **Sun Aug 30, 9:30pm EDT** | **Live standard draft** — 1 min/pick |
| _TBD_ | NFL week 1 — **Yahoo locks most settings** |
| Nov 28, 2026 | Trade deadline |
| Week 15 | Playoffs — 6 teams, weeks 15-17, ends Mon Jan 4 |

## Weeks

| Week | File | Record | Notes |
|---|---|---|---|
| — | | | _add a row when the week's file is created_ |

## Open questions

| Question | Blocks | Raised |
|---|---|---|
| Sleeper ran a losers bracket (`loser_bracket_id` set); Yahoo has no consolation-bracket setting — does the toilet bowl matter? | league announcement | 2026-08-25 |
| 6 of 12 teams / 3 rounds gives seeds 1-2 a week-15 bye — is that the intended bracket? | draft | 2026-08-25 |
| Yahoo gated the Fantasy API behind an approval form with no published turnaround — apply and wait, or read the settings out of the commissioner UI instead? | the entire Yahoo pull | 2026-08-25 |
| `draft_rounds` is 3 against a 16-slot roster — misconfigured on Sleeper? | draft | 2026-08-25 |

## Resume here

**Scoring is done — nothing to apply in Yahoo before the draft.** The diff found 31
exact matches and one real difference (interceptions), resolved in Yahoo's favour.
See `_project/DECISIONS.md` for the three accepted exceptions.

**Next steps, in order:**
1. Tell the league the 3 real changes (INT -2, 60+ FG pays 5, no forced-fumble points)
   — draft is Sunday, so this wants saying before then.
2. ~~Apply for Yahoo Fantasy API access~~ — **submitted 2026-08-25**, awaiting Yahoo.
   If granted with write, change `SCOPE` in `src/ff/yahoo/auth.py` from `fspt-r` to
   `fspt-w` and re-run `ff yahoo login`.
3. FantasyPros key, then draft prep.

_Superseded — kept for the record:_ register the Yahoo dev app (`docs/yahoo-setup.md`) — `ff status` shows
`YAHOO_CLIENT_ID`/`SECRET` still empty, and nothing Yahoo-side can run without them.
Then renew the original league for 2026 in the Yahoo UI (renew, don't create — a fresh
league starts on Yahoo defaults and throws away the settings this whole exercise is
trying to preserve), then `ff yahoo login` → `ff yahoo leagues` → `ff yahoo pull` →
`ff yahoo verify-mapping` → `ff diff`.

The Sleeper side is captured and safe. Expect the diff to be small; if it isn't,
suspect the mapping table before believing the numbers.
