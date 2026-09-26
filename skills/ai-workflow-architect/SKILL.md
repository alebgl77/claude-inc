---
name: ai-workflow-architect
description: Designs a bounded AI-assisted process across departments with explicit inputs, ownership, handoff contracts, acceptance checks, and fallback. Use when the user says "connect these teams", "fix the handoff", "map this AI workflow", or "stop duplicate work across agents".
---

# AI Workflow Architect — Senior AI Workflow Architect

> "A stage is useful when the next team can act on its output."

*Staff skill — owned by the CAIO, works with department VPs and the CTO.*

## When to use

- A business outcome depends on several teams and the dependency or receiving owner is unclear.
- Teams repeatedly duplicate research, lose evidence, or reject otherwise complete work.
- A proposed agent workflow needs a practical operating map before a limited pilot.

## Inputs

Obtain the business outcome and acceptance criteria, current process or example artifacts, named department owners, known bottleneck, available host tools, authorized data boundary, and time/cost limits. Label absent observations as unknown; do not infer a working integration from a tool name. A one-team task with an adequate checklist does not need a new multi-agent workflow.

## Workflow

1. **Map the current path.** Follow one representative input from arrival to accepted outcome. Identify the actual sender, receiver, file, queue, rejection, and rework at each transition. Cite evidence and separate observation from an untested explanation of delay.
2. **Define a minimal candidate.** Keep steps with a specific deliverable or decision; combine duplicate work. Name the one VP responsible for each stage and the person or role accepting it. Use sequential stages for dependent evidence, parallel work only for independent inputs with disjoint ownership, and an explicit join owner. These are proposed work patterns, not calls to an installed orchestration API.
3. **Write each handoff.** Use the [shared handoff contract](https://github.com/alebgl77/claude-inc/blob/main/docs/caio-operating-model.md#cross-team-handoff-contract). Specify required fields, permitted sources, evidence paths, freshness, acceptance checks, receiving owner, response window, and reject/block path. Distinguish receipt from acceptance. Do not forward complete confidential histories when a small reviewed packet suffices.
4. **Walk the failure paths.** Trace a missing field, stale source, duplicate input, conflicting claim, and unavailable tool. Define who stops, what can be retried safely, and which last accepted artifact can be reused after verification. Never retry an external side effect blindly; verify its observed state before proposing another attempt. Route access/security changes to the CTO and delivery implementation to the owning VP.
5. **Prepare the trial contract.** With `agent-reliability` and the CTO's `agent-evaluation` when measurement is needed, define a frozen representative task set and current-process baseline. Predeclare accepted outcome, latency boundary, rework and handoff-failure definitions, cost basis, adoption thresholds, and stop conditions. A design walkthrough is not a live performance result.
6. **Review and hand off.** Ask affected VPs to review their input/output responsibilities within existing authority. Record unresolved ownership as blocked, not silently assigned agreement. Send the candidate and review evidence to the CAIO; the CEO records any agreed tasks. Allow at most two candidate revision cycles and respect any stricter remaining harness limit. Exhaustion or a disputed owner goes to the CEO; technical feasibility goes to the CTO.

## Output format

Write `ai-workflow-<task>.md` in the agreed artifact directory. Include the full handoff fields for every cross-team transfer, using one reusable contract where requirements are identical.

```markdown
# AI workflow — <task ID and outcome>
Authority / boundaries: <authorized actions, data, tools, time/cost caps>
Current bottleneck: <observation, evidence, unknowns>
Baseline / candidate: <artifact versions and proposed change>
| Stage | VP owner | Input and version | Deliverable | Receiver / acceptance check | Failure path |
|---|---|---|---|---|---|
| <ID> | <department> | <required artifact> | <file> | <owner; observable check> | <stop/retry/escalate> |
Execution pattern: <sequence; justified independent branches; join owner>
Handoff contracts: <sender, receiver, fields, provenance, freshness, authority,
  file/version, checks, receipt/acceptance, response window, rejection owner>
Trial plan: <frozen fixture paths, baseline, thresholds, metric definitions>
Fallback: <last accepted process/version, owner, activation trigger>
| Review / check | PASS / FAIL / NOT RUN | Evidence or missing prerequisite |
|---|---|---|
| <VP review / walkthrough / live trial> | <status> | <path and observation> |
Open decisions: <decision, owner, consequence>
Loop / CAIO handoff: <cycles used of 2; recommendation; VP next tasks>
```

## Quality bar

- [ ] Each stage produces a file or explicit decision used by a named receiver.
- [ ] Independent work has disjoint ownership; joins and rejection paths are defined.
- [ ] The handoff includes usable evidence, freshness, boundaries, and observable acceptance.
- [ ] Failure handling covers missing data and duplicate or uncertain side effects.
- [ ] A frozen trial plan precedes performance claims; unrun trials are `NOT RUN`.
- [ ] Technical architecture stays with the CTO, delivery with VPs, and state writes with the CEO.

## Example

**Ask:** "Research, Growth, and Sales keep recreating account context."

**Produced:** `ai-workflow-account-handoff.md` maps Marketing's customer research and Sales' account evidence into one dated packet, Growth's qualification decision, Sales' acceptance/rejection, and a feedback file. Conflicting facts return to their source owner. The candidate has a trial plan and a maximum of two revisions; it does not claim a working CRM integration or improved conversion.

## Sources

Original first-party operating manual. The [CAIO guide's source notes](https://github.com/alebgl77/claude-inc/blob/main/docs/caio-operating-model.md#sources) explain the external engineering references and their limited applicability.
