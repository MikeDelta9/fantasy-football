# Scoring change-list: sleeper -> yahoo

Yahoo's Fantasy Sports API is read-only for league settings, so apply these
by hand in **League Settings -> Edit League Settings -> Modify Stat Categories**
(commissioner only, and locked once the season starts).

## Change these values

| Category | Sleeper | Yahoo |
|---|---|---|
| Interception Thrown | -1 | -2 |

## Present in Yahoo but not in Sleeper -- confirm or zero out

| Category | Sleeper | Yahoo |
|---|---|---|
| FG Made 50+ | -- | 5 |

## No Yahoo equivalent -- decide on a substitute

| Category | Sleeper | Yahoo |
|---|---|---|
| FG Made 50-59 | 5 | -- |
| FG Made 60+ | 6 | -- |
| Forced Fumble | 1 | -- |

## Scored zero on one side, absent on the other -- no action (4)

These score identically whether or not Yahoo lists the category.

Extra Point Missed, FG Missed, Points Allowed 21-27, Fumble

## Already matching (31)

Passing Yards, Passing TD, Passing 2-Pt Conversion, Rushing Yards, Rushing TD, Rushing 2-Pt Conversion, Reception, Receiving Yards, Receiving TD, Receiving 2-Pt Conversion, Extra Point Made, FG Made 0-19, FG Made 20-29, FG Made 30-39, FG Made 40-49, Sack, Interception, Fumble Recovery, Defensive TD, Safety, Blocked Kick, Special Teams TD, Points Allowed 0, Points Allowed 1-6, Points Allowed 7-13, Points Allowed 14-20, Points Allowed 28-34, Points Allowed 35+, Fumble Lost, Fumble Recovery TD (offense), Return TD (ST player)

## Unmapped -- review by hand

- `sleeper` **def_2pt** = 2.0
- `sleeper` **def_st_ff** = 1.0
- `sleeper` **def_st_fum_rec** = 2.0
- `sleeper` **st_ff** = 1.0
- `sleeper` **st_fum_rec** = 2.0
- `yahoo` **Defense/Special Teams: Extra Point Returned** = 2.0
