# 2026 Migration — non-scoring settings checklist

Settings `ff diff` does **not** cover. These port by hand into the Yahoo commissioner
UI. Source values read from `data/snapshots/sleeper-league-20260826-003127.json`
(pulled 2026-08-25); that snapshot is the authority, this table is the working copy.

Status of the port lives in `../SEASON_INDEX.md`, not here.

## Roster

| Setting | Sleeper value | Yahoo notes |
|---|---|---|
| Starters | QB, RB, RB, WR, WR, TE, FLEX, K, DEF (9) | **Confirmed 2026-08-25:** `W/R/T` = 1, `W/R` = 0. Three-position flex, matches Sleeper. |
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

---

# Verified against Yahoo — 2026-08-25

Yahoo side read from the commissioner settings page (league <league-id>) via
`ff yahoo import-ui`. The API was not available; see `_project/LEARNINGS.md`.

## Matches — nothing to do

| Setting | Sleeper | Yahoo |
|---|---|---|
| Roster | QB, RB, RB, WR, WR, TE, FLEX, K, DEF + 7 BN + 1 IR | QB, WR, WR, RB, RB, TE, W/R/T, K, DEF + 7 BN + IR |
| Teams | 12 | 12 |
| Playoff teams / start | 6 / week 15 | 6 / weeks 15-17, ends Mon Jan 4 |
| Playoff reseeding | `playoff_seed_type` 1 | Yes |
| Waiver type | rolling (`waiver_type` 0) | Continual rolling list |
| Waiver clear time | 2 days | 2 days |
| Waiver day | Tuesday (`waiver_day_of_week` 1) | Game Time - Tuesday |
| Trade review | league vote (`veto_auto_poll` 1) | League Votes |
| Trade reject time | 2 days | 2 days |
| Draft pick trading | off (`pick_trading` 0) | No |
| Bench lock | off | No |
| Median scoring | off (`league_average_match` 0) | No |
| IR from waivers/FA | allowed | Yes |

## Gaps — decide before the draft

| # | Finding | Why it matters |
|---|---|---|
| 1 | **Sleeper has `max_keepers: 1`. Yahoo has no keeper setting at all** — draft type is "Live Standard Draft", and no keeper row appears anywhere in league settings. | The single biggest non-scoring difference. If the league expects to keep a player, this must be configured **before Sun Aug 30**. If nobody has used the keeper slot in practice, it is a Sleeper leftover and the correct action is to say so out loud rather than silently drop it. *Unresolved.* |
| ~~2~~ | **RESOLVED 2026-08-25.** Trade deadline moved to **Nov 21, 2026**, which falls in week 11 and matches Sleeper's `trade_deadline: 11`. *verified 2026-08-25.* |
| 3 | Veto votes: Sleeper `veto_votes_needed: 6` vs Yahoo "Votes Required to Veto: **Default**". | Yahoo's default for a 12-team league is not stated on the settings page. Worth confirming it lands near 6. *Unresolved.* |
| 4 | Sleeper `draft_rounds: 3` against 16 roster slots. | Pre-existing open question. Yahoo runs a full standard draft, so this does **not** carry over — it looks like a Sleeper misconfiguration that never mattered. No Yahoo action. |
| 5 | Sleeper `max_subs: 2` / `sub_*` settings. | Sleeper in-game substitution features. No Yahoo equivalent and no scoring impact. No action. |

## Season duration & playoffs — verified 2026-08-25

2026 NFL calendar: **Sept 9, 2026 → Jan 10, 2027, 18 weeks.** *doc — nfl.com schedule.*

| Setting | Sleeper | Yahoo | Verdict |
|---|---|---|---|
| Scoring starts | week 1 (`start_week`) | Week 1 | match |
| Regular season | weeks 1-14 | weeks 1-14 | match |
| Playoff start | 15 (`playoff_week_start`) | Week 15 | match |
| Playoff teams | 6 (`playoff_teams`) | 6 | match |
| Round length | 1 week (`playoff_round_type` 0) | weeks 15, 16, 17 | match |
| Reseeding | on (`playoff_seed_type` 1) | Yes | match |
| Divisions | none | No | match |
| Tie-breaker | not in payload | Higher seed wins | Yahoo-only; no conflict |

