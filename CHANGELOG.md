# Changelog

Notable changes to Claude, Inc. Loosely follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

## [1.0.1] — 2026-07-28

### Fixed
- `install.sh` and `bin/company` are executable in git again — `git clone && ./install.sh` works
- `.gitattributes` forces LF endings, so the scripts survive a checkout on Windows
  (`core.autocrlf=true` used to inject `\r` and break bash)

### Added
- `scripts/validate.py` — the company's compliance officer: validates all 50 job descriptions,
  the CLI roster, agent/skill cross-references, README coverage, manifests and shell scripts
- GitHub Actions workflow running that validation plus CLI and install smoke tests on every push and PR
- Issue templates ("Propose a new hire", bug report), `SECURITY.md`, `CODE_OF_CONDUCT.md`, this changelog

## [1.0.0] — 2026-07-12

### Added
- 1 CEO (`CLAUDE.md`, `/company`, `/standup`), 7 departments as subagents, 42 employees as skills
- Three ways to hire: Claude Code plugin marketplace, `curl` installer, universal `company` CLI
