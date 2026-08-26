# Fantasy Football — Decisions

Standing decisions that constrain future work. A decision belongs here when reversing
it would cost real effort or when it will otherwise get re-litigated every few months.
Anything that is merely "what happened" goes in `PROGRESS.md`.

Format: one row per decision, with enough context to understand *why* without opening
another file.

---

## Platform & migration

| Decision | Date | Context |
|---|---|---|
| Move the league from Sleeper to Yahoo | 2026-08 | Commissioner preference; Yahoo's API offers write access to rosters and transactions, which Sleeper has none of |
| Sleeper is the source of truth for scoring | 2026-08-24 | The league's settled scoring lives there; Yahoo is a blank target to be matched to it |
| Scoring changes applied by hand in the Yahoo UI | 2026-08-24 | No API path exists. The diff produces a change-list; browser automation is an accelerator, not a substitute for verifying with a re-pull |

## Tooling

| Decision | Date | Context |
|---|---|---|
| Python + uv, not Node | 2026-08-24 | uv already installed; better fit for projection/analysis work downstream |
| Repo lives at `~/projects/fantasy-football`, not OneDrive | 2026-08-24 | Personal project; OneDrive fights with `.venv` and lockfiles |
| Own memory-compiler instance | 2026-08-24 | Personal and ACT client knowledge must not mix in the injected index |
| `/ffSave` commits; `/actSave` does not | 2026-08-24 | This repo is git-backed, so version history is free and `PROGRESS.md` stops being the only record |

## Scoring rules that could not be ported

*Fill in as the migration runs. Every `NO YAHOO EQUIV` row in the diff that you resolve
gets a line here, so next season's diff doesn't re-open the question.*

| Sleeper rule | Resolution | Date | Announced to league? |
|---|---|---|---|
| `pass_2pt` / `rush_2pt` / `rec_2pt`, all = 2 | **No loss.** Yahoo's single combined 2-pt category set to 2 reproduces Sleeper exactly, because all three Sleeper values are equal. Nothing to announce. | 2026-08-25 | n/a — no change in outcome |