**Week 18 is deliberately unused.** Championship is week 17, ending Mon Jan 4, 2027 —
which is what Yahoo's "ends Monday, Jan 4" refers to. Week 18 (Jan 7-10) is when
playoff-bound NFL teams rest starters. Keep it excluded. *verified 2026-08-25.*

**Bracket shape:** 6 of 12 teams over 3 rounds means seeds 1-2 bye in week 15 and
seeds 3-6 play in. A preference, not a constraint — the only structural choice here
that could reasonably be different. *asserted 2026-08-25 — standard Yahoo behaviour
for 6 teams / 3 rounds, not observed on a rendered bracket (Yahoo's bracket page 404s
pre-draft).*

### Gap 6 — consolation bracket

Sleeper's snapshot has a populated `loser_bracket_id` (and `loser_bracket_overrides_id`),
so the league ran a losers bracket. Yahoo's settings page offers **no consolation
bracket option** — the nearest setting is "Lock Eliminated Teams: No", which only means
eliminated teams keep playing out matchups. If the toilet bowl matters, this is a real
loss and needs saying out loud. *Unresolved.*

## Trades, waivers, roster rules — verified 2026-08-25

Yahoo values read from the **edit-settings form** (`/f1/<league-id>/editleaguesettings`),
which shows the true selected option rather than the summary page's rendering.
Read only — nothing submitted. *verified 2026-08-25.*

### Trades

| Setting | Sleeper | Yahoo (form field) | Verdict |
|---|---|---|---|
| Trades enabled | on (`disable_trades` 0) | on | match |
| Max trades / season | unlimited | `max_trades` = No maximum | match |
| Draft pick trading | off (`pick_trading` 0) | `TDP` = No | match |
| Trade review | league vote (`veto_auto_poll` 1) | `trade_review` = Votes (all league managers) | match |
| Trade reject time | 2 days (`trade_review_days`) | `trade_reject_time` = 2 days | match |
| Veto votes needed | 6 (`veto_votes_needed`) | `trade_veto_votes` = **6** | **resolved 2026-08-25** |
| Veto vote visibility | hidden (`veto_show_votes` 0) | no equivalent setting | Yahoo gap |
| Trade deadline | week 11 (`trade_deadline`) | `trade_end_date` = **Nov 21, 2026** (wk 11) | **resolved 2026-08-25** |

### Waivers and acquisitions

| Setting | Sleeper | Yahoo (form field) | Verdict |
|---|---|---|---|
| Waiver type | rolling (`waiver_type` 0) | `waiver_type` = Continual rolling list | match |
| Waiver clear time | 2 days | `waiver_time` = 2 days | match |
| Waiver run day | Tuesday (`waiver_day_of_week` 1) | `WR` = Game Time - Tuesday | match |
| FAAB budget | 100, **inert** — type is rolling, not FAAB | n/a | no action |
| Max acquisitions / season | unlimited | `max_moves` = No maximum | match |
| Max acquisitions / week | unlimited | `max_weekly_adds` = No maximum | match |
| Post-draft players | — | `post_draft_players` = Follow Waiver Rules | Yahoo-only |
| Can't Cut List | **no such concept** | `cant_cut_list` = **Yahoo Sports** | **Yahoo-only, ON** |

### Roster rules

| Setting | Sleeper | Yahoo (form field) | Verdict |
|---|---|---|---|
| IR slots | 1 (`reserve_slots`) | 1 (IR in roster string) | match |
| IR eligibility | COV/DNR/Doubtful/NA/Out/Sus | Yahoo's own, narrower list | **differs** |
| Add injured direct to IR | — | `ALLOW_ADD_TO_DL_EXTRA_POS` = Yes | Yahoo-only, permissive |
| Bench lock | off | `lock_benched_players` = No | match |
| In-game subs | `max_subs` 2 | none | Sleeper-only, no scoring impact |
| Taxi squad | unused (all `taxi_*` 0) | none | match |

### League type and draft

