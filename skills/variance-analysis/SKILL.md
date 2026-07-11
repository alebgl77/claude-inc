---
name: variance-analysis
description: "Explains budget-vs-actual or period-over-period variances: sets a materiality threshold first, builds the variance table in dollars and percent, decomposes drivers (price, volume, mix, timing, one-offs), draws a bridge waterfall, and writes the so-what per material line with forecast impact. Use when the user says 'why are we over budget', 'explain the miss vs plan', 'build the monthly flux commentary', or 'what drove the revenue variance'."
---

# Variance Analysis — Variance Analyst

> "Explain the variances."

## When to use

- Budget vs actual needs explaining — "why is opex 30% over plan?".
- Monthly flux commentary is due — "write the June-vs-May flux notes for the close".
- One line moved hard — "what drove the gross margin drop?".
- Leadership wants the story — "the board asks: are we beating plan, and why?".
- The forecast needs updating off the variances — "what does this miss mean for full year?".

## Workflow

1. **Load budget and actuals with code** (pasted or CSV/XLSX — never mental math on long columns). Align line items and periods, mapping renamed or regrouped lines explicitly. Verify both columns foot to their reported totals before analyzing.
2. **Set materiality first**, before looking at any variance: propose a threshold (e.g., greater of $25k or 5% of the line's budget), confirm with the user or record it as an assumption. This prevents cherry-picking.
3. **Build the variance table:** budget, actual, $ variance, % variance, F/(U) tagged by the line's nature — revenue above plan is favorable, cost above plan is unfavorable.
4. **Split material from immaterial.** Lines above threshold each get analysis; the rest roll into one "all other" line whose net is shown.
5. **Decompose each material variance into drivers:** price, volume, mix, timing (shifted between periods, not gone), one-off (non-recurring). Use unit and rate data where available; where not, state the split as an estimate with its basis.
6. **Build the bridge waterfall:** budget total → one bar per driver → actual total, as a text waterfall (or chart if plotting is available). Bars must sum exactly to the total variance — no plug bar.
7. **Write the "so what" per material line:** root cause, whether it persists, and the action it implies. One tight paragraph each — no restating the table in prose.
8. **Note forecast impact:** classify each material variance run-rate (annualize it) vs one-time (exclude it), and state the resulting full-period outlook adjustment.

## Output format

```
# Variance Analysis — <scope> — <period> vs <baseline>
Materiality: greater of $<X> or <Y>% of line budget

## Variance table
| Line | Budget | Actual | Var $ | Var % | F/(U) | Driver summary |
|------|-------:|-------:|------:|------:|:-----:|----------------|
| <line> | | | | | | <price/volume/mix/timing/one-off> |
| All other (below threshold) | | | <net> | | | n/a |
| **Total** | | | <T> | | | |

## Bridge (budget → actual)
Budget                       <B>
  <driver 1, e.g. Volume>    −<amt>
  <driver 2, e.g. Price>     +<amt>
  <driver 3, e.g. Timing>    +<amt>
  <driver 4, e.g. One-off>   −<amt>
Actual                       <A>
Check: bars sum to total Var $ <T> ✓

## Commentary (material lines)
**<Line> — <Var $> <F/(U)>.** <root cause; persists or not; implied action.>

## Forecast impact
Run-rate: <lines → annualized effect>. One-time: <lines>. Outlook: <adjustment>.
```

## Quality bar

- [ ] Materiality stated before analysis and applied consistently.
- [ ] Table computed in code; line variances re-foot to the total variance exactly.
- [ ] Waterfall bars sum to the total — no unexplained plug.
- [ ] Every driver split labeled data-based or estimated (with basis).
- [ ] F/(U) orientation correct by line nature — a cost underspend reads favorable.
- [ ] Commentary says why and what next, not a prose restatement of the table.

## Example

**Invocation:** "`budget-q2.xlsx` vs `actuals-q2.xlsx` — why did we miss?"
**Produced:** Variance table across 28 lines at $25k/5% materiality; four material lines; a waterfall showing revenue −$180k split into volume −$210k and price +$30k; one-paragraph commentary per line; a forecast note cutting full-year revenue $150k for the run-rate volume shortfall while excluding a one-off $25k credit.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
