---
name: pipeline-review
description: Audits pipeline health from a deal list (CSV, table or plain notes) — prioritises deals, flags zombies and single-threaded risks, checks close-date realism and outputs a weekly action plan. Use when the user says "review my pipeline", "which deals should I focus on", "why is nothing closing", or shares a list of open deals.
---

# Pipeline Review — Pipeline Doctor

> "Pipeline truth over pipeline comfort."

## When to use

- "Review my pipeline" (paste/attach deals: name, value, stage, last contact, next step)
- "What should I focus on this week?"
- "My forecast feels fake"
- Weekly ritual; also before any forecast conversation
- Works from a CSV, a markdown table, or messy notes — it will structure them first

## Workflow

1. **Normalise the data** into: deal, value, stage, last meaningful contact, next step (dated?), single or multi-threaded.
2. **Apply the health checks**: no dated next step = zombie; last contact > 14 days = cooling; one contact person = single-threaded; close date in the past or "end of quarter" 3 quarters running = fiction; stage vs. evidence mismatch (e.g. "negotiation" but no proposal sent).
3. **Score priorities**: value × probability × momentum. Big-but-dead loses to small-but-moving.
4. **Prescribe per deal**: exactly one action — advance (specific move), revive (pattern-break touch), or kill (graceful close-out that preserves the relationship).
5. **Summarise the week**: top 3 focus deals with their actions, deals to kill this week, and the one systemic habit to fix (found in the patterns — e.g. "you never set next steps on first calls").
6. **Forecast sanity line**: weighted realistic total vs. optimistic total, in one sentence.

## Output format

```
## Pipeline review — {date} · {n} deals · realistic: {€X} (optimistic: {€Y})

| Deal | Value | Health | Diagnosis | THE action this week |
|------|-------|--------|-----------|----------------------|
| ...  | ...   | 🟢🟡🔴 | ...       | ...                  |

**Focus 3**: 1. {deal} → {action} 2. ... 3. ...
**Kill list**: {deals} — with the close-out line to send
**Systemic fix**: {the one habit}
```

## Quality bar

- [ ] Every deal gets exactly one action, none gets "keep monitoring"
- [ ] Zombies named and killed out loud, with a graceful exit message
- [ ] Single-threaded deals flagged with a second-contact suggestion
- [ ] Realistic vs. optimistic totals both stated
- [ ] The systemic fix targets a pattern, not a deal

## Example

**Ask**: "12 deals pasted from my notes, which 3 matter?"
**Produced**: normalised table, 4 zombies flagged (2 killed with exit lines), focus 3 with concrete moves ("send option-B nudge before Thursday"), systemic fix: every call ends with a dated next step.
