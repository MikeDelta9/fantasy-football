# Operations registry

An **operation** is a repeatable thing this project can do — usually FantasyPros data
plus league state, turned into an answer. This file is the menu and the status board.

The point of a registry rather than a pile of scripts: an idea can sit here as `idea`
costing nothing, and the ones that earn a build get built with the others' context
already written down.

## How to use it

- **Add freely.** A one-line row for a half-formed idea is the intended use.
- **Promote when it earns it** — usually the second or third time you want the answer.
- Built operations become `ff <verb>` subcommands and get a line in the season index
  the first time they're run for real.
- Kill rows that turn out to be bad ideas. Record *why* in `DECISIONS.md` if the reason
  is non-obvious, so it doesn't come back.

**Status:** `idea` → `spec` (inputs/outputs written down) → `built` → `retired`

---

## Scoring-aware valuation

The through-line for most of these: FantasyPros publishes projections under *standard*
scoring formats, but this league's scoring is its own thing. Re-scoring raw projected
stat lines through `ff.scoring` is the single highest-leverage operation here — nearly
everything below is a consumer of it.

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| Custom-scored projections | "What is this player actually worth in *our* league?" | FantasyPros stat projections + our scoring settings | **built** — `ff/draft/score.py` |
| Positional value curves / VORP | "Where does the drop-off make a position scarce?" | custom-scored projections + roster slots | **built** — `ff/draft/board.py`, flex demand allocated to whoever wins the slots |
| Cheat sheet / tiers | Draft board tiered by our scoring, not PPR defaults | custom-scored projections | **built** — tiers break on unusual drop-off |

## Draft

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| ADP vs value gap | "Who goes later than they're worth in our format?" | consensus rank (no ADP endpoint on our plan) + custom-scored projections | **built** — the "Where consensus is wrong" view |
| Draft simulator | "If I take X here, what's likely there next round?" | consensus rank + expert spread + roster needs | **partly built** — surplus already prices "what will still be there next pick" |
| ~~Keeper valuation~~ | n/a — Yahoo offers no keeper setting on this league type | | dropped 2026-08-25 |
| Live draft assistant | Best available by our values, during the draft | draft state + tiers | **half-built** — page and recommendation work; pick tracking is manual until the draft room can be polled |

### Added 2026-08-25

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| Draft-room polling | "Who has been taken, without me typing it" | Yahoo draft client DOM or its XHR feed | idea — blocked until a live/mock draft exists to inspect |
| Waiver priority valuation | "Is this player worth burning priority #3?" | rolling waiver position + rest-of-season projections | idea — the biggest unserved edge; FantasyPros assumes FAAB |
| Win-probability lineup | "Maximise P(win), not expected points" | weekly projections + spread + opponent roster | idea — H2H wants variance shaped by whether you are favoured |
| Playoff-window SOS | "Who is good in weeks 15-17 specifically" | schedule + defensive rankings | idea |
| Opponent modelling | "How do my 11 leaguemates actually behave?" | logged picks, waivers, trades over time | idea — no product can know this |

## In-season

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| Weekly lineup optimizer | "Best legal starting lineup this week" | weekly projections + roster + slots | idea |
| Start/sit with margins | "How close is this call?" — a 0.3-point edge is noise | projections + variance | idea |
| Waiver/FAAB targets | "Who's worth a claim, and what's a sane bid?" | rest-of-season value + roster holes + budget | idea |
| Trade evaluator | "Does this trade help, accounting for what I'd start?" | both rosters + rest-of-season projections | idea |
| Playoff odds / strength of schedule | "What do I actually need to make the playoffs?" | standings + remaining schedule | idea |
| Injury / bye coverage check | "Which week am I about to be short at a position?" | roster + bye weeks + status | idea |

## League admin

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| Scoring change-list | What to change in Yahoo to match Sleeper | both platforms' settings | **built** (`ff diff --out`) |
| Mapping coverage check | "Which Yahoo stat categories does `CANON` not model?" — the reverse of `verify-mapping`, which only validates ids we already have | Yahoo stat-category catalogue + `mapping.py` | idea |
| Non-scoring settings diff | "Which league settings besides scoring still don't match?" — currently a hand-maintained checklist | both platforms' settings | idea |
| Season recap | End-of-year writeup for the league | final standings + weekly records | idea |
| Rule-change impact | "If we changed X, who would it have helped last year?" | historical stats + candidate scoring | idea |

---

## Promoting an idea

Before building, write the row out into a short spec — a `## <name>` section in this
file is enough:

1. **Question** — the sentence a human would actually ask.
2. **Inputs** — which API calls, which league state, which snapshot.
3. **Output** — a table? a file in `deliverables/`? a CLI print?
4. **How you'd know it's wrong** — the part that matters most. A projection tool that
   silently uses default PPR scoring looks completely fine and is completely useless.
