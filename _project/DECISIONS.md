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
| ~~Sleeper is the source of truth for scoring~~ | 2026-08-24 | **Superseded 2026-08-25.** Written believing Yahoo was a blank target. It is not: the league is returning to its *original* Yahoo league with settings intact, and Sleeper's scoring is a hand-typed copy of those settings. |
| The original Yahoo settings are canonical where the two disagree | 2026-08-25 | Yahoo's overrides (pass TD 6 vs default 4, INT -2 vs default -1) are the league's deliberate, long-standing rules. Sleeper is a copy-of-a-copy, so a disagreement is evidence of re-entry drift on Sleeper, not of a decision. Sleeper remains the source of truth for *rosters and league state* — this reverses direction for scoring only. |
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
| `pass_int` = -1 | **Yahoo wins; keep -2.** Yahoo's default is -1, so the original league's -2 was deliberate and survived intact. Sleeper is where the value drifted. No Yahoo edit. | 2026-08-25 | Yes — the league last played -1 on Sleeper |
| `fgm_60p` = 6 (Yahoo's 50+ bucket pays 5) | **Accept 5.** Yahoo cannot split 50-59 from 60+. Raising the bucket to 6 would over-pay every 50-59 kick, which are far more common. Costs 1 pt on 60+ kicks only. | 2026-08-25 | Yes — minor, but it is a real rule change |
| `ff` / `def_st_ff` / `st_ff` = 1 (forced fumble) | **Accept the loss.** Yahoo has no forced-fumble stat to configure. Fumble recovery still pays 2 on both, so strip-and-recover still scores; only an unrecovered strip goes unrewarded. | 2026-08-25 | Yes |
| `def_2pt` = 2 | **No loss.** Pairs with Yahoo's *Extra Point Returned* = 2. Same event, same value, different label. | 2026-08-25 | n/a |
| `def_st_fum_rec` / `st_fum_rec` = 2 | **No loss.** Already covered by Yahoo's *Fumble Recovery* = 2. | 2026-08-25 | n/a |
| Can't Cut List (Yahoo-only feature, no Sleeper equivalent) | **Keep Yahoo's list.** It is how the league has always run — the Can't Cut List predates the ESPN and Sleeper eras. Not a new restriction, a returning one. | 2026-08-25 | Worth a line for members who joined during the ESPN/Sleeper years |
