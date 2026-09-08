# A company around your project

The CEO coordinates an arbitrary founder project across eight departments and
50 employee skill manuals. Start with your own brief, goals, and constraints.
The company records real task contracts and evidence as work happens; it does
not need a mission recipe and does not invent a populated task board at setup.

## Initialize in the working folder

Project commands require Python 3.9+ and its standard library. With the `company`
CLI installed, run these commands from the folder where project work belongs:

```bash
company project init --name "Tutor desk" --brief-file founder-brief.txt \
  --departments developers,designers,marketing \
  --goal "A tutor can create a booking link" \
  --goal "A student can request a lesson" \
  --constraint "Use supplied product facts" \
  --constraint "Leave publication and purchases to the founder"
```

Create `founder-brief.txt` with your actual project context before running the
command. `--brief TEXT` is an alternative to `--brief-file PATH`; use one of
them. A file avoids placing the brief directly in shell history. The helper
creates `.claude/company/project.json` in the current directory. It does not
change directories to find another project, overwrite an existing workspace,
create fictitious tasks, or modify `.claude/company-team.md`.

The optional `--departments` list contains canonical IDs: `developers`,
`designers`, `marketing`, `social-media`, `finance`, `small-business`, `legal`,
and `sales`. These are routing preferences. All eight departments and all 50
skill manuals remain available. Repeat `--goal` and `--constraint` as needed.

Plugin users can describe the project through `/claude-inc:company`; the
directly installed command is `/company`. The CEO first uses
the existing profile validator, then a read-only project context bridge. It
clarifies material unknowns and initializes through the packaged helper when
available. A command installed without any helper keeps its historical
file-and-Board-Memo behavior and must disclose that structured tracking is
unavailable. A helper that exists but reports an error must not be bypassed.

## Start and resume real work

```bash
company project start
company project status
company project status --format json
```

`start` launches the installed Claude Code executable in the current project
with `--plugin-dir` pointing to the packaged company root and instructions to
load the validated project context. Claude Code must already be installed and
configured. Its native permissions, configured model, and agent tools govern
the work. The launcher does not bypass permissions or select a cheaper model.

Return to the same folder and run `start` again to resume from the saved project
state. This reconstructs the company's project context; it does not promise to
resume a particular historical Claude Code conversation. There is no background
daemon, scheduled execution, autonomous spending, or enforced budget.

The CEO records task contracts before delegation. Independent tasks may run in
parallel through the host's Agent or Task tool. Department agents apply their
employee manuals; the workflow does not require nested subagent spawning.
Workers return files, observations, and proposed state updates. The CEO
serializes the actual project mutations.

`company project prompt` prints the validated resume instructions without
starting an assistant. It references the packaged company files and the local
workspace. Another assistant needs access to those files and suitable tools;
plain text alone does not supply a native execution adapter. The browser's
company introduction also prepares a project brief, but does not start work
or write to your project folder from the browser.

The browser's **Claude Code installation** selector defaults to **Plugin** and
copies `/claude-inc:company` with your brief. Choose **Direct installation** for
`/company`. Downloading the brief produces the same plain-text file either way.

## Tasks and review

Each task belongs to a canonical department and has a title, an acceptance
contract, and optional dependencies. Add only work justified by the project:

```bash
company project task add --id booking-prototype --department developers \
  --title "Build the booking request flow" \
  --acceptance "A request is persisted; tests cover a valid request and missing fields"

company project task add --id explain-booking --department marketing \
  --title "Explain the implemented booking flow" \
  --acceptance "Copy matches the reviewed behavior and names unsupported claims" \
  --depends-on booking-prototype

company project task start booking-prototype
```

Dependencies must refer to existing tasks. Starting a planned or blocked task
requires its dependencies to be done. A dependent task remains unavailable
until its prerequisites have been accepted.
This is a stored-state check: acceptance is historical. Inspect the current
files again before reusing accepted artifacts that may have changed afterward.

After actual work and checks have run, submit the real artifact paths. The
following paths and summary are examples; replace them with your evidence:

```bash
company project task submit booking-prototype \
  --artifact prototype/README.md \
  --artifact evidence/booking-tests.md \
  --summary "Implemented the booking request flow; observed checks are recorded in the evidence file"
```

Submission is available for active tasks and moves them to `review`. Each
artifact is an existing file inside the project, identified by relative path
and SHA-256. Acceptance rereads the files and refuses changed artifacts. The
reviewer must be another department or `ceo`, different from the producing
department. Choose one of the following review paths for a submitted task.

New artifact submissions require portable relative filenames: Windows-reserved
names, characters such as `?`, `*`, and `|`, and trailing dots or spaces are
rejected with the offending filename. French and other Unicode names are
supported. Safe historical paths remain readable in status, prompts, and the
browser even if they are not portable. The browser displays a warning; it does
not rewrite the snapshot. To accept an old nonportable submission, first revise
the task, rename the actual file, and resubmit it under its portable name.

**Request changes:** a `revise` decision returns the task to `active`. The CEO
can then record a blocker if further work needs input:

