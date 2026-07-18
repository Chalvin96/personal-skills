---
name: update-knowledge
description: Use when you incidentally discover a durable current-state fact about how existing code behaves — a knowledge doc that is wrong, misleading, or silent — outside of any completed change. For folding a shipped change into knowledge use openspec-to-knowledge; for multi-store KB sync use knowledge-ops.
---

# Update knowledge

## Overview

Canonical knowledge (OKF or equivalent) drifts because corrections are learned
incidentally — mid-debug, mid-review, mid-planning — and never written down. Core
principle: **maintain at the moment of use.** When you re-encounter a concept and
learn something true about it, find the existing note and improve it.

## When to use

- A knowledge doc states something the code contradicts (e.g. `is_published` = public
  when it is really a readiness gate).
- A doc is silent on a durable rule you just had to reverse-engineer.
- Exploration or brainstorming surfaced a current-state fact future readers need.

**When NOT to use:**
- The fact comes from a completed, verified change → **openspec-to-knowledge**.
- It is unbuilt or proposed design → it belongs in the OpenSpec change, not knowledge.
- Multi-store ingestion/sync/dedup across KBs → **knowledge-ops**.

## The loop

1. **Verify in code first.** Read the source proving the fact. Never write knowledge
   from memory or from another doc — the thing you are fixing is often a doc that
   trusted memory. Cite the file/line to yourself.
2. **Discover the knowledge system + validator** from agent instructions and repo
   structure (index frontmatter, log, concept format). If none exists, say so; do
   not invent one.
3. **Find the ONE concept that owns this truth.** Update that note in place — do not
   append a duplicate or scatter the fact. Keep the note atomic: one concept, whole.
4. **Write current-state only.** State how it *is* — not the history of your
   confusion, not the change that might come. Delete the stale statement in the same
   scope while you are there.
5. **Preserve local format** — frontmatter, links, indexes. Bump the concept's
   timestamp if the format carries one.
6. **Append the change log** in the system's own log style: one line stating what
   current truth changed, not the story of finding it.
7. **Validate.** Run the validator the repo defines; fix every failure. If you cannot
   locate it, report that — never claim a check you did not run. For OKF bundles, see
   **okf-validate**.
