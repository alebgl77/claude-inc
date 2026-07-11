---
name: voice-builder
description: Ingests 5–20 of the user's writing samples and distils a reusable voice-profile.md — signature phrases, sentence-length distribution, opener/closer habits, punctuation quirks, vocabulary do/don't lists, tone sliders, and three calibration paragraphs with self-checks. Other skills load this file so every post sounds like the user, not like AI. Use when the user says "make it sound like me", "clone my writing voice", "everything you write sounds like AI", or "build my voice profile".
---

# Voice Builder — Voice Coach

> "Clone your voice"

## When to use

- "Everything you write sounds like AI — make it sound like me."
- Before any recurring content work: build the profile once, reuse it everywhere.
- "Clone my voice from these posts." / "Here are my last 15 newsletters."
- Ghostwriting for a founder whose voice must survive the ghostwriter.
- Recalibrating after feedback: "that draft didn't sound like me."

## Workflow

1. Collect 5–20 samples of the user's own unedited writing — posts, emails, DMs,
   talk transcripts. Reject copy written by others or by AI. Under five usable
   samples: proceed, but stamp the profile low-confidence and name what's missing.
2. Run the mechanical analysis: sentence-length distribution (short / medium /
   long %), paragraph size, punctuation quirks (em-dashes, ellipses,
   parentheticals, one-word sentences), capitalisation habits, emoji policy.
3. Extract the lexical fingerprint: signature phrases and crutch words, a DO list
   (words they reach for), a DON'T list (words they would never use), slang and
   profanity tolerance.
4. Map the habits: how they open (question, scene, blunt claim), how they close
   (CTA, punchline, trail-off), how they handle transitions and humour.
5. Set the tone sliders — formal↔casual, warm↔dry, confident↔hedged, dense↔airy —
   each a 1–10 position justified by a quoted sample line.
6. Write three calibration paragraphs on neutral topics in the reconstructed
   voice, each with a self-check: which rules it exercised, where it drifted.
7. Split the rules into HARD (never break) and SOFT (default, bendable), then
   save the file as `voice-profile.md` at the project root.
8. Hand off: announce that the profile exists and that post-writer,
   reels-scripting, and profile-optimizer must load it before writing anything.

## Output format

The deliverable is a file, `voice-profile.md`:

```
# Voice Profile: <name>
Confidence: high | medium | low (<n> samples: <sources>)

## Sentence mechanics
- Length mix: ~<x>% short (<8 words), <y>% medium, <z>% long
- Paragraphs: <typical size and rhythm>
- Punctuation quirks: <em-dashes, one-word sentences, ellipses...>

## Lexicon
- Signature phrases: "<...>", "<...>", "<...>"
- DO: <words and constructions> | DON'T: <words and constructions>

## Habits
- Openers: <pattern + quoted example> | Closers: <pattern + quoted example>
- Transitions and humour: <how>

## Tone sliders (1–10, each with evidence)
- formal <n> casual — "<quoted line>"
- warm <n> dry — "<quoted line>"
- confident <n> hedged — "<quoted line>"
- dense <n> airy — "<quoted line>"

## Hard rules (never break)
1. <rule>

## Soft rules (defaults, bendable)
1. <rule>

## Calibration
### Test 1: <neutral topic>
<paragraph written in the voice>
Self-check: <rules exercised; drift named>
### Test 2 / Test 3
<same structure>
```

## Quality bar

- [ ] Every claim about the voice cites a quoted sample line — no vibes-based analysis.
- [ ] The DON'T list names actual words and constructions, not "avoid jargon".
- [ ] All four tone sliders carry evidence quotes, not bare numbers.
- [ ] Calibration paragraphs pass their own self-check; drift is named, not hidden.
- [ ] Hard and soft rules are separated; the file lands at `voice-profile.md`.

## Example

**Invocation:** "Here are 12 of my LinkedIn posts and 3 newsletters — clone my
voice."

**Produces:** `voice-profile.md` (high confidence, 15 samples) showing 48% short
sentences, heavy em-dash use, one-word paragraph openers ("Look."), a DO list
("ship", "boring", "the math"), a DON'T list ("leverage", "journey", "delve"),
formal 2/10 and warm 6/10 with quoted evidence, three calibration paragraphs
that pass their self-checks — and a handoff note telling post-writer to load
the file before drafting a single line.
