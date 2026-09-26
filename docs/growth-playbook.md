# Growth: from evidence to accepted opportunity

Growth connects sourced account evidence, qualification, experiments, and revenue
feedback. Its six manuals work across B2B SaaS, services, and ecommerce; choose
the business outcome before choosing tools. Marketing owns research, positioning,
copy, and creative. Sales owns outreach, opportunity acceptance, CRM truth, and
deals. Growth owns the hypotheses and measurement that connect them.

The CEO sets priorities and alone records project-state changes. The CTO owns
technical and security acceptance; Developers owns production implementation.
Use CAIO advice for a specific process, reliability, shared-context, or adoption
problem. Neither executive advice nor a tool recommendation grants new authority.
Carry forward authority already granted for the same scope.

## Start with the relevant manuals

| Manual | Working result | Receiver |
|---|---|---|
| [growth-strategy](../skills/growth-strategy/SKILL.md) | Constraint, ICP, chosen motion, and first experiment brief | Growth VP and CEO |
| [account-intelligence](../skills/account-intelligence/SKILL.md) | Dated source facts, separate inferences, qualification reasons | Marketing and Sales |
| [growth-engineering](../skills/growth-engineering/SKILL.md) | Identity, event, extraction, and measurement contracts | Developers, CTO, experiment owner |
| [growth-experiments](../skills/growth-experiments/SKILL.md) | Frozen experiment card and evidence-based decision | Growth VP and CEO |
| [lifecycle-growth](../skills/lifecycle-growth/SKILL.md) | Value states, bounded interventions, retained-value checks | Marketing, Sales, product owner |
| [revenue-operations](../skills/revenue-operations/SKILL.md) | Reconciled accepted/won/retained outcomes and cohort costs | Sales, Finance, strategy owner |

From a clone with the CLI available:

```bash
company growth "Qualify supplied account signals and prepare a Sales-reviewed experiment" --print
company mission b2b-growth --brief "Plan a bounded B2B pilot using supplied evidence; prepare files for review" --format prompt
company caio "Resolve missing provenance in the Growth to Sales handoff" --print
```

These commands prepare scoped prompts. The mission recipe does not run the work,
create a project, fetch accounts, connect a CRM, or send messages. Use the
[project workspace](project-workspace.md) when recorded task continuity is useful.
New workspaces support Growth ownership; historical eight-department workspaces
keep their roster and frozen policies. Use a new workspace for Growth tasks.
CAIO is advisory, with no task-owner or reviewer enum.

## A fully specified synthetic B2B pilot

**Every company, source fact, date, count, cost, and outcome in this worked case
is synthetic.** It demonstrates the operating method, not an executed campaign,
verified prospect list, or measured business improvement. The included HTML
fixture demonstrates extraction separately; it does not substantiate this case.

The fictional vendor, RelayDesk, offers shared operations reporting to B2B service
companies. The founder's fictional mandate is a feasibility pilot within EUR
3,600 of allocated research, assets, operations, and first Sales-review cost.
Live outreach would require that mandate in the actual user session. Here all
outreach, CRM actions, and revenue collection remain unexecuted.

### Source facts and qualification

Freeze `ICP-v1` before scoring: an independent B2B service account, 50–250 staff,
at least two operating regions, a shared reporting workflow, and service coverage
within the offer's supported geography. Exclude current customers, open
opportunities, competitors, and related accounts already represented in the
cohort. One legal/operating account is one unit; collapse parent/subsidiary
clusters before eligibility and do not enroll related accounts separately.

For the fictional account `A017`, the synthetic evidence register contains:

| ID | Synthetic source fact | Provenance and time | What remains unknown |
|---|---|---|---|
| F1 | Company profile says 120 staff and three regions | `sources/A017-profile.html`, publisher A017; observed 2026-09-25 UTC; publication date unknown | Accuracy beyond the supplied snapshot |
| F2 | Update describes a shared reporting workflow launched 2026-09-18 | `sources/A017-update.html`, publisher A017; observed 2026-09-25 UTC; event date source-asserted | Whether the workflow causes pain or needs replacement |
| F3 | Published coverage matches the supported geography | Same profile; observed 2026-09-25 UTC | Budget, buyer authority, and purchase timing |

