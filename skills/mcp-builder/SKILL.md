---
name: mcp-builder
description: Scaffolds and ships MCP servers in Python (FastMCP) or TypeScript (@modelcontextprotocol/sdk) — tools designed around workflows rather than raw endpoints, with model-guiding schemas and error messages, pagination, a direct-call test harness, and wiring into .mcp.json or claude mcp add. Use when the user says "build an MCP server for X", "wrap this API so Claude can call it", "add a tool to our server", or "connect Claude to our internal service".
---

# MCP Builder — Tool Wright

> "Wire up MCP servers"

A tool is UX for a model: obvious names, forgiving inputs, errors that say what to do next.

## When to use

- "Build an MCP server for <API or service>" — GitHub, Jira, a database, an internal REST API
- "Wrap this API so Claude can call it" / "connect Claude to our ticketing system"
- Adding, renaming, or hardening tools on an existing server
- A server's tools confuse the model — vague names, loose schemas, cryptic errors
- Choosing Python vs TypeScript for a new integration

## Workflow

1. Pick the stack. Python + FastMCP for speed and data-heavy work; TypeScript + `@modelcontextprotocol/sdk` when the target has a first-class npm client. Match the host repo's language when embedding.
2. Design around workflows, not endpoints. List the 3–7 jobs the model must do ("find overdue invoices", not "GET /invoices"); one tool per job; merge chatty endpoint pairs into single tools.
3. Name and specify. `verb_noun` tool names. Every input field gets a type, a description, an example, and an enum when the value set is closed. Required vs optional is explicit.
4. Write errors that teach. Each failure states what was wrong and what a valid call looks like — `expected date YYYY-MM-DD, got '3/4/25'` — never a bare stack trace or status code.
5. Paginate every list. `page_size` capped (default 20), `next_cursor` in the result, total count when cheap — nothing returns unbounded output.
6. Build a direct-call harness: a script that invokes every tool in-process, no MCP client involved, asserting on real responses. Run until green.
7. Wire it in — project `.mcp.json` entry or `claude mcp add <name> -- <command>` — then restart and smoke-test one live call from Claude Code.
8. Ship a README: tool list with one-line jobs, auth env vars, config snippet.
9. Iterate with the consumer: watch Claude use the tools on a real task; rename or re-scope anything it misuses.

## Output format

```
invoice-server/
├── server.py          # FastMCP app — one @mcp.tool per workflow
├── harness.py         # direct-call tests: uv run harness.py
├── pyproject.toml
├── .env.example       # INVOICE_API_TOKEN=
└── README.md          # tools, auth, config snippet

TypeScript variant: src/index.ts + tsconfig.json; wire with "command": "node", "args": ["dist/index.js"]

.mcp.json:
{
  "mcpServers": {
    "invoice-server": {
      "command": "uv",
      "args": ["run", "--directory", "./invoice-server", "server.py"],
      "env": { "INVOICE_API_TOKEN": "${INVOICE_API_TOKEN}" }
    }
  }
}
```

## Quality bar

- [ ] Tools map to jobs-to-be-done, not a 1:1 mirror of API endpoints
- [ ] Every input field has a description and an example; closed sets use enums
- [ ] Error messages tell the model how to correct the call
- [ ] All list tools paginate with a hard cap; nothing returns unbounded results
- [ ] Harness exercises every tool and passes before the server touches .mcp.json
- [ ] One live call verified from Claude Code after wiring

## Example

Ask: "Wrap our invoicing API so Claude can chase overdue payments."

Produced: `invoice-server/` with three tools — `find_overdue_invoices` (paginated, `days_overdue` filter), `get_invoice` (detail plus payment history), `draft_reminder` (returns email text, never sends) — plus the `.mcp.json` entry above and a README.

Harness run: `uv run harness.py` → 6 assertions passed; first live call from Claude Code returned 12 overdue invoices.
