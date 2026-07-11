---
name: reconciliation
description: "Matches two datasets — bank vs ledger, subledger vs GL — via exact matching, fuzzy matching (amount tolerance, date window, reference similarity), and split detection; buckets exceptions (timing, missing, duplicate, amount mismatch), ages unmatched items, proposes adjusting entries, and proves the bridge between the two balances. Use when the user says 'reconcile the bank statement', 'these two reports don't agree', or 'the AR subledger is off from the GL'."
---

# Reconciliation — Reconciler

> "Reconcile the books."

## When to use

- Bank vs ledger — "reconcile June's bank statement against GL cash".
- Subledger vs GL — "the AR subledger says 412k, the GL says 405k — why?".
- Processor vs books — "match Stripe payouts to booked revenue".
- Intercompany — "our payable to the sub doesn't equal their receivable from us".
- Any two lists that should agree and don't.

## Workflow

1. **Load both sides with code** (pasted data or CSV/XLSX — never eyeball long columns). Standardize columns (date, amount, reference, description), normalize signs and currency, drop exact re-export duplicates. Record each side's row count and total — these anchor the bridge.
2. **Exact pass.** Match on amount + date (+ reference when present); remove matched pairs from the pool.
3. **Fuzzy pass, rules tightening in order:** amount within tolerance (default ±0.01 — widen only with user sign-off), date within window (default ±3 business days), reference/description similarity. Log every fuzzy match with the rule that made it.
4. **One-to-many pass.** Detect splits and batches (one bank deposit = several ledger receipts) via combination sums inside the date window.
5. **Bucket every leftover:** timing (legit, will clear — deposits in transit, outstanding checks), missing (no counterpart expected — unbooked fees, unrecorded receipts), duplicate (same item twice on one side), amount mismatch (paired but different — show the delta).
6. **Age the unmatched** by days outstanding: 0–7, 8–30, 31–60, 60+. Anything over 30 days gets a priority flag.
7. **Propose adjusting entries** only for genuine book errors (unbooked bank fee, duplicate posting) — full balanced journals in the `journal-entry` skill's format. Timing items never get forced adjustments.
8. **Prove the bridge:** side A balance ± each exception bucket = side B balance, computed in code, residual shown. Target 0.00; anything else is stated, never hidden.

## Output format

```
# Reconciliation — <A> vs <B> — <period>

## Bridge
<A> balance                     <amount>
  + timing: <description>       <amount>
  − missing on <side>: <desc>   <amount>
  ± mismatches (net)            <amount>
= <B> balance                   <amount>
Residual: 0.00 ✓  (or: <amount> — UNRESOLVED, see exceptions)

## Match summary
Exact: <n> | Fuzzy: <n> (rules logged) | One-to-many: <n> | Unmatched: <n>

## Exceptions
| # | Side | Date | Amount | Ref | Bucket | Age (days) | Action |
|---|------|------|-------:|-----|--------|-----------:|--------|
| 1 | Bank | <date> | <amt> | <ref> | missing | <n> | book JE-R1 |

## Proposed adjusting entries
JE-R1 — <memo> — Dr <account> <amt> / Cr <account> <amt> (support: <ref>)

## Aging of unmatched
0–7: <n> / <amt> | 8–30: <n> / <amt> | 31–60: <n> / <amt> | 60+: <n> / <amt>
```

## Quality bar

- [ ] Bridge computed in code and proves out; any residual stated explicitly, never hidden.
- [ ] Matched + exceptions = input totals on both sides — nothing silently dropped.
- [ ] Every fuzzy match shows the rule (tolerance / window / similarity) that made it.
- [ ] Every unmatched item bucketed and aged — no "miscellaneous" pile.
- [ ] Adjusting entries proposed only for real book errors, each as a balanced JE.
- [ ] Tolerances and windows stated up front as assumptions.

## Example

**Invocation:** "Reconcile `bank-jun.csv` against `gl-cash-jun.xlsx`."
**Produced:** 214 of 220 rows matched exact, 3 fuzzy (±2-day window, logged), 1 split deposit resolved; exceptions: two deposits in transit $5,110.00 (timing) and one $45.00 unbooked bank fee (missing → JE-R1); bridge: bank $88,214.16 + 5,110.00 = $93,324.16 = GL $93,369.16 − 45.00, residual 0.00.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
