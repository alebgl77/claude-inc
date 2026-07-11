---
name: customer-research
description: Mines reviews, interviews, support tickets and forum threads for voice-of-customer insight — verbatim pains, desires, objections and triggers, clustered into themes with JTBD statements and a message-market map. Use when the user says "analyze these reviews", "what do customers actually want", "synthesize this feedback", or before writing any positioning or copy.
---

# Customer Research — Voice of Customer

> "Synthesise user voice"

## When to use

- "Here are 200 reviews — what do customers actually care about?"
- "Synthesize these interview notes / support tickets"
- "What objections keep coming up?"
- Before positioning, landing copy, or ads — copy written without voice-of-customer is guessing
- Works on pasted text or files; optional upgrade: web search to mine public reviews and Reddit threads

## Workflow

1. **Ingest the corpus**: pasted text, CSV/exports, or files. Note the source mix and any sampling bias (e.g. only angry customers write tickets).
2. **Extract verbatims** into four buckets: pains, desires, objections, buying triggers. Keep the customer's exact words — never paraphrase at this stage.
3. **Cluster into themes** per bucket; count frequency so loud-but-rare doesn't beat quiet-but-common.
4. **Write JTBD statements** for the top clusters: "When {situation}, I want to {motivation}, so I can {outcome}."
5. **Build the message-market map**: their words → your copy blocks (headline candidates, bullet candidates, objection-handling lines) — quoted or lightly compressed, never marketing-speak.
6. **Flag the gaps**: pains competitors' messaging ignores, plus anything surprising that contradicts current positioning.
7. **Hand off**: name the top theme a copywriter should lead with, and the one objection every asset must answer.

## Output format

```
## Voice of Customer — {corpus, n items, sources}

### Themes by frequency
| Bucket | Theme | Freq | Best verbatim |
|--------|-------|------|---------------|

### JTBD (top 3)
1. When ..., I want to ..., so I can ...

### Message-market map
| They say (verbatim) | Use it as |
|---------------------|-----------|
| "..."               | Headline / bullet / objection-handler |

### Gaps & surprises
- ...

### Handoff
Lead with: {theme}. Must answer: {objection}.
```

## Quality bar

- [ ] Every theme backed by ≥ 2 verbatims, quoted exactly
- [ ] Frequencies counted, not vibed
- [ ] Sampling bias of the corpus stated up front
- [ ] JTBD statements contain a real situation, not a demographic
- [ ] Map entries are usable copy blocks, not categories
- [ ] At least one finding that challenges the current positioning (or explicit "none found")

## Example

**Ask**: "Analyze these 80 G2 reviews of my scheduling tool."
**Produced**: theme table (top pain: "double-booked because integrations lag", 19 mentions), 3 JTBD statements, a message-market map with 8 ready-to-use lines, gap ("nobody markets to the assistant persona who actually configures it"), and the handoff note.
