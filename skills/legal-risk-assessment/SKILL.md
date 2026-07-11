---
name: legal-risk-assessment
description: "Severity-by-likelihood legal risk register for a situation or deal — enumerates concrete risks, scores each one impact 1-5 × likelihood 1-5, renders a heat-map table, attaches mitigations to every risk at or above threshold, defines escalation criteria for immediate human counsel, and sets monitoring triggers. Use when the user says 'what's our exposure', 'how risky is this deal', 'assess the legal risk of this', or before committing to anything with real downside."
---

# Legal Risk Assessment — Risk Assessor

> "Flag legal risk"

Turns "this feels risky" into a scored, sorted register with owners and tripwires. Works from a description of the situation plus any documents provided.

## When to use

- "What's our exposure if we sign this?" — deal downside read
- "How risky is operating without a signed DPA for a quarter?"
- "Rank the legal risks of this expansion plan"
- Before an exec or board commit on a contested move
- Clause-level contract surgery belongs to `review-contract`; this skill scores the whole situation

## Workflow

1. Frame the situation: the decision at stake, timeline, jurisdictions, counterparties, and what "bad" concretely looks like for the business.
2. Enumerate risks across the standard surfaces — contractual, regulatory, IP, privacy and data, employment, litigation, reputational-with-legal-consequence. Each risk is a concrete event ("residuals clause lets the vendor reuse our roadmap"), never a category name ("IP risk").
3. Score each risk: impact 1-5 (1 = nuisance cost … 5 = company-changing) × likelihood 1-5 (1 = remote … 5 = expected). Score = impact × likelihood, with a one-line rationale per score — unexplained numbers are guesses.
4. Render the heat map sorted by score, descending.
5. Attach a mitigation to every risk at or above threshold (default: score ≥ 8, overridable): the action, its owner, and the residual score once done.
6. Define escalation criteria — observable conditions that send this to human counsel immediately (e.g., any impact-5 risk, regulator contact, a litigation threat received, press involvement).
7. Set monitoring triggers: events that reopen the assessment ("counterparty misses a payment", "new guidance published on X"), each with a named watcher.
8. Deliver the dated register and a one-sentence bottom line: proceed, proceed with mitigations, or do not proceed.

## Output format

```
LEGAL RISK REGISTER — <matter> — <date>
Decision at stake: <one line>   Mitigation threshold: score ≥ 8

HEAT MAP (sorted by score)
| # | Risk (concrete event) | Impact (1-5) | Likelihood (1-5) | Score | Rationale  |
|---|-----------------------|--------------|------------------|-------|------------|
| 1 | <risk>                | 4            | 4                | 16    | <one line> |
| 2 | <risk>                | 5            | 2                | 10    | <one line> |
| 3 | <risk>                | 2            | 3                | 6     | <one line> |

MITIGATIONS (score ≥ threshold)
| Risk # | Mitigation action | Owner | Residual score |
|--------|-------------------|-------|----------------|
| 1      | <action>          | <who> | <I × L after>  |

ESCALATE TO HUMAN COUNSEL IMMEDIATELY IF
- <observable condition>
- <observable condition>

MONITORING TRIGGERS
- <event> → reassess risk #<n> — watcher: <who>

BOTTOM LINE: <proceed / proceed with mitigations / do not proceed> — <one sentence why>

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] Every risk is a concrete event, not a category label
- [ ] Every score carries a one-line rationale — no bare numbers
- [ ] Every risk at or above threshold has a mitigation, an owner, and a residual score
- [ ] Escalation criteria are observable conditions, not judgment calls
- [ ] Register is dated and every monitoring trigger names a watcher
- [ ] Bottom line commits to one recommendation

## Example

**Invocation:** "We're about to sign a 3-year exclusive distribution deal in a market we've never operated in. Exposure?"

**Produces:** A register of seven risks. Top score 16: exclusivity lock-in with no minimum-performance exit (impact 4 × likelihood 4), mitigated by a termination-for-underperformance clause (residual 8). Escalation fires if the counterparty demands a non-compete covering existing markets; monitoring trigger on quarterly sales versus floor, watched by the deal owner. Bottom line: proceed with mitigations.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
