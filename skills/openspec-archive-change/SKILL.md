---
name: openspec-archive-change
description: Finalize a completed OpenSpec change by merging durable behavior and rationale into canonical knowledge, then removing the change artifacts and matching specs. Use when finishing verified work without retaining OpenSpec process history.
---

Finalize a completed change without retaining process history.

If the work is in a registered OpenSpec store, read [store selection](../_personal-shared/openspec-store-selection.md) before running commands.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec list --json` and ask the user to select.

   Show only active changes (not already archived).
   Include the schema used for each change if available.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check artifact completion status**

   For `wayfinder-driven`, also run
   `wayfinder-validate <change-dir>`.
   Refuse archive while a blocking ticket is unresolved or unintegrated, a
   cycle is incomplete, or traceability is invalid.

   Run `openspec status --change "<name>" --json` to check artifact completion.

   Parse the JSON to understand:
   - `schemaName`: The workflow being used
   - `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`: path and scope context
   - `artifacts`: List of artifacts with their status (`done` or other)

   **If any artifacts are not `done`:**
   - Display warning listing incomplete artifacts
   - Ask the user to confirm they want to proceed
   - Proceed if user confirms

3. **Check task completion status**

   Read the tasks file (typically `tasks.md`) to check for incomplete tasks.

   Count tasks marked with `- [ ]` (incomplete) vs `- [x]` (complete).

   **If incomplete tasks found:**
   - Display warning showing count of incomplete tasks
   - Ask the user to confirm they want to proceed
   - Proceed if user confirms

   **If no tasks file exists:** Proceed without task-related warning.

4. **Enforce the knowledge gate**

   Use `artifactPaths.specs.existingOutputPaths` to enumerate changed
   capabilities. Read the completed implementation, change specs, and canonical
   knowledge. Refuse archival until every durable behavior is captured in the
   smallest relevant knowledge concepts and the knowledge validator passes.

   Do not sync delta specs to `openspec/specs/`. Capture important rationale in
   the relevant concept or decision record. If a matching capability spec already
   exists, remove it only after its complete current behavior is in knowledge.

5. **Remove completed artifacts**

   Remove `openspec/changes/<name>/` and matching capability directories under
   `openspec/specs/`. Do not create or retain a dated archive directory. Validate
   OpenSpec and canonical knowledge after removal.

6. **Display summary**

   Show archive completion summary including:
   - Change name
   - Schema that was used
   - Removed change path
   - Knowledge concepts updated
   - Capability specs removed or skipped
   - Note about any warnings (incomplete artifacts/tasks)

**Output On Success**

```
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Removed:** the completed active change and matching capability specs
**Knowledge:** ✓ Current behavior merged
**Specs:** ✓ Matching current-state specs removed

All artifacts complete. All tasks complete.
```

**Guardrails**
- Always prompt for change selection if not provided
- Use artifact graph (openspec status --json) for completion checking
- Don't block archive on warnings - just inform and confirm
- Show a clear summary of what was removed and where durable knowledge lives
- Never retain completed change artifacts or sync them into `openspec/specs/`;
  canonical knowledge is the sole current-state source of truth.
