---
name: call-prep
description: Prepares a sales call end-to-end — account context, attendee angles, discovery questions, demo focus, pricing guardrails and a one-page cheat sheet. Use when the user says "prep me for my call with X", "I have a demo tomorrow", "meeting with a prospect", or any time a discovery, demo or negotiation conversation is scheduled.
---

# Call Prep — Deal Prepper

> "Walk in sharper than anyone on the invite."

## When to use

- "Prep me for my call with {company} at {time}"
- "Demo tomorrow — what should I focus on?"
- "Negotiation call, they want a discount"
- Feeds on `account-research` output; triggers `proposal-builder` after a good call

## Workflow

1. **Situate the deal**: stage (first call / discovery / demo / negotiation), what's already been said, what's at stake, who requested the meeting.
2. **Refresh intel**: 5-minute delta on the account — anything new since the brief (news, site changes, replies).
3. **Attendee angles**: per participant — role, what they win if this succeeds, what they fear, one rapport hook.
4. **Set THE goal**: the single outcome that makes this call a win (e.g. "budget owner confirms Q3 window"), plus the fallback outcome.
5. **Write the question set**: 5 discovery questions ordered situation → pain → impact → decision process → timeline; 3 traps to avoid (features monologue, premature pricing, agreeing to unscoped work).
6. **Demo/negotiation focus** (if applicable): the 2 capabilities to show tied to their pains — or the concession ladder: floor price, tradeables (scope, term, case study), walk-away line.
7. **Compress to one page**: the cheat sheet below, glanceable mid-call.

## Output format

```
## Call sheet — {company} · {date/time} · stage: {stage}
GOAL: {one outcome} · Fallback: {outcome}

**Attendees**: {name/role} — wins: ... · fears: ... · hook: ...
**Context delta**: ...
**Open with**: "..."
**Questions (in order)**: 1. ... 5. ...
**Show / Concede**: {demo focus or concession ladder}
**Do NOT**: • ... • ...
**Close with**: "..." → next step proposed on the call
```

## Quality bar

- [ ] One explicit goal — not "build rapport"
- [ ] Questions follow situation→pain→impact→process→timeline and are open-ended
- [ ] Every demo item maps to a stated or hypothesised pain
- [ ] Negotiation floor and tradeables written BEFORE the call, not improvised
- [ ] Fits on one page; readable at a glance during the call

## Example

**Ask**: "Call in 2h with the founder + ops manager of a 12-person agency, second call, they saw pricing."
**Produced**: goal "verbal yes on pilot scope", attendee angles (founder = margin, ops = workload), 5 questions, concession ladder starting at scope-trim not price-cut, and a close line proposing the pilot start date.
