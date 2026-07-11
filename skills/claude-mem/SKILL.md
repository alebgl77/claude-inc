---
name: claude-mem
description: Persistent filesystem memory across sessions — maintains memory/ with decisions.md, context.md, glossary.md and sessions/YYYY-MM-DD.md, loads and summarizes state at session start, appends decisions and open threads at session end, compacts monthly, and refuses secrets and transient noise. Use when the user says "remember this", "what did we decide about X", "pick up where we left off", or when starting or closing a session on a long-running project.
---

# Claude-Mem — Memory Keeper

> "Persistent memory"

Chat context evaporates; files don't. Give every project a paper trail the next session can boot from.

## When to use

- "Pick up where we left off" — session start on any long-running project
- "Remember this" / "log that decision" the moment a choice lands
- "What did we decide about <topic>, and why?"
- "What does <codename/acronym> mean again?" — glossary lookups
- "Wrap up" / "save state before we stop" — session end

## Workflow

1. Locate or initialize `memory/` at the project root: `decisions.md`, `context.md`, `glossary.md`, `sessions/`. Create missing files with headers; never overwrite existing ones.
2. Session start: read `context.md`, `decisions.md`, and the last two session files; deliver a ≤10-bullet summary — active decisions, open threads, next actions — and confirm it matches the user's picture.
3. During work, log decisions the moment they land: append to `decisions.md` with date, decision, rationale, and alternatives rejected. Same-session or it didn't happen.
4. New shorthand — nickname, acronym, codename — gets a one-line `glossary.md` entry on first use.
5. Session end: write `sessions/YYYY-MM-DD.md` — what got done, decisions made (pointer, not copy), open threads, next actions.
6. Monthly compaction: fold session files older than 30 days into `context.md` (keep decisions, threads, and state; drop the play-by-play), delete the folded files, and dedupe `decisions.md` keeping the latest ruling per topic.
7. Refuse to store: secrets, tokens, passwords, keys; personal data beyond names and roles; transient noise (build logs, one-off stack traces, dead ends already resolved). Say what was excluded and why.

## Output format

```
memory/
├── decisions.md       # append-only choices + rationale
├── context.md         # compacted long-term project state
├── glossary.md        # shorthand → meaning
└── sessions/
    └── 2026-07-11.md  # one file per working session

decisions.md entry:
## 2026-07-11 — Postgres over SQLite for prod
Why: concurrent writers. Rejected: SQLite (single-writer lock), DynamoDB (no team experience).

glossary.md entry:
ATLAS — internal codename for the billing rewrite (started 2026-05)

sessions/YYYY-MM-DD.md:
# Session 2026-07-11
Done: <shipped work, one line each>
Decisions: → decisions.md (2026-07-11)
Open threads: <unresolved, with current state>
Next: <first action for the next session>
```

## Quality bar

- [ ] Session opened with a memory summary, never a cold start
- [ ] Every decision logged same-session with rationale and rejected alternatives
- [ ] Session file written before the session closes
- [ ] Zero secrets, credentials, or transient noise in any memory file
- [ ] Compaction shrinks bytes without losing a single decision or open thread
- [ ] Summaries stay ≤10 bullets — memory serves recall, not re-reading

## Example

Ask: "We're going with JWT over server sessions — remember that, then wrap up."

Produced: appended `## 2026-07-11 — JWT over server sessions` (why: stateless scaling; rejected: session store adds a Redis dependency) to `decisions.md`, wrote `sessions/2026-07-11.md` with two open threads (refresh-token rotation, logout semantics), and echoed the entry back for confirmation.

## Credits

Inspired by the claude-mem project.
