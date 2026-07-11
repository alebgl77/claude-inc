---
name: close-management
description: "Runs the month-end close: generates a day-by-day runbook from D-2 to D+5 as CLOSE-<month>.md with an owner matrix, dependency-ordered tasks (subledgers → accruals → reconciliations → flux → lock), numeric flux thresholds, a preparer/reviewer sign-off log, and close metrics such as days-to-close and reopened entries. Use when the user says 'set up our month-end close', 'kick off the June close', or 'our close takes two weeks — fix it'."
---

# Close Management — The Closer

> "Run the close."

## When to use

- A close is starting — "kick off the June close".
- No process exists — "we close by vibes, build us a real checklist".
- The close drags — "we lock on D+12, get us to D+5".
- Mid-close status — "where are we, what's blocking the lock?".
- Post-close review — "how did this close go vs last month?".

## Workflow

1. **Intake.** Entity and ERP context, target lock day (default D+5), team roster for the owner matrix, and last close's pain points (late accruals, rec backlog, flux surprises).
2. **Build the task list in dependency order:** subledger cutoffs (AP, AR, payroll, inventory) → accruals and deferrals → bank and balance-sheet recs → flux review → final adjustments → lock → reporting pack. Nothing schedules before its inputs exist.
3. **Assign day and people.** Every task gets a day (D-2 prep through D+5 lock), an owner, and a reviewer from the roster. Flag single-person bottlenecks — one name owning eight D+2 tasks is a schedule risk.
4. **Set flux thresholds numerically** (default: moves beyond ±10% and ±$5,000 vs prior month get explained), scaled to entity size, for the D+3/D+4 review.
5. **Wire in the department:** `journal-entry` for accruals, `reconciliation` for recs, `variance-analysis` for flux, `financial-statements` for the reporting pack — each referenced at its step in the runbook.
6. **Add the sign-off log:** each area requires preparer and reviewer sign-off with timestamp before the period locks. No sign-off, no lock.
7. **Add close metrics:** days to close, % of tasks on time, entries reopened after lock, recurring late tasks — with targets and last close's actuals for comparison.
8. **Generate `CLOSE-<month>.md`** from the template below. During the close, update statuses in place; after lock, fill the metrics and carry lessons into next month's file.

## Output format

```
# CLOSE-2026-06 — Month-End Close Runbook
Target lock: D+5 (2026-07-07) | Status: IN PROGRESS

## Owner matrix
| Area | Preparer | Reviewer |
|------|----------|----------|
| AP & accruals | <name> | <name> |
| Revenue & AR | <name> | <name> |
| Payroll | <name> | <name> |
| Cash & recs | <name> | <name> |

## D-2 — prep
- [ ] AP/AR cutoff communicated to teams — <owner>
- [ ] Recurring JE list refreshed — <owner>
## D+1 — subledgers
- [ ] AP, AR, payroll, inventory subledgers closed — <owner>
- [ ] Bank recs started (`reconciliation`) — <owner>
## D+2 — accruals & recs
- [ ] Accruals and deferrals posted (`journal-entry`) — <owner>
- [ ] Balance-sheet recs complete — <owner>
## D+3/D+4 — flux review
- [ ] Flux vs prior month, threshold ±10% / ±$5,000 (`variance-analysis`) — <owner>
- [ ] Adjustments from flux posted — <owner>
## D+5 — lock & report
- [ ] Sign-off log complete, period locked — <owner>
- [ ] Reporting pack issued (`financial-statements`) — <owner>

## Sign-off log
| Area | Preparer ✓ | Reviewer ✓ | Timestamp |
|------|-----------|-----------|-----------|
| <area> | | | |

## Close metrics
| Metric | Target | This close | Last close |
|--------|-------:|-----------:|-----------:|
| Days to close | 5 | | |
| Tasks on time | 95% | | |
| Reopened entries after lock | 0 | | |
```

## Quality bar

- [ ] Every task has a day, an owner, and a reviewer — zero unowned steps.
- [ ] Dependency order holds — no task scheduled before its inputs exist.
- [ ] Flux thresholds are numbers, not vibes.
- [ ] Sign-off log covers every area and gates the lock.
- [ ] Metrics carry targets plus last close's actuals when known.
- [ ] File generated as CLOSE-<month>.md and updated in place through the close.

## Example

**Invocation:** "Kick off the June close — 4-person team, target D+5."
**Produced:** `CLOSE-2026-06.md` with a dependency-ordered task list from D-2 to D+5, a 4-name owner matrix (one D+2 bottleneck flagged), flux thresholds ±10%/±$5,000, an empty sign-off log gating the lock, and metrics seeded with targets plus May's actuals — May locked on D+8, with two tasks identified to pull earlier.

*Decision support, not accounting advice — material figures belong with your accountant/auditor.*
