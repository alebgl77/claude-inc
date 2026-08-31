---
description: Configure an optional active team profile in three short questions
argument-hint: [--global]
---

Read and follow `${CLAUDE_PLUGIN_ROOT}/onboarding/ONBOARDING.md`.

Arguments from the founder:

> $ARGUMENTS

Use project scope by default. Use global scope only when the arguments contain `--global`. The guarded helper saves an accepted project profile as `.claude/company-team.md` or an accepted global profile in the user's Claude directory as `company-team.md`.

Never write either target directly. After the founder accepts the proposal, pass the complete candidate profile on standard input to `"${CLAUDE_PLUGIN_ROOT}/bin/company" profile-save project` or `"${CLAUDE_PLUGIN_ROOT}/bin/company" profile-save global`. The helper performs the target preflight, schema and size validation, private temporary write and atomic replacement. If it reports that a regular profile already exists, ask for a separate replacement confirmation. Only after that distinct confirmation may you retry the same command with `--replace`. Never use `--replace` preemptively.

Do not remove any installed skill. Do not research until the initial proposal is visible and the founder gives distinct consent. Research is suggestions-only and must apply the documented quality gate. It must not download, install, copy, activate or execute third-party content.
