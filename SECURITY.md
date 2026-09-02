# Security

Claude, Inc. ships markdown instructions plus two shell scripts. It runs with whatever
permissions your AI CLI already has. The CLI and installers add no network research,
credentials or daemons.

## Reporting a vulnerability

Open a [security advisory](https://github.com/alebgl77/claude-inc/security/advisories/new)
rather than a public issue for anything exploitable.

## What reviewers check on every PR

- A skill instructing the model to exfiltrate files, credentials or environment variables
- A skill telling the model to run destructive commands (`rm -rf`, force-push, credential edits)
- Prompt-injection payloads hidden in instructions ("ignore previous instructions")
- Anything in `install.sh` or `bin/company` that fetches and executes remote code

## Onboarding research boundary

Optional onboarding can propose research after it has shown an initial team proposal. It must receive separate, explicit consent before using an engine's network research tools. The repository's CLI and installers contain no research or download code.

Research is metadata-only. After consent, an engine may inspect required remote pages or code read-only while treating them as untrusted. It must not save, download, install, execute, activate, import or copy third-party skills or instructions. Each recommendation must pass the quality gate in `onboarding/ONBOARDING.md`, including license, maintenance, documentation, compatibility, source, version pin and prompt-injection review. Popularity alone is not evidence of safety or quality. A candidate is rejected when its content cannot be audited, its install is opaque, or material security signals remain unresolved.

Team profiles must be regular files, not symbolic links. The CLI checks the exact byte size, rejects NUL bytes, then performs a bounded frontmatter read and validates it against the built-in department and skill registries. It sends only scope, departments and skills to an engine prompt. The free-form body, profile path and stored research status stay local, and stored research metadata never authorizes network access. A present but invalid project profile blocks global fallback.

The onboarding model never writes a profile directly. The CLI save helper checks the target and its direct parent, rejects symbolic links and non-regular files, validates the candidate before final placement, writes a private temporary file in the destination directory, and uses an atomic rename. A regular existing profile is replaced only after a separate confirmation and an explicit `--replace` retry.

## Installer ownership boundary

The Bash and PowerShell installers record managed target content in
`.claude-inc-manifest-v1` and global CLI ownership separately in
`~/.claude/.claude-inc-cli-manifest-v1`. They acquire an exclusive target lock
and, when installing the CLI, `~/.claude-inc-cli-install.lock` before taking
snapshots. The global preflight and the checks immediately before application
fail closed on collisions, modified managed content, unsafe paths or concurrent
changes.

A remote bootstrap clones into a separate candidate, resolves its commit and
promotes it only after preflight to the commit-addressed sibling cache
`<cache>.checkouts/<commit>`. It never pulls into the active legacy cache, and
an existing immutable checkout must match the candidate before reuse.

Application uses staged content and a journaled rollback. If automatic recovery
cannot finish, the installer retains the rollback directory, its journal and
the installation lock paths, then prints their exact locations. Treat those
paths as active recovery state: first confirm that no installer is running,
inspect the retained journal and backups, and reconcile the managed files. Only
after verifying recovery should you remove the exact retained paths reported by
that failed run. Do not discard a lock or rollback directory solely because an
installation returned an error.

## What this project deliberately does not do

Store secrets or phone home. Installation copies the company files and can create a local CLI link or wrapper. Optional onboarding runs only with an explicit flag; otherwise it is deferred. Read the installer before piping it into a shell.
