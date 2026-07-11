---
name: review-contract
description: "Clause-by-clause contract review — inventories key clauses (term, termination, liability cap, indemnity, IP, payment, confidentiality, governing law, auto-renewal), flags deviations from market-standard positions with RED/YELLOW/GREEN severity and verbatim quotes, drafts redline language, and sets negotiation priority. Use when the user says 'review this contract', 'what's wrong with this MSA', 'can we sign this as-is', or pastes any agreement for analysis."
---

# Review Contract — Contract Reviewer

> "Review any contract"

Works on pasted contract text or a file. No playbook required: deviations are measured against explicit market-standard positions, so every judgment is visible and overridable.

## When to use

- "Review this MSA before tomorrow's call" — any contract that deserves more than a skim
- "Can we sign this vendor agreement as-is?" — a go/no-go read with fixes attached
- "What would you push back on here?" — building a negotiation position from scratch
- "They sent their redline back — does it hurt?" — re-review of a revised draft
- Standalone NDAs move faster through `triage-nda`; use this skill when confidentiality terms sit inside a bigger deal

## Workflow

1. Ingest the contract (pasted text or file path). Record parties, which side we are, contract type, effective date, and any deadline mentioned.
2. Inventory the nine key clauses: term, termination, liability cap, indemnity, IP ownership/license, payment, confidentiality, governing law and disputes, auto-renewal. A missing clause is a finding, not a blank — mark it MISSING.
3. Benchmark each clause against market-standard positions, stated explicitly (e.g., liability capped at 12 months' fees and mutual; indemnity limited to third-party IP, bodily injury, and confidentiality claims; termination for cause with 30-day cure; auto-renewal with a 30-day-or-longer opt-out; no unilateral mid-term price increases).
4. Assign severity per finding — RED: dealbreaker or uncapped exposure, do not sign as-is; YELLOW: off-market but fixable with targeted language; GREEN: market or better. Quote the operative text verbatim under every RED and YELLOW.
5. Draft a redline for every RED and YELLOW: replacement language ready to paste into the document, not a description of what to change.
6. Order negotiation priorities: REDs first, ranked by exposure; then YELLOWs ranked by cost-to-fix, marking which are trade material ("give to get").
7. Assemble the report in the output format. When working in a folder, save it beside the contract as `<contract-name>-review.md` and report the path.

## Output format

```
CONTRACT REVIEW — <contract name> — <date>
Parties: <counterparty> / <us> (we are the <customer/vendor/licensor/...>)
Type: <MSA / SaaS / services / license>   Deadline: <date or none>

CLAUSE INVENTORY
| Clause          | Present? | Severity | vs. market standard  |
|-----------------|----------|----------|----------------------|
| Term            | §<n>     | GREEN    | <one line>           |
| Termination     | §<n>     | YELLOW   | <one line>           |
| Liability cap   | MISSING  | RED      | uncapped by silence  |
| Indemnity       | §<n>     | <sev>    | <one line>           |
| IP              | §<n>     | <sev>    | <one line>           |
| Payment         | §<n>     | <sev>    | <one line>           |
| Confidentiality | §<n>     | <sev>    | <one line>           |
| Governing law   | §<n>     | <sev>    | <one line>           |
| Auto-renewal    | §<n>     | <sev>    | <one line>           |

FINDINGS
[RED] <clause> — <business impact, one line>
  Quote:   "<verbatim clause text>"
  Redline: "<paste-ready replacement language>"
[YELLOW] <clause> — <business impact, one line>
  Quote:   "<verbatim clause text>"
  Redline: "<paste-ready replacement language>"
[GREEN] <clauses at market or better — one line, no action>

NEGOTIATION PRIORITY
1. <RED finding> — must fix; walk away if refused
2. <RED finding> — must fix; fallback: <fallback position>
3. <YELLOW finding> — push; trade against <concession we can give>

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] All nine key clauses inventoried; MISSING treated as a finding with severity
- [ ] Every RED and YELLOW quotes the clause verbatim — no paraphrase-only flags
- [ ] Every RED and YELLOW ships a paste-ready redline, not "negotiate this"
- [ ] Each severity justified in one line of plain business impact
- [ ] Negotiation order ranks by exposure and leverage, not page order
- [ ] Market-standard baseline stated wherever a deviation is flagged

## Example

**Invocation:** "Review this SaaS agreement — we're the customer, they want it signed Friday." (contract pasted)

**Produces:** A review flagging RED on one-way indemnity ("Customer shall indemnify Provider against any and all claims arising from use of the Services") with a mutual, capped redline; YELLOW on a 12-month auto-renewal with a 90-day opt-out window; GREEN on payment and confidentiality. Negotiation priority puts indemnity first with a fallback cap at 12 months' fees, and marks the opt-out window as trade material.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
