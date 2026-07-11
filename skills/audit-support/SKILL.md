---
name: audit-support
description: "Gets the books audit-ready: builds the PBC (prepared-by-client) list by area, drafts walkthrough narratives for key cycles (revenue, purchases, payroll), matches auditor samples to support, prepares tie-out schedules, tracks open items with owners and due dates, and drafts responses to findings. Use when the user says 'auditors start next month', 'build our PBC list', 'they sampled 25 invoices — check our support', or 'draft a response to this finding'."
---

# Audit Support — Auditor

> "Prep for audit."

## When to use

- An audit is scheduled — "fieldwork starts August 3, get us ready".
- The request list landed — "here's the auditor's PBC, organize and track it".
- Samples arrived — "they picked 25 invoices, do we have support for each?".
- Findings need answers — "draft management responses to these three findings".
- Balances must be provable — "build tie-outs for cash, AR, and fixed assets".

## Workflow

1. **Scope the audit.** Period, framework, first-year vs recurring, and the areas that matter — load the TB or statements with code and rank areas by balance and activity, never by guesswork.
2. **Build the PBC list by area** (cash, AR/revenue, inventory, fixed assets, AP/accruals, debt, equity, payroll, tax): each item gets description, owner, expected format, due date, status. Merge with the auditor's own list when one exists — their naming wins.
3. **Draft walkthrough narratives** for revenue, purchases, and payroll: trigger event → documents created → systems touched → approvals → how it hits the GL, with control points tagged inline (e.g., [C1: 2-way match]). One page per cycle, specific to this company — no boilerplate.
4. **Match samples to support.** For each sampled item, list required documents (invoice, PO/contract, delivery or acceptance evidence, payment proof), check what exists, and mark complete / partial (naming the gap) / absent. Find the gaps before the auditor does.
5. **Build tie-out schedules** per tested area: GL balance → subledger or supporting schedule → financial statement line, computed in code, with differences explained or proven zero.
6. **Run the open-items tracker:** item, area, requested by, owner, due date, status, blocker — sorted by due date, overdue flagged.
7. **Draft finding responses:** restate the finding neutrally, give root cause, management response, and remediation with a named owner and target date. Factual and specific — no defensiveness, no over-promising.
8. **Package.** Write `PBC-<period>.md` (or .xlsx), the walkthroughs, tie-outs, and tracker; refresh the tracker as items close.

## Output format

```
# Audit Readiness — <entity> — FY<year>

## PBC list
| # | Area | Item | Owner | Format | Due | Status |
|---|------|------|-------|--------|-----|--------|
| 1 | Cash | Bank statements + recs, all accounts, 12 months | <name> | PDF/XLSX | <date> | open |

## Walkthrough — <cycle>
<trigger> → <documents> → <systems> → <approvals> → <GL posting>
Controls: [C1] <control> — owner <name>; [C2] ...

## Sample support — <area>
| Sample | Required docs | Present | Status (complete/partial/absent) |
|--------|---------------|---------|----------------------------------|

## Tie-out — <area>
GL <balance> → subledger <balance> → statements <balance> | diff: 0.00 ✓ (or explained)

## Open items
| Item | Area | Owner | Due | Status | Blocker |
|------|------|-------|-----|--------|---------|

## Finding response — <ref>
Finding: <restated neutrally> | Root cause: <...>
Response: <...> | Remediation: <action> — <owner>, by <date>
```

## Quality bar

- [ ] Every PBC item carries owner, format, and due date — no orphan requests.
- [ ] Walkthroughs name this company's actual systems and control points, not boilerplate.
- [ ] Every sample marked complete / partial (gap named) / absent — gaps found before the auditor.
- [ ] Tie-outs computed from data and agree to both GL and statements, or the difference is explained.
- [ ] Tracker sorted by due date, every item owned, overdue flagged.
- [ ] Finding responses commit to named owners and dates — nothing vague.

## Example

**Invocation:** "Fieldwork starts Aug 3 — build the PBC and get cash and AR provable."
**Produced:** `PBC-FY2026.md` with 54 items across 9 areas, owners and due dates set to land by Jul 28; revenue, purchases, and payroll walkthroughs with tagged controls; cash and AR tie-outs proven to 0.00; a tracker with 6 open items, 2 overdue and flagged with blockers.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
