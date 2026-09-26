# Repository playbook

## PATTERNS

### PB-1 · preserve-project-roster
provenance: T2 2026-09 · hits: 0
WHEN: Adding a department while supporting saved company project workspaces.
DO: Define exact accepted ordered rosters; derive project operations from the validated saved roster.
DO: Apply that roster to owners, reviewers, lifecycle, harness activation, prompts and browser rendering.
DO: Preserve saved profiles, digests and history; never migrate during a read or silently enable a new department.
VERIFY: Frozen legacy fixtures stay byte-identical; new workspaces accept the new department and old ones reject it atomically.

### PB-2 · extend-company-studio
provenance: T2 2026-09 · hits: 1
WHEN: Extending the company directory, executive staff or mission catalog.
DO: Update canonical registries, validators and manuals before generating company and mission data.
DO: Generate both README and studio organization maps from the same source; check every destination without rewriting.
DO: Preserve compatibility aliases and distinguish advisory executives from departmental task owners.
VERIFY: All canonical manuals appear once; builder --check detects stale copies; browser interaction works at desktop and mobile widths.

## QUARANTINE

None.
