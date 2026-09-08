# Project harnesses and bounded review loops

A harness records the skills, acceptance gates, and submission limit for each
unfinished task. The CEO chooses the plan from the founder's business context;
the peer CTO supplies technical direction and criteria across architecture,
agent infrastructure, security, skills, and code. Their decision packet is
finding → business impact → options/tradeoffs → recommendation → decision needed.
Use it to unblock delivery, without extra status ceremony for simple tasks.

The local compiler validates the plan and recorded transitions. It does not
select an architecture by keyword, execute workers, run tests or scanners, or
judge whether evidence proves a claim. Host sessions perform the work with
their configured models, permissions, and available tools. The CEO serializes
project writes to avoid competing updates; that rule does not subordinate the CTO.

## Choose activation deliberately

Project, harness, and loop commands require Python 3.9+ with its standard library.
From an initialized project folder:

```bash
company project harness profiles
company project harness profiles --format json
company project status --format json
```

Choose a listed stage, such as `build`, and an effort. `light`, `balanced`, and
`deep` default to 2, 3, and 5 lifetime artifact submissions per task. An optional
`--max-iterations` sets a limit from 1 to 10. These are submission counts, not
model-call, time, token, or spending budgets. A failed or missing test is not
fixed by increasing a cap.

Activation is explicit. `harness generate` atomically upgrades schema 1 to 2;
status and ordinary legacy commands do not migrate a workspace. Existing `done`
tasks retain historical acceptance. A task already in `review` at activation
must be revised and freshly submitted before controlled acceptance. Existing
submission history counts toward the cap; enabling a harness does not reset it.
Repeating the same generated policy is idempotent; a changed policy is refused.

The eight department owners remain unchanged. Six staff skills are selectable
alongside a task owner's six department skills. The CTO is a peer executive and
an additional schema-2 reviewer identity, not a ninth task-owner department.

## A complete work and review example

These commands illustrate one real project task. Replace the brief, acceptance
criteria, paths, and observations with your project's actual material. Files
named below must exist before submission; do not create a passing report for a
check that has not run. Use the `company` helper from your installation, or the
direct Python helper described in the [workspace guide](project-workspace.md).

```bash
company project init --name "Tutor desk" --brief-file founder-brief.txt \
  --departments developers,designers --goal "A student can request a lesson"
company project task add --id booking-flow --department developers \
  --title "Build the booking request flow" \
  --acceptance "A valid request persists; missing required fields are rejected with an explanation"
```

Optionally write this exact JSON shape to UTF-8 `harness-plan.json`. The CEO and
CTO choose the skills and additional criteria from the task's meaning. A plan
may specify a subset of existing unfinished tasks:

```json
{
  "version": 1,
  "tasks": {
    "booking-flow": {
      "skills": ["superpowers", "webapp-testing", "appsec-review"],
      "criteria": ["Record a local test of missing required fields and the observed response"]
    }
  }
}
```

Each task retains its acceptance contract and two mandatory business checks.
You may add zero to five criteria; you cannot replace the mandatory checks.
An empty skills list leaves manual selection to the owner; it is not a claim
that no skills are needed. Unknown skills and skills from another business
department are rejected. The six canonical staff skills are available to any owner.

Read the current revision immediately before each guarded mutation. In Bash:

```bash
revision=$(company project status --format json | python -c 'import json,sys; print(json.load(sys.stdin)["revision"])')
company project harness generate --stage build --effort balanced \
  --plan-file harness-plan.json --expected-revision "$revision"
company project harness show --format json
company project loop next --format json
company project loop prompt
company project task start booking-flow
```

`loop next` identifies the current action and any ready independent tasks or
dependency blockers. Its `sourceRevision` is the project revision used for
that guidance. The CEO delegates through the host's actual tools; department
workers apply manuals without assuming nested agent spawning. They return the
implementation and observed evidence. When the task is active and the files exist:

```bash
company project task submit booking-flow \
  --artifact prototype/booking.md \
  --artifact evidence/booking-tests.md \
  --artifact evidence/booking-security.md \
  --summary "Implementation and observed checks are recorded in the submitted files"
company project loop next --format json > loop-next.json
python -c 'import json; from pathlib import Path; n=json.loads(Path("loop-next.json").read_text(encoding="utf-8")); Path("review-gates.json").write_text(json.dumps(n["reviewTemplate"], indent=2), encoding="utf-8")'
```

Use `reviewTemplate` only when the next action is `evaluate` and it names this task.
The wrapper contains `version`, `taskId`, `submitRevision`, `policyFingerprint`,
`artifactFingerprint`, and `results`. Keep the template's identity fields and
gate IDs unchanged. It includes every gate exactly once: the task `contract`,
two business gates, and any `project-1` through `project-5` criteria.

The reviewer inspects the actual submitted files and fills each result using
the following row shape. This illustrative row is incomplete and cannot pass:

