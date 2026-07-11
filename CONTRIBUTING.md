# Contributing — open a position

Claude, Inc. hires by pull request. One PR = one new employee (or one promotion of an existing one).

## Hiring a new employee (adding a skill)

1. Create `skills/<slug>/SKILL.md`:

```markdown
---
name: <slug>
description: <What it does + "Use when ..." trigger phrases. Third person, under 500 chars.>
---

# <Display Name> — <Role>

> <One-line tagline>

## When to use
## Workflow
## Output format
## Quality bar
## Example
```

2. Put them on a team: add the slug to the VP roster in `agents/<department>.md`, to `skills_of()` in `bin/company`, and to the department table in `README.md`.
3. That's it. Departments stay at whatever size makes sense — 6 was the founding class, not a law.

## Quality bar (we do fire)

- The description must make the skill trigger at the right moment — write real trigger phrases.
- Workflows are numbered, concrete, and executable by a model with no extra context.
- Output formats are explicit templates, not vibes.
- No placeholder prose. If a section says nothing, delete it.
- Skills must work with zero external dependencies; optional MCPs may be mentioned as upgrades.

## Promotions (improving a skill)

Sharpen triggers, tighten workflows, add a better example. Keep diffs surgical.

## Everything else

Typos, docs, installer fixes: just send it.
