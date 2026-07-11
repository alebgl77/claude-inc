---
name: plan-payroll
description: Plans payroll cash: true loaded cost per hire (gross plus employer taxes, benefits, tools), a payroll calendar with cutoffs and cash-out dates, a scenario table for new hire vs raise vs contractor-vs-employee, and a payroll-to-revenue check against rough industry bands. Use when the user asks "can I afford to hire", "what does an employee really cost me", "raise or contractor", or wants payroll dates mapped against cash. Organizes the numbers; a local professional confirms the rules.
---

# Plan Payroll — Payroll Planner

> "Plan payroll."

Payroll is the one bill a small business can never pay late. This skill makes its true size and timing visible before commitments get made.

## When to use

- "Can I afford to hire someone in September?" — before the offer goes out, not after.
- "What does a 4,000/month employee actually cost me?"
- "Should this be a contractor or an employee?" — the cost half; a professional confirms classification.
- "Map the next quarter's payroll dates against my cash."
- Payroll creeping up while revenue isn't — ratio check time.

## Workflow

1. **Gather inputs.** Pasted or CSV: payroll register (role, gross, frequency), pay schedule, trailing revenue by month, and the decision on the table (hire, raise, contractor). Ask for local employer-cost rates if the user has them.
2. **Compute loaded cost per person with code.** Gross + employer taxes/contributions + benefits + tools and seat costs. If local rates are unknown, apply a stated planning multiplier (1.25–1.40 × gross is a common band) and label it ASSUMPTION in the output.
3. **Build the payroll calendar.** For each of the next 3–6 runs: cutoff date, approval date, cash-out date, expected amount — and flag collisions with rent, loan payments, and tax dates.
4. **Model the scenarios.** New hire (loaded monthly delta plus first-90-days cash before they produce), raise (annual loaded delta), contractor at equivalent output (rate × hours vs loaded cost, and the utilization point where the employee wins).
5. **Check payroll-to-revenue.** Total loaded payroll ÷ revenue, before and after the change. Compare against rough planning bands — services 30–50%, retail 15–25%, restaurants 25–35%, agencies and software 40–60% — labeled as rough bands, not law.
6. **Stress-test.** After the change, does committed cash cover at least two full payroll cycles? If not, the plan ships with an ALERT and a cheaper variant: later start, part-time ramp, or contractor first.
7. **Deliver the plan** in the format below, assumptions on their own lines where the accountant can attack them.

## Output format

```
PAYROLL PLAN — <business> — <date>

TRUE COST (monthly, <currency>)
Role   | Gross | Employer taxes* | Benefits | Tools | Loaded | × gross
<role> | 4,000 | 1,120           | 350      | 130   | 5,600  | 1.40
TOTAL  | ...   | ...             | ...      | ...   | ...    | ...
*ASSUMPTION: <local rates supplied / planning multiplier used>

PAYROLL CALENDAR (next <n> runs)
Run date | Cutoff | Approve by | Cash out | Amount | Collides with
<date>   | <date> | <date>     | <date>   | ...    | <rent / tax / loan / — >

SCENARIOS
Option                  | Monthly loaded Δ | First-90-days cash | Break-even signal
New hire <role>         | +5,600           | −16,800            | <revenue or utilization needed>
Raise <person> +<x>%    | +<Δ>             | −<Δ × 3>           | <what must be true to justify it>
Contractor, same output | +<rate × hrs>    | −<total>           | <hours/month where employee wins>

PAYROLL-TO-REVENUE
Now: <x>% | After change: <y>% | Rough band for <industry>: <a>–<b>%
Verdict: <inside band / above band> — <what that means for the next two cycles>

STRESS TEST: committed cash covers <n> payroll cycles after the change — <PASS / ALERT>
Cheaper variant if ALERT: <later start / part-time ramp / contractor first>
```

## Quality bar

- [ ] Loaded cost computed with code; every component itemized, no single blended guess.
- [ ] Assumptions (multiplier, rates, benefit estimates) labeled as ASSUMPTION in the output.
- [ ] Calendar shows cash-out dates — the day money leaves the account — not just pay dates.
- [ ] Scenario table covers all three options with identical columns, comparable at a glance.
- [ ] Ratio benchmark presented as a rough band with the industry named.
- [ ] Two-payroll-cycle stress test included, with a cheaper variant whenever it reads ALERT.

## Example

**Invocation:** "Payroll register attached. Can I afford a second technician at 3,600 gross starting September?"

**Produced:** Loaded cost 4,930/month (multiplier 1.37, labeled ASSUMPTION), a Sep–Nov calendar with two collisions flagged (rent and the Q3 estimate), a scenario table showing a contractor wins below 95 hours/month, the ratio moving 34% → 41% against a 30–50% services band, stress test PASS at 2.4 cycles — recommendation: hire, but start October 1 to clear the Q3 tax date.

*Rules vary by jurisdiction — confirm with a local professional before filing or paying.*
