# Where the company goes next

**Our ambition: you change one business decision, and the whole virtual company
responds coherently.**

This roadmap proposes the next capabilities. They are not shipped features or
dated commitments. The founder owns the goals, mandate, and final decisions;
CEO and CTO lead as peers. The founder should see what each department changed,
why, and which decision needs attention next.

**Future scenario:** a founder changes service pricing. Finance revisits the
assumptions, Sales revises the offer, Marketing checks its claims, Legal reviews
the terms, and developers and designers update the relevant implementation.
CEO and CTO bring the unresolved business and technical tradeoffs to the founder
in one decision brief. The proposed result is consistent work across departments;
it does not predict how the market will respond.

## The foundation today: v1.5.1

- Eight departments, 48 employee manuals and six staff manuals: 54 unique skill
  manuals, with nine registered agents. These are operating instructions, not
  54 continuously running workers.
- Native Claude Code execution with local projects, dependencies, artifacts, and
  recorded reviews. See the [project workspace guide](docs/project-workspace.md).
- Optional business harnesses with task policies, lifetime submission budgets,
  revision checks, and explicit extensions. See [harness loops](docs/harness-loops.md).
- A website directory, brief preparation, and read-only project snapshots, plus
  optional focused [Mission Studio recipes](docs/mission-studio.md).

Local contract tests do not establish real model delivery quality or security.
Reviewer labels are declarations, not authenticated identities. NVIDIA and
scanner references in the manuals are neither installed checks nor certifications.

## The proposed sequence

Each milestone must earn the next through the evidence below.

| Milestone | Status | Founder-visible benefit | Required proof |
|---|---|---|---|
| A. First delivery | NEXT | A useful result with visible handoffs | Repeated pilots against baselines |
| B. Shared decisions | PLANNED AFTER A | Change direction without rebuilding everything | Traced changes across departments |
| C. Earned staffing | PLANNED AFTER A/B | Teams suited to the actual work | Held-out comparisons under equal budgets |
| D. Company forks | EXPLORATION, DEPENDS ON A–C | Compare alternatives before committing | Isolated, reproducible scenarios |

## A. The first real company delivery

**Next:** instrument one local Claude Code pilot for a real, consented project or
an explicitly synthetic one. Start with one concrete project involving at least
three departments. Bring CEO business scope and CTO technical and security
review into the same decision brief; activating all 54 manuals is not the goal.

The pilot must demonstrate interruption and resumption without repeating an
already completed external action. Require explicit user authorization before
external publishing, spending, or new data transmissions, and enforce declared
limits for each run.

Publish a sanitized brief, artifacts, chronology, failures, founder
interventions, and actual usage where the host reports it. Missing usage stays
unknown. Record model aliases and the resolved runtime identity observed for each
run without pinning the configuration.

**Gate:** three runs per configuration (company, single agent, and fixed team),
using the same disclosed case, inputs, and budgets, with business acceptance
criteria defined beforehand and human review. This is an initial pilot-sized
comparison. Include at least one case outside a software business before
generalizing beyond software.

## B. One decision, every affected team

**Planned after A:** explicitly link business assumptions and decisions to tasks,
artifacts, and their consumers. A changed decision would compute impact from
those links, flag superseded evidence, propose only affected rework, and route
unresolved CEO/CTO tradeoffs to the founder. Accepted tasks remain immutable
history; revisions create superseding work with traceable links.

An optional local live company view would require an authenticated companion
with scoped permissions. The static Pages website continues to prepare briefs
and display snapshots; native execution remains in Claude Code.

**Gate:** demonstrate a price change across departments and a requirement change.
Identify all affected artifacts through declared links, preserve unaffected work,
review incomplete links, and measure human arbitration. Missing links must remain
visible uncertainty; the company cannot assume it sees every consequence.

## C. Teams that earn their place

**Planned after A/B:** propose staffing and business harness updates from the
goal, project phase, risk, and previous failures. Stage changes separately from
the current frozen policy. Keep the full company available while activating
only useful skills.

CTO skill admission would require pinned-source attribution and licensing,
declared permissions, security scan coverage and unknowns, sandbox evaluation
with and without the skill, a shadow trial, and explicit promotion and rollback.
A candidate cannot approve itself or loosen a currently failed gate to pass.
NVIDIA SkillSpector and SkillEvaluator are candidate integrations and references,
not mandatory vendors or installed scanners.

**Gate:** compare candidate and current teams or policies on versioned, held-out
business cases under the same disclosed budgets. Require quality and safety
thresholds declared in advance, report tradeoffs, and retain the current setup
without a demonstrated gain. Lower usage is a possible finding, not a promise.

## D. Fork the company. Compare the options.

**Exploration, dependent on A–C:** branch a local business scenario from a
checkpoint, such as subscription versus service fee. Compare assumptions,
generated artifacts, work, risks, and observed usage; the founder selects a
reconciled proposal. A scenario is not a forecast.

Replay would read evidence or run an isolated simulation, with external writes
off by default and no duplicated real actions. A portable company recipe and
sanitized evidence/replay pack would let others reproduce the case. Import must
allow permission and reference previews without implicit execution.

Wider runtime support, bounded recurring operation, and portfolios of companies
would follow only after equivalent capability, permission, budget, isolation,
and resume conformance.

## What earns a release

The headline measure is the proportion of projects reaching a reviewed, useful
result without the founder coordinating every handoff. Track interventions,
reversions, stale work caught, elapsed time, actual host usage, and uncertainty.
Run evidence should be opt-in, redacted, and reproducible. Stars come after people
completing projects, returning, and sharing useful real cases.

## Help prove the first milestone

Three bounded starting contributions for gate A:

- Define one baseline fixture and a human review rubric shared across all runs.
- Build an evidence recorder with redaction and explicit unknown usage fields.
- Add an interrupted-run recovery test that detects repeated external actions.

Use the [contribution guide](CONTRIBUTING.md) for repository conventions.

## Design references

Primary sources checked 2026-09-08:

- [Paperclip](https://github.com/paperclipai/paperclip) documents agent organizations, goals, and budgets.
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) models software-company operating procedures.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) supports state checkpoints.
- [Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) document coordination and current limitations.
- [NVIDIA SkillEvaluator](https://docs.nvidia.com/skills/skillevaluator) separates deterministic, semantic, and live evaluation.

Our differentiating hypothesis is decision coherence across departments with
observable outcomes. Teams and memory alone are established building blocks.
