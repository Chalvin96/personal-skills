---
name: grill-me
description: Stress-test a feature, non-trivial bug fix, architectural change, or UI design before implementation. Use when the user says "grill me", asks to pressure-test a design, or needs unresolved decisions captured in OpenSpec.
---

# OpenSpec Grill

Resolve one decision at a time before implementation. This is exploration, not
implementation: do not edit production code or canonical current-state knowledge while facts remain provisional.

## Workflow

1. Read the repository's canonical knowledge source and inspect code for questions that
   can be answered from the repository. Do not ask the user for discoverable
   facts.
2. Decide whether the work needs OpenSpec. Use it for features, non-trivial bug
   fixes, and architectural changes; skip it for isolated typo/config changes.
3. For OpenSpec work, locate a named active change with:

   ```bash
   openspec list --json
   ```

   If the user has not named one, derive a concise kebab-case name and create it
   only after the change goal is clear:

   ```bash
   openspec new change <name>
   ```

4. Ask exactly one question at a time. Give a recommended answer and its
   trade-off. Follow the answer down the next unresolved branch.
5. Once the change is understood, use OpenSpec's current instructions to write
   the proposal and design. Capture only settled decisions; keep behavioral
   requirements and tasks for `$writing-plans`.

   ```bash
   openspec instructions proposal --change <name> --json
   openspec instructions design --change <name> --json
   ```

6. End by naming the OpenSpec change and recommending `$writing-plans` to make
   it apply-ready.

## UI visual companion

For UI work, offer a visual companion only when the next question would be
clearer as a mockup, wireframe, flow, diagram, or side-by-side comparison than
as prose. Make the offer its own message and wait for the answer:

> This next decision may be clearer visually. I can show mockups, diagrams, or
> comparisons as we go. Want to use the visual companion?

If the user accepts and the host exposes a browser-based visual companion, open
it for the first visual question. Before starting it, read
[visual-companion.md](visual-companion.md) and use `scripts/start-server.sh`
with `--project-dir` and `--open`. Otherwise, use the best available visual
artifact (for example, an image, diagram, or text wireframe). Decide per
question whether the visual companion helps; keep requirements, trade-offs, and
other text-first questions in the normal conversation. If the user declines,
continue text-only and do not offer again unless they raise it.

For every visual screen, first discover the target project's design system from
its agent instructions, canonical knowledge, tokens, component library, and
existing UI. Use those tokens, type scale, components, and interaction patterns;
do not invent a parallel visual language.

## Guardrails

- Preserve accepted decisions in the repository's canonical current-state knowledge.
- Keep exploratory notes in OpenSpec; update canonical knowledge only after implementation and verification.
- If the user rejects the change, keep the rationale in the OpenSpec proposal
  only when it would prevent the same design from being re-proposed later.
