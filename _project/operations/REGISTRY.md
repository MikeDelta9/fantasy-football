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
| Custom-scored projections | "What is this player actually worth in *our* league?" | FantasyPros stat projections + our scoring settings | idea |
| Positional value curves / VORP | "Where does the drop-off make a position scarce?" | custom-scored projections + roster slots | idea |
| Cheat sheet / tiers | Draft board tiered by our scoring, not PPR defaults | custom-scored projections | idea |

## Draft

| Operation | What it answers | Inputs | Status |
|---|---|---|---|
| ADP vs value gap | "Who goes later than they're worth in our format?" | ADP + custom-scored projections | idea |
| Draft simulator | "If I take X here, what's likely there next round?" | ADP distributions + roster needs | idea |
| Keeper valuation | "Is this keeper worth its round cost?" | keeper rules + projections | idea |
| Live draft assistant | Best available by our values, during the draft | draft state + tiers | idea |

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
