---
name: proposal-builder
description: Builds proposals, quotes and offers that close — problem restatement in the client's words, scoped options, anchored pricing, timeline, terms and next step. Use when the user says "write a proposal", "send them a quote", "build an offer for X", or after a successful discovery or demo call.
---

# Proposal Builder — Rainmaker

> "A proposal is the call you already had, written down."

## When to use

- "Write the proposal for {client}"
- "They asked for a quote"
- "Turn these call notes into an offer"
- After `call-prep` + the call itself; hand the notes over — the proposal should contain zero new ideas

## Workflow

1. **Harvest the inputs**: call notes, agreed pains, stated budget signals, decision process, deadline. Missing a pain confirmed by the client? Stop and say so — a proposal without confirmed pain is a brochure.
2. **Restate the problem in their words** (verbatims from the call). This section wins or loses the deal.
3. **Design 3 options** (Good/Better/Best): the middle one is the one you want them to pick; the small one makes it safe, the big one makes it look reasonable. Each option = outcome, scope bullets, what's excluded, price.
4. **Anchor value before price**: quantify the cost of the problem or value of the outcome using THEIR numbers when given.
5. **Timeline & responsibilities**: start date, milestones, what you need from them (the hidden deal-killer).
6. **Terms**: validity date (7-14 days), payment schedule, the one guarantee you can honour. Flag anything for `review-contract` (legal) before sending.
7. **Close with a single next step**: signature link / kickoff date / reply "option B" — one action, dated.
8. **Format**: deliver as a clean markdown file ready for PDF/docx conversion.

## Output format

```
## Proposal — {client} · valid until {date}
### 1. Where you are (your words)     ← verbatims
### 2. Where you want to be           ← outcome, quantified
### 3. Options
| | Good | Better ★ | Best |
|Outcome|...|...|...|
|Scope|...|...|...|
|Not included|...|...|...|
|Price|...|...|...|
### 4. Timeline & who does what
### 5. Terms (validity · payment · guarantee)
### 6. Next step: {one dated action}
```

## Quality bar

- [ ] Problem section uses the client's actual words from the call
- [ ] Exactly 3 options; the target option is visibly the rational choice
- [ ] Exclusions explicit — scope creep dies here
- [ ] Price appears AFTER value, never in the first screen
- [ ] Validity date + one single next step
- [ ] Nothing promised that Legal or the product can't back

## Example

**Ask**: "Proposal for the agency pilot we discussed — they said 'we lose 2 days a week on reporting'."
**Produced**: proposal opening on that verbatim, 3 options (pilot / pilot+training ★ / full rollout), value anchor (2 days × loaded cost), 14-day validity, next step "reply with your option by Friday, kickoff Monday".
