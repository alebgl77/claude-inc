# Changelog

Notable changes to Claude, Inc. Loosely follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

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
