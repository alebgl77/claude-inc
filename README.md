<div align="center">

# 🏢 Claude, Inc.

### Hire a 42-employee AI company in one command.

**7 departments · 42 skills · 1 CEO — the whole org chart, running inside Claude Code (or any AI CLI).**

[![compliance](https://github.com/alebgl77/claude-inc/actions/workflows/validate.yml/badge.svg)](https://github.com/alebgl77/claude-inc/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Employees](https://img.shields.io/badge/employees-42-orange)
![Departments](https://img.shields.io/badge/departments-7-8A2BE2)
![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20any%20CLI-green)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome%20(we're%20hiring)-brightgreen.svg)](CONTRIBUTING.md)

*You are the founder. This repo is your payroll.*

</div>

<img src="assets/banner.png" alt="Claude, Inc. — hire a 42-employee AI company in one command" width="100%">

---

## Why

Everyone screenshots the org-chart infographics. Nobody ships them.

**Claude, Inc.** turns the *"Build Your Whole Team with Claude"* org chart into a working company: every department is a real Claude Code **subagent**, every employee is a real **skill**, and the CEO is a routing brain that briefs them, parallelizes them, and reports back like a board memo.

No SaaS. No API keys. No framework. Just markdown with a job description — the way Claude was meant to be staffed.

## The org chart

```mermaid
graph TD
    CEO["🧠 CEO<br/><i>your AI CLI</i>"]
    CEO --> DEV["👨‍💻 Developers<br/>6 skills"]
    CEO --> DES["🎨 Designers<br/>6 skills"]
    CEO --> MKT["📣 Marketing<br/>6 skills"]
    CEO --> SOC["📱 Social Media<br/>6 skills"]
    CEO --> FIN["💰 Finance<br/>6 skills"]
    CEO --> SMB["🏪 Small Business<br/>6 skills"]
    CEO --> LEG["⚖️ Legal<br/>6 skills"]
```

You talk to the CEO. The CEO briefs the departments. The departments put their employees to work. You get files and a board memo. **That's the whole product.**

## Hire everyone in 60 seconds

**Option A — Claude Code plugin (recommended)**

```
/plugin marketplace add alebgl77/claude-inc
/plugin install claude-inc@claude-inc
```

**Option B — one-liner (installs skills + agents into `~/.claude`, plus the `company` CLI)**

```bash
curl -fsSL https://raw.githubusercontent.com/alebgl77/claude-inc/main/install.sh | bash
```

**Option C — clone and walk into the office**

```bash
git clone https://github.com/alebgl77/claude-inc && cd claude-inc
./install.sh --project   # hires the company into this project's .claude/
claude
```

## Your first day as founder

```bash
# Brief the CEO — routes across departments, in parallel, returns a Board Memo
/company ship a landing page for my invoicing app, with pricing, legal-clean claims and 3 LinkedIn posts

# Morning standup — all 7 departments report on your current project
/standup

# Or talk to one department directly, from ANY terminal
company dev "my tests fail after the last refactor"
company legal "triage this NDA: $(cat nda.md)"
company marketing "10 ad variants for my beta launch"
```

Skills also fire on their own — say *"review this contract"* in any conversation and the Contract Reviewer shows up to work. The org chart is there when you need coordination, invisible when you don't.

## Meet the company

<details open>
<summary><b>👨‍💻 Developers</b> — VP of Engineering</summary>

| Employee | Role | Superpower |
|---|---|---|
| `superpowers` | Skill Forge | 14-skill power pack |
| `context7` | Docs Fetcher | Live library docs |
| `mcp-builder` | Tool Wright | Wire up MCP servers |
| `skill-creator` | Skill Smith | Build your own skills |
| `webapp-testing` | QA Engineer | Browser-test your app |
| `claude-mem` | Memory Keeper | Persistent memory |

</details>

<details>
<summary><b>🎨 Designers</b> — VP of Design</summary>

| Employee | Role | Superpower |
|---|---|---|
| `ui-ux-pro-max` | Design Lead | Full UI/UX system |
| `taste` | Taste Maker | Design-taste critic |
| `frontend-design` | Front of House | Build front-end UIs |
| `transitions` | Motion Artist | CSS motion library |
| `web-artifacts` | Prototyper | Live web prototypes |
| `brand-guidelines` | Brand Keeper | Build a brand kit |

</details>

<details>
<summary><b>📣 Marketing</b> — CMO</summary>

| Employee | Role | Superpower |
|---|---|---|
| `copywriting` | Word Smith | High-converting copy |
| `ai-seo` | Search Whisperer | Rank in AI search |
| `cro` | Conversion Lead | Lift conversion rates |
| `ad-creative` | Ad Maker | Ad headlines & visuals |
| `customer-research` | Voice of Customer | Synthesise user voice |
| `lead-magnets` | Bait Master | Build lead magnets |

</details>

<details>
<summary><b>📱 Social Media</b> — Head of Social</summary>

| Employee | Role | Superpower |
|---|---|---|
| `post-writer` | Ghostwriter | Write LinkedIn posts |
| `profile-optimizer` | Profile Doctor | Optimise your profile |
| `reels-scripting` | Reel Writer | Script your Reels |
| `hook-generator` | Hook Smith | Scroll-stopping hooks |
| `voice-builder` | Voice Coach | Clone your voice |
| `youtube-thumbnail` | Cover Tester | Test thumbnail covers |

</details>

<details>
<summary><b>💰 Finance</b> — CFO</summary>

| Employee | Role | Superpower |
|---|---|---|
| `financial-statements` | Statement Builder | Build the statements |
| `journal-entry` | Journal Keeper | Post journal entries |
| `reconciliation` | Reconciler | Reconcile the books |
| `variance-analysis` | Variance Analyst | Explain the variances |
| `audit-support` | Auditor | Prep for audit |
| `close-management` | The Closer | Run the close |

</details>

<details>
<summary><b>🏪 Small Business</b> — COO</summary>

| Employee | Role | Superpower |
|---|---|---|
| `cash-flow-snapshot` | Cash Watcher | Snapshot your cash |
| `invoice-chase` | Debt Chaser | Chase late invoices |
| `plan-payroll` | Payroll Planner | Plan payroll |
| `margin-analyzer` | Margin Analyst | Analyse margins |
| `tax-prep` | Tax Prepper | Prep your taxes |
| `run-campaign` | Campaign Runner | Run a campaign |

</details>

<details>
<summary><b>⚖️ Legal</b> — General Counsel</summary>

| Employee | Role | Superpower |
|---|---|---|
| `review-contract` | Contract Reviewer | Review any contract |
| `triage-nda` | NDA Triage | Fast NDA review |
| `compliance-check` | Compliance Officer | Check compliance |
| `legal-risk-assessment` | Risk Assessor | Flag legal risk |
| `vendor-check` | Vendor Vetter | Vet a vendor |
| `signature-request` | Signature Wrangler | Route for signature |

</details>

## How it works

The infographic maps 1:1 onto Claude Code primitives — no magic, just org design:

| On the org chart | In this repo | Mechanism |
|---|---|---|
| **CEO** | `CLAUDE.md` + `/company` | Routing brain: parses the mission, delegates, arbitrates, writes the Board Memo |
| **7 departments** | `agents/*.md` | Subagents with their own context windows — they run **in parallel** |
| **42 employees** | `skills/*/SKILL.md` | Skills with trigger-rich descriptions — VPs hire them per task, or they self-trigger |

```
you ──mission──▶ CEO ──briefs──▶ VP(s) ──hire──▶ skill(s) ──ship──▶ files + Board Memo
```

![The full org chart — 1 CEO, 7 departments, 42 employees](assets/org-chart.svg)

Every employee follows the same contract: **When to use → Workflow → Output format → Quality bar → Example.** That's what makes 42 of them manageable — and what makes PRs reviewable.

And the company audits itself: `python3 scripts/validate.py` (run in CI on every push) checks every job description, cross-references the CLI roster against the departments, and fails the build if an employee is hired twice, orphaned, or missing from the docs.

## Works with any CLI

The `company` CLI composes fully self-contained prompts (department charter + all 6 employee manuals + your task). If `claude` is installed it runs it; otherwise pipe it anywhere:

```bash
company roster                                   # meet the team
company brief "launch my product"                # CEO mode
company finance "reconcile bank.csv vs ledger.csv"
company design "critique screenshot.png" --print | gemini   # any engine
CLAUDE_INC_ENGINE=codex company dev "add tests"              # or set an engine
```

No Claude Code? No problem. The hierarchy travels as plain text.

## FAQ

**Is this over-engineering?** For "fix a typo", yes — which is why skills also trigger individually and the CEO skips ceremony on single-department tasks. For "prepare my product launch", a parallel org beats one long chat every time.

**Does `/company` burn tokens?** Departments are subagents with their own context, so big missions fan out real work. Brief the CEO like you'd brief a real one: clear scope, only the departments you need.

**Finance/Legal outputs?** Decision support with mandatory disclaimers, not professional advice. The VPs are contractually incapable of forgetting this.

**Can I hire more employees?** Yes — [we're hiring](CONTRIBUTING.md). One PR = one new employee.

## Credits

- Org chart concept: **[Build Your Whole Team with Claude](https://charliehills.substack.com)** by Charlie Hills — this repo is the runnable formalisation of that map.
- Some employees are self-contained homages to great ecosystem projects: [obra/superpowers](https://github.com/obra/superpowers), [Context7](https://github.com/upstash/context7), claude-mem.
- Built with [Claude Code](https://docs.claude.com/en/docs/claude-code) subagents, skills and plugins.

## License

[MIT](LICENSE) — take the whole company, it's yours.

---

<div align="center">

**If your new workforce ships something, [⭐ star the company](https://github.com/alebgl77/claude-inc) — it's cheaper than payroll.**

</div>
