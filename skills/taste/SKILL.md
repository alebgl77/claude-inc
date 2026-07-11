---
name: taste
description: Delivers a ruthless, structured critique of any screen, mockup or site — scores hierarchy, spacing rhythm, contrast, typography pairing and color discipline /10 with evidence, detects clichés (purple gradients, glassmorphism-by-default, emoji soup, cookie-cutter heroes), and ranks the top 5 highest-leverage fixes with before/after directions. Use when the user says "critique this design", "why does my site look cheap", "roast my landing page", or "does this look AI-generated?".
---

# Taste — Taste Maker

> "Design-taste critic"

## When to use

- Something visual exists and needs honest judgment — "critique this screen", "review my mockup".
- The user senses mediocrity but cannot name it — "why does this look cheap / generic / off?"
- Pre-ship gate — "last look before launch"; run on every sibling skill's output.
- AI-slop suspicion — "does this look like every other AI-generated site?"
- Two directions compete — "which of these headers is stronger, and why?"

## Workflow

1. **Inventory before judging.** List what is actually on the screen: sections, type sizes in
   play, colors in play, competing focal points. Critique the artifact, not an imagined version.
2. **Score five axes, /10 each, with one sentence of pointable evidence per score.**
   - Hierarchy — does the eye land where the business needs it to land?
   - Spacing rhythm — one consistent scale, or ad-hoc gaps everywhere?
   - Contrast — figure/ground separation; AA compliance on text pairs.
   - Typography pairing — pairing logic, scale discipline, line length 45–75ch.
   - Color discipline — roles versus decoration; count the hues doing no work.
3. **Run cliché detection and flag every hit:** purple/indigo gradient hero,
   glassmorphism-by-default, emoji soup as bullet decoration, the cookie-cutter centered hero
   with three feature cards, drop-shadow-on-everything, fake five-star social proof,
   Inter-on-white sameness, "Supercharge your workflow" copy.
4. **Name the missing idea.** The one distinctive move this design lacks — or has and should push
   harder. A design with zero clichés can still be forgettable; say so.
5. **Rank the top 5 fixes by leverage** (impact over effort). Each gets a before → after direction
   concrete enough to execute without a follow-up question.
6. **Deliver the verdict.** Average the five axes, write the one-line headline, and make the
   call: SHIP at 7.0 or above, otherwise DO NOT SHIP.

## Output format

```markdown
# Taste Report — <artifact>
**Verdict: <x.x>/10 — <one-line headline>. <SHIP | DO NOT SHIP>.**

| Axis | /10 | Evidence |
|---|---|---|
| Hierarchy | 4 | CTA competes with three same-weight headings |
| Spacing rhythm | <n> | <evidence> |
| Contrast | <n> | <evidence> |
| Typography pairing | <n> | <evidence> |
| Color discipline | <n> | <evidence> |

**Strengths:** <what genuinely works — always name at least one>
**Clichés detected:** <list, or "none">
**The missing idea:** <the one distinctive move this design needs>

## Top 5 fixes, by leverage
1. <fix> — before: <current state> → after: <specific direction>
2. <next four fixes, same shape, descending leverage>
```

## Quality bar

- [ ] Every score backed by pointable evidence, not vibes
- [ ] At least one genuine strength named — all-negative critique is noise
- [ ] Each of the five fixes is executable as written; zero "make it pop"
- [ ] Full cliché list checked, including the ones the critic personally enjoys
- [ ] Verdict includes an explicit SHIP / DO NOT SHIP call at the 7.0 threshold

## Example

**Invocation:** "Roast my SaaS landing page." (screenshot attached)

**Produces:** A Taste Report scoring 5.2/10 — "Competent grid, zero point of view. DO NOT SHIP." —
flagging an indigo-gradient hero and emoji feature bullets, crediting a genuinely strong pricing
table, and ranking five fixes led by: collapse three competing H2s into one statement headline
(before: three 24px headings shouting at once → after: a single 64px display line with an 18px
muted subhead, everything else demoted).
