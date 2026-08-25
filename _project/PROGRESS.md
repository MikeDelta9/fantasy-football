# Fantasy Football — Progress Log

**Log started:** 2026-08-24

Session-by-session narrative: what happened, in order. Standing decisions belong in
`DECISIONS.md`; reusable gotchas belong in `LEARNINGS.md`; current status belongs in
the season index. This file is the story, not the state.

---

## Session Log

### 2026-08-24 — Project created; tooling scaffolded; context system built

**What came out of it**

1. **Scaffolded the repo** — Python + uv, `ff` CLI, read-only clients for Sleeper and
   Yahoo, a canonical scoring mapping, and normalize → diff → report. 6 tests passing.

2. **Established the hard constraint.** The Yahoo Fantasy Sports API has no endpoint
   for league scoring settings; its write scopes cover rosters, add/drops, trades and
   draft picks only. The migration therefore ends in a markdown change-list applied in
   the commissioner UI, not an API write. *verified 2026-08-24 (Yahoo API docs).*

3. **Split the knowledge base from ACT's.** A second compiler instance at
   `~/fantasy-memory-compiler`, selected by a router hook at
   `~/.claude/hooks/memory_router.py`. Personal and client work no longer mix in
   either direction.

4. **Built this context system** — `_project/` durable layer, `seasons/2026/` work
   units, the `ff-context` skill, and `/ffSave`.

**Open**

- No credentials yet: Sleeper league ID, Yahoo dev app, FantasyPros key.
- Nothing pulled from either platform, so the scoring mapping is unverified against
  a real league.
