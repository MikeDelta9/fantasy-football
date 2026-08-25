# Sleeper → Yahoo migration runbook

**Direction:** Sleeper is the platform of record. Yahoo is the target and the
thing that gets edited.

## The one hard constraint

The Yahoo Fantasy Sports API cannot write league settings. Its write endpoints
are limited to:

- roster / lineup changes (`PUT .../roster`)
- add, drop, add-drop transactions
- trade proposals and responses
- draft picks

There is **no** endpoint for stat categories, stat modifiers, roster slots,
playoff structure, or waiver rules. Those are commissioner-UI-only, and Yahoo
locks most of them once the regular season begins. Plan to make every scoring
change before week 1.

## Steps

1. **Snapshot Sleeper.** `ff sleeper pull` — writes the whole league object
   (scoring, roster positions, waiver settings) to `data/snapshots/`. Do this
   before anything else; Sleeper leagues can be deleted and the API has no
   history.
2. **Create the Yahoo league** in the UI, custom settings, matching team count.
3. **Authorize the API.** `docs/yahoo-setup.md`, then `ff yahoo login`.
4. **Verify the stat-id mapping.** `ff yahoo verify-mapping`. The ids in
   `ff/scoring/mapping.py` are the standard NFL set but Yahoo has added ids over
   the years; this command checks them against Yahoo's own catalogue. Fix
   `mapping.py` before trusting a diff.
5. **Snapshot Yahoo.** `ff yahoo pull`.
6. **Diff.** `ff diff --out docs/change-list.md`.
7. **Apply** the change-list in *League Settings → Edit League Settings →
   Modify Stat Categories*.
8. **Re-pull and re-diff** to confirm you land at zero actionable rows.

## Reading the diff statuses

| Status | Meaning |
|---|---|
| `OK` | Same value on both platforms. |
| `CHANGE` | Category exists on both, values differ. Edit Yahoo. |
| `ADD` | Scored in Sleeper, absent in Yahoo. Enable it in Yahoo. |
| `REMOVE?` | Scored in Yahoo, absent in Sleeper. Usually a Yahoo default you want zeroed. |
| `NO YAHOO EQUIV` | No Yahoo stat category exists. Needs a decision, not an edit. |
| unmapped | The mapping table doesn't know the key. Review by hand and add it to `mapping.py`. |

## Known unportable categories

Sleeper scoring rules with no Yahoo counterpart:

- **Positional reception premiums** (`rec_te`, `rec_rb`, `rec_wr`, `bonus_rec_te`).
  Yahoo has a single league-wide reception value. TE premium is the common one —
  the usual substitute is a flat TE bonus that Yahoo also lacks, so most leagues
  drop it and note the change to the members.
- **Yardage bonuses** (`bonus_rush_yd_100`, `bonus_rec_yd_100` and friends).
  Yahoo has no threshold bonuses at all.
- **Forced fumbles** (`ff`) — Yahoo scores fumble *recoveries* only.
- **2-point conversions** are one combined Yahoo category (stat id 16) where
  Sleeper splits pass/rush/rec. Yahoo's value has to cover all three.

Record whatever you decide in `docs/decisions/` so next season's diff doesn't
re-litigate it.

## If you want the edits automated

The change-list is designed to be handed to browser automation — the
`claude-in-chrome` skill can drive the Yahoo commissioner settings form. Treat
that as an accelerator, not a source of truth: screenshot the resulting settings
page and re-run `ff diff` to confirm, because a silently missed field in a long
form is the exact failure mode this whole project exists to prevent.

## Not covered by the scoring diff

The diff compares scoring only. These carry over by hand and are worth their own
checklist:

- roster positions and bench/IR depth (`roster_positions` in the Sleeper snapshot)
- waiver type (FAAB vs rolling), budget, and waiver day
- trade deadline and review period
- playoff team count, start week, and any bye structure
- keeper/dynasty rules — Yahoo's keeper support is much thinner than Sleeper's
