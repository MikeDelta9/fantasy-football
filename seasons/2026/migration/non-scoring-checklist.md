# 2026 Migration — non-scoring settings checklist

Settings `ff diff` does **not** cover. These port by hand into the Yahoo commissioner
UI. Source values read from `data/snapshots/sleeper-league-20260826-003127.json`
(pulled 2026-08-25); that snapshot is the authority, this table is the working copy.

Status of the port lives in `../SEASON_INDEX.md`, not here.

## Roster

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| Starters | QB, RB, RB, WR, WR, TE, FLEX, K, DEF (9) | Yahoo calls FLEX "W/R/T" — confirm it's RB/WR/TE, not W/R |
| Bench | 7 | |
| IR slots | 1 (`reserve_slots`) | Yahoo IR eligibility is narrower than Sleeper's; Sleeper here allows COV/DNR/Doubtful/NA/Out/Sus |
| Total | 16 + 1 IR | |

## Waivers

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| `waiver_type` | 0 | **Interpretation unconfirmed** — 0 is rolling/standard order in Sleeper's enum, not FAAB. `waiver_budget` is 100 but may be inert. Verify in the Sleeper UI before mirroring. |
| `waiver_budget` | 100 | |
| `waiver_clear_days` | 2 | |
| `waiver_day_of_week` | 1 | Enum unconfirmed; check the UI |
| `waiver_bid_min` | 0 | |

## Trades

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| Trade deadline | week 11 | |
| Review period | 2 days | |
| Veto votes needed | 6 | Yahoo's veto model differs — commissioner review is the closer analogue |
| Pick trading | off | |

## Playoffs

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| Playoff teams | 6 | |
| Start week | 15 | |
| `playoff_type` / `playoff_round_type` | 1 / 0 | Enums unconfirmed — check round length (1-week vs 2-week finals) in the UI |
| Seeding | `playoff_seed_type` 1 | |

## Keepers

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| Max keepers | 1 | Yahoo's keeper support is thinner than Sleeper's — confirm the cost model carries |
| Keeper deadline | `"0"` (metadata) | Unset |

## Flagged

- **`draft_rounds` is 3** against a 16-slot roster and 12 teams. That cannot fill the
  rosters and looks misconfigured on the Sleeper side. Resolve before the draft; it
  also changes what "1 keeper" costs.
- League continues from `previous_league_id` 1257434478813392896 — prior-season history
  exists on Sleeper and will **not** follow the league to Yahoo.
