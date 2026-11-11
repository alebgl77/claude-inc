---
name: skill-creator
description: Writes and trigger-tests a new SKILL.md. Use for creating or fixing a skill.
---

# Skill Creator — Skill Smith

> "Build your own skills"

## When to use

- "Make me a skill for <recurring task>" — anything you've done three times deserves a SKILL.md
- "Turn this workflow into a skill" after a session that went well
- "Add a new employee to <department>" in this repo
- "My skill never triggers" / "the wrong skill fires" — description surgery
- Standardizing a process so the whole team runs it the same way
- Typical requests: "make me a skill for X", "turn this workflow into a skill", "add a new employee to the team", or "my skill never triggers".

## Workflow

1. Interview for the job-to-be-done: the task, three real phrasings the user would type to ask for it, available inputs, the artifact that means "done", and what must never happen.
2. Choose the slug: lowercase, hyphenated, specific (`api-changelog`, not `helper`); check `skills/` for collisions.
3. Write the description before the body — it is the trigger. Third person, capability first, then one "Use for ..." or "Use when ..." cue built from the nouns in step 1. Hard limit 100 characters in this repo: Claude Code lists every installed skill's description inside one shared budget and drops the least-used ones when it overflows.
4. Write the body in this repo's format: `# Name — Role`, quoted tagline, `## When to use` (ending with `- Typical requests:` quoting the phrasings from step 1), `## Workflow` (5–9 executable steps), `## Output format` (code-block template), `## Quality bar` (checkboxes), `## Example`.
5. Save to `skills/<slug>/SKILL.md` — directory name must equal frontmatter `name`, exactly.
6. Trigger-test with five paraphrased asks: a synonym rewrite, a vague version, a jargon version, an adjacent-but-different task (must NOT fire), and the exact phrase. Judge each against the description alone.
7. Iterate the description until at least 4/5 positives fire and the negative stays quiet — widen with user vocabulary, narrow with distinguishing nouns.
8. Dry-run the workflow once end to end; rewrite any step that needed unstated context.

## Frontmatter contract

```
---
name: <slug>            # must equal the directory name, lowercase-hyphenated
description: <capability + one "Use for ..." cue in user vocabulary; third person; at most 100 chars>
---
```

Body sections, in order: title with role, tagline quote, When to use, Workflow, Output format, Quality bar, Example.

## Trigger-miss failure modes

- Describes implementation, not the job — "uses Playwright" instead of "browser-tests your app". Users ask for jobs.
- No user vocabulary — the description names the mechanism, and `## When to use` quotes no real request.
- Too generic — collides with sibling skills and the wrong employee shows up.
- Over 100 characters — the listing budget is shared, so a long description costs another skill its place.
- First-person or imperative voice — reads like instructions, not a capability index.

## Output format

```
skills/<slug>/SKILL.md   (created)

Trigger test:
| Ask (paraphrase) | Should fire | Fired |
|---|---|---|
| <synonym rewrite> | yes | yes |
| <vague version> | yes | yes |
| <jargon version> | yes | yes |
| <adjacent task> | no | no |
| <exact phrase> | yes | yes |

Score: 5/5 — shipped
```

## Quality bar

- [ ] `name` equals the directory slug, exactly
- [ ] Description is third person, at most 100 chars, and built from words users say
- [ ] `## When to use` ends with `- Typical requests:` quoting real phrasings
- [ ] Workflow steps are executable with zero unstated context
- [ ] Output format is a copy-paste template, not a description of one
- [ ] Trigger test scores at least 4/5 and the adjacent negative stays quiet
- [ ] Example shows one real ask and the artifact it produced

## Example

Ask: "Turn our release-notes ritual into a skill."

Produced: `skills/release-notes/SKILL.md` — the description "Release notes from merged changes. Use for changelogs."; "write the release notes", "what changed this sprint", and "draft the changelog" quoted under When to use; a 7-step workflow from `git log` to published notes; trigger test 5/5, with the adjacent ask "write API docs" correctly staying quiet.
