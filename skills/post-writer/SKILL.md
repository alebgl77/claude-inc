---
name: post-writer
description: Writes LinkedIn and X posts that read human — a hook line drawn from proven patterns, whitespace rhythm, story or insight structure, a soft CTA — and delivers three full variants per ask (story, contrarian, list). Applies the project's voice profile when one exists and enforces platform length rules. Use when the user says "write a LinkedIn post about...", "turn this into an X post", "draft the launch announcement", or "this sounds corporate — make it human".
---

# Post Writer — Ghostwriter

> "Write LinkedIn posts"

## When to use

- Turning a win, launch, lesson, or opinion into a LinkedIn or X post.
- "Write a LinkedIn post about our migration off Kubernetes."
- "Turn this blog post into an X post that isn't just a summary."
- "Draft my new-role announcement" / "announce our funding round".
- Rescuing a stiff draft: "make this sound like a person wrote it."

## Workflow

1. Extract the one idea. Decide what the reader should think, feel, or do after
   reading. One post carries one idea — park the extras as future posts and say so.
2. Load `voice-profile.md` if it exists. Its signature phrases, sentence lengths,
   punctuation quirks, and vocabulary do/don't override generic style everywhere.
3. Apply platform physics:
   - LinkedIn: only the first 2–3 lines show before "...see more", so the hook
     must survive the fold; 900–1,300 characters is the sweet spot; breaks are free.
   - X: 280 characters and the hook is the whole post; thread only if every tweet
     stands alone.
4. Write the hook first. Draft 5–10 candidates across proven patterns — specific
   number, contrarian, mistake, transformation, curiosity gap — and promote the
   strongest to line one.
5. Build the body on one spine:
   - Story: context → tension → resolution → lesson.
   - Insight: claim → evidence → implication.
   Keep paragraphs to 1–2 lines. Whitespace is the pacing; never a wall of text.
6. Close soft: a question worth answering, an invitation, or a plain "follow for
   more on <topic>" — never "thoughts?" or "agree?".
7. Produce three full variants of the same idea: story-led, contrarian-led,
   list-led.
8. Self-edit: delete the first sentence if the post works without it (it usually
   does), cut adverbs, read aloud for cadence, then run the quality bar.

## Output format

```
## Post: <topic> — <platform>

### Variant A — Story
<full post text, formatted exactly as it should be pasted>

### Variant B — Contrarian
<full post text>

### Variant C — List
<full post text>

---
Recommended: <A | B | C> — <one-line reason>
Character counts: A <n> | B <n> | C <n> (limit: <platform rule>)
Voice profile: applied | not found — generic voice used
```

## Quality bar

- [ ] Line one stops the scroll with zero context — no throat-clearing, no "So,".
- [ ] One idea per post; every line earns the next.
- [ ] No paragraph over two lines; the post breathes.
- [ ] Zero corporate tells: no "thrilled to announce", "game-changer", "in
      today's fast-paced world".
- [ ] Hashtags 0–3, end of post only, each one a real discovery channel.
- [ ] Inside platform limits; the LinkedIn hook survives the "...see more" fold.

## Example

**Invocation:** "Write a LinkedIn post: we cut our AWS bill 60% by deleting three
services nobody used."

**Produces:** three paste-ready variants — story ("We were paying $14k a month for
software nobody had opened since March."), contrarian ("Your cloud bill isn't an
engineering problem. It's an archaeology problem."), list (the three services,
what each cost, what replaced them) — with the contrarian flagged as recommended
for a CTO audience, character counts per variant, and a soft closing question
asking readers what's hiding in their own billing console.
