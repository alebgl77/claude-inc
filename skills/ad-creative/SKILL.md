---
name: ad-creative
description: Generates batches of ad concepts — headlines, primary text, and visual briefs — organised by angle and awareness level, with per-platform specs for Meta, LinkedIn, X and TikTok. Use when the user asks to "write ads", "give me ad headlines", "create ad variations", "make a visual brief", or needs creative for a paid campaign.
---

# Ad Creative — Ad Maker

> "Ad headlines & visuals"

## When to use

- "Write me 10 ad variations for this product"
- "I need headlines for a Meta campaign"
- "Give me a visual brief for this ad concept"
- Launching or refreshing any paid campaign where creative volume and angle diversity decide performance
- Creative fatigue: CTR dropping and the account needs new concepts, not new budgets

## Workflow

1. **Collect inputs**: product, offer, target customer, awareness level (unaware → most aware), platform(s), and any voice/brand profile on file (`voice-profile.md`, `BRAND.md`).
2. **Build the angles matrix**: pain, desire, curiosity, social proof, contrarian, urgency — crossed with the audience's awareness level. Kill angles the offer can't cash.
3. **Draft 10 headline + primary-text variants**, each tagged with its angle. Headlines ≤ 40 chars where the platform truncates; primary text front-loads the payoff in line one.
4. **Write a visual brief per concept**: composition (subject, framing, background), text overlay (≤ 5 words), color contrast note, and why it stops the scroll in-feed.
5. **Apply platform specs**: Meta (1:1 + 4:5, headline 40c), LinkedIn (1.91:1, professional proof-led), X (short, punchy, meme-literate), TikTok (9:16, native-not-polished, hook in first frame).
6. **Name every asset** with a tracking convention: `{campaign}_{angle}_{format}_{v#}`.
7. **Rank the batch**: top 3 to launch first, with one-line rationale each.

## Output format

```
## Ad Batch — {product / campaign}
Audience: {who} · Awareness: {level} · Platforms: {list}

| # | Angle | Headline | Primary text (first line) | Platform fit |
|---|-------|----------|---------------------------|--------------|
| 1 | ...   | ...      | ...                       | ...          |
(10 rows)

### Visual briefs
**Concept {n} — {angle}**: composition · overlay ("≤5 words") · contrast note · scroll-stop rationale

### Launch order
1. #{n} — {why}  2. #{n} — {why}  3. #{n} — {why}

### Asset naming
{campaign}_{angle}_{format}_{v#}
```

## Quality bar

- [ ] Every variant maps to exactly one angle — no mushy hybrids
- [ ] No claim the landing page can't back up
- [ ] Text overlays are ≤ 5 words and legible at thumbnail size
- [ ] At least 3 distinct angles represented in the top 10
- [ ] Naming convention applied to every asset
- [ ] Platform specs respected (ratios, character limits, tone)

## Example

**Ask**: "Write ads for my invoicing app for freelancers, Meta + LinkedIn."
**Produced**: 10 headline/text variants across pain ("Chasing invoices at 11pm again?"), desire, social proof and contrarian angles; 4 visual briefs; launch order with rationale; assets named `invapp_pain_4x5_v1`-style — ready for the ads manager.
