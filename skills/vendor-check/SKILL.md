---
name: vendor-check
description: "Vendor agreement status check — inventories what exists versus what is needed (MSA, DPA, SOW, SLA, insurance certs, security review), builds a gap analysis table, runs an expiration and renewal radar with dates and notice windows, notes surviving obligations, and delivers an onboarding go/no-go checklist. Use when the user says 'are we set up with this vendor', 'what do we have signed with them', 'can we onboard them', or ahead of a renewal or offboarding."
---

# Vendor Check — Vendor Vetter

> "Vet a vendor"

Answers one question fast: can we safely start (or keep) working with this vendor, and what paper is missing? Works from provided documents, pasted excerpts, or the user's answers.

## When to use

- "Do we have paper with Acme?" — inventory before new spend
- "Can we onboard this vendor by Monday?" — the go/no-go call
- "What renews with them this quarter?" — expiration radar
- "We're dropping this vendor — what survives termination?" — offboarding read
- A found agreement with ugly clauses goes deeper via `review-contract`

## Workflow

1. Profile the engagement: what the vendor does, what data or systems they touch, annual spend, business criticality, jurisdictions.
2. Derive the "needed" list from that profile: MSA always; DPA whenever personal data flows; SOW per work package; SLA when availability matters; insurance certificates (types and minimums) proportional to risk; security review when they touch systems or data.
3. Inventory what exists from attached files, pasted excerpts, and the user's answers: document, status (signed / draft / expired / missing), signature date, term.
4. Build the gap analysis table: needed vs. exists vs. verdict — OK / EXPIRING / EXPIRED / MISSING / WRONG-SCOPE (e.g., an SOW hanging off a terminated MSA).
5. Run the renewal radar: every date that matters — expirations, auto-renewal deadlines with their notice windows, insurance cert renewals — sorted soonest first, with days remaining from today.
6. Note surviving obligations: whatever outlives termination or expiry (confidentiality, data return and deletion, audit rights, indemnities), each citing its source document and clause.
7. Deliver the onboarding go/no-go checklist: blockers that must exist before access or PO, follow-ups allowed within 30 days, one owner per item, one verdict.

## Output format

```
VENDOR CHECK — <vendor> — <date>
Engagement: <what they do>   Touches: <data / systems>   Criticality: <H / M / L>

INVENTORY vs. NEEDED
| Document        | Needed? | Exists?       | Date / term     | Verdict |
|-----------------|---------|---------------|-----------------|---------|
| MSA             | YES     | signed <date> | <term, renewal> | OK      |
| DPA             | YES     | missing       | —               | MISSING |
| SOW             | YES     | draft         | —               | GAP     |
| SLA             | <Y/N>   | <status>      | <dates>         | <...>   |
| Insurance certs | <Y/N>   | <status>      | <expiry>        | <...>   |
| Security review | <Y/N>   | <status>      | <date>          | <...>   |

RENEWAL / EXPIRATION RADAR (soonest first)
| Date   | Event             | Notice window   | Days out | Action        |
|--------|-------------------|-----------------|----------|---------------|
| <date> | <MSA auto-renews> | <60 days prior> | <n>      | <decide by …> |

SURVIVING OBLIGATIONS
- <obligation> — source: <doc §n> — runs until <when>

ONBOARDING GO/NO-GO
[ ] BLOCKER: <must exist before access or PO> — owner: <who>
[ ] FOLLOW-UP: <within 30 days> — owner: <who>
VERDICT: <GO / GO WITH CONDITIONS / NO-GO> — <one line>

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] "Needed" list derived from the engagement profile, not a fixed template
- [ ] Every inventory row carries a verdict — no blank cells
- [ ] Radar shows the notice window and days remaining, not just the expiry date
- [ ] Surviving obligations cite their source document and clause
- [ ] Go/no-go separates blockers from follow-ups, each with an owner
- [ ] Unknowns surfaced as questions to the user, never guessed into the table

## Example

**Invocation:** "Marketing starts with a new email vendor Monday — where do we stand?" (signed MSA attached, nothing else)

**Produces:** Inventory showing the MSA OK but the DPA MISSING despite subscriber data flowing, SOW still in draft, no security review on file. Radar flags the MSA auto-renewal's 60-day notice window opening in three weeks. Verdict: NO-GO until the DPA is signed and the security questionnaire returned — both owned and dated on the checklist.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
