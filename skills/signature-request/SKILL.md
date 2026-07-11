---
name: signature-request
description: "Pre-signature gate and routing plan for a finalized document — verifies exact legal entity names, signatory authority, attached exhibits, filled blanks, consistent dates, and counterparty details, then sets the signing order (sequential vs. parallel, with reasons), writes envelope instructions for any e-sign tool, and creates post-signature filing and obligations-calendar entries. Use when the user says 'send this for signature', 'get this signed', or 'set up the envelope'."
---

# Signature Request — Signature Wrangler

> "Route for signature"

The last gate before ink: nothing routes until the document proves it is actually ready to sign. Works on the final document plus deal facts from the user.

## When to use

- "Contract's final — get it signed" — execution time
- "Set up the envelope for the MSA and SOW" — multi-document routing
- "Who signs first, us or them?" — signing-order call
- "It's signed — now what?" — filing and obligations follow-through
- Terms still moving? Back to `review-contract` — nothing unfinalized enters this gate

## Workflow

1. Confirm the document is final: no tracked changes, no open comments, version confirmed by the deal owner. Not final → stop and say exactly what is still open.
2. Run the pre-signature checklist: legal entity names exact (registry names, not brand names); signatory authority on both sides (name, title, basis); every exhibit and schedule attached and cross-referenced correctly; every blank filled — dates, amounts, addresses, notice emails; dates consistent (effective vs. signature vs. term start); counterparty details verified (entity number, registered address, signer identity).
3. Fix or flag: mechanical defects (an empty notice address) get filled from known facts or asked; anything substantive reopens review — the gate never "signs around" a defect.
4. Set the signing order: sequential when one signature depends on another (counterparty signs first so we execute last and control the effective date); parallel when signatures are independent and speed wins. Always state the why.
5. Write envelope instructions portable to any e-sign tool: recipients (name, email, role, order), fields per signer (signature, date, title), CC-on-completion list, reminder cadence, expiration, and the message subject and body.
6. Plan post-signature filing: where the executed copy lives, who receives copies, and the file-naming convention.
7. Create obligations-calendar entries: renewal and opt-out deadlines, payment milestones, deliverables, notice windows — each with a date, an owner, and an alert lead time.
8. Deliver the packet. Nothing is actually sent without explicit human confirmation.

## Output format

```
SIGNATURE PACKET — <document> — <date>

PRE-SIGNATURE GATE
[ ] Entity names exact       <ours> / <theirs>                 — PASS/FAIL
[ ] Signatory authority      <name, title> / <name, title>     — PASS/FAIL
[ ] Exhibits attached        <list, cross-refs checked>        — PASS/FAIL
[ ] Blanks filled            <remaining: 0>                    — PASS/FAIL
[ ] Dates consistent         <effective vs. signing vs. term>  — PASS/FAIL
[ ] Counterparty verified    <entity no., address, signer>     — PASS/FAIL
GATE RESULT: <CLEAR TO ROUTE / BLOCKED — list the FAILs>

SIGNING ORDER: <sequential / parallel> — <why>
1. <name, title, entity> — <reason they sign first>
2. <name, title, entity>

ENVELOPE INSTRUCTIONS (portable to any e-sign tool)
- Recipients: <name — email — role — order>
- Fields per signer: <signature, date, title>
- CC on completion: <who>
- Reminders: <cadence>   Expires: <date>
- Message: "<subject> / <one-line body>"

POST-SIGNATURE
- File executed copy: <location> as <naming convention>
- Distribute to: <who>
- Obligations calendar:
  | Date   | Obligation                     | Owner | Alert lead |
  |--------|--------------------------------|-------|------------|
  | <date> | <renewal notice window opens>  | <who> | <30 days>  |

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
```

## Quality bar

- [ ] Gate runs on the actual final document, not a description of it
- [ ] Every gate item marked PASS or FAIL — any FAIL blocks routing
- [ ] Entity names checked against registered legal names, not brand names
- [ ] Signing order comes with a stated reason, not a default
- [ ] Envelope instructions executable in any e-sign tool without follow-up questions
- [ ] Every future obligation lands on the calendar with an owner and an alert

## Example

**Invocation:** "The Acme MSA is final — route it. Their CFO signs, then our CEO."

**Produces:** Gate result BLOCKED on one item — Exhibit B is referenced in §4.2 but not attached — all else PASS. Once cleared: sequential order (Acme CFO first; our CEO last to control the effective date), full envelope instructions with 3-day reminders, filing to the contracts archive as `2026-07-acme-msa-executed.pdf`, and three calendar entries including the 60-day renewal notice window with a 30-day alert.

*Issue-spotting support, not legal advice — engage counsel for binding decisions.*
