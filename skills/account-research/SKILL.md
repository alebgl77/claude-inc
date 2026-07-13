---
name: account-research
description: Researches a company or person and returns actionable sales intel — what they do, recent signals, likely pains, entry angle and talk tracks. Use when the user says "research this company", "who is this prospect", "intel on X before I reach out", or before any outreach, call or proposal targeting a specific account.
---

# Account Research — Prospector

> "Know them better than their own website does."

## When to use

- "Research {company} before I contact them"
- "Who is {name} at {company}?"
- "Why would {company} buy {my product}?"
- Always before `draft-outreach` or `call-prep` — research is their fuel
- Works from public web (search + site + LinkedIn-style signals); upgrades with any CRM/enrichment MCP if connected

## Workflow

1. **Frame the mission**: what does the user sell, and what would make this account a good or bad fit? Write the fit hypothesis first.
2. **Company scan**: what they do (in one sentence a human would say), size/stage signals, business model, who their customers are.
3. **Signal sweep**: last 90 days — funding, hiring, launches, leadership changes, tech choices, public complaints. Date every signal.
4. **People map**: likely buyer, likely champion, likely blocker — with role-based reasoning when names aren't public.
5. **Pain hypotheses**: top 3, each tied to an observed signal (not generic industry pains).
6. **Entry angle**: the single most credible reason to talk to them THIS month, plus 2 conversation openers in natural language.
7. **Disqualifiers**: honest list of reasons to skip this account. Recommendation: pursue / park / drop.

## Output format

```
## Account brief — {company}
Fit hypothesis: {1 line} · Verdict: PURSUE / PARK / DROP

**What they do**: ...
**Signals (dated)**: • {date} — {signal} → {why it matters}
**People**: buyer {role} · champion {role} · blocker {role}
**Top pains (evidence-tied)**: 1. ... 2. ... 3. ...
**Entry angle**: ...
**Openers**: "..." / "..."
**Disqualifiers**: ...
```

## Quality bar

- [ ] Every signal is dated and sourced (link or "observed on their site")
- [ ] Pains reference evidence, not industry clichés
- [ ] The entry angle would survive being read aloud to the prospect
- [ ] A clear verdict — no fence-sitting
- [ ] Under 1 page; a rep can absorb it in 3 minutes

## Example

**Ask**: "Research Maison Verdier (wine e-commerce) for my SEO service."
**Produced**: brief showing recent PrestaShop 9 migration + 2 job posts for marketing, pain hypothesis "traffic lost in migration", entry angle referencing their broken category pages, verdict PURSUE with two openers.
