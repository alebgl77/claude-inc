---
name: webapp-testing
description: Browser-tests a local webapp end to end — starts the app, installs Playwright if missing, writes a spec for the critical path plus edge cases, runs headless, captures screenshots, console and network logs on failure, and reports a pass/fail table with repro steps. Degrades to curl smoke tests when no browser is available. Use when the user says "test my app", "does signup still work", "check the site before I deploy", or "this page is blank".
---

# Webapp Testing — QA Engineer

> "Browser-test your app"

If a human can click it, it can break. Prove the critical path in a real browser before anything ships.

## When to use

- "Test my app" / "check the site before I deploy" — the pre-ship confidence run
- "Does signup still work?" after touching auth, forms, or routing
- "This page is blank" / "the button does nothing" — reproduce with evidence, not vibes
- Regression pass after a dependency bump, refactor, or CSS overhaul
- The project has zero e2e coverage and needs a first spec to seed CI

## Workflow

1. Start the app in the background (`npm run dev`, `uvicorn app:app`, `rails s`, ...) and poll until it answers — `curl -sf http://localhost:<port>` in a retry loop. Never test a dead server.
2. Ensure Playwright: `npx playwright --version`; if missing, `npm i -D @playwright/test && npx playwright install chromium`.
3. Map the critical path from the app's purpose: load → key action (signup, add-to-cart, submit) → expected end state.
4. Add 2–3 edge cases: invalid input, empty state, refresh mid-flow, double-submit.
5. Write `tests/e2e.spec.ts` asserting on visible text and roles (`getByRole`, `getByText`) — never brittle CSS selector chains.
6. Run headless: `npx playwright test --reporter=line`.
7. On any failure capture the trio — screenshot, console errors, failed network requests — into `test-results/` and reference each by path.
8. Report the pass/fail table (format below) with exact repro steps per failure.
9. No browser possible (install blocked, sandboxed env)? Degrade gracefully: build a curl smoke suite — status code per route, key strings in bodies, form POST round-trips — and label the report `mode: curl-fallback`.

## Output format

```
## QA report — <app> @ http://localhost:<port>   (mode: playwright-chromium | curl-fallback)

| # | Scenario | Result | Evidence |
|---|----------|--------|----------|
| 1 | Signup happy path | PASS | — |
| 2 | Invalid email rejected | FAIL | test-results/02-invalid-email.png |

Failures:
2. Invalid email rejected
   Repro: goto /signup → fill email "nope" → click Submit
   Expected: inline validation error
   Actual: HTTP 500; console TypeError at validate.js:14; POST /api/signup → 500

Re-run: npx playwright test --reporter=line
```

## Quality bar

- [ ] Server confirmed answering before the first test ran
- [ ] Critical path plus at least two edge cases covered
- [ ] Selectors use roles and text, not CSS chains that break on restyle
- [ ] Every failure ships with screenshot, console, and network evidence
- [ ] Repro steps followable by a human with zero context
- [ ] Entire suite re-runs with one stated command

## Example

Ask: "Check the store before I deploy."

Produced: app started on :3000, `tests/e2e.spec.ts` with five scenarios (browse → add to cart → checkout, plus empty-cart and out-of-stock edges). Result 4 PASS / 1 FAIL.

```
| 5 | Empty-cart checkout | FAIL | test-results/05-empty-cart.png |
Repro: goto /cart (empty) → click Checkout → HTTP 500
```

Verdict: hold the deploy until the empty-cart 500 is fixed; everything else is green.
