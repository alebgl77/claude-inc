---
name: ai-seo
description: Optimizes content to get cited by AI assistants (ChatGPT, Perplexity, Google AI Overviews) and rank in classic SERPs — entity-rich intros, question-shaped H2s, 40-60 word extractable answers, schema.org JSON-LD, llms.txt, internal links, and E-E-A-T signals. Runs in audit or rewrite mode. Use when the user says "optimize this for SEO", "why doesn't ChatGPT cite us", "make this page rank", or "audit our content for AI search".
---

# AI SEO — Search Whisperer

> "Rank in AI search"

## When to use

- A page must rank in Google and get quoted by AI answers — "make this pillar page rank"
- Diagnosing invisibility — "why doesn't Perplexity ever cite our docs?"
- Pre-publish optimization pass — "SEO-check this post before it ships"
- Site-level AI readiness — "do we need an llms.txt? Set it up"
- Not for net-new persuasion copy — that's `copywriting`

## Workflow

1. **Pick the mode.** Audit (score an existing page, list fixes) or rewrite (produce the optimized version). If the page exists, audit first; rewrite on request or when most findings are structural.
2. **Entity pass.** The first 100 words must name the entity, its category, and 1-2 differentiators in plain declarative sentences ("X is a Y that Z"). AI systems quote pages that define themselves.
3. **Map real queries to H2s.** Rewrite headings as the questions users actually ask — People Also Ask phrasing, support-ticket phrasing. One question, one H2.
4. **Write extractable answers.** Directly under each H2, a 40-60 word standalone answer: complete sentences, no "as mentioned above", quotable verbatim by an AI. Depth and nuance follow after it.
5. **Emit schema.** JSON-LD matching the page type — Article, FAQPage, Product, HowTo. Fill every required property; no empty fields, no invented ratings.
6. **Create or update llms.txt.** Site purpose, key pages with one-line descriptions, canonical sources.
7. **Internal linking.** 3-5 contextual links with descriptive anchors (never "click here"), pointing at the money page and its supporting cluster.
8. **E-E-A-T pass.** Author byline with credentials, published/updated dates, cited primary sources, and at least one first-hand signal — original data, screenshots, a tested-by-us statement.
9. **Deliver** the scorecard (audit) or the full rewrite plus schema and llms.txt snippet (rewrite).

## Output format

```
MODE: <audit | rewrite>
PAGE: <path or URL>
TARGET QUERIES: <3-5 real queries this page should own>

SCORECARD (audit mode)
| Check | Status | Finding | Fix |
|---|---|---|---|
| Entity-rich intro | PASS/FAIL | ... | ... |
| Question-shaped H2s | ... | ... | ... |
| Extractable answers (40-60 w) | ... | ... | ... |
| Schema JSON-LD | ... | ... | ... |
| llms.txt | ... | ... | ... |
| Internal links | ... | ... | ... |
| E-E-A-T signals | ... | ... | ... |

REWRITE (rewrite mode)
<optimized page content>

SCHEMA
<script type="application/ld+json">{ ... }</script>

LLMS.TXT ENTRY
<lines to add>
```

## Quality bar

- [ ] Entity, category, and differentiator named in the first 100 words
- [ ] Every H2 is a question a real user asks
- [ ] A 40-60 word standalone answer sits directly under each H2
- [ ] JSON-LD has no missing required properties for its type
- [ ] 3-5 internal links with descriptive anchors
- [ ] Author, dates, and sources present — E-E-A-T covered

## Example

**Invocation:** "Audit docs/guides/what-is-rate-limiting.md — Google traffic is flat and AI tools never cite it."

**Produced:**
- Scorecard: 7 checks, 4 FAIL — vague intro, statement-style H2s, no schema, no dates
- Rewritten intro plus 5 H2s recast as questions, each with a 40-60 word direct answer
- FAQPage JSON-LD, an llms.txt entry, and 4 internal links into the API docs cluster
