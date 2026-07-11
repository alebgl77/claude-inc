---
name: context7
description: Anti-hallucination protocol for library APIs — resolves the exact installed version from the lockfile, fetches current official docs (Context7 MCP if installed, web fetch otherwise), quotes the doc before writing any code, and pins the version in output. Use when code touches a fast-moving library (Next.js, React, LangChain, Prisma, Tailwind), when the user says "check the actual docs" or "what's the current API for X", or after any deprecation or breaking-change error.
---

# Context7 — Docs Fetcher

> "Live library docs"

Trained knowledge ages; your dependencies don't wait. The docs are the source of truth — memory is only a hint.

## When to use

- Writing code against fast movers — Next.js, React, LangChain, Prisma, Tailwind — where trained knowledge is stale by default
- "Check the actual docs before you write this" / "is this still the right API in v15?"
- "This worked in v4 but breaks in v5" — any deprecation warning or breaking-change error
- Choosing between API generations — "app router or pages router way?"
- Before adding a dependency — verify the current install command and quickstart, not remembered ones

## Workflow

1. List the libraries the task touches and flag fast movers (any project with major releases in the past year).
2. Resolve the exact installed version from the lockfile — `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`, `uv.lock`, `Cargo.lock`, `go.sum`. Grep the lockfile itself; never trust manifest ranges or memory.
3. Fetch current docs for that version. Optional upgrade: with the Context7 MCP server installed, call `resolve-library-id` then `get-library-docs`. Otherwise WebFetch/WebSearch the official docs, changelog, and migration guide — official sources only.
4. Quote the relevant passage verbatim — signature, options, gotchas — before writing a single line of code.
5. Write the code against the quoted signature, exactly; no extra parameters from memory.
6. Pin the library and version in the output header; note any deprecations between installed and latest.
7. If lockfile and docs disagree (docs describe a newer API), surface it: ship code for the installed version plus the upgrade path.
8. If the doc page covers multiple versions, confirm the version selector matches the installed one before quoting.
9. No network at all? Say so loudly, mark the code UNVERIFIED, and list exactly which signatures must be checked before merge.

## Output format

```
Library: <name>@<exact version>   (source: <lockfile>)
Docs: <official URL or Context7 library ID>   (fetched <date>)

Doc quote:
> <verbatim excerpt covering every API surface used below>

Code:
<snippet that matches the quote>

Version notes: <deprecations, breaking changes, upgrade advice — or "none">
```

## Quality bar

- [ ] Version came from a lockfile, not a guess or a `^range`
- [ ] Doc passage quoted verbatim before code was written
- [ ] Code uses only the quoted, verified surface — zero from-memory APIs
- [ ] Library and version pinned in the output header
- [ ] Source is official (docs, changelog, repo) with fetch date recorded
- [ ] Docs-vs-lockfile disagreements surfaced with an upgrade path

## Example

Ask: "Add streaming to our LangChain chat endpoint."

Run: lockfile shows `langchain==0.3.14`; 0.3 docs fetched; quoted the `astream_events` signature and event schema; wrote the endpoint against it; flagged the deprecated alternative and the migration notes.

```
Library: langchain==0.3.14   (source: uv.lock)
Docs: python.langchain.com/docs/how_to/streaming   (fetched 2026-07-11)
Doc quote: > "astream_events(version='v2') yields event dicts with event, name, data"
Version notes: astream_log deprecated in 0.3; event payload keys renamed in 0.4
```

## Credits

Inspired by Upstash Context7.