Those paths are planned example artifacts, not files shipped in this repository.
Preserve excerpts, source identifiers, actual snapshot hashes, and the researcher
in a real evidence register. Never invent a hash for this example. Recheck F1/F3
within 90 days and F2 within 30 days of observation; missing or expired required
evidence causes deferral. Parsing later does not renew those windows.

The frozen starting fit rubric gives 0–2 points each for evidenced workflow,
segment/capacity, and supported geography. Require at least 5/6, all must-haves,
no exclusion, and a relevant current signal. A017 scores 6/6 in this fictional
case and is a **candidate**, with readiness labeled `observed change`. The
hypothesis “regional reporting creates coordination friction” remains an
inference. Funding, hiring, page text, and a high score do not prove buying intent.
An account with an unknown must-have is `defer`, with the missing fact and owner.

### Sales acceptance contract

Growth hands Sales `account-handoff.md` and `account-evidence.csv` containing the
account ID, ICP/rubric versions, source references and clocks, rule-by-rule fit,
unknowns, exclusions, and a proposed discovery question. Marketing receives the
same verified problem/audience facts for its diagnostic-offer copy; it must not
turn the unverified friction hypothesis into a claim about that account.

Sales returns a dated disposition within two working days of packet receipt:
`accepted`, `rejected`, or `deferred`, with a reason and next owner. Packet
acceptance means usable research. It is distinct from a **Sales-accepted
opportunity**, which requires all four conditions:

1. Fit and exclusion checks pass on current evidence.
2. A relevant stakeholder confirms a problem the actual offer can address.
3. Sales records the supporting interaction and a unique opportunity/account ID.
4. The stakeholder and Sales agree a dated next step inside the acceptance window.

A message, reply, scheduled meeting, or research score alone does not qualify.
Sales controls outreach and CRM entry under existing authority. Feedback codes
are `no-fit`, `stale-evidence`, `duplicate`, `no-confirmed-problem`,
`no-agreed-next-step`, and `accepted`; timing unknown is deferred. Keep source
facts and Sales observations separate so Growth can revise a future rubric
without rewriting the frozen experiment.

### Frozen experiment card: GD-01 v1

| Field | Synthetic predeclared rule |
|---|---|
| Owner and mechanism | Growth VP; a relevant operations diagnostic may help eligible accounts articulate a confirmed problem and agree a next step |
| Cohort | 80 independent eligible accounts under ICP-v1, deduplicated before assignment; no shared parents, current customers, or open opportunities |
| Assignment | Account-level 1:1 randomization; sort stable account IDs, shuffle with seed `20261001`, assign first 40 control and remaining 40 treatment; retain the assignment file |
| Exposure | Every user/contact within an account inherits its account assignment; freeze account mappings and prohibit overlapping offer tests in this cohort |
| Control / treatment | Existing approved Sales offer v1 / Marketing's operations diagnostic offer v1; same channel, contact cap, follow-up policy, and Sales acceptance rubric |
| Primary metric | Unique accounts with at least one Sales-accepted opportunity within 30 days of assignment / all eligible assigned accounts in that arm |
| Estimand | Difference in assigned-account acceptance rates, treatment minus control; retain nonresponding and unexposed assigned accounts in the denominator |
| Enrollment / analysis | 2026-10-01 through 2026-10-14 UTC; follow each account for 30 days; freeze acceptance data at 2026-11-13 23:59 UTC and analyze on 2026-11-14 |
| Information plan | Assumed control rate 10%; worthwhile improvement +10 percentage points; two-sided alpha 0.05 and 80% power require roughly 200 independent accounts per arm by a normal two-proportion planning approximation |
| Sample constraint | 40 per arm cannot meet that plan; GD-01 is a feasibility pilot, with business impact predeclared inconclusive and no revenue-lift scaling decision |
| Analysis method | Report counts, rates, absolute difference, per-arm Wilson 95% intervals and a Newcombe interval for the difference; one primary comparison, no subgroup success claims |
| Decision | Continue to a separately scoped, adequately sized test only if feasibility gates pass; iterate packet/process defects within authorized limits; stop for a guardrail failure; otherwise inconclusive |
| Revenue follow-up | Preserve original cohort/assignment; reconcile accepted, won/lost, collected, and retained outcomes over 90 days from assignment; final revenue review 2027-01-13 |

Do not silently discard accounts with missing outcomes. Show missing/immature
counts; unresolved source coverage prevents a business interpretation. More
contacts, page views, repeated extracts, or user events do not increase the
independent account sample. A discovered parent overlap invalidates independence
and requires a disclosed design correction before another experiment.

