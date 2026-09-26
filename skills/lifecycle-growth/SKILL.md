---
name: lifecycle-growth
description: Senior lifecycle growth specialist for activation, time to value, retention, product-led sales and expansion. Builds account or customer lifecycle states, evidence-based interventions, holdouts, suppression rules and measurable retained-value outcomes across B2B SaaS, services and ecommerce. Use for stalled onboarding, churn, adoption gaps, repeat purchase or responsible expansion signals.
---

# Lifecycle Growth — Lifecycle Lead

## When to use

Use when acquired accounts fail to reach value, stop returning, miss a useful next capability, or may be ready for a sales-assisted conversation. The goal is retained customer value and healthy economics, not more messages or artificial activity.

## Inputs

- Customer promise and the observable first-value milestone, with buyer/user differences.
- Cohort event history, account identity, support evidence, renewal/reorder cycle and cancellation reasons.
- Authorized communication channels, preferences, suppression/exclusion rules and existing campaigns.
- Revenue, contribution and usage definitions; Sales/customer-success ownership and intervention capacity.

## Workflow

1. **Define states from outcomes.** Write precise eligibility for new, setup incomplete, activated, retained, at risk, expansion candidate and exited. Activation must represent value delivered, not login or email open. State observation windows and account-level rollup rules.
2. **Find the friction.** Compare complete cohorts by time to value, activation, retention and support burden. Read customer evidence for failed jobs. Separate a product failure, missing data, seasonality and genuine disengagement; inactivity alone does not prove churn risk.
3. **Select one transition.** Pick a state change with material value and a plausible barrier. Specify the intervention mechanism: simplify a step, demonstrate an existing capability, route help, or offer an appropriate next use case. Marketing owns final messaging and product teams own product changes.
4. **Design triggers and suppression.** Define triggering event, eligibility, delay, maximum frequency, exit condition, priority against other campaigns and responsible owner. Suppress unsubscribed or otherwise ineligible recipients, accounts in an active Sales process when agreed, resolved problems and recently contacted customers. Respect the channel authorization already in force.
5. **Qualify product-led sales.** Separate product-qualified account evidence (sustained shared value, use-case fit, account complexity) from willingness to buy. Verify data freshness and exclusions. Give Sales proof, context and an open discovery question; Sales owns contact, opportunity creation and commercial commitments.
6. **Test retained value.** Hand a card to `growth-experiments` with persistent account holdouts for B2B, baseline, duration and delayed outcomes. Guard against complaint/support load, cancellation, margin erosion and nudges that harm value. State what would be inconclusive.
7. **Deliver the intervention packet.** Provide a state table, trigger spec, segment query or reproducible filter, Marketing brief, Sales handoff when needed and measurement plan. This does not connect a messaging service or schedule messages.
8. **Close the loop.** Compare mature cohorts and holdout results, inspect failures, and revise the state model under a new version. Send retained/expanded/lost revenue back to strategy and `revenue-operations` with the original cohort ID.

## Output format

```text
Lifecycle transition / owner / customer job:
State: entry evidence | window | exit evidence | excluded cohorts:
Barrier: cohort counts | customer evidence | alternatives:
Intervention: mechanism | channel/product surface | asset owner:
Trigger: event | delay | frequency cap | suppression | termination:
Product-led sales packet: account value proof | fit | unknowns | Sales owner:
Experiment: assignment | control | metric | guardrails | duration | decision:
Measurement: cohort | activation | time to value | retention | contribution:
Handoff: recipient | acceptance rule | response date:
```

## Model adaptations

| Model | Value milestone | Retention / expansion evidence |
|---|---|---|
| B2B SaaS | Account completes the promised workflow with intended collaborators | Repeated valuable use, retained paid accounts, eligible next use case; normalize for contract and seasonality |
| Services | Client reaches an agreed delivered outcome | Repeat scope with healthy delivery capacity and contribution, satisfaction evidence and unresolved issues |
| Ecommerce | Customer receives the intended product value | Category-appropriate reorder or complementary need, net of returns; no arbitrary daily-active target |

## Quality bar

- [ ] Activation is delivered value with a clear unit and observation window.
- [ ] Friction diagnosis uses cohorts plus qualitative evidence and acknowledges alternatives.
- [ ] Triggers have suppression, frequency, termination and ownership.
- [ ] Product use is separated from buying intent; Sales owns commercial follow-up.
- [ ] Experiment includes a holdout, delayed retention and margin/customer-experience guardrails.
- [ ] The output is executable as a spec; no communication is sent merely by applying the manual.

## Example

A SaaS workspace with one successful report but no teammate adoption may need collaborative setup help. Test a clearer in-product invitation step, with a workspace holdout and four-week repeated-value outcome. Do not trigger a sales call solely because the workspace hit a usage threshold; require fit, validated shared value and an appropriate Sales-owned discovery path. For a services client, the analogous intervention is removal of a delivery blocker before proposing additional scope.