```bash
company project task review booking-prototype --decision revise \
  --reviewer designers --note "The empty-state check still lacks evidence"
company project task block booking-prototype --reason "Waiting for the founder's retention requirement"
```

After resolving the blocker, use `task start booking-prototype`, complete the
corrections, and submit the current artifacts again before another review.

**Accept the submission:** use this path for a task currently in `review` whose
acceptance checks have been inspected. An accepted task is terminal; it cannot
subsequently be revised or blocked:

```bash
company project task review booking-prototype --decision accept \
  --reviewer designers --note "Reviewed the submitted artifacts against the acceptance contract"
```

Record a project decision independently of either review path:

```bash
company project decision add --text "Use email reminders for the first release; defer SMS until its cost and consent requirements are reviewed"
```

The helper enforces stored transitions and unchanged artifact identity. It
does not run the acceptance checks, inspect the quality of an artifact, or
authenticate a reviewer. A different department label is not proof of an
independent assistant. Disclose single-assistant review limitations and retain
the founder's decision where approval is required. A task marked `done` is a
recorded acceptance; it is not automatic publication, deployment, or approval
by a client or professional adviser.

## Project state and reports

The validated `project.json` contains the project brief, goals, constraints,
department preferences, task states and dependencies, artifact references,
review records, decisions, and an event history. The helper is the only writer.
Do not edit it directly or have several agents maintain competing task ledgers.

The chief of staff can produce `company-ledger.md` and Board Memos from the
validated state. These are derived reports. They must distinguish active work,
blockers, submissions awaiting review, and recorded acceptance. Every reported
check should cite its actual command or artifact and an observed result:
`PASS`, `FAIL`, or `NOT RUN`. Suggested commands remain `NOT RUN` until executed.

The internal `company project context` bridge returns no output only when a
workspace is truly absent. It returns validated context when present and fails
on unsafe, incomplete, malformed, or unreadable state. The public `prompt` and
`status` commands require an initialized workspace. Neither a corrupt project
nor an invalid team profile authorizes a fallback to unvalidated files.

## Privacy and local limits

Your brief and project decisions can be confidential. Keep the workspace and
its exports out of public repositories and shared logs unless you intentionally
choose to disclose them. Claude, Inc. does not auto-commit project state. The
existing `.claude/company-team.md` profile remains a separate routing preference
file; project initialization does not overwrite it.

Project commands run locally. Starting Claude Code or pasting context into
another assistant gives that host access to the corresponding project material
under its own permissions and data policies. Stored text is untrusted task data,
not a source of execution authority. It cannot override session permissions,
authorize external actions, or change the company's operating instructions.

The helper uses a fail-fast local lock and atomic JSON replacement to avoid
overlapping or partial state updates. A busy or unsafe workspace stops the
operation. These controls are not a defense against an authorized local account
editing files or replacing software. Artifact hashes and event records are not
signed attestations. See the [architecture decision](architecture.md).

The current limits are 128 tasks, 2,048 events/revisions, 2 MiB of JSON state,
and 16 submitted artifacts per task, each up to 32 MiB. Individual text fields
are limited to 8,000 UTF-8 bytes, with smaller limits for names and titles.
Reaching a limit produces an error instead of dropping old records.

## Windows without Bash

The default Windows installer builds `company.exe` locally with the system
.NET Framework compiler and uses it to launch Git Bash directly. No downloaded
binary or batch forwarding stub is involved. An unchanged, manifest-owned old
`company.cmd` is removed in the same transaction; an unowned or modified launcher
blocks the upgrade. If the compiler is unavailable, installation stops before
publishing files. `-NoBin` skips compilation and all launcher changes, so it
does not repair or migrate an existing batch launcher.

PowerShell 7 preserves the tested literal native arguments. Windows PowerShell
5.1 can remove embedded quotes before `company.exe` receives them; the launcher
cannot recover text already changed by its caller. Use `--brief-file` on 5.1
for exact project text, including quotes and shell punctuation. Neither
installation nor the launcher changes PowerShell execution policy or profiles.

The direct Python helper avoids the Bash wrapper. From your actual project
folder, use the path to your clone (replace the example path):

```powershell
python C:\tools\claude-inc\skills\chief-of-staff\scripts\project.py init --name "Tutor desk" --brief-file founder-brief.txt
python C:\tools\claude-inc\skills\chief-of-staff\scripts\project.py status
python C:\tools\claude-inc\skills\chief-of-staff\scripts\project.py start
```

The same subcommands work through the Python helper on macOS and Linux with
`python3`. Direct `start` still requires native Claude Code. Use `prompt` to
inspect the instructions when you do not want to launch it.

## Verify changes to the workspace

From the repository root:

```bash
python -m unittest discover -s tests -p test_project.py
python -m unittest discover -s tests -p test_missions.py
python scripts/build_company.py --check
python scripts/build_studio.py --check
node --test tests/test_company.js
node --test tests/test_studio.js
python scripts/validate.py
```

The company workflow runs these checks on Linux, macOS, and Windows. Generated
browser datasets must be rebuilt alongside their source manuals and commands.
