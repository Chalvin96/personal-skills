---
name: openspec-to-knowledge
description: Distill a verified, completed OpenSpec change into a repository's canonical current-state knowledge. Requires the OpenSpec CLI. Use after implementation and tests pass, before archiving a change, or when the user asks to turn a finished spec into knowledge.
---

# OpenSpec to knowledge

Use this skill after implementation, not while a change is still exploratory.
Its outcome is concise current-state knowledge, never a copy of proposal, design,
or task history.

1. Select the completed change. Read `openspec status --change <name> --json`,
   every change artifact, the final code diff, and verification results. If
   tasks or verification are incomplete, stop and report the gap.
2. Discover the repository's canonical knowledge system and its validator from
   agent instructions and repository structure. If no canonical knowledge system
   exists, state that explicitly; do not invent one without user direction.
3. Extract only durable facts that are true in the final code: behavior,
   contracts, invariants, architecture boundaries, operational procedures, data
   shape, and decisions that future work must know.
4. Update the smallest affected knowledge concepts. Preserve their local format,
   indexes, links, timestamps, and change log. Remove stale statements found in
   the same scope.
5. Exclude temporary alternatives, rejected options, task checklists, rollout
   narration, and implementation history. Those remain in OpenSpec archive
   artifacts.
6. Run the knowledge validator and `openspec validate <name> --strict`. Fix
   every failure. Mark the knowledge-maintenance task complete only after both
   pass.
7. Report the concepts changed, the validations run, and that the change is
   ready for `openspec archive <name>`.

## Completion criteria

Completion requires all implemented behavior represented by the change to be
either captured in canonical knowledge or intentionally excluded as non-durable,
with both knowledge and OpenSpec validation passing.
