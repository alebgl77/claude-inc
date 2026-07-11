---
name: skill-creator
description: Authors new SKILL.md employees for this repo — interviews for the job-to-be-done, picks a slug, writes a trigger-rich description under 500 chars, fills the standard body sections, then tests triggering against five paraphrased asks and iterates. Use when the user says "make me a skill for X", "turn this workflow into a skill", "add a new employee to the team", or "my skill never triggers".
---

# Skill Creator — Skill Smith

> "Build your own skills"

## When to use

- "Make me a skill for <recurring task>" — anything you've done three times deserves a SKILL.md
- "Turn this workflow into a skill" after a session that went well
- "Add a new employee to <department>" in this repo
- "My skill never triggers" / "the wrong skill fires" — description surgery
- Standardizing a process so the whole team runs it the same way

## Workflow

1. Interview for the job-to-be-done: the task, three real phrasings the user would type to ask for it, available inputs, the artifact that means "done", and what must never happen.
2. Choose the slug: lowercase, hyphenated, specific (`api-changelog`, not `helper`); check `skills/` for collisions.
3. Write the description before the body — it is the trigger. Third person, capability first, then "Use when ..." quoting the phrasings from step 1. Hard limit 500 characters.
4. Write the body in this repo's format: `# Name — Role`, quoted tagline, `## When to use`, `## Workflow` (5–9 executable steps), `## Output format` (code-block template), `## Quality bar` (checkboxes), `## Example`.
5. Save to `skills/<slug>/SKILL.md` — directory name must equal frontmatter `name`, exactly.
6. Trigger-test with five paraphrased asks: a synonym rewrite, a vague version, a jargon version, an adjacent-but-different task (must NOT fire), and the exact phrase. Judge each against the description alone.
7. Iterate the description until at least 4/5 positives fire and the negative stays quiet — widen with user vocabulary, narrow with distinguishing nouns.
8. Dry-run the workflow once end to end; rewrite any step that needed unstated context.

## Frontmatter contract

```
---
name: <slug>            # must equal the directory name, lowercase-hyphenated
description: <capability + "Use when ..." with real user phrases; third person; under 500 chars>
---
```

Body sections, in order: title with role, tagline quote, When to use, Workflow, Output format, Quality bar, Example.

## Trigger-miss failure modes

- Describes implementation, not the job — "uses Playwright" instead of "browser-tests your app". Users ask for jobs.
- Zero quoted user phrases — the matcher has nothing to catch.
- Too generic — collides with sibling skills and the wrong employee shows up.
- Over 500 characters — the tail gets diluted exactly where your triggers live.
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
- [ ] Description is third person, under 500 chars, and quotes real user phrasings
- [ ] Workflow steps are executable with zero unstated context
- [ ] Output format is a copy-paste template, not a description of one
- [ ] Trigger test scores at least 4/5 and the adjacent negative stays quiet
- [ ] Example shows one real ask and the artifact it produced

## Example

Ask: "Turn our release-notes ritual into a skill."

Produced: `skills/release-notes/SKILL.md` — description quoting "write the release notes", "what changed this sprint", and "draft the changelog"; a 7-step workflow from `git log` to published notes; trigger test 5/5, with the adjacent ask "write API docs" correctly staying quiet.