| Setting | Sleeper | Yahoo (form field) | Verdict |
|---|---|---|---|
| League type | redraft (`type` 0) | `LDPT`/Live Standard Draft | match |
| Scoring type | H2H | `scoring_type` = Head-to-Head | match |
| Season start | week 1 | `league_start_week` = Week 1 (Sep 9) | match |
| Fractional points | yes (decimal values) | Yes | match |
| Negative points | yes | Yes | match |
| Median scoring | off (`league_average_match` 0) | `median_score` = No | match |
| Second opponent | — | `second_opponent` = No | match |
| Divisions | none | `divisions` = No | match |
| Invites | commissioner only | `INV_PERMISSIONS` = Commissioner Only | match |
| Draft clock | — | `LDPT` = 1 Minute | preference — confirm for a 12-team live draft |
| Postponed-game injury status | — | `apply_ppd_game_status` = **Yes** | **set 2026-08-25** — recovers some of Sleeper's permissive IR |

### Gaps — ranked

| # | Finding | Action |
|---|---|---|
| ~~7~~ | **RESOLVED 2026-08-25 — set to 6.** Veto votes = "Default", an option distinct from the explicit 1-19 the dropdown also offers. Yahoo never states what Default resolves to. Sleeper was an explicit 6. | Set to 6 by the commissioner, verified on the form. *verified 2026-08-25.* |
| ~~8~~ | **RESOLVED 2026-08-25 — keeping Yahoo's list.** Earlier note said the league had "never met this rule"; that was wrong. The league *started* on Yahoo, so the Can't Cut List is original behaviour returning, not a new restriction. Only members who joined during the ESPN/Sleeper years will find it unfamiliar. *verified 2026-08-25 (commissioner).* |
| 9 | **Yahoo's IR is narrower than Sleeper's.** Sleeper permitted stashing COV/DNR/Doubtful/NA/Out/Sus; Yahoo's IR slot accepts fewer statuses. | No setting to change — it is a platform limit. Worth a line in the announcement. *Accepted.* |
| 10 | Veto votes were hidden on Sleeper (`veto_show_votes` 0). Yahoo offers no equivalent. | No action available. *Accepted.* |

**Closed:** Yahoo's edit-settings form contains **no keeper field of any kind**, confirming
gap 1 is a platform-level absence on this league type, not an oversight.

## Roster slots — verified 2026-08-25

Read from Yahoo's roster-position editor (`/f1/<league-id>/editrosterpositions`), which
exposes the raw per-slot counts rather than the settings page's summary string.
Read only — nothing submitted.

| Slot | Sleeper | Yahoo | Verdict |
|---|---|---|---|
| QB | 1 | `QB` = 1 | match |
| RB | 2 | `RB` = 2 | match |
| WR | 2 | `WR` = 2 | match |
| TE | 1 | `TE` = 1 | match |
| Flex | 1 (`FLEX`) | `W/R/T` = 1 | match |
| K | 1 | `K` = 1 | match |
| DEF | 1 | `DEF` = 1 | match |
| **Starters** | **9** | **9** | match |
| Bench | 7 | `BN` = 7 | match |
| IR | 1 (`reserve_slots`) | `IR` = 1 | match |
| **Total** | **16 + IR** | **16 + IR (16/30 used)** | match |

**Closed — flex type.** `W/R/T` = 1 and `W/R` = 0, so the flex is WR/RB/TE, matching
Sleeper's `FLEX`. The earlier "confirm it's RB/WR/TE, not W/R" question is answered.
*verified 2026-08-25.*

**Closed — no IDP.** Every individual-defensive slot (`D`, `DB`, `DL`, `LB`, `DT`,
`DE`, `CB`, `S`) is 0, as is `OFF`. Team DEF only, same as Sleeper. Superflex
(`Q/W/R/T`) is 0. *verified 2026-08-25.*

Yahoo caps rosters at 30 slots; 16 are used, so no capacity constraint applies.

## Applied — 2026-08-25

Changes made by the commissioner in the Yahoo UI and verified by re-reading the
edit-settings form:

| Setting | Was | Now |
|---|---|---|
| `trade_veto_votes` | Default (value unstated by Yahoo) | **6** — matches Sleeper's `veto_votes_needed` |
| `apply_ppd_game_status` | No | **Yes** — postponed-game players become IR-eligible |
| `trade_end_date` | November 28, 2026 (≈ wk 12) | **November 21, 2026** — week 11, matches Sleeper |

Deliberately unchanged: `lock_benched_players` = No, matching Sleeper's
`bench_lock: 0` and the league's unlimited-acquisitions setup.

`cant_cut_list` = Yahoo Sports — **kept deliberately**, it is the league's original behaviour.
