---
name: compliance-check
description: "Compliance pre-flight for a feature, campaign, or initiative — maps the data and activity involved, checks applicable regimes (privacy/GDPR-style, consumer protection, marketing rules, sector-specific), lists required approvals and notices, builds a gap list with remediation owners, and ends in a go/no-go recommendation with conditions. Use when the user says 'can we ship this', 'is this campaign legal', 'any compliance issues here', or before anything touching personal data launches."
---

# Compliance Check — Compliance Officer

> "Check compliance"

A pre-flight, not an audit: it tells the team what clears the runway and what grounds the launch. Works from a plain-language description of the initiative.

## When to use

- "Can we ship this feature next sprint?" — the pre-launch gate
- "Is this email campaign legal?" — marketing-rules check
- "We want to start collecting <new data>" — privacy read before the schema changes
- "Ops wants to roll this out in Germany" — new-jurisdiction scan
- Post-incident exposure questions belong to `legal-risk-assessment`; this skill runs before launch, not after damage

## Workflow

1. Restate the initiative in one paragraph from user input: what ships, to whom, in which jurisdictions, on what date. Ask for whichever of those four is missing.
2. Map data and activity: personal data categories (sensitive flagged), the flow from collection → storage → sharing → retention, plus regulated activity — payments, minors, automated decisions, health or financial data, outbound marketing.
3. Run the regimes checklist, marking each APPLIES / N/A / UNCLEAR: privacy and data protection (lawful basis, notice, DPIA, cross-border transfer, processor terms); consumer protection (pricing claims, dark patterns, cancellation flows); marketing rules (consent for email/SMS, unsubscribe mechanics, endorsement disclosures); sector-specific regimes (health, finance, children, telecom); and existing contract commitments (DPAs, MSAs) that constrain the plan.
4. For every APPLIES: name the concrete requirement — approval, notice, consent, record, or filing — and whether the plan meets it today.
5. Build the gap list: requirement → current state → remediation → owner → deadline. Every UNCLEAR becomes a resolve-by task with an owner, never a silent assumption.
6. Decide: GO / GO WITH CONDITIONS / NO-GO. Conditions must be testable ("ship after the consent checkbox is unbundled from the ToS"), never "ensure compliance".
7. Deliver the report and name the human approvals still outstanding (DPO, counsel, finance) so nobody mistakes a pre-flight for sign-off.

## Output format

```
COMPLIANCE PRE-FLIGHT — <initiative> — <date>
Scope: <what / who / where / when>

DATA & ACTIVITY MAP
- Personal data: <categories — sensitive flagged>
- Flow: <collection → storage → sharing → retention>
- Regulated activity: <payments / minors / automated decisions / none>

APPLICABLE REGIMES
| Regime                    | Applies? | Requirements triggered            |
|---------------------------|----------|-----------------------------------|
| Privacy / data protection | YES      | <lawful basis, notice, DPIA, ...> |
| Consumer protection       | N/A      | —                                 |
| Marketing rules           | UNCLEAR  | <what to resolve, by whom>        |
| Sector-specific: <which>  | YES      | <requirement>                     |
| Existing contract terms   | <...>    | <DPA / MSA constraint>            |

REQUIRED APPROVALS & NOTICES
- <approval or notice> — <in place / needed / unclear>

GAP LIST
| # | Gap | Remediation | Owner | Due |
|---|-----|-------------|-------|-----|
| 1 | <requirement not met> | <fix> | <who> | <date> |

RECOMMENDATION: <GO / GO WITH CONDITIONS / NO-GO>
Conditions: <numbered, testable — empty only on a clean GO>

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] Every regime marked APPLIES / N/A / UNCLEAR — nothing skipped silently
- [ ] Every UNCLEAR carries a resolve-by task and owner, never an assumption
- [ ] Every gap has a named owner and a deadline
- [ ] Conditions on a GO are testable, not "ensure compliance"
- [ ] Sensitive data categories called out wherever they appear
- [ ] Outstanding human approvals listed by role

## Example

**Invocation:** "We want to add session-replay analytics to the EU checkout flow next month."

**Produces:** Map showing behavioral data plus payment-adjacent inputs; privacy regime APPLIES (lawful basis, notice update, DPIA, processor DPA with the replay vendor), consumer protection N/A, marketing N/A. Gap list: mask card fields (engineering, pre-launch), update the privacy notice (legal, pre-launch), run the DPIA (DPO, two weeks). Recommendation: GO WITH CONDITIONS — all three gaps closed before traffic.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
