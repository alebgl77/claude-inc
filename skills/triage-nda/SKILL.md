---
name: triage-nda
description: "Ten-minute NDA triage — classifies an incoming NDA as GREEN (sign under standard delegation), YELLOW (targeted fixes, listed), or RED (full review). Screens mutuality, term and survival, definition breadth, embedded non-solicits or non-competes, missing standard carve-outs, residuals clauses, and IP assignment smuggling. Use when the user says 'can I sign this NDA', 'quick look at this NDA', or forwards any confidentiality agreement."
---

# Triage NDA — NDA Triage

> "Fast NDA review"

Built for speed: seven screens, one verdict, ten minutes. Works on pasted NDA text or a file.

## When to use

- "Can I just sign this NDA?" — the speed call
- "Sales needs this countersigned today" — deal-velocity triage
- "Is this NDA actually mutual?" — direction check
- Screening a batch of inbound NDAs before a partner event
- Confidentiality terms embedded in a larger agreement belong to `review-contract`, not here

## Workflow

1. Ingest the NDA (pasted text or file). Confirm it is a standalone NDA; note parties, stated purpose, and our disclosure direction (mostly disclosing, mostly receiving, or both).
2. Screen mutuality: obligations must run both ways if information does. One-way obligations against us while we disclose is RED territory.
3. Check term and survival: an agreement term of 1-3 years and confidentiality survival of 2-5 years are standard; indefinite survival passes only for trade secrets.
4. Check definition breadth: "Confidential Information" should be bounded — marked, or reasonably understood as confidential. Definitions sweeping in all business contacts or "any information disclosed by any means at any time" get flagged.
5. Hunt embedded landmines: non-solicit, non-compete, exclusivity, or standstill clauses do not belong in an NDA — any one of them forces RED.
6. Verify the four standard carve-outs: public knowledge, prior possession, independent development, compelled disclosure (with notice where lawful). Each missing carve-out is a YELLOW fix with insert language.
7. Screen residuals and IP: a residuals clause broad enough to gut confidentiality is RED; any assignment of IP, feedback, or derivatives smuggled into an NDA is RED.
8. Classify and deliver: GREEN — sign under standard delegation; YELLOW — apply the listed fixes, then sign; RED — route to full review with reasons quoted.

## Output format

```
NDA TRIAGE — <counterparty> — <date>
Direction: <mutual / we disclose / we receive>   Purpose: <one line>

VERDICT: <GREEN — sign under standard delegation | YELLOW — fix, then sign | RED — full review>

SCREENS
| Check                              | Result | Note              |
|------------------------------------|--------|-------------------|
| Mutuality                          | PASS   |                   |
| Term & survival                    | FLAG   | <what and why>    |
| Definition breadth                 | PASS   |                   |
| Embedded non-solicit / non-compete | PASS   |                   |
| Standard carve-outs (4)            | FLAG   | missing: <which>  |
| Residuals clause                   | PASS   | none present      |
| IP assignment smuggling            | PASS   | none present      |

FIXES (YELLOW verdicts)
1. <clause> — Quote: "<verbatim>" → Insert: "<replacement language>"
2. <clause> — Quote: "<verbatim>" → Insert: "<replacement language>"

RED REASONS (RED verdicts)
- <finding> — Quote: "<verbatim>" — why it forces full review

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] Verdict is exactly one of GREEN / YELLOW / RED — no hedging
- [ ] All seven screens run and shown, passes included
- [ ] Every FLAG quotes the offending text verbatim
- [ ] Every YELLOW fix ships insert language — a YELLOW without fixes is a RED
- [ ] Embedded non-solicit, non-compete, exclusivity, or standstill always forces RED
- [ ] Triage completes on the NDA text alone, no outside context required

## Example

**Invocation:** "BD forwarded this mutual NDA from Acme — okay to sign?" (NDA pasted)

**Produces:** Verdict YELLOW. Carve-outs missing independent development (insert provided); survival is seven years ("the obligations herein shall survive for seven (7) years") redlined to three; the other five screens pass. Two paste-ready fixes — sign under standard delegation once applied.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