Preflight must reconcile all 80 IDs, persistent assignments, exposure records,
Sales timestamps, and deduplicated opportunity joins. For a real test, run the
declared allocation-mismatch check (chi-square, flag p < 0.01), inspect missing
outcomes and treatment leakage, and freeze the offer, rubric, and event versions.
Fixed-horizon efficacy peeking cannot stop the test early; cost and safety stops
apply immediately without establishing efficacy.

Feasibility gates are at least 95% complete source packets, at least 95% Sales
dispositions inside two working days, and zero assignment contamination. Guardrails
are no actions outside existing authority, no disclosure to an unauthorized
recipient, allocated total cost at most EUR 3,600, and at most 20% of packets
requiring correction for missing required facts. Sales stops affected contact on
an authority or recipient issue; Growth pauses the pilot on another breach and
returns the evidence to the CEO. CAIO can repair a recurring transfer defect;
CTO reviews any technical or security change. No watcher is installed.

### Synthetic result and revenue feedback

Assume all 80 primary outcomes are mature and known, and all feasibility gates
pass. The fictional summary is:

| Measure | Control | Treatment |
|---|---:|---:|
| Assigned independent accounts | 40 | 40 |
| Unique Sales-accepted opportunities | 4 | 8 |
| Accepted-opportunity rate | 10% | 20% |
| Allocated cohort cost | EUR 1,200 | EUR 2,400 |
| Cost per accepted opportunity | EUR 300 | EUR 300 |

The descriptive difference is +10 percentage points. This table is arithmetic
on invented observations, not evidence of lift. A real analysis must supply
the predeclared intervals and diagnostics before any inference; none has been
run here. The predeclared decision remains **inconclusive for business impact**.
Passing feasibility can justify preparing a larger test, not scaling acquisition.

Cost per accepted opportunity uses research labor, data/tool allocation,
Marketing asset allocation, campaign operations, and Sales first-review labor.
The synthetic control allocations are EUR 600/0/200/0/400; treatment allocations
are EUR 600/200/800/400/400. Overhead and later deal-closing labor are excluded
equally; this is not customer acquisition cost or profit. With zero acceptances,
report cost and `undefined: zero accepted opportunities`.

Revenue Operations returns a versioned feedback file joining the original
account, ICP, signal, assignment, and opportunity IDs. It preserves reasons for
every rejection/defer, unmatched IDs, duplicate corrections, and observation
dates. Sales owns accepted/won/lost truth; Finance supplies collected revenue
and contribution definitions. The later revenue/retention data are unavailable
in this example: report pending, never zero or projected wins. Strategy changes
the next cohort or hypothesis only after that review; it does not backfill a
successful result into GD-01.

## Adapt the outcome to the business

| Model | Useful outcome and unit | Adaptation and guardrail |
|---|---|---|
| SaaS | Account reaches shared value and retains paid use | Preserve workspace assignment; measure activation and retained use separately from intent; protect support load and cancellation |
| Services | Client accepts scoped work with sustainable collected contribution | Verify delivery capacity, margin, scope, and contract dependencies; retain account assignment across contacts |
| Ecommerce | Customer generates fulfilled contribution and appropriate repeat purchase | Declare customer/visitor unit, purchase/refund windows, discounts, stock, and consent/suppression; do not force a Sales-opportunity metric onto self-serve orders |

For insufficient volume or long sales cycles, report a bounded feasibility or
observational pilot and its limitations. A different business model requires its
own baseline and sample plan; the synthetic B2B thresholds are not defaults for
every business.

## Tools, evidence, and references

Use the [Growth toolkit](growth-toolkit.md) for the tested local HTML extractor
and optional measurement choices. Use the [CAIO operating model](caio-operating-model.md)
when the handoff itself needs evaluation. Neither document establishes ROI.

Primary methodology references checked 2026-09-26:

- [PostHog: A/B testing mistakes](https://posthog.com/product-engineers/ab-testing-mistakes)
  discusses choosing meaningful metrics and avoiding premature experiment decisions.
- [GrowthBook: Open Guide to A/B Testing](https://docs.growthbook.io/assets/files/open-guide-to-ab-testing.v1.0-228e9312b957a9716766cd8887b18a11.pdf)
  provides experimental-design and inference background. The pilot's synthetic
  thresholds and business contracts above are project examples, not vendor results.
