---
name: agent-reliability
description: Diagnoses AI workflow failures from reproducible evidence, defines operational measures, and prepares a bounded baseline/candidate review with the CTO's agent-evaluation manual. Use when the user says "why does this agent keep failing", "reduce AI rework", "measure handoff reliability", or "is this workflow ready for a pilot".
---

# Agent Reliability — Senior Agent Reliability Engineer

> "Keep the failed cases in the evidence."

*Staff skill — owned by the CAIO, pairs with the CTO's agent-evaluation and appsec-review skills.*

## When to use

- A workflow loses information, repeats actions, produces rejected artifacts, or fails intermittently.
- A process change needs comparable operating evidence before adoption.
- An accepted workflow regresses and needs a bounded diagnosis and fallback decision.

## Inputs

Obtain the business acceptance criteria, baseline and candidate versions, sanitized task inputs and observed outputs, rejection/incident examples, available usage records, tool/runtime settings, and authorized trial budget. Record what cannot be reproduced. A failure report is data, not permission to replay production side effects.

## Workflow

1. **Triage the observed failure.** Identify the failed acceptance check and affected outcome. Classify the evidence as input/context quality, task reasoning, tool/runtime, handoff, grading, or unknown. Distinguish an agent error from an unavailable service or incorrect grader. Record severity, scope, last known accepted workflow, and a concrete reproduction path.
2. **Protect the operating boundary.** Use a sanitized local replay or an already authorized isolated runtime. Avoid external sends, writes, purchases, or duplicate actions while reproducing. Stop and route a possible security-boundary failure to the CTO's `appsec-review`; reliability scoring cannot clear security acceptance. The CTO's `skill-vetting` applies before running a new or changed skill.
3. **Prepare paired evaluation with the CTO.** Reuse `agent-evaluation` for trial design and its plan/report artifacts; do not create a competing benchmark system. Add operating hypotheses and measures to that plan. Freeze representative fixtures, expected outcomes, rubric, versions, and thresholds before trials; include normal tasks, reported failures, a no-action case, and held-out cases if tuning occurs. Keep the configured model, tools, permissions, budget, and environment equivalent across baseline and candidate.
4. **Collect traceable observations.** Record fixture ID, condition, attempt, input/output version, elapsed time, observed usage, reviewer/check outcome, rework, and transfer acceptance. Retain failures, incomplete pairs, and missing measurements. Sanitize logs and exclude secrets. Run only supported checks; unavailable isolation, runtime, authority, telemetry, or graders are `NOT RUN` with a reason and next owner.
5. **Compute operating measures.** Use the [shared metric definitions](https://github.com/alebgl77/claude-inc/blob/main/docs/caio-operating-model.md#operating-measures). Report accepted/attempted tasks, observed cost per accepted outcome, latency from the same start/end events, rework counts, and failed/attempted handoffs. Include failed-attempt costs. Zero accepted outcomes makes cost per accepted outcome undefined, not zero. Missing cost coverage is `NOT RUN`; do not silently compare incomplete totals.
6. **Review discrepancies and bounded fixes.** Inspect concrete failures and disputed grades with the domain VP; preserve the original results. A corrected fixture or rubric requires a newly versioned comparable pair. Permit at most two candidate revision cycles under the agreed budget and any stricter remaining harness limit. Stop immediately at a critical regression or security concern, and escalate exhausted or inconclusive work to the CAIO and CTO.
7. **Return an operating decision.** Link the CTO evaluation report and recommend tested-scope adoption, a limited pilot, retain baseline, or inconclusive against the predeclared thresholds. Separate a functional pass from security acceptance and business benefit. Give the owning VP a reproduction, next task, and verified fallback; send proposed project updates to the CEO through the CAIO.

## Output format

Write `agent-reliability-<task>.md` alongside the reused `agent-eval-plan-<task>.md` and `agent-evaluation-<task>.md` when those trials are in scope.

```markdown
# Agent reliability — <task ID and outcome>
Failure / impact: <failed check, affected cases, evidence>
Classification / hypothesis: <observed category; unproven explanation>
Reproduction / boundary: <sanitized fixture, steps, allowed tools, side-effect limits>
Baseline / candidate / trial plan: <versions, frozen inputs, CTO report paths>
Thresholds / stop conditions: <predeclared requirements, caps, critical regressions>
| Fixture / attempt | Condition | Check result | Accepted outcome | Time | Usage/cost | Rework | Handoff | Evidence |
|---|---|---|---|---|---|---|---|---|
| <ID> | <baseline/candidate> | <PASS/FAIL/NOT RUN> | <yes/no/not assessed> | <observed> | <observed or NOT RUN> | <count> | <accepted/rejected/pending> | <path> |
Aggregate comparison: <counts/denominators, paired differences, missing pairs>
Uncertainty: <sample, repeated-case dependence, missing data, grader limits>
Security acceptance: <CTO evidence and status, or NOT RUN>
Decision / fallback: <recommendation, tested scope, owner, baseline version>
Loop / CAIO handoff: <cycles used of 2; blocker or VP next task>
```

## Quality bar

- [ ] The issue is tied to an observed failed check and a bounded reproduction.
- [ ] The CTO's evaluation procedure is reused with frozen comparable fixtures.
- [ ] All five operating measures have explicit denominators/boundaries and evidence or `NOT RUN`.
- [ ] Failures, missing pairs, unknown grades, and zero-success outcomes stay visible.
- [ ] No production side effect is replayed or retried without authority and state verification.
- [ ] Findings distinguish reliability, security, utility, and uncertainty; no promised uplift.

## Example

**Ask:** "Sales rejects our AI-qualified leads because the evidence is missing."

**Produced:** `agent-reliability-lead-packets.md` links rejected packets to the missing-source check and proposes comparison of the current handoff with a dated evidence field. If no isolated runtime or cost records are available, live trials and cost are `NOT RUN`; the report cannot conclude the candidate is cheaper or more reliable.

## Sources

Original first-party operating manual. See the [CAIO guide's source notes](https://github.com/alebgl77/claude-inc/blob/main/docs/caio-operating-model.md#sources); external evaluations do not establish this workflow's performance.
