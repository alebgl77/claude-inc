---
name: margin-analyzer
description: Breaks unit economics down per product, service, or client: revenue minus direct costs into a contribution-margin ranking, allocated overhead into net margin, a price floor per unit, a push/fix/kill mix analysis, and three pricing moves with quantified margin impact. Use when the user says "revenue is up but profit isn't", "which clients actually make us money", "should we raise prices", "what should we stop selling", or pastes a sales and cost export.
---

# Margin Analyzer — Margin Analyst

> "Analyse margins."

Revenue is vanity, margin is sanity: this skill finds where the profit actually lives — and where it quietly leaks.

## When to use

- "Revenue is up 20% but the bank account isn't — where does the money go?"
- "Which products / services / clients actually make us money?"
- "Should we raise prices, and on what?"
- "A client is pushing for a discount — where's my floor?"
- Before adding a product line or killing one: run the mix first.

## Workflow

1. **Pick the unit and ingest data.** Product, service line, or client — whichever the decision is about. From pasted data or CSV: revenue per unit and direct costs (materials, direct labor hours × loaded rate, payment fees, shipping, subcontractors).
2. **Compute contribution margin with code.** Revenue − direct costs, per unit; rank by CM%. Show absolute and percentage — a 70% margin on 500 buys less than a 25% margin on 40,000.
3. **Allocate overhead and state the method.** Default driver: revenue share; switch to direct-labor hours when the business is labor-heavy. Compute net margin per unit. The allocation choice changes the answer — say which was used and why.
4. **Set price floors.** Floor = direct cost ÷ (1 − target CM%). Below the floor, work is declined or re-scoped — the floor is where discounting stops.
5. **Run the mix analysis.** Margin% against volume: PUSH (high margin — sell more of it), FIX (volume without margin — reprice, re-scope, or re-cost), KILL (low margin, low volume — sunset or replace).
6. **Model three pricing moves with code.** For example: +x% on the top-decile clients, a minimum order or engagement size, killing the worst SKU and redirecting its volume. Quantify annual margin impact and name every assumption.
7. **Pick the first move.** The one the owner can execute this month without losing a strategic client — and define "strategic" here (referrals, volume floor, flagship logo), not as a feeling.

## Output format

```
MARGIN ANALYSIS — <business> — <period> — unit: <product / service / client>

CONTRIBUTION MARGIN RANKING
Rank | Unit   | Revenue | Direct costs | CM     | CM% | Volume
1    | <name> | 38,000  | 14,400       | 23,600 | 62% | ...
...  | ...    | ...     | ...          | ...    | ... | ...

OVERHEAD: <total> allocated by <revenue share / direct-labor hours> — because <reason>
NET MARGIN
Unit | CM% | Overhead share | Net margin | Net%
...  | ... | ...            | ...        | ...

PRICE FLOORS (decline or re-scope below these)
Unit | Direct cost | Target CM% | Floor | Current price | Headroom
...  | ...         | ...        | ...   | ...           | ...

MIX
PUSH: <units> — <why, and the move that grows them>
FIX:  <units> — <reprice / re-scope / re-cost, with the number>
KILL: <units> — <sunset plan and where the freed capacity goes>

PRICING MOVES (modeled)
1. <move> → +<amount>/yr margin (<assumptions>)
2. <move> → +<amount>/yr (<assumptions>)
3. <move> → +<amount>/yr (<assumptions>)
First move: #<n> — executable this month because <reason>.
```

## Quality bar

- [ ] All margins computed with code from row-level data — no averaged averages.
- [ ] Direct labor costed at loaded rates, never bare wages.
- [ ] Overhead allocation method stated, with one sentence on why it fits this business.
- [ ] Every FIX and KILL names its number: the reprice, the re-scope, or the sunset date.
- [ ] Pricing moves quantified with explicit assumptions, not "should improve margins."
- [ ] Client rankings marked internal-only — flagged before anything ships externally.

## Example

**Invocation:** "Sales and job-cost export for H1 attached — which services are worth it?"

**Produced:** A CM ranking across five service lines: installs at 61% CM, maintenance contracts at 11% after loaded labor. Overhead allocated by labor hours (labor-heavy shop); price floors per line; mix verdict — push installs, fix maintenance with a +14% reprice at renewal, kill one-off repairs under 150. Three modeled moves worth 31,000/yr combined, with the maintenance reprice picked as the month-one move.
