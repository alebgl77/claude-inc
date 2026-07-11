---
name: frontend-design
description: Writes production-grade, distinctive interface code — one strong art direction (editorial, brutalist, soft-depth, retro-terminal), a real typographic scale, custom details (cursor, selection, focus states), semantic HTML, delivered as a single file or as components. Ships with an anti-AI-slop checklist so nothing leaves looking template-made. Use when the user says "build this page", "code the UI", "make me a beautiful front-end", or "this looks like every AI site — redo it".
---

# Frontend Design — Front of House

> "Build front-end UIs"

## When to use

- It is time to write real interface code — "build the landing page", "code this dashboard UI".
- An existing front-end looks generic — "this screams AI-generated, give it a point of view".
- A design system exists and needs its first consumer — pairs with `ui-ux-pro-max` tokens.
- The user wants craft, not scaffolding — "make it feel expensive", "no template energy".

## Workflow

1. **Commit to one art direction before writing a line.** Editorial (serif display, generous
   whitespace, hairline rules), brutalist (raw borders, mono, hard shadows), soft-depth (layered
   surfaces, tinted shadows), retro-terminal (phosphor palette, restraint with the scanlines),
   industrial (dense, technical, visible grid) — or argue for another. Write the direction as one
   sentence; every later decision must serve it.
2. **Set the typographic reality.** Two families max; display size at least 3x body — no
   14/16/18 mush. Tighten letter-spacing on large sizes, widen it on small caps and labels.
   Load one hosted family at most; fall back to a deliberate system stack.
3. **Structure in semantic HTML first.** Landmarks (header/nav/main/section/footer), heading
   order without skips, buttons are `<button>`, links are `<a>`, inputs have labels. No div soup.
4. **Style with intent.** Spacing on one scale, color through role variables, and exactly one
   signature move executed hard — an oversized numeral, an asymmetric grid, sticky marginalia, an
   unexpected hover. One. Not four.
5. **Craft the custom details.** `::selection` tinted to the palette, `:focus-visible` rings
   designed rather than default blue, cursor changes where they mean something, real empty and
   error states.
6. **Wire interactions in vanilla JS** — or the project's existing framework. Event delegation,
   no dependencies for what CSS already does.
7. **Run the anti-slop checklist below.** Any hit is rework, not an excuse.
8. **Deliver** one self-contained file (or components matching repo conventions) opening with a
   three-line comment: the art direction, its rules, its one signature move.

## Anti-slop checklist

Reject on sight: purple/indigo gradient hero — glassmorphism without a reason — emoji as icons —
the three-feature-cards-with-rounded-icons row — default-Tailwind sameness (stacks of
`p-4 rounded-xl shadow-md` cards) — Inter-on-white with blue-600 buttons — `transition: all` —
border-radius 12px on everything — "Supercharge your workflow" copy — perfectly symmetric
everything. Any hit means rework before delivery.

## Output format

```html
<!-- direction: EDITORIAL — serif display, hairline rules, ivory ground, one oxblood accent.
     rules: no gradients; hierarchy via size and weight only; hover = underline offset shift.
     signature: oversized drop-cap section numerals. -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Product — the one-line promise</title>
  <style>
    /* 1. tokens  2. layout  3. components  4. details (::selection, :focus-visible, cursor) */
  </style>
</head>
<body>
  <header><!-- nav, one primary action --></header>
  <main><!-- sections in document order, headings intact --></main>
  <footer><!-- real links, no dead ends --></footer>
  <script>/* minimal, event-delegated */</script>
</body>
</html>
```

## Quality bar

- [ ] Art direction named in the header comment and recognizable within three seconds of load
- [ ] Zero hits on the anti-slop checklist
- [ ] Semantic HTML throughout: landmarks, intact heading order, real controls
- [ ] `:focus-visible` styled on every interactive element; AA contrast on all text
- [ ] Exactly one signature move — visible, deliberate, serving the direction
- [ ] No horizontal scroll at 360px or 1440px; text measures stay between 45 and 75ch

## Example

**Invocation:** "Build a landing page for a bakery-focused POS startup — warm but not cute."

**Produces:** One `index.html` (~350 lines), direction "editorial-warm": Fraunces display over a
system sans, flour-white ground with rye-brown ink and one burnt-orange accent, an oversized
ligature headline as the signature move, hairline section rules, oxblood `::selection`, designed
focus rings on the pricing table — no gradient, no emoji, no card-grid hero.
