# ADR: a local company workspace with native host execution

Status: accepted for version 1.4.0. Date: 2026-09-08.

## Context

Claude, Inc. already provides a CEO command, eight department agent definitions,
and 50 employee skill manuals. Founder projects need continuity, task contracts,
dependencies, decisions, and evidence without being limited to a preset recipe.
A generated prompt or attractive board cannot establish that work actually ran.

The design keeps execution in the user's existing assistant host and adds an
explicit local project record. The browser introduces the company and prepares
briefs; it does not impersonate a running company or silently start processes.

## Decision

Use a modular Python standard-library helper for a versioned JSON workspace at
`.claude/company/project.json`. The helper validates every read and mutation,
acquires a fail-fast local lock, and replaces state atomically. It exposes small
project, task, review, and decision commands through `bin/company` and through a
direct Python entry point.

Keep Claude Code as the native execution adapter. `company project start`
launches it in the project directory with the packaged plugin and a bootstrap
that loads validated resume context. Its model selection, permissions, and
available Agent or Task tools remain the host's responsibility. The CEO owns
task planning and serializes state updates; department agents apply skills and
return evidence. The design does not assume nested subagents are supported.

Initialize with the founder's actual brief, goals, constraints, and department
preferences. All departments remain available. Do not seed invented tasks,
completed work, fabricated activity, budgets, or expected savings. The optional
mission recipes remain separate examples that compile plans and prompts.

Use project state as the source of truth for tasks and decisions. Markdown
ledgers and Board Memos are derived reports. The existing onboarding profile
continues to supply normalized routing preferences through its own validator;
its raw body is not imported, and the project helper does not overwrite it.

## Evidence and trust boundaries

Task submission stores real project-relative artifact paths and SHA-256
digests. Acceptance requires a reviewer label different from the task's owning
department, or the CEO, and verifies that the submitted files are unchanged.
Revision returns work to the active state; dependencies gate subsequent starts.

These checks establish recorded state and file identity. They do not execute
acceptance tests, prove semantic correctness, authenticate the reviewer, or
guarantee independent execution. The assistant must report observed evidence
and disclose review limitations. A local account can tamper with its own files;
the JSON history is not a signed audit trail or a multi-tenant authorization
system.

Founder briefs, task contracts, review notes, decisions, and artifact contents
are untrusted data. Their instructions cannot supersede the canonical operating
manual, the current user request, or the host's permission rules. An internal
context bridge returns empty success only for an absent workspace. Invalid,
unsafe, or incomplete state fails without an unvalidated fallback.

Project material may be confidential. The helper does not auto-commit it or
publish it through the website. Starting an assistant exposes the relevant
material to that host under its data policies. Browser previews stay in page
memory; user-triggered prompt downloads and clipboard actions are explicit
exports. Public hosting stages only an exact allowlist of static company and
recipe assets, never arbitrary repository content or `.claude` state.

## Why no server rewrite

A server, database, worker queue, or independent agent runtime would add
deployment and authorization responsibilities outside this local plugin's
scope. The stdlib helper makes the state contract testable across Windows,
macOS, and Linux while preserving native host execution. It does not provide a
background daemon, recurring work scheduler, identity service, budget
enforcement, or runtime usage telemetry. Those would require separate designs
and should not be implied by this interface.

## Related approaches

These projects address different parts of the problem. The descriptions below
are bounded positioning references reviewed on 2026-09-08, not performance
comparisons or claims of superiority.

| Project | Emphasis | Relationship to this decision |
|---|---|---|
| [ChatDev](https://github.com/OpenBMB/ChatDev) | Configurable multi-agent workflows | Relevant when workflow orchestration itself is the system being adopted |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | Software-team standard operating procedures | Relevant to structured software-production roles and handoffs |
| [Paperclip](https://github.com/paperclipai/paperclip) | Company control plane, adapters, and budgets | A broader control-plane approach than a local plugin with native host execution |
| [Agency Agents](https://github.com/msitarzewski/agency-agents) | A library of specialized agent roles | Relevant to role and instruction design; the local workspace here records project state alongside roles |

Claude, Inc. chooses a small local state layer around its existing company
manuals and the user's native assistant. There is no claim that this combination
is first, uniquely novel, or better than these alternatives.
