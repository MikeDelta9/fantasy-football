# Scoring & settings — capability thread

| | |
|---|---|
| **Covers** | How a scoring rule travels from Sleeper to Yahoo, and everything that can go wrong on the way |
| **Code** | `src/ff/scoring/` (mapping → normalize → diff → report), `src/ff/yahoo/client.py` (flatten) |
| **Docs** | `docs/league-migration.md` (runbook) · `docs/yahoo-setup.md` (auth) |
| **Last verified** | 2026-08-24 |

> **A map, not a store.** Values live in the snapshots; status lives in the season
> index. Every claim below carries a confidence label.

---

## 1. The spine

```
Sleeper league object              GET api.sleeper.app/v1/league/<id>
  └ scoring_settings  { "pass_td": 4, "rec": 0.5, ... }   flat string->number map
       │
       │  normalize_sleeper()   key -> canonical, via mapping.by_sleeper_key
       ▼
  {canonical_key: points}  +  .unmapped  (keys the table doesn't know)
       │
       │                       ┌─ normalize_yahoo()  stat_id -> canonical
       │                       │     via flatten() then mapping.by_yahoo_id
       ▼                       ▼
  diff_scoring(source=sleeper, target=yahoo)
       │
       ├ match              values agree
       ├ differs            both have it, values disagree      -> edit Yahoo
       ├ missing_in_target  Sleeper only, Yahoo CAN hold it     -> add in Yahoo
       ├ missing_in_source  Yahoo default not used in Sleeper   -> zero it out
       └ unportable         Sleeper only, Yahoo has no category -> DECISION, not an edit
       │
       ▼
  report.to_markdown()  ->  seasons/<year>/migration/change-list.md
       │
       ▼
  APPLIED BY HAND — Yahoo League Settings > Edit League Settings > Modify Stat Categories
       │
       ▼
  re-pull + re-diff to confirm zero actionable rows
```
*verified 2026-08-24 (unit tests cover match / differs / missing / unportable / unmapped).*

## 2. Where it breaks

**The mapping table is the single point of failure.** `ff/scoring/mapping.py` hardcodes
Yahoo stat ids. A wrong id doesn't error — it produces a confidently wrong diff, which
is the worst failure mode this project has. `ff yahoo verify-mapping` compares every id
against Yahoo's own `/game/nfl/stat_categories` catalogue. **Run it before trusting any
diff in a new season.** *asserted — the ids are the standard NFL set but have not been
checked against a live Yahoo response yet.*

**Yahoo's pseudo-array JSON.** `flatten()` collapses `{"0": …, "1": …, "count": n}` into
lists and merges sibling single-key dicts. It refuses to merge when a key repeats,
because that case is a real collection and merging would keep only the last element —
which would silently drop every stat modifier but one. *verified 2026-08-24 (a test
exists specifically for this; it caught the bug during the build).*

**Unmapped ≠ absent.** Anything the table doesn't know is collected into `.unmapped` and
printed separately, never dropped. If a scoring rule seems to have vanished, look at the
unmapped section before suspecting the diff. *verified 2026-08-24.*

**The season lock.** Yahoo freezes most league settings once the regular season begins.
Scoring work is a preseason activity with a hard deadline, not something to iterate on
in week 3. *doc.*

## 3. Not covered by the scoring diff

The diff compares scoring only. These carry over by hand and need their own checklist —
see `docs/league-migration.md`:

- roster positions, bench and IR depth (`roster_positions` in the Sleeper snapshot)
- waiver type (FAAB vs rolling), budget, waiver day
- trade deadline and review period
- playoff team count, start week, bye structure
- keeper/dynasty rules — Yahoo's support here is much thinner than Sleeper's

## 4. Decisions this thread constrains

Every `unportable` row resolved during the migration gets a line in
`_project/DECISIONS.md` under "Scoring rules that could not be ported", including
whether the league was told. Without that, next preseason's diff re-opens a question
that was already settled — and the league notices.
