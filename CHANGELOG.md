# Changelog

Notable changes to Claude, Inc. Loosely follows [Keep a Changelog](https://keepachangelog.com).

## [1.4.1] - 2026-09-08

### Fixed
- Replaced the Windows batch launcher with a locally compiled `company.exe`
  that transports literal arguments directly to Bash. Owned legacy launchers
  migrate transactionally; collisions and modifications fail before publication.
  `-NoBin` leaves existing launchers untouched and is not a migration.
- Preserved fenced Markdown sections in generated employee output examples,
  including internal headings previously truncating 18 of the 50 examples.
- Made browser copy actions distinguish plugin commands (`/claude-inc:company`)
  from direct installation (`/company`), and corrected plugin onboarding guidance.
- Rejected nonportable artifact filenames on new submissions while preserving
  read access to safe legacy project records. Accepting such an old submission
  requires revision, renaming, and resubmission; state is never silently renamed.

### Tests and compatibility
- Added real installed project lifecycle checks, a recording host, Windows
  literal-argument regression checks, and launcher migration/rollback coverage.
- Documented Windows PowerShell 5.1's caller-side quote loss: use `--brief-file`
  for exact text. PowerShell 7's native argument path is covered by the regression.

## [1.4.0] - 2026-09-08

### Added
- Local project workspaces for arbitrary founder briefs, goals, constraints,
  department preferences, tasks, dependencies, review records, and decisions
- `company project` commands to initialize, inspect, start, and resume work in
  native Claude Code, with validated context and normal host permissions
- Task submission with real artifact SHA-256 values, unchanged-artifact review
  checks, explicit blockers, and gated state transitions
- A company-first browser introduction, project workspace guide, architecture
  decision, and project/frontend checks across Linux, macOS, and Windows

### Changed
- The canonical CEO and chief of staff use validated structured project state;
  Markdown ledgers become derived reports when a workspace exists
- The website leads with the complete company; five optional mission recipes
  move to `missions.html`
- Public Pages artifacts use an exact static-file allowlist; confidential local
  project state is excluded

## [1.3.0] - 2026-09-08

### Added
- Mission Studio: a browser workspace that opens locally, shows selected manuals
  and ordered handoffs, and exports prompts, plans, and template-only mission cards
- Five mission recipes: `launch`, `validate`, `release`, `proposal`, and `content`,
  with named deliverables, evidence checks, and a separate final reviewer assignment
- Local `company missions` and `company mission` commands with Markdown, JSON,
  and prompt output; Python 3.9+ is required only for the new mission commands
- Independent Mission Studio CI on Linux, macOS, and Windows, including compiler
  tests, frontend tests, and generated dataset freshness checks

### Fixed
- Made `commands/company.md` the canonical, self-contained CEO manual used by
  `/company` and `company brief`; direct installs now place it at
  `.claude/commands/company.md`, and the unsupported plugin-root `CLAUDE.md` is
  no longer shipped
- Reworked both installers as locked, preflighted transactions with separate
  content and global CLI manifests, commit-addressed immutable remote checkouts,
  safe pruning and conservative rollback that retains recovery state when an
  automatic restoration cannot complete

## [1.2.0] - 2026-08-30

### Added
- Optional three-question team onboarding through `company onboard`, `/onboard`,
  `install.sh --onboard` and `install.ps1 -Onboard`
- Reversible project and global active-team profiles with strict validation;
  all 50 skills remain installed as the available bench
- Suggestions-only skill-gap research policy with explicit consent, candidate
  quality gates and no automatic download, installation or execution
- Validated `profile-context` routing for both CLI and plugin company commands

### Security
- Centralized profile writes in a guarded CLI helper with bounded input, strict
  schema validation, symlink and special-file rejection, private temporary files
  and atomic replacement
- Required separate confirmation before replacing a regular profile and blocked
  global fallback when a project profile is present but invalid

### Fixed
- `bin/company` ends quietly when a reader closes the pipe early
  (`company brief | head -20`). Parents that ignore SIGPIPE (Node, .NET, CI runners)
  pass that `SIG_IGN` down to the CLI, so a closed pipe surfaced as
  `printf: write error: Broken pipe` and status 1 instead of the signal; every
  stdout write now ends the way the default SIGPIPE would, silently with 141
- CI probes a closed pipe on every command, so the noise cannot come back unnoticed

## [1.1.0] - 2026-08-27

### Added
- **Sales department** (8th floor, 6 hires): `account-research`, `draft-outreach`, `call-prep`,
  `proposal-builder`, `objection-handler`, `pipeline-review`
- **Executive staff** (2 hires): `chief-of-staff` (mission ledger, decision log, weekly review)
  and `token-accountant` (books the company's own token spend, reporting to the CFO)
- `company sales` and aliases (`sell`, `revenue`, `deals`); `company brief` now ships the two
  staff manuals alongside the CEO manual

### Changed
- Headcount 42 → 50, departments 7 → 8; README, org chart, CLAUDE.md routing table and manifests updated
- The founding 42 are untouched: the original org chart remains canonical

## [1.0.1] - 2026-07-28

### Fixed
- `install.sh` and `bin/company` are executable in git again: `git clone && ./install.sh` works
- `.gitattributes` forces LF endings, so the scripts survive a checkout on Windows
  (`core.autocrlf=true` used to inject `\r` and break bash)

### Added
- `scripts/validate.py`: the company's compliance officer validates all job descriptions,
  the CLI roster, agent/skill cross-references, README coverage, manifests and shell scripts
- GitHub Actions workflow running that validation plus CLI and install smoke tests on every push and PR
- Issue templates ("Propose a new hire", bug report), `SECURITY.md`, `CODE_OF_CONDUCT.md`, this changelog

## [1.0.0] - 2026-07-12

### Added
- 1 CEO (`CLAUDE.md`, `/company`, `/standup`), 7 departments as subagents, 42 employees as skills
- Three ways to hire: Claude Code plugin marketplace, `curl` installer, universal `company` CLI
