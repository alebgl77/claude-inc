# The routing desk

This guide describes the unreleased `1.6.0-dev.0` source on `main`.

The routing desk answers one question: who in the company should handle this
request, and with which manuals? An assistant makes the decision. A local
helper gives it a knowledge base to decide from and checks the result against
the canonical roster. The helper never calls a model.

| Part | Where | Role |
|---|---|---|
| Routing desk | `agents/router.md`, registered as `router` (`orgware:router` in the plugin) | The assistant's charter: how to route and the decision contract |
| Knowledge base | compiled by `skills/chief-of-staff/scripts/route.py` | What the desk knows about departments, manuals, playbooks and boundaries |
| Decision check | `company route check` | Accepts or rejects a decision against the roster |
| Local memory | `.claude/company-routing.json` in the working folder | How earlier routes in this folder ended |

The desk is not a department or an executive. It owns no task, reviews no work,
and has no employees. The company still has nine departments, 64 manuals, and
peer CEO, CTO, and CAIO executives.

## Ask the desk

```bash
company route "Our trial page converts at 1.8% and the new pricing needs a legal check"
company route "Our trial page converts at 1.8% and the new pricing needs a legal check" --print | gemini
```

`company route` composes the desk's charter and a routing packet for that
request, then runs your configured assistant, or prints the prompt with
`--print`. In Claude Code, the CEO can delegate the same question to the
`router` agent, which reads the packet in its own context and returns only the
decision.

The request travels as literal data on standard input. The helper reads at most
8,000 UTF-8 bytes and rejects control characters. Text inside a request cannot
change the desk's rules.

## The knowledge base

The knowledge base is compiled at every call from the files that are actually
installed, so it cannot drift from them. There is no generated copy to refresh.

| Source | What the desk learns |
|---|---|
| Each manual's frontmatter and `## When to use` | A one-line summary, when to use it, and the example requests it quotes |
| Each department charter's `## Your team` table | The role of each employee and when to hire them |
| Prose in the charters that points to employees with `→` | The department's own chains and routing examples |
| The CEO manual's routing table and the notes beside it | What each department is hired for, and the boundaries between them |
| The executive charters | When the CTO or CAIO is consulted |
| The mission catalog | Optional staged blueprints for standard outcomes |

`company route kb` prints the compiled knowledge base as JSON, with a SHA-256
digest of its content. On this source at 2026-11-11 it held 64 manual cards and
405 example requests quoted in the manuals.

To teach the desk something, edit the manual or charter it comes from. A new
example request belongs on the `- Typical requests:` line of that manual's
`## When to use`.

## The routing packet

`company route packet` prints what the assistant reads, with the request on
standard input:

1. A **shortlist** of the manuals whose words best match the request, each with
   its summary, when to hire it, when to use it, and typical requests.
2. The **complete index**: every department, manual, and staff skill on one
   line each.
3. The **department playbooks**, the **boundaries**, and the **mission recipes**.
4. The **local routing memory** for this folder.
5. The request, between explicit data delimiters.

The shortlist is a deterministic word match (BM25 with light stemming). It is
English-centric and misses paraphrases, which is why the complete index is
always present: the shortlist can expand a candidate, but it can never hide one.
A request in French gets a thin shortlist and the same full index.

`--top N` sets the shortlist length from 1 to 12; the default is 6. A packet is
about 18,000 bytes on this source. Quote the request when you use
`company route "<request>"`: a first bare word such as `check` or `packet` is
read as a helper operation.

If the routing memory cannot be read safely, the packet says so and the desk
routes without it. Recording an outcome and `company route memory` stop with an
error instead.

## The decision

The desk replies with one JSON object:

```json
{
  "version": 1,
  "kbDigest": "<digest printed at the top of the packet>",
  "mode": "company",
  "class": "fix-trial-conversion",
  "assignments": [
    {"department": "marketing", "skills": ["cro", "copywriting"], "task": "Audit the trial page and rewrite the sections the audit flags", "dependsOn": []},
    {"department": "legal", "skills": ["compliance-check"], "task": "Check the new pricing claims and terms before the page ships", "dependsOn": [1]}
  ],
  "executives": [],
  "confidence": "medium",
  "rationale": "Marketing owns conversion audits and copy; Legal owns the pre-launch check of the claims.",
  "alternatives": [],
  "questions": []
}
```

`company route check` reads a decision on standard input or from
`--decision-file PATH` and applies these rules:

