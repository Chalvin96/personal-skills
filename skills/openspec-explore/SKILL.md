---
name: openspec-explore
description: Explore an uncertain change without implementing it. Requires the OpenSpec CLI. Use when the user wants to investigate, compare options, or clarify requirements before proposing a change.
license: MIT
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.5.0"
---

# Explore an OpenSpec change

Explore is a thinking mode. Read code, documentation, and OpenSpec artifacts;
form hypotheses; distinguish facts from assumptions; and surface the next
decision. Do not modify application code.

If the work is in a registered OpenSpec store, read
[store selection](../_personal-shared/openspec-store-selection.md) before running
commands.

1. Establish the question, affected area, and whether an active change exists.
2. Inspect only the relevant code, current-state knowledge, and OpenSpec context.
3. Present evidence, options, trade-offs, and open questions. Ask the user when
   a choice changes scope or behavior.
4. When the route is clear, create or recommend an OpenSpec proposal; when it
   is not, state the smallest next investigation.

Completion means the user can make the next decision or start a well-scoped
proposal. Implementation belongs to `openspec-apply-change`.
