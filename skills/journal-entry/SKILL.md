---
name: journal-entry
description: "Drafts correct double-entry journal entries from described business events, with templates for accruals, deferrals, depreciation, payroll, prepaids, and corrections. Every entry carries a date, memo, and support reference; reversals are drafted where due; a running debits-equal-credits check covers each entry and the batch. Use when the user says 'what is the journal entry for this', 'book this accrual', 'record June payroll', or 'fix this posting error'."
---

# Journal Entry — Journal Keeper

> "Post journal entries."

## When to use

- A business event needs booking — "what's the JE for the $18k legal invoice covering June?".
- Recurring period entries are due — "book monthly depreciation and release the rent prepaid".
- Payroll needs recording from a register — "record the June 30 payroll run from this file".
- A posting was wrong — "we hit expense instead of prepaid, fix it".
- Next period's open needs reversing entries set up in advance.

## Workflow

1. **Parse the event.** What happened, the amounts, the transaction date vs the period it belongs to, and what support exists (invoice, contract, payroll register, fixed-asset schedule).
2. **Identify accounts and direction.** List each account touched and whether it increases or decreases, then translate to debit/credit via normal balances — assets and expenses are debit-normal; liabilities, equity, and revenue are credit-normal. Never guess signs.
3. **Apply the matching template** when one fits:
   - Accrual: Dr Expense / Cr Accrued liabilities — reverses next period
   - Deferral: Dr Cash / Cr Deferred revenue — released as earned
   - Depreciation: Dr Depreciation expense / Cr Accumulated depreciation
   - Payroll: Dr Gross wages + employer taxes / Cr Withholdings payable, Taxes payable, Cash (net)
   - Prepaid release: Dr Expense / Cr Prepaid asset
   - Correction: reverse the wrong entry in full, then post the correct one — never net the difference
4. **Compute derived amounts with code** — prorations, straight-line depreciation, payroll splits from a CSV/XLSX register. No mental math over long columns.
5. **Draft each entry** with post date, account lines, debits, credits, a memo that explains why (not just what), and a support reference.
6. **Handle reversals.** Tag every entry that should auto-reverse (most accruals) and draft the reversing entry dated the first day of the next period.
7. **Run the balance check in code:** debits = credits per entry and across the whole batch, printed explicitly.
8. **Flag review items** — estimates, unusual accounts, anything material enough to deserve a second pair of eyes, each with its basis stated.

## Output format

```
# Journal Batch — prepared <date>

## JE-001 — <post date> — <memo>
Support: <reference>
| Account | Dr | Cr |
|---|---:|---:|
| <account debited> | <amt> | |
| <account credited> | | <amt> |
Check: Dr <X> = Cr <X> ✓ | Reverses: <date> / no

## JE-002 — ...

## Batch check
Total Dr <T> = Total Cr <T> ✓ across <n> entries

## Review items
- <entry>: <estimate or judgment and its basis>  (or: none)
```

## Quality bar

- [ ] Each entry balances and the batch balances — both computed in code and shown.
- [ ] Debit/credit direction verified against normal balances, not guessed.
- [ ] Every entry has a date, a why-memo, and a support reference — no bare postings.
- [ ] Corrections reverse the original in full; no netted shortcuts.
- [ ] Reversing entries drafted and dated wherever the template requires them.
- [ ] Estimates flagged with their basis for reviewer sign-off.

## Example

**Invocation:** "We got an $18,000 legal invoice on Jul 3 for work done in June — book it properly."
**Produced:** JE-001 accruing $18,000 into June (Dr Legal expense / Cr Accrued liabilities, memo citing the invoice), JE-002 reversing it on Jul 1, batch check Total Dr 36,000 = Total Cr 36,000 across 2 entries, no review items.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