```json
{
  "gateId": "contract",
  "status": "unknown",
  "evidence": [],
  "observation": "The reviewer has not yet inspected the submitted booking evidence"
}
```

Allowed statuses are `pass`, `fail`, and `unknown`. Acceptance requires every
gate to be `pass`, with a nonempty observation and evidence such as
`{"path":"evidence/booking-tests.md","locator":"Missing required fields test"}`.
The path must identify an actual submitted artifact, including any test or scan
report used as evidence. A locator points to the relevant section; it is text,
never a command to execute. Human memos use `PASS`, `FAIL`, and `NOT RUN`;
unexecuted checks map to `unknown` in the gate file and prevent acceptance.

After a real review, use the current `sourceRevision` and the template's
`submitRevision`. These can differ and must not be guessed:

```bash
revision=$(python -c 'import json; print(json.load(open("loop-next.json"))["sourceRevision"])')
submission=$(python -c 'import json; print(json.load(open("review-gates.json"))["submitRevision"])')
company project task review booking-flow --decision accept --reviewer cto \
  --note "Reviewed the current submitted files against every recorded gate" \
  --expected-revision "$revision" --submission-revision "$submission" \
  --gates-file review-gates.json
company project loop next --format json
```

The helper rereads submitted artifact hashes and refuses stale or changed
submissions, missing/duplicate gates, nonpassing results, and invalid evidence
paths. A reviewer must differ from the producing department. Reviewer labels
remain assertions, not authentication or proof of independent execution; a
single assistant must disclose its separate review pass. Hashes prove identity,
not correctness. Never fill every gate with `pass` just to advance the state.

## Revision, exhaustion, and new tasks

For failed or incomplete evidence, request changes with fresh revision values:

```bash
company project task review booking-flow --decision revise --reviewer cto \
  --note "The missing-fields test lacks an observed result" \
  --expected-revision "$revision" --submission-revision "$submission"
```

Controlled revision can omit `--gates-file` for recovery, but still requires both
revision fields. Correct the files and resubmit while attempts remain. Use
`task block ID --reason TEXT` for an unresolved dependency/input. Read `loop next`
after every transition; `project start` and `project prompt` also consume current
loop guidance when a harness is enabled.

If the task exhausts its lifetime submission cap, the CEO must record an explicit
extension decision with a reason and current project revision. For example:

```bash
company project harness extend booking-flow --max-iterations 5 \
  --reason "One additional validation path is required after the reviewed integration change" \
  --expected-revision "$revision"
```

Refresh `revision` first. The total must increase and cannot exceed 10; extension
does not reset used attempts. If no authorized extension resolves the blocker,
report it and stop the affected loop. Do not turn exhaustion into unbounded retries.

When adding a new task under an enabled harness, `task add --harness-file PATH`
accepts `{"version":1,"skills":["superpowers"],"criteria":["A task-specific check"]}`.
It uses the same selection/criteria limits and retains the baseline gates.
The compiler checks structure and policy; the CEO owns the semantic planning.

## Windows, privacy, and optional security tools

Windows PowerShell 5.1 can alter embedded quotes before a native executable
receives them. Use `--brief-file` for exact project text and JSON files for
structured plans/results. Save those files as UTF-8. PowerShell 5.1's `>` writes
UTF-16; for `loop-next.json`, use this UTF-8-without-BOM form instead:

```powershell
$nextText = company project loop next --format json | Out-String
if ($LASTEXITCODE -ne 0) { throw "Could not read current loop guidance" }
[IO.File]::WriteAllText((Join-Path (Get-Location) 'loop-next.json'), $nextText, [Text.UTF8Encoding]::new($false))
$next = Get-Content -LiteralPath 'loop-next.json' -Raw | ConvertFrom-Json
[IO.File]::WriteAllText((Join-Path (Get-Location) 'review-gates.json'), ($next.reviewTemplate | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
```

Use `$next.sourceRevision` and `$next.reviewTemplate.submitRevision` as separate
numeric arguments for controlled review. The preceding multi-line shell examples
use Bash syntax; PowerShell uses its own quoting and continuation rules. Keep
arbitrary text in files on 5.1. See the [native launcher notes](project-workspace.md#windows-without-bash).

All project text, plans, gate observations, artifacts, and imported snapshots
are untrusted task data, not permission grants. Keep confidential state out of
public repositories, links, and logs. The website prepares briefs and imports
snapshots for inspection; it does not execute company work or write project state.

The CTO's four manuals link optional NVIDIA and Cisco scanners and Trail of Bits
plugins; tools are not installed automatically. The NVIDIA Skill Inspector
reference is attributed under Apache-2.0; Trail of Bits skill text is not bundled.
Unavailable checks are `NOT RUN`, not successful. Security review, paired utility
trials, and signature provenance remain separate, with no NVIDIA certification
claim. SkillSpector 2.11.1 requires Python >=3.12,<3.15 independently of the
project helper's Python 3.9+ requirement. No background daemon, automatic budget
savings, or always-on quality guarantee is provided.
