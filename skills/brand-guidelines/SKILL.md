---
name: brand-guidelines
description: Generates a brand kit from a company one-liner — positioning adjectives, a palette with hex codes, usage ratios and do/don'ts, a display+text type pairing with fallback stacks, a voice & tone table (say / never say), a logo brief, and a one-page BRAND.md brandbook other skills consume. Use when the user says "we need a brand", "create our visual identity", "pick our colors and fonts", "define our voice", or before designing anything for a company with no identity yet.
---

# Brand Guidelines — Brand Keeper

> "Build a brand kit"

## When to use

- A company has a one-liner and nothing else — "we need a brand for this".
- Visuals exist but are incoherent — "our colors and fonts differ on every page; fix the source".
- Copy has no consistent voice — "define how we sound in the product and in emails".
- Upstream of sibling skills — run before `ui-ux-pro-max` or `frontend-design` for a new venture.

## Workflow

1. **Extract positioning from the one-liner.** Ask or infer the audience, the enemy (what the
   brand stands against — "enterprise bloat", "hidden fees"), and the price position. Distill
   into exactly three positioning adjectives plus one anti-adjective: "confident, warm, precise —
   never cute".
2. **Translate adjectives into a palette.** One ground, one text, one accent, plus semantics —
   each with a hex code, a name that carries meaning ("Glacier", not "Blue 2"), a usage ratio
   (60/30/10), one do and one don't.
3. **Pair type.** One display face + one text face with real contrast between them (serif/sans,
   geometric/humanist), the weights worth licensing, and a CSS fallback stack for each. State
   the pairing logic in a single sentence.
4. **Write the voice & tone table.** Four traits, each with a verbatim say-this sentence and a
   verbatim never-say-this counter-example, all grounded in the positioning adjectives.
5. **Draft the logo brief — not the logo.** Concept direction, construction (wordmark vs mark,
   geometric basis), clearspace rule, minimum size, and the misuse list: no gradients, no
   stretching, no drop shadows, no recoloring.
6. **Assemble BRAND.md, one page.** Downstream skills must be able to consume it without asking
   a single follow-up question.
7. **Stress-test the kit.** Apply it mentally to a button, an error message, and an invoice
   footer. If any feels off-brand, revise the kit — never the artifact.

## Output format

```markdown
# BRAND.md — <Company>
**One-liner:** <as given>
**Positioning:** <adj>, <adj>, <adj> — never <anti-adjective>.

## Palette — 60/30/10
| Name | Hex | Role | Ratio | Do | Don't |
|---|---|---|---|---|---|
| Paper | #FAF9F7 | ground | 60% | page and card backgrounds | text |
| Ink | #101828 | text | 30% | body copy, headings | large filled areas |
| Glacier | #2563EB | accent | 10% | CTAs, links, focus rings | full-bleed backgrounds |

## Type
- Display: <face> (<weights>) — fallback: <stack>
- Text: <face> (<weights>) — fallback: <stack>
- Pairing logic: <one sentence>

## Voice & tone
| Trait | Say | Never say |
|---|---|---|
| Precise | "Backups run every 10 minutes." | "Blazingly fast backups!" |

## Logo brief
<direction> / <construction> / clearspace: <rule> / min size: <px> / misuse: <list>
```

## Quality bar

- [ ] Exactly three positioning adjectives plus one anti-adjective, all load-bearing
- [ ] Every palette entry has hex, role, ratio, one do and one don't — no orphan swatches
- [ ] Type pairing ships real fallback stacks and names the weights to license
- [ ] Voice table uses verbatim example sentences, never abstract descriptions
- [ ] BRAND.md fits one page and pre-answers the questions downstream skills would ask
- [ ] Text color on ground color passes WCAG AA

## Example

**Invocation:** "Brand kit for 'Ledgerly — bookkeeping that closes your month in a day'."

**Produces:** `BRAND.md`: positioning "precise, calm, unstoppable — never playful"; a palette of
warm Paper ground (60%), Ink #101828 text (30%), Ledger Green #0E9F6E accent (10%) plus amber/red
semantics, each with do/don'ts; Fraunces display over Inter text ("editorial authority over
utilitarian clarity"); a four-row voice table (Say: "Your month is closed." Never: "Boom! Books
done!"); and a wordmark brief with tabular numerals as the identity hook, cap-height clearspace,
and a no-gradients-ever misuse list.
