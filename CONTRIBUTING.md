# Contributing — open a position

Claude, Inc. hires by pull request. One PR = one new employee (or one promotion of an existing one).

## Hiring a new employee (adding a skill)

1. Create `skills/<slug>/SKILL.md`:

```markdown
---
name: <slug>
description: <What it does, then one "Use for ..." or "Use when ..." cue. Third person, at most 100 characters.>
---

# <Display Name> — <Role>

> <One-line tagline>

## When to use
## Workflow
## Output format
## Quality bar
## Example
```

   Keep the description that short on purpose. Claude Code shows every installed
   skill's name and description on each turn inside one budget shared by all
   skills (1% of the context window, 8,000 characters by default) and drops the
   descriptions of the least-used skills beyond it. `python3 scripts/validate.py`
   fails when the whole company needs more than 7,200 characters. End
   `## When to use` with a `- Typical requests: "...", "..."` line quoting real
   phrasings: that is where the detail belongs, and it loads only when needed.

2. Put them on a team: add the slug to the VP roster in `agents/<department>.md`, to `skills_of()` in `bin/company`, and to the department table in `README.md`.
3. That's it. Departments stay at whatever size makes sense — 6 was the founding class, not a law.

## Quality bar (we do fire)

- The description names the job in words a user would say, in at most 100 characters; real example requests go under `## When to use`.
- Workflows are numbered, concrete, and executable by a model with no extra context.
- Output formats are explicit templates, not vibes.
- No placeholder prose. If a section says nothing, delete it.
- Skills must work with zero external dependencies; optional MCPs may be mentioned as upgrades.

## Promotions (improving a skill)

Sharpen triggers, tighten workflows, add a better example. Keep diffs surgical.

## Everything else

Typos, docs, installer fixes: just send it.
