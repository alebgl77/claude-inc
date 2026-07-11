---
name: cro
description: Conversion audit for funnels and pages — a section-by-section friction log (clarity, anxiety, distraction, motivation), heuristic checks (message match, above-the-fold value prop, form cost), an ICE-scored hypothesis backlog, and top-3 A/B test designs with success metrics and minimum-sample notes. Use when the user says "why isn't this page converting", "audit our signup flow", "conversion dropped after the redesign", or "what should we A/B test next".
---

# CRO — Conversion Lead

> "Lift conversion rates"

## When to use

- A page or funnel underperforms — "the trial page converts at 1.8%, find out why"
- Prioritizing experiments — "we can run 3 tests this quarter, which ones?"
- Pre-launch conversion review — "sanity-check this pricing page before we ship"
- Post-change regression — "signups dropped 20% after the redesign"
- Not for writing the new copy itself — findings hand off to `copywriting`

## Workflow

1. **Collect the funnel.** Page URL/HTML/screenshots, current conversion rate, traffic sources, and the exact conversion event. No baseline number? Ask for the best estimate and mark the audit directional.
2. **Walk the friction log.** Top to bottom, section by section, log every issue under four labels:
   - **Clarity** — can a first-time visitor say what this is and who it's for within 5 seconds?
   - **Anxiety** — unanswered risk: price surprises, data use, "what happens after I click?"
   - **Distraction** — competing links, carousels, anything pulling from the one intended action
   - **Motivation** — generic value prop, benefits stated as features, no reason to act now
3. **Run the heuristics.**
   - Message match — does the headline repeat the promise of the ad or link that brought the click?
   - Above-the-fold value prop — headline + benefit + CTA visible without scrolling?
   - Form cost — field count × sensitivity; every field must earn its place
4. **Write the hypothesis backlog.** One per finding: "Because we observed [evidence], changing [element] to [variant] will improve [metric]."
5. **Score ICE.** Impact, Confidence, Ease — each 1-10 with a one-line justification. Rank by the product.
6. **Design the top 3 tests.** Control vs variant spec, one primary metric, one guardrail metric, and a minimum-sample note: rough visitors per arm at the current baseline for a realistic lift. Flag tests that traffic volume would stretch past a month.
7. **Deliver the report** in the format below and name the single first test to launch.

## Output format

```
FUNNEL: <page/flow> | BASELINE: <CR%, period> | TRAFFIC: <sources>

FRICTION LOG
| # | Section | Type (C/A/D/M) | Finding | Severity (killer/major/cosmetic) |
|---|---------|----------------|---------|----------------------------------|

HEURISTICS
Message match: <pass/fail + note> | Above-fold prop: <pass/fail> | Form cost: <n fields, verdict>

HYPOTHESIS BACKLOG
| # | Because / change / expect | I | C | E | ICE | Rank |
|---|---------------------------|---|---|---|-----|------|

TOP-3 TEST DESIGNS
Test 1: <name>
- Variant: <exact change>
- Primary metric: <...> | Guardrail: <...>
- Sample note: ~<n> visitors/arm at <baseline>% to detect a <x>% relative lift
<repeat for Tests 2-3>

FIRST MOVE: <the one test to launch this week, and why it wins the tie>
```

## Quality bar

- [ ] Every hypothesis cites observed evidence from the friction log, not taste
- [ ] Each ICE score carries a one-line justification
- [ ] Each test has exactly one primary metric plus a guardrail
- [ ] Sample-size note present — no recommending underpowered tests
- [ ] Severity labels separate conversion killers from cosmetics
- [ ] The first-move recommendation is executable within a week

## Example

**Invocation:** "Our B2B trial signup page converts at 2.1% from Google Ads — audit it." (page HTML attached)

**Produced:**
- Friction log: 9 findings — headline breaks message match with the ad, an 11-field form, full nav menu on a PPC landing page
- 7 hypotheses ICE-ranked; cutting the form to 4 fields ranks #1 (ICE 648)
- 3 test designs with metrics and a ~8,800 visitors/arm sample note; first move: cut the form
