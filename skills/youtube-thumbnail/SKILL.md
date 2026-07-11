---
name: youtube-thumbnail
description: Designs and tests YouTube thumbnails — 3–5 concept briefs covering composition, face or object, a 3-word-max overlay, and colour contrast against YouTube's UI, each run through a curiosity check, a mobile legibility test at 168×94 px, and a /10 scoring rubric, ending in a verdict and an A/B rotation plan. Generates mockups when an image tool is available. Use when the user says "thumbnail ideas for this video", "which cover wins?", "my CTR is stuck at 3%", or "test these two thumbnails".
---

# YouTube Thumbnail — Cover Tester

> "Test thumbnail covers"

## When to use

- "Thumbnail ideas for my video about <topic>."
- "Which of these two covers should I use?" — a scored verdict, not a shrug.
- CTR is flat and packaging is the suspect: "my CTR is stuck at 3%."
- Pre-production: designing title + thumbnail as one package before filming.

## Workflow

1. Get the inputs: video topic, the exact title, the target viewer, and where the
   impressions come from (browse, suggested, search) — thumbnails compete
   differently on each surface.
2. Define the ONE emotion or question the thumbnail must trigger. The thumbnail
   asks a question the title answers (or the reverse) — the two must never repeat
   each other.
3. Draft 3–5 concept briefs. Each specifies composition (focal point on a
   rule-of-thirds intersection), face or object (expression, prop, angle), a text
   overlay of three words or fewer (or none), and a palette with deliberate
   contrast against YouTube's white/dark UI and red accents.
4. Curiosity-check each concept: does it open a loop the title closes? Does it
   spoil the payoff? Does it still make sense with the title covered?
5. Run the mobile legibility test: judge each concept at 168×94 px — focal point
   readable, overlay text at 25%+ of frame height, nothing critical under the
   timestamp corner or lost at the edges.
6. Score every concept /10 with the rubric: clarity at a glance (3), curiosity
   (3), contrast vs UI (2), title synergy (2). Rank them.
7. If an image generation tool is available in the session, produce mockups of
   the top two concepts; otherwise ship briefs precise enough for a designer or
   a Canva session.
8. Write the A/B rotation plan: which concept launches, the numeric swap trigger
   (e.g. CTR under 4% after 48 hours or 10k impressions), and what the variant
   changes — exactly one variable.

## Output format

```
## Thumbnails: "<video title>"
Target emotion/question: <one line> | Surface: browse / suggested / search

### Concept 1 — <name>
- Composition: <focal point + layout>
- Face/object: <expression or prop>
- Overlay: "<3 words max>" | none
- Colours: <palette + contrast note vs YouTube UI>
- Curiosity check: pass / fail — <reason>
- Mobile check (168×94): pass / fail — <reason>
- Score: <n>/10 (clarity /3, curiosity /3, contrast /2, synergy /2)

### Concept 2–5 — <same structure>

### Verdict
Launch: Concept <n> — <one-line reason>
A/B plan: swap to Concept <m> if <numeric trigger>; variable changed: <one thing>
Mockups: <file paths | "no image tool available — briefs are designer-ready">
```

## Quality bar

- [ ] 3–5 concepts, each fully specified — no "something eye-catching" hand-waving.
- [ ] Overlay is three words or fewer and repeats none of the title's words.
- [ ] Every surviving concept passes the 168×94 mobile test; failures are cut.
- [ ] Scores use the rubric weights, and the verdict follows the scores or says
      exactly why it doesn't.
- [ ] The A/B plan changes one variable and has a numeric swap trigger.

## Example

**Invocation:** "Thumbnails for 'I Tried Waking Up at 5AM for 30 Days' — which
one wins?"

**Produces:** four scored briefs — Concept 2 is an extreme close-up of an
exhausted face lit by phone glow at 5:00, overlay "DAY 23." in yellow, 8/10;
Concept 4 is a before/after split that fails the curiosity check by spoiling
the arc, 5/10 — a verdict launching Concept 2, an A/B swap to Concept 3 if CTR
sits under 4% after 10k impressions, and a note that no image tool is connected,
so the briefs ship designer-ready.
