---
name: web-artifacts
description: Turns any idea into a live single-file HTML prototype in minutes — inline CSS/JS, CDN-only dependencies (cdnjs), mobile-first, seeded with believable fake data, interactive states wired — ready to open in a browser or paste as a Claude artifact. Use when the user says "prototype this", "show me a working demo", "make this idea clickable", "can we test this flow before building it", or needs to feel an interaction instead of reading a spec.
---

# Web Artifacts — Prototyper

> "Live web prototypes"

## When to use

- An idea needs to be felt, not described — "prototype this so I can click through it".
- A stakeholder demo is imminent — "I need something to show in an hour".
- A flow is contested — "would users even get this? build it and let's see".
- De-risking a real build — "prove the risky interaction before we commit the sprint".

## Workflow

1. **Scope-cut first: what is the ONE interaction to prove?** Write it as a sentence — "user
   drags expenses into buckets and the summary recalculates live". Everything not serving that
   sentence gets faked or cut.
2. **Choose the thinnest stack that proves it.** Default is vanilla HTML/CSS/JS in one file.
   Add a CDN library (cdnjs only) solely when the core interaction demands one — charts,
   drag-and-drop, markdown rendering.
3. **Seed believable fake data.** 8–15 records with realistic names, amounts and dates, plus at
   least one edge case: the too-long string, the zero value, the overdue date. Declare it as
   `const DATA = [...]` at the top of the script so reviewers can tweak it live.
4. **Build mobile-first.** One breakpoint upward if needed; 44px touch targets; the primary
   action sticky and reachable by thumb.
5. **Wire the interactive states.** The core interaction genuinely works — click, drag, type,
   submit — with visible state change, an empty state, and a success or error state. Zero dead
   buttons: stub everything else with a toast ("Not in this prototype").
6. **Polish for ten minutes, not two hours.** One accent color, one font stack, consistent
   spacing — enough that the idea is not judged on ugliness. This is not the design system pass.
7. **Ship.** One .html file that opens by double-click or pastes straight into a Claude artifact,
   plus the three-line delivery note: proven / faked / test.

## Output format

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Prototype — <the one interaction></title>
  <!-- CDN deps only if the core interaction needs them:
       https://cdnjs.cloudflare.com/ajax/libs/chart.js/4.4.1/chart.umd.min.js -->
  <style>/* mobile-first; one accent; system font stack */</style>
</head>
<body>
  <main><!-- the ONE interaction, fully wired --></main>
  <script>
    const DATA = [/* 8-15 seeded records, edge cases included */];
    // state -> render() -> delegated event handlers, all inline
  </script>
</body>
</html>
```

Delivery note, always attached:

```
PROVES: <the one interaction, now working>
FAKED:  <auth, persistence, API calls — hardcoded or stubbed>
TEST:   <what to watch when a human first touches it>
```

## Quality bar

- [ ] Opens by double-clicking the file — no build step, no server, no install
- [ ] The ONE interaction fully works, with visible state changes and an empty state
- [ ] Fake data reads as real and includes at least one edge case
- [ ] Zero dead buttons — everything clickable responds or admits it is stubbed
- [ ] Usable one-handed at 375px wide
- [ ] Dependencies, if any, load from cdnjs — and only because the core interaction demanded them

## Example

**Invocation:** "Prototype a Splitwise-style expense splitter for ski trips."

**Produces:** `expense-splitter.html` (~300 lines): six friends and twelve expenses seeded
(including a 0.00 lift-pass refund edge case), an add-expense form with validation states,
per-person balances recomputed live on every change, a settle-up view, an empty state for a fresh
trip — vanilla JS, zero dependencies, opens by double-click. Delivery note: PROVES live balance
math; FAKED persistence; TEST whether users understand "who paid" versus "who owes".
