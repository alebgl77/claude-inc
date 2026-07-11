---
name: tax-prep
description: Organizes tax season — an organizer, not tax advice: a document checklist by category (income, expenses, assets, payroll, prior filings), an expense-category sweep that flags plausibly missed deductions in generic jurisdiction-agnostic categories, a quarterly-estimate calendar template, a clean handoff pack for the accountant, and an open-questions list. Use when the user says "tax season is coming", "what does my accountant need", "am I missing deductions", or pastes an expense ledger.
---

# Tax Prep — Tax Prepper

> "Prep your taxes."

This skill is the organizer, not the adviser: it collects, categorizes, and flags, so the accountant's expensive hours go to judgment instead of shoebox archaeology.

## When to use

- "Tax season is coming and my records are a mess."
- "What does my accountant actually need from me?"
- "Am I missing deductions?" — the sweep hunts categories with suspicious zeros.
- "Set up my quarterly estimate reminders."
- Any time an expense ledger or bank export needs to become an accountant-ready pack.

## Workflow

1. **Frame the job.** Organizer, not adviser: nothing here decides what is deductible — it surfaces candidates and questions for a professional to rule on.
2. **Build the document checklist** across five categories — income, expenses, assets, payroll, prior filings — and mark each item have / missing / n-a from what the user provides.
3. **Sweep the expense ledger with code.** From pasted data or CSV, categorize every transaction into generic buckets: software and subscriptions, professional fees, insurance, rent and utilities, vehicle and mileage, equipment (depreciation candidates), travel and meals, training, bank and payment fees, bad debt, home office. Flag uncategorized and personal-looking rows instead of guessing.
4. **Hunt the zeros.** Compare the buckets against how the business plainly operates: client-site visits all year but no mileage logged, a home-based business with no home-office entries, laptops bought but nothing tagged as equipment. Each suspicious zero becomes a flagged candidate — never a claim.
5. **Lay out the quarterly-estimate calendar.** A four-slot template with the user's local due dates left to fill in, plus a monthly set-aside habit: a fixed percentage of net moved to a tax sub-account.
6. **Assemble the accountant handoff pack.** File manifest with paths, summary totals (revenue, expenses by bucket, payroll, estimates already paid), the checklist, and the sweep.
7. **Write the open-questions list.** Everything ambiguous, one line each, phrased as questions the accountant can answer in a single pass.

## Output format

```
TAX PREP PACK — <business> — tax year <year>

DOCUMENT CHECKLIST                                  [have / missing / n-a]
Income:   sales reports, invoices issued, platform payout statements, interest
Expenses: ledger or bank + card exports, receipts over <threshold>, loan statements
Assets:   purchases over <threshold> (date, cost, use), disposals, vehicle/mileage log
Payroll:  payroll register, filings made, contractor payments and their forms
Prior:    last year's return, carryforwards, estimated payments made this year

EXPENSE SWEEP (computed from ledger)
Bucket                 | Entries | Total | Flag
Software/subscriptions | 41      | 3,880 | ok
Vehicle/mileage        | 0       | 0     | ZERO — site visits all year, nothing logged
Uncategorized          | 17      | 2,310 | needs owner review (rows listed below)

POSSIBLY MISSED (candidates, not claims)
- <bucket> — why it's plausible here — the document that would support it

QUARTERLY ESTIMATE CALENDAR (fill in local dates)
Q1 due <date> | Q2 due <date> | Q3 due <date> | Q4 due <date>
Set-aside habit: move <x>% of net income to the tax sub-account monthly.

ACCOUNTANT HANDOFF
Files: <manifest with paths>
Totals: revenue <amt> | expenses <amt> | payroll <amt> | estimates paid <amt>

OPEN QUESTIONS FOR THE ACCOUNTANT
1. <question — specific transaction, date, amount>
2. <question>
```

## Quality bar

- [ ] Sweep computed with code over every row — nothing categorized by skimming.
- [ ] Zero tax advice: candidates and questions only; decisions left to the professional.
- [ ] Buckets stay generic and jurisdiction-agnostic — no form numbers, no rate claims.
- [ ] Every "possibly missed" item names the supporting document to go find.
- [ ] Uncategorized and personal-looking transactions listed, never silently dropped.
- [ ] Handoff pack openable by an accountant with zero follow-up about file locations.

## Example

**Invocation:** "A year of bank transactions attached — get me ready for my accountant meeting Friday."

**Produced:** `tax/tax-prep-pack-2026.md`: a checklist showing three missing items (Q2 estimate receipt, contractor forms, mileage log), a sweep of 1,340 transactions into 11 buckets, four flagged zeros including an unlogged home office, a filled calendar template, totals for the accountant, and nine open questions — the Friday meeting runs off one document.

*Rules vary by jurisdiction — confirm with a local professional before filing or paying.*
