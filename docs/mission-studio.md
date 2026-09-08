# Optional mission recipes

Mission Studio is an optional recipe desk inside Claude, Inc. Start an arbitrary
founder project through the [company workspace](project-workspace.md); use a
recipe when it fits a particular piece of that work.

Mission Studio compiles a brief into an ordered plan and a prompt containing the
selected employees' full manuals. Each recipe names the handoffs, deliverables,
requested evidence, and final reviewer. You run the resulting prompt in an
assistant of your choice.

## Open the Studio

[Try Mission Studio](https://alebgl77.github.io/claude-inc/missions.html)

1. Download and extract the repository ZIP, or clone the repository.
2. Open `studio/missions.html` directly in a browser. Keep the `studio` files together.
3. Choose a recipe and edit its example brief.
4. Inspect the handoffs and selected manuals, then copy or download the prompt.

The browser app needs no build, package installation, API key, Python, or server.
Its assets and bundled manual content are local. You can also download the plan
as Markdown or export a template-only SVG mission card.

The context comparison counts unique selected employee manuals and their UTF-8
byte size against all 50 employee manuals. Reusing an employee across stages does
not add another copy. Bytes are not tokens, prices, or a prediction of an
assistant's total context use.

## Compile from the terminal

Mission commands require Python 3.9+ and use only its standard library. Existing
`company` commands keep their Bash requirements and do not acquire a Python
dependency. Install the `company` CLI through the existing repository installer
to use:

```bash
company missions
company mission launch --brief "Launch my invoicing app for freelancers"
company mission launch --brief "Launch my invoicing app for freelancers" --format json
company mission launch --brief "Launch my invoicing app for freelancers" --format prompt
```

`markdown` is the default format. Use it to inspect the plan, `json` for structured
output, and `prompt` for the full brief and employee manuals. Omitting `--brief`
uses the recipe's example brief; replace it before asking an assistant to work on
your project. An explicit blank brief is rejected. Briefs are limited to 8,000
UTF-8 bytes; tabs and line breaks are allowed.

From a clone on Windows, these commands need no Bash or `company` installation:

```powershell
python skills/chief-of-staff/scripts/mission.py list
python skills/chief-of-staff/scripts/mission.py show launch --brief "Launch my invoicing app for freelancers" --format prompt
```

The same direct Python commands work on macOS and Linux; use `python3` if that is
your Python 3 executable. To save a result, redirect stdout to a file:

```bash
company mission launch --brief "Launch my invoicing app for freelancers" --format prompt > launch-prompt.md
```

Mission commands only print to stdout. They never invoke an assistant or engine,
even if one is installed or `CLAUDE_INC_ENGINE` is set, and they do not read stored
team profiles. This differs from department commands such as `company dev`,
which can invoke an installed engine.

## What a plan can tell you

A recipe assigns work and asks for evidence. It does not execute tasks, inspect
your project, enforce verification, or demonstrate completed work. The prompt
asks the executing assistant to report each check as `PASS`, `FAIL`, or `NOT RUN`
with actual evidence. Unknown or unperformed checks must stay `NOT RUN`.

The final reviewer is a separate assignment within the plan, not an independent
service. Review the generated output and its evidence yourself before relying on
it. A prompt alone cannot guarantee that an assistant follows the instructions.

## Privacy and sharing

The Studio makes no network calls and has no telemetry or browser persistence.
Your edited brief stays in page memory until you close or reload the page. The
compiler does not save it or access stored team profiles.

- Copied prompts and downloaded prompts or plans include your brief. Clipboard
  contents and saved files remain wherever you put them; pasting into an
  assistant sends the content to that assistant under its own data policy.
- A preset URL selects a built-in recipe. It does not include your edited brief.
  On a hosted copy of the Studio, that URL can be shared with other people.
  Opened through `file://` or a localhost preview, the Studio explains that it is local and copies
  the recipe name instead; recipients need their own copy.
- The exported SVG card describes the recipe template. It omits your brief and
  does not claim that the mission's work or checks have been completed.

## Author a recipe or update manuals

The source of truth for recipes is
[`skills/chief-of-staff/references/missions.json`](../skills/chief-of-staff/references/missions.json).
The compiler lives in
[`skills/chief-of-staff/scripts/mission.py`](../skills/chief-of-staff/scripts/mission.py).
Recipes refer to existing employee manuals rather than creating new employees.

When changing a recipe, keep its handoffs ordered and its deliverables concrete.
Give checks observable evidence requirements and retain a distinct final
reviewer assignment. Do not turn requested checks into claims of completed work.

The tracked `studio/missions.js` bundles compiled data and employee manuals so
the browser does not have to fetch files. After changing the catalog, roster,
manuals, or compiler output, rebuild it from the repository root:

```bash
python scripts/build_studio.py
```

Commit the source changes and regenerated dataset together. Do not hand-edit
`studio/missions.js`. Verify with Python 3.9+ and a Node.js LTS release; no
third-party packages are required:

```bash
python -m unittest discover -s tests -p test_missions.py
node --test tests/test_studio.js
python scripts/build_studio.py --check
python scripts/validate.py
```

`--check` fails when the tracked dataset is stale. The independent
`missions.yml` workflow runs these checks on Linux, macOS, and Windows. The
existing compliance workflow continues to cover the rest of the company.
