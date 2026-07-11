---
name: cash-flow-snapshot
description: Builds a 13-week rolling cash forecast from a bank export, receivables, and payables: opening balance, weekly inflows tagged committed/likely/hopeful, fixed and variable outflows, a lowest-point alert, and runway in weeks — plus three levers (collect faster, cut, delay) whenever runway falls under 8 weeks. Use when the user asks "how much cash do we have", "how many weeks can we last", "will we make payroll next month", or drops a bank CSV and wants to know what's coming.
---

# Cash Flow Snapshot — Cash Watcher

> "Snapshot your cash."

Thirteen weeks is the horizon a small business actually lives in: long enough to see trouble coming, short enough that the numbers stay honest.

## When to use

- "How much cash do we actually have, and how long does it last?"
- "Will we make payroll on the 15th?" — any survival question pinned to a date.
- "Here's our bank export and open invoices — what's coming?"
- Before any decision that moves real money: a hire, a bulk order, new equipment, a lease.
- On a schedule: monthly when healthy, weekly when tight.

## Workflow

1. **Collect inputs.** Take pasted data or files: current balance of every cash account, open receivables (client, amount, due date), open payables (vendor, amount, due date), and recurring items (payroll, rent, loans, subscriptions). A raw bank CSV works — derive the recurring pattern from 3+ months of history.
2. **Set the opening balance.** Sum all cash accounts as of today and state the as-of date explicitly. This is the anchor every other number hangs from.
3. **Tier the inflows.** Committed = invoiced with a due date or contractually scheduled. Likely = recurring history or a firm verbal agreement. Hopeful = pipeline and wishes. Never blend the tiers.
4. **Map the outflows.** Fixed (payroll, rent, loan payments, subscriptions) on their real calendar dates; variable (materials, shipping, ads) estimated from the trailing 8–12 weeks of actuals.
5. **Compute the 13-week ladder with code.** Week by week: opening + inflows − outflows = closing. Run three scenarios: committed-only, committed+likely, all-in. No mental math on real money.
6. **Find the low point.** The minimum closing balance in the committed-only scenario, with its week and dates. That number — not the average — is the headline.
7. **Measure runway.** Weeks until the committed-only closing crosses zero; report "13+" if it never does. Give the committed+likely runway for context.
8. **If runway < 8 weeks, pull three levers.** Quantify each in weeks of runway bought:
   - Collect faster: name the invoices to chase today; propose deposits on new work.
   - Cut: the largest discretionary variable cost that dies without killing revenue.
   - Delay: which payable, and the exact ask to the vendor (split, +30 days, pause).
9. **Deliver the snapshot** in the format below and date the next refresh — weekly if runway < 8, monthly otherwise.

## Output format

Save as `cash/snapshot-<YYYY-MM-DD>.md` so refreshes diff cleanly.

```
CASH FLOW SNAPSHOT — <business> — as of <date>
Opening balance: <amount> across <n> account(s)

13-WEEK LADDER (<currency>; closing shown for committed-only)
Wk | Start  | In: committed | In: likely | In: hopeful | Out: fixed | Out: variable | Close
01 | 42,300 | 18,000        | 6,500      | 0           | 21,400     | 4,100         | 34,800
02 | 34,800 | 9,200         | 4,000      | 2,500       | 12,700     | 3,800         | 27,500
...
13 | ...    | ...           | ...        | ...         | ...        | ...           | ...

LOW POINT: <amount> in week <n> (<dates>) — ALERT if below one payroll cycle
RUNWAY: <n> wks committed-only | <n> wks committed+likely | <n> wks all-in

LEVERS (mandatory when runway < 8 weeks)
1. Collect faster: <named invoices / deposit terms> → +<n> weeks
2. Cut: <named expense> → +<n> weeks
3. Delay: <named payable, the exact ask> → +<n> weeks

Next refresh: <date>
```

## Quality bar

- [ ] Every figure traces to a source row (bank line, invoice, bill) — zero vibes.
- [ ] Ladder computed with code from the raw inputs, reproducible on refresh.
- [ ] Confidence tiers never blended; the headline runway is committed-only.
- [ ] Low point cross-checked against the next two payroll dates and any tax due date.
- [ ] Levers name a specific invoice, expense, or vendor — each quantified in weeks bought.
- [ ] As-of date and next refresh date printed on the snapshot.

## Example

**Invocation:** "Bank CSV and open invoices attached — do we survive the summer?"

**Produced:** `cash/snapshot-2026-07-11.md`: opening balance 41,700; low point 9,400 in week 6, two weeks before August payroll; runway 7 weeks committed-only. Levers: chase the two invoices over 5,000 (+2.1 weeks), pause the trade-show booth (+1.4 weeks), move the annual insurance premium to monthly (+0.9 weeks). Refresh booked for Monday.
