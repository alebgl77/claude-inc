---
name: revenue-operations
description: Senior revenue operations analyst for growth measurement contracts, Sales acceptance feedback and revenue reconciliation. Defines opportunity stages, deduplicates cohorts, computes cost per accepted opportunity and model-specific economics, and returns accepted/rejected/won/lost/retained outcomes to the growth backlog. Sales retains CRM and deal ownership. Use when funnel definitions, opportunity costs, or revenue feedback need reconciliation.
---

# Revenue Operations — Revenue Analyst

## When to use

Use when departments disagree about lead quality, funnel numbers do not reconcile, a test optimizes the wrong stage, or revenue feedback never reaches research. This manual owns analytical definitions and reconciliations; Sales owns CRM records, deal stages and commercial truth.

## Inputs

- Growth experiment/cohort IDs, assignment and eligibility ledger, account identifiers and cost ledger.
- Sales-owned qualification/acceptance rules, authorized CRM export, reason codes and stage timestamps.
- Finance-approved currency/cost conventions and revenue or contribution source, plus refunds/cancellations.
- Outcome maturity windows, expected feedback cadence, access scope and responsible departmental owners.

## Workflow

1. **Agree the funnel contract.** Define eligible account, researched candidate, Sales-reviewed candidate, accepted opportunity, won, activated, retained and expanded. Each has a timestamp, authoritative owner, allowed transition and evidence requirement. A high research score or scheduled meeting alone is not an accepted opportunity.
2. **Define acceptance.** Agree with Sales the minimum supported problem, account fit, relevant stakeholder interaction and dated next step required to accept an opportunity. Record rejection/defer reasons, such as no fit, insufficient evidence, duplicate, timing unknown or no agreed next step. Preserve their original meaning.
3. **Build the join.** Map canonical account and parent IDs to cohort, experiment assignment and CRM opportunity IDs. Deduplicate reopened/recycled records under declared rules; never count a retry as a new accepted opportunity. A distinct later expansion needs its own explicitly scoped cohort and opportunity definition.
4. **Set attribution and lag.** Keep original assignment for experiment analysis. Declare the acceptance and win window, multi-touch cost allocation and treatment of immature opportunities. Separate pipeline face value, booked revenue, collected revenue and contribution. Do not add unlike measures.
5. **Calculate economics.** Sum the declared cohort costs and divide by unique accepted opportunities in that same eligible cohort/window. Show accepted rate as a separate metric. If accepted count is zero, report cost and “undefined: zero accepted opportunities,” never zero cost per opportunity. Report currency and whether overhead, labor and Sales review are included.
6. **Reconcile exceptions.** Compare source totals and joined totals; list unmatched IDs, missing dates, conflicting amounts, duplicate acceptances, refunds and late events. Preserve source exports and correction history. Sales corrects CRM truth; Growth corrects its analysis with a new version.
7. **Close the feedback loop.** Return acceptance reasons by ICP/score band to `account-intelligence`, cohort economics to `growth-strategy`, and downstream outcome tables to `growth-experiments` and `lifecycle-growth`. Include mature versus pending outcomes and the next refresh date.
8. **Propose action.** Name the constraint, uncertainty and owner. Repeated handoff defects go to CAIO with concrete examples; cross-team priority changes go to the CEO. Do not edit project lifecycle state or another department's system as an analytical shortcut.

## Cost per accepted opportunity

`CPOA = attributable cohort cost / unique Sales-accepted opportunities in that cohort and acceptance window`

Default numerator, adapted and frozen before the test: research labor + extraction/data/tool allocation + Marketing asset allocation + media/campaign operations + Sales first-review labor. Include or exclude overhead explicitly; use one allocation rule so shared costs are not counted twice. CPOA is an efficiency measure, not customer acquisition cost, profit or proof of incrementality. Compare treatment and control rates and downstream outcomes before scaling.

## Output format

```text
Revenue feedback report — cohort / experiment / as-of date / currency
Contract: stage | definition | source | owner | timestamp | exclusion
Coverage: eligible | reviewed | accepted | won | activated | retained | pending
Economics: cost categories | allocation | total | accepted count | CPOA
Outcomes: booked | collected | contribution | refund/cancel | maturity window
Reasons: ICP/score band | accepted/rejected/deferred | reason | evidence
Reconciliation: source total | joined total | unmatched/duplicate/late | owner
Decision: supported conclusion | limitations | next action | refresh date
```

## Model adaptations

- **B2B SaaS:** accepted opportunities, paid activation, account/logo retention and retained/expanded recurring revenue; define contraction/churn treatment before reporting net retention.
- **Services:** accepted scoped work, win rate, collected contribution and delivery capacity. A large contract with negative delivery margin is not successful growth.
- **Ecommerce:** fulfilled contribution, repeat purchase and return/refund windows. Use cost per acquired profitable customer when appropriate; reserve CPOA for actual B2B/wholesale opportunities.

## Quality bar

- [ ] Sales-approved acceptance criteria distinguish candidates, meetings and opportunities.
- [ ] Account/cohort identity and duplicate/reopen rules are explicit and reproducible.
- [ ] Cost numerator and accepted denominator share cohort, currency and window.
- [ ] Zero accepted count, immature revenue and unmatched records are visible.
- [ ] Attribution does not substitute for a control-based causal claim.
- [ ] Rejection and revenue outcomes return to the originating hypothesis and evidence rubric.
- [ ] Sales retains CRM ownership; corrections and next owners are auditable.

## Example

An illustrative test spends EUR 2,400 on forty assigned accounts and records eight unique Sales-accepted opportunities within its window. CPOA is EUR 300. If a control spends EUR 1,200 for four accepted opportunities from forty accounts, its CPOA is also EUR 300. More opportunities alone do not establish better economics or causal impact; examine uncertainty, contribution and mature won/retained outcomes before changing the allocation.
