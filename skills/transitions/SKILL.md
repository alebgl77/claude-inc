---
name: transitions
description: Builds a complete CSS motion system — duration and easing tokens (fast 120ms micro-feedback, base 200ms, slow 320ms entrances; standard, decelerate and spring curves), enter/exit/emphasis patterns, stagger rules, and prefers-reduced-motion fallbacks — delivered as a copy-paste CSS/JS snippet library. Use when the user says "add animations", "make this feel smooth", "the transitions are janky", or "animate this modal / dropdown / list without making it feel like a template".
---

# Transitions — Motion Artist

> "CSS motion library"

## When to use

- A UI works but feels dead or abrupt — "make it feel alive", "everything just pops in".
- Motion exists but is chaotic — "every component animates differently, unify it".
- Specific effects are requested — "animate this modal / dropdown / list / page load".
- Accessibility review flagged motion — "we need prefers-reduced-motion support".

## Workflow

1. **Audit what changes.** List every state change in the UI — appear, disappear, reorder,
   attention. Motion attaches to changes, not to components.
2. **Define duration tokens.** `--motion-fast: 120ms` for micro-feedback (hover, press),
   `--motion-base: 200ms` for most transitions, `--motion-slow: 320ms` for entrances and large
   surfaces. Exits run roughly 20% faster than their enters.
3. **Define easing tokens.** Standard `cubic-bezier(0.2, 0, 0, 1)` for most moves; decelerate
   `cubic-bezier(0, 0, 0, 1)` for entrances; spring `cubic-bezier(0.34, 1.56, 0.64, 1)` reserved
   for playful emphasis — at most once per view.
4. **Build the pattern set.** Enter: fade-rise 8px, scale-in 0.96→1. Exit: fade-fall, faster.
   Emphasis: one pulse, or one shake for errors — never looping. Only `transform` and `opacity`
   ever animate; layout properties are off-limits.
5. **Set stagger rules.** Lists stagger 30–40ms per item, total capped at 400ms; past ten items,
   stagger the first eight and land the rest together.
6. **Write the reduced-motion fallback.** Under `prefers-reduced-motion: reduce`, collapse
   animations to fast opacity fades — never delete feedback entirely.
7. **Emit the library.** `motion.css` (tokens + patterns) and a trigger snippet
   (IntersectionObserver scroll-ins, class-toggle helpers), with a one-line usage note per
   pattern: what it is for, what it must never be used for.

## Output format

```css
/* motion.css — tokens */
:root {
  --motion-fast: 120ms;
  --motion-base: 200ms;
  --motion-slow: 320ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-decelerate: cubic-bezier(0, 0, 0, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
/* enter — use for: content appearing; never for: hover feedback */
.enter-rise { animation: rise var(--motion-slow) var(--ease-decelerate) both; }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } }
/* stagger — set style="--i: n" per item; cap the cascade at 400ms */
.stagger > * { animation-delay: calc(var(--i, 0) * 35ms); }
/* reduced motion — feedback stays, movement goes */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms !important;
    transition-duration: 80ms !important;
  }
}
```

```js
// scroll-in trigger — pairs with .enter-rise via [data-animate]
const io = new IntersectionObserver(
  (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add('enter-rise')),
  { threshold: 0.15 }
);
document.querySelectorAll('[data-animate]').forEach((el) => io.observe(el));
```

## Quality bar

- [ ] Every duration and easing is a token — zero inline magic numbers
- [ ] Exits faster than enters; nothing exceeds 400ms except a declared hero moment
- [ ] Only transform and opacity animate — no layout properties, no `transition: all`
- [ ] prefers-reduced-motion fallback present and verified by toggling the OS setting
- [ ] Spring easing appears at most once per view
- [ ] Staggers capped — no two-second cascades on long lists

## Example

**Invocation:** "My settings modal and dropdown feel abrupt, and list items just pop in."

**Produces:** `motion.css` with the token block; modal enter at 320ms decelerate (scale-in) with a
160ms exit; dropdown at 200ms standard with `transform-origin: top`; a 35ms stagger on the list
capped at 400ms; the IntersectionObserver trigger; and a reduced-motion block that converts every
pattern to a fast opacity fade.
