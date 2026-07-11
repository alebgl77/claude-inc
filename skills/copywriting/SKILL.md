---
name: copywriting
description: Direct-response copywriting for landing pages, emails, and ads. Picks the right framework (AIDA, PAS, 4U headlines), loads brand voice if a profile exists, builds a 10-variant headline matrix, writes proof-backed body copy toward a single CTA, and pressure-tests every line. Use when the user says "write the landing page", "draft this launch email", "I need headlines for this offer", "punch up this copy", or any request for words that must convert.
---

# Copywriting — Word Smith

> "High-converting copy"

## When to use

- Landing page, sales page, or hero copy — "write the landing page for our beta launch"
- Emails that must get opened and clicked — "draft the announcement email for new pricing"
- Short-form promo or ad copy blocks — "I need 10 headlines for this offer"
- Rewrites of flat, underperforming copy — "punch up this hero section"
- Not for long-form SEO content — hand that to `ai-seo`

## Workflow

1. **Lock the brief.** One reader (role, pain, current belief), one offer, one action, one success metric. If any piece is missing, state your assumption in one line and keep moving.
2. **Pick the framework.**
   - **AIDA** — cold traffic; the reader needs the problem built before the pitch.
   - **PAS** — problem-aware readers; agitate the pain they already feel, then resolve it.
   - **4U** (urgent, unique, useful, ultra-specific) — headlines and subject lines.
3. **Load the voice.** Look for a brand or voice profile in the project (`brand/`, `voice.md`, style guide). If found, extract tone rules and banned words. If not, mirror the user's existing copy and flag the gap at the top of the deliverable.
4. **Build the headline matrix.** 10 variants across distinct angles — benefit, pain, curiosity, proof/number, how-to, question, contrarian, urgency, comparison, story. Score each 0-4 on the 4Us; mark the top 3.
5. **Write the body.** Follow the framework beat by beat. Attach a proof element to every claim — stat, customer quote, mini case, demo line, or guarantee. No naked promises.
6. **One CTA.** Action verb + concrete outcome ("Send your first invoice free"). Repeat it verbatim in long assets; kill every competing link.
7. **Reading-level pass.** Target grade 7 or below. Short sentences. Cut hedges and intensifiers — "really", "very", "arguably" all die.
8. **Run the "so what?" test.** Read every line as the target reader asking "so what?". Any line without an answer gets cut or rewritten until the benefit is explicit.
9. **Deliver** in the output format below.

## Output format

```
ASSET: <landing hero / email / ad block>
READER: <one-line persona + what they believe today>
FRAMEWORK: <AIDA | PAS | 4U> — <why, one clause>
VOICE SOURCE: <profile file | mirrored from existing copy | assumption>

HEADLINE MATRIX
| # | Angle | Headline | 4U score | Top 3 |
|---|-------|----------|----------|-------|
| 1 | Benefit | ... | 3/4 | * |
| 2 | Pain | ... | 2/4 | |
| ... 10 rows total ... |

FINAL COPY
<the full asset, framework beats as written sections>

CTA: <exact button or link text>
CHECKS: reading level ~grade <n> | claims proven <n>/<n> | so-what pass done
```

## Quality bar

- [ ] Every claim ships with its proof element in the copy itself
- [ ] One big idea, one CTA — no competing asks anywhere in the asset
- [ ] Headline matrix holds 10 genuinely distinct angles, not synonyms
- [ ] Reading level at or below grade 7
- [ ] Every line survives the "so what?" test
- [ ] Voice matches the profile — or the assumption is flagged at the top

## Example

**Invocation:** "Write the hero section for InvoiceOwl, an invoicing tool for freelance designers who hate admin."

**Produced:**
- Brief: freelance designer billing 5-10 clients, believes invoicing tools are enterprise overkill; metric = trial starts
- Framework: PAS. Matrix of 10 scored headlines — "Get paid 9 days faster. Design in the time you save." marked top
- 120-word hero with two proof points (payment-speed stat, customer quote), CTA "Send your first invoice free"
- Checks: grade 6, 2/2 claims proven, so-what pass complete
