# Security

Claude, Inc. ships markdown instructions plus two shell scripts. It runs with whatever
permissions your AI CLI already has — it adds no network access, no credentials, no daemons.

## Reporting a vulnerability

Open a [security advisory](https://github.com/alebgl77/claude-inc/security/advisories/new)
rather than a public issue for anything exploitable.

## What reviewers check on every PR

- A skill instructing the model to exfiltrate files, credentials or environment variables
- A skill telling the model to run destructive commands (`rm -rf`, force-push, credential edits)
- Prompt-injection payloads hidden in instructions ("ignore previous instructions…")
- Anything in `install.sh` or `bin/company` that fetches and executes remote code

## What this project deliberately does not do

Store secrets, phone home, or run anything at install time beyond copying files into `~/.claude`
and creating one symlink. Read `install.sh` before piping it into bash — it is 80 lines.
