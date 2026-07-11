---
name: financial-statements
description: "Builds a full statement set — P&L, balance sheet, and indirect cash flow — from a trial balance or transaction export, mapping accounts to a standard chart and proving every tie-out in code. Use when the user says 'build a P&L from this trial balance', 'turn this export into financials', 'I need a balance sheet for the board', or 'my statements don't tie'. Works on pasted data or CSV/XLSX files."
---

# Financial Statements — Statement Builder

> "Build the statements."

## When to use

- A trial balance needs to become statements — "build a P&L and balance sheet from this TB".
- A raw transaction export needs rolling up — "here's the ledger dump, make me financials".
- Statements exist but fail internal checks — "my balance sheet is off by 3,412 — find it".
- Someone external asked for financials — "the investor wants Q2 statements by Friday".
- You need a statement-level base before deeper work — flux commentary, audit prep, a close pack.

## Workflow

1. **Ingest with code.** Load the pasted table or CSV/XLSX (pandas or equivalent — never mental math on long columns). Standardize columns, normalize debit/credit signs, and confirm the trial balance foots: total debits = total credits. If it does not, stop and report the gap before building anything on top.
2. **Map to a standard chart.** Classify every account — Assets, Liabilities, Equity, Revenue, COGS, Operating expenses, Other income/expense, Tax — with current vs non-current splits for balance sheet lines. Every judgment mapping is recorded as an assumption.
3. **Build the P&L.** Revenue → COGS → gross profit → opex by category → operating income → other items → tax → net income, with subtotals and margins as % of revenue.
4. **Build the balance sheet.** Current and non-current sections; roll period net income into retained earnings; present total assets against total liabilities + equity.
5. **Build the cash flow (indirect).** Start at net income; add back non-cash items (depreciation, amortization, write-offs); adjust for working-capital deltas (AR, inventory, prepaids, AP, accruals); then investing and financing; land on net change in cash.
6. **Run tie-outs in code, not by eye:** (a) balance sheet balances; (b) P&L net income equals net income in the equity roll-forward; (c) cash flow ending cash equals balance sheet cash; (d) every statement subtotal re-foots from the mapped trial balance.
7. **Scan for anomalies.** Contra-normal balances (credit AR, debit revenue), hard swings vs prior period when one is provided, suspicious round numbers, unmapped orphans. Each gets a note and a suggested action.
8. **Deliver.** Fill the output template; when the user wants artifacts, write `statements-<period>.md` and/or `statements-<period>.xlsx` alongside the source data.

## Output format

```
# Financial Statements — <Entity> — <Period>

## Income statement
| Line | Amount | % of revenue |
|------|-------:|-------------:|
| Revenue | | |
| COGS | | |
| **Gross profit** | | |
| Operating expenses (by category) | | |
| **Operating income** | | |
| Other income/(expense) | | |
| Tax | | |
| **Net income** | | |

## Balance sheet
| Line | Amount |
|------|-------:|
| Current assets | |
| Non-current assets | |
| **Total assets** | <A> |
| Current liabilities | |
| Non-current liabilities | |
| Equity (incl. period NI <N>) | |
| **Total liabilities + equity** | <A> |

## Cash flow (indirect)
Operating: NI <N> + non-cash <> + working capital Δ <> = <>
Investing: <> | Financing: <>
Net change in cash <Δ> → Ending cash <C>

## Tie-out checks
- TB foots: Dr <D> = Cr <D> — PASS/FAIL
- Balance sheet balances — PASS/FAIL
- NI → retained earnings — PASS/FAIL
- Ending cash ties across statements — PASS/FAIL

## Mapping & assumptions
- <account> → <category> — <why>

## Anomalies
- <item>: <what looks off> → <suggested action>
```

## Quality bar

- [ ] Every computation runs in code on the actual data; every subtotal re-foots.
- [ ] All four tie-out checks executed with PASS/FAIL shown — no silent passes.
- [ ] Every account mapped; every judgment mapping listed under assumptions.
- [ ] One sign convention, stated once, applied everywhere.
- [ ] Anomalies surfaced with suggested actions, never absorbed into totals.
- [ ] Cash flow reconciles to the actual change in cash — no plug.

## Example

**Invocation:** "Here's `tb-2026-06.xlsx` — build June financials."
**Produced:** June P&L, balance sheet, and indirect cash flow with all four tie-outs passing; a 42-account mapping table with 3 judgment calls listed as assumptions; one anomaly — a credit balance in AR flagged as a likely unapplied customer payment, with a proposed reclass entry.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
