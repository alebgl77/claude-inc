---
name: invoice-chase
description: Runs collections on late invoices: builds an aging ladder (current/30/60/90+), assigns each invoice a rung on an escalation sequence with ready-to-send emails — friendly nudge, firm reminder with late-fee mention, final notice — plus a phone script, tone rules that preserve the relationship, a chase log, and when-to-write-off guidance. Use when the user says "clients haven't paid", "this invoice is 45 days overdue", "write a payment reminder", or pastes an invoice list or AR aging.
---

# Invoice Chase — Debt Chaser

> "Chase late invoices."

Unpaid invoices are interest-free loans you never agreed to make. This skill gets the money in while keeping the client.

## When to use

- "Three clients haven't paid since March — get the money in."
- "This invoice is 45 days overdue, what do I send?" — any single stubborn invoice.
- "Here's my invoice export / AR aging — who do I chase first?"
- Receivables creeping past 30 days while the owner "doesn't want to be annoying."
- Standing up a weekly collections routine so lateness stops compounding.

## Workflow

1. **Build the aging ladder.** From pasted data or CSV (client, invoice #, amount, issue date, due date, last contact), compute days overdue with code and bucket: current, 1–30, 31–60, 61–90, 90+.
2. **Prioritize.** Rank by amount × age. Most of the money usually sits in three invoices — name them as this week's targets.
3. **Assign each invoice a rung** based on days overdue and chase history. Never skip a rung the client hasn't actually received; pressure without a paper trail reads as hostility.
4. **Draft the emails from the templates below,** personalized: their name, the exact amount, the real due date, and one specific detail proving a human wrote it.
5. **Apply the tone rules.**
   - Assume incompetence before malice — rung 1 always presumes an oversight.
   - Escalate consequences, never insults. The facts get harder; the manners don't change.
   - The money and the relationship are separate threads: chase firmly, stay warm.
   - Every message offers one easy exit: confirm a date, pay a part, or flag a dispute.
6. **Open the chase log.** Every action and response gets a row — it is both memory and, if things ever go legal, evidence.
7. **Set the cadence.** Rungs 7 days apart from the first overdue day; phone at 60+ days or after a silent final notice. Diarize the next action before closing the session.
8. **Know when to fold.** Recommend write-off when chasing costs more than the balance: client dark after final notice plus a call, a dispute with no resolution path, or an amount worth less than the hours to collect it. Pair every write-off with stop-work and prepayment terms going forward.

## Output format

```
INVOICE CHASE PACK — <business> — <date>

AGING LADDER
Bucket  | Count | Total | % of AR
Current |  ...  |  ...  |  ...
1–30    |  ...  |  ...  |  ...
31–60   |  ...  |  ...  |  ...
61–90   |  ...  |  ...  |  ...
90+     |  ...  |  ...  |  ...

TOP TARGETS (amount × age)
1. <client> — inv <#> — <amount> — <days> days — rung <n> — next: <action> on <date>
2. ...
3. ...

RUNG 1 — FRIENDLY NUDGE (1–14 days late)
Subject: Quick check — invoice <#>
Hi <name> — a quick nudge on invoice <#> (<amount>), due <date>. I suspect it
slipped through the cracks. Could you confirm it's scheduled? Happy to resend
the PDF or fix any detail on our side. Thanks!

RUNG 2 — FIRM REMINDER (15–44 days late)
Subject: Invoice <#> — now <n> days past due
Hi <name> — invoice <#> (<amount>) is now <n> days past due and I haven't heard
back on my last note. Could you confirm payment by <date>? Per our terms,
balances over 30 days accrue a <x>% late fee, which I'd much rather not apply.
If something is blocking payment, tell me and we'll sort it together.

RUNG 3 — FINAL NOTICE (45+ days late)
Subject: Final notice — invoice <#>
Hi <name> — despite two reminders, invoice <#> (<amount>, due <date>) remains
unpaid. If payment doesn't arrive by <date+7>, we'll pause current work and
refer the balance for collection — an outcome neither of us wants. Call me
today at <phone> and we can resolve this in ten minutes.

RUNG 4 — PHONE SCRIPT (60+ days, or silence after final notice)
Open: "I'm calling about invoice <#> — I'd like to fix this today. What's going on?"
If they promise → pin an exact date; confirm it by email within the hour.
If they dispute → isolate the disputed line; get the undisputed rest paid now.
If no answer → voicemail: amount, deadline, callback number. Log the attempt.

CHASE LOG
Date | Invoice | Client | Rung | Action | Response | Next step | Due

WRITE-OFF WATCHLIST
<invoice> — <amount> — <reason> — recommended: <write off / collections / stop-work>
```

## Quality bar

- [ ] Days overdue computed with code from actual dates — never estimated.
- [ ] Every email states the invoice number, exact amount, and original due date.
- [ ] Escalation follows the ladder; no client jumps a rung they never received.
- [ ] Late fee mentioned only if it exists in the terms the client actually signed.
- [ ] Chase log row written for every action, with the next step diarized.
- [ ] Write-off calls compare the balance against the realistic cost to collect it.

## Example

**Invocation:** "Invoice export attached — 11 open, some ancient. Who do I chase and what do I send?"

**Produced:** An aging ladder showing 62% of AR sitting in three invoices; rung assignments for all 11; personalized rung-2 and rung-3 emails for the top three (18,400 total); a phone script for the client silent since April; a chase log with next actions dated; and one 240 write-off recommendation, paired with prepayment terms for that client going forward.
