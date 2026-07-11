---
name: superpowers
description: Runs 14 numbered engineering protocols in one pack — brainstorm, spec, plan, scaffold, TDD red-green-refactor, systematic debugging, refactoring, code review, performance, security, docs, git hygiene, release checklist, postmortem. Use when the user says "build this feature properly", "debug this systematically", "review my diff", "run a security pass", "ship the release", "write the postmortem", or names any engineering phase from idea to retrospective.
---

# Superpowers — Skill Forge

> "14-skill power pack"

## When to use

- End-to-end feature work that deserves discipline — "let's build this properly, not vibe-code it"
- A bug that resists poking — "debug this systematically", "it fails randomly and I'm lost"
- Pre-merge and pre-ship gates — "review my diff", "run a security pass", "are we ready to release?"
- After an incident — "write the postmortem"
- Any single phase named outright — spec it, plan it, refactor it, profile it, document it

## The 14 protocols

| # | Protocol | Core move |
|---|---|---|
| P1 | Brainstorm | Generate 3+ approaches, score against constraints, pick one on the record. |
| P2 | Spec | Acceptance criteria and non-goals written before any code. |
| P3 | Plan | Ordered steps, each independently verifiable. |
| P4 | Scaffold | Skeleton with tooling wired — lint, test runner, entry point, CI hook. |
| P5 | TDD | Red-green-refactor: failing test first, minimal pass, then clean. |
| P6 | Systematic debugging | Reproduce → isolate → hypothesize → fix → regress. |
| P7 | Refactoring | Behavior-preserving change under green tests, one move at a time. |
| P8 | Code review | Line-level and design-level pass — correctness, security, perf, readability. |
| P9 | Performance pass | Measure first, profile the hot path, fix, re-measure. |
| P10 | Security pass | Inputs, authn/z, secrets, dependencies, injection surfaces. |
| P11 | Docs | README, API reference, runbook — written from the reader's seat. |
| P12 | Git hygiene | Small atomic commits, imperative messages, clean history. |
| P13 | Release checklist | Version, changelog, tests green, rollback plan, ship, verify live. |
| P14 | Postmortem | Blameless timeline, root cause, action items with owners. |

## Workflow

1. Identify the task's phase: idea, build, break/fix, ship, or learn.
2. Pick the matching protocol(s) from the table and announce the pick — "Running P6 — systematic debugging."
3. Execute the protocol as concrete steps. P6, for example: reproduce deterministically, isolate by bisecting code/data/env, state one falsifiable hypothesis, fix, add a regression test.
4. For a full feature, chain: P1 → P2 → P3 → P4 → P5 → P8 → P11 → P12 → P13. Skip a link only by saying so and why.
5. End every protocol with an artifact — spec file, failing-then-passing test, review notes, changelog — never just narrative.
6. If the task changes phase mid-flight (the build surfaces a bug), switch protocols explicitly; don't blur two into mush.
7. Log each run in the output format below and hand the next protocol its inputs.

## Output format

```
## Protocol run — P<n> <name>
Phase: <idea | build | fix | ship | learn>
Trigger: <the ask, one line>
Steps executed:
1. <step> → <result>
2. <step> → <result>
Artifact: <path or inline block>
Verdict: PASS | FAIL — <one-line reason>
Next: P<n> <name> | done
```

## Quality bar

- [ ] Protocol named before work started, not retrofitted after
- [ ] Every run produced a concrete artifact, not just prose
- [ ] P5/P6 runs end with a test that fails without the fix and passes with it
- [ ] Feature chains hit at least P2, P5, and P8 — or the skip is justified in writing
- [ ] Verdicts are earned: FAIL reported as FAIL, never softened to "mostly works"

## Example

Ask: "The login test is flaky — fix it properly."

Run P6: reproduced 5x (fails ~40%), isolated to the token-expiry check reading the real clock, hypothesis "clock skew between test container and issuer" confirmed by freezing time, fixed with an injected clock, regression test added that fails on the old code. Artifact: `tests/auth/token-clock.spec.ts`. Verdict PASS. Next: P12, one atomic commit.

## Credits

Inspired by obra/superpowers.
