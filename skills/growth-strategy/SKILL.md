---
name: growth-strategy
description: Senior growth strategist for a measurable growth system across B2B SaaS, services and ecommerce. Converts business constraints, ICP evidence and unit economics into a prioritized experiment portfolio with owners, handoffs and explicit decisions. Use for growth planning, choosing ABM versus product-led sales, diagnosing a stalled funnel, or aligning acquisition with retention and revenue.
---

# Growth Strategy — Growth Architect

## When to use

Use when the business needs a growth direction, not just a campaign: an unproven ICP, expensive opportunities, weak activation, stalled expansion or competing ideas with no decision rule. Marketing owns positioning and assets; Sales owns deals. This manual owns the growth hypothesis portfolio.

## Inputs

- Offer, pricing, contribution margin, delivery capacity and intended growth horizon.
- Buyer, end user, economic decision maker, segment and geography; distinguish evidence from assumptions.
- Last complete funnel cohorts with counts and dates: eligible accounts → accepted opportunities → won → activated → retained or expanded.
- Customer research, reasons for rejection/loss/churn, current acquisition and product motion, and available measurement.
- Constraints: staffing, budget ceiling, implementation lead time and already-authorized actions.

Missing baseline is a measurement task, not permission to invent one. Start a data inventory and name the decision it blocks.

## Workflow

1. **Map the money path.** Draw the stages with entry/exit criteria, counts, lag and owner. For SaaS, follow account activation and retained recurring revenue; for services, follow qualified work, delivery capacity and contribution margin; for ecommerce, follow fulfilled profitable orders and repeat purchase, net of returns.
2. **Select the constraint.** Compare stage losses, cost and delay. Choose one constraint supported by cohort data or label it an untested diagnosis. Separate weak demand from poor qualification, slow time to value and capacity limits.
3. **Write ICP v1.** Define the job/problem, account attributes, buyer role, must-have fit, exclusions, evidence sources and falsifiers. Include a negative ICP. Do not use a title, funding event or technology alone as a need signal. Route the evidence plan to `account-intelligence`.
4. **Choose a motion.** Compare ABM for identifiable high-value accounts, product-led sales for demonstrated account value and buying complexity, self-serve for short low-friction purchases, and partner/referral for trust or distribution access. Give the reason, cost constraint and an exit condition for the choice.
5. **Set a metric tree.** Choose a business outcome and leading indicators with denominators. Example: contribution from won accounts ← accepted-opportunity rate × win rate × contribution per win; activation and retention guard against buying poor-fit customers. Record measurement lag.
6. **Build the backlog.** Each idea states the causal hypothesis, target cohort, evidence strength, measurable effect worth pursuing, cost, dependency and owner. Rank by expected decision value and reversible effort; do not dress guesses up as precise ROI. Unknown tracking comes before a test it would invalidate.
7. **Sequence the first cycle.** Select at most three non-conflicting tests within capacity. Send design to `growth-experiments`, tracking to `growth-engineering`, assets to Marketing and qualification review to Sales. Specify which account cohort cannot be reused during the test.
8. **Define review cadence.** Review tracking and safety as needed; review efficacy only under the test's declared rule. Revisit ICP using accepted/rejected and won/lost cohorts. Return a recommendation to the CEO for cross-team priorities, without writing project lifecycle state.

## Output format

Produce `growth-strategy.md` with these completed sections:

```text
Decision and horizon:
Business model / buyer / user / account unit:
Constraint with cohort evidence and missing data:
ICP: must-haves | exclusions | sources | falsifier:
Chosen motion and reason; alternative and exit condition:
Business outcome / leading indicators / guardrails:
Backlog: ID | hypothesis | cohort | effect worth testing | evidence | cost | dependency | owner:
First cycle: test IDs | handoff recipient | acceptance rule | dates:
Review: decision owner | observation date | revenue feedback source:
```

Complete a first experiment brief; a ranked idea list alone is not finished work.

## Quality bar

- [ ] One chosen constraint is supported or explicitly provisional.
- [ ] ICP contains exclusions and falsifiers, with buyer/user differences.
- [ ] Metric definitions reconcile to revenue, margin or retained value and include time windows.
- [ ] Selected motion fits deal size, buying behavior and delivery capacity.
- [ ] Backlog exposes cost, dependencies and uncertainty; owners can act on the first brief.
- [ ] Handoffs preserve Marketing's asset ownership and Sales' deal ownership.
- [ ] Every proposed test can return inconclusive; no claimed ROI without observed outcomes.

## Example

A B2B services firm has spare delivery capacity but few accepted opportunities. The plan first checks why Sales rejected recent accounts, builds a narrow operations-team ICP, and tests a diagnostic-offer brief through Marketing and Sales. Success is contribution from won work at a sustainable cost per accepted opportunity. A SaaS company with ample signups but poor account activation would instead start with time to first shared value; a shop with high returns would prioritize profitable fulfillment before increasing acquisition.
