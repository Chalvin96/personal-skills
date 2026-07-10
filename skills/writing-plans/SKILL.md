---
name: writing-plans
description: Turn an agreed feature, non-trivial bug fix, or architectural change into validated OpenSpec proposal, design, behavioral specs, and tasks. Use before implementation when requirements are sufficiently clear.
---

# OpenSpec Planning

Write the implementation plan as OpenSpec artifacts.

## Workflow

1. Announce: "I'm using the writing-plans skill to create the implementation
   plan."
2. Discover and read the repository's canonical knowledge source and any OpenSpec change selected by
   the user. Use `$grill-me` first when material product or design decisions are
   still unresolved.
3. Reuse a named active change, or create one with a concise kebab-case name:

   ```bash
   openspec new change <name>
   openspec status --change <name> --json
   ```

4. Create every apply-required artifact in the dependency order reported by
   `status`. Before each artifact, get its current template and rules:

   ```bash
   openspec instructions <artifact> --change <name> --json
   ```

   - `proposal.md`: why, scope, capability names, and impact.
   - `specs/<capability>/spec.md`: observable SHALL requirements and testable
     scenarios; use delta headings when modifying an existing capability.
   - `design.md`: decisions, alternatives, risks, migration, and affected knowledge.
   - `tasks.md`: small ordered checkboxes with exact files, tests, and commands.

5. If the repository has canonical current-state knowledge, the final task group
   MUST update affected concepts using that repository's validator. Keep proposal
   and task history in OpenSpec.
6. Validate before offering implementation:

   ```bash
   openspec validate <name> --strict
   ```

7. Report the change name and state that `/opsx:apply <name>` is the next step.
   Do not implement production code in this skill.

## Guardrails

- Split unrelated capabilities into separate changes.
- Keep requirement behavior in specs and implementation mechanics in design/tasks.
- Do not archive until tasks, implementation verification, and required knowledge updates pass.