| Field | Rule |
|---|---|
| `mode` | `direct`: exactly one assignment and no executive. `company`: two or more assignments, or one with an executive. `clarify`: one to three questions. `decline`: no assignment. |
| `assignments` | At most nine. Each names a canonical department, one to six manuals from that department or from staff, a task of at most 600 bytes, and the earlier assignment numbers it depends on. |
| `executives` | `cto` and `caio` only. They are consulted and never own an assignment. |
| `class` | Two to four lowercase hyphenated tokens that name the kind of job, such as `write-landing-copy`. |
| `confidence` | `high`, `medium`, or `low`. A `low` route must name at least one alternative. |
| `alternatives` | At most three, each with a department, manuals, and why it would be the better route. |
| `kbDigest` | Must equal the current knowledge base digest. A stale digest means the company changed since the packet was printed. |

A rejected decision exits with status 1 and lists every problem on standard
error. An accepted one prints the decision with its staffing: for each
assignment, the charter and manual paths, the size of the selected manuals next
to the size of all six, and an argument array for the matching department
prompt. Byte counts compare files. They are not token or cost estimates.

The check establishes that a decision fits the roster and the contract. It does
not establish that the route is the best one.

## Load only what the route selected

```bash
company marketing --skills cro,copywriting "Audit the trial page and rewrite the sections the audit flags"
```

`--skills` composes a department prompt with the charter and only the listed
manuals, which must belong to that department or to staff. Without it, the
prompt holds all six manuals as before. The charter still describes every
employee, so the department can say when the task needs one that was not loaded.

In a project workspace, the same departments and manuals feed task contracts
and a harness plan's `skills` selection. The harness applies the same
membership rule.

## Routing memory

```bash
company route record --decision-file decision.json --outcome accepted
company route record --decision-file decision.json --outcome rerouted
company route memory
```

Record `accepted` when the founder took the routed work, and `rerouted` when it
had to go elsewhere. The memory is one small JSON file in the working folder,
`.claude/company-routing.json`. It holds request classes, routes, and two
counters per route. It holds no request text.

| Standing | Meaning |
|---|---|
| `established` | At least three accepted uses and no reroute |
| `unproven` | Fewer than three accepted uses and no reroute |
| `mixed` | Both accepted and rerouted |
| `avoid` | Rerouted and never accepted |

Three accepted uses with no reroute is the smallest count that gives 80%
confidence that the route is accepted at least half the time (the one-sided
exact binomial bound is 0.585). The desk follows an `established` route unless
the request differs in a way it can name, and never proposes an `avoid` route
for that class. The other two standings are evidence, not rules.

The memory is a learning aid for one folder, not a second project record. It
does not replace task contracts, reviews, or the founder's decisions. Limits are
256 request classes and eight routes per class; reaching one is an error, and
nothing is dropped. Writes use a fail-fast lock, refuse linked paths, and
replace the file atomically. Class names are chosen by the assistant: the
charter tells it never to use a person, company, or product name.

## Measure it

```bash
company route eval                 # shortlist self-check
company route eval --dataset       # labelled requests as JSON Lines
company route eval --score answers.jsonl
```

`eval` holds each example request out of its own card and checks whether the
shortlist still finds that manual. On this source, measured 2026-11-11: 364 of
405 phrases within the default six (0.90) and 284 first. This measures the word
match only.

**How well an assistant routes has not been measured.** To measure it, export
the labelled requests with `--dataset`, run your assistant on each one, and
save one `{"request": ..., "decision": ...}` object per line. `--score` reports
the share of requests whose expected manual and department appear in the
decision, with exact 95% binomial intervals. Those requests are quoted in the
packet, so the result is in-sample; paraphrase them for a stricter test. Each
run is a model call that your assistant bills.

## Limits

- The desk proposes staffing. It grants no permission to publish, send, buy,
  sign, install, or access anything, and the CEO or founder can overrule it.
- A valid decision can still be a poor route. Only outcomes and measurement say
  otherwise.
- The helper needs Python 3.9+. Without it, the CEO routes from the manual's
  routing table and says the decision was not checked.
- A historical eight-department workspace keeps its saved roster. The desk can
  name Growth; such a workspace still cannot give Growth a task.
- Routing memory is local, unsigned, and editable by the account that owns the
  folder. It is evidence for the desk, not an audit trail.

## Verify changes

```bash
python -m unittest discover -s tests -p test_route.py
python scripts/validate.py
```
