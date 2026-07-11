---
name: openspec-archive-change
description: Archive a completed OpenSpec change after merging durable behavior into canonical knowledge. Requires the OpenSpec CLI. Use when finalizing a verified change without retaining current-state specs under openspec/specs.
---

Archive a completed change in the experimental workflow.

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

   Do not sync delta specs to `openspec/specs/`. If a matching capability spec
   already exists there, remove it only after its complete current behavior has
   been merged into knowledge.

5. **Perform the archive**

   Run `openspec archive "<name>" --skip-specs` with the selected store flag when
   applicable. Validate OpenSpec and canonical knowledge after the move.

6. **Display summary**

   Show archive completion summary including:
   - Change name
   - Schema that was used
   - Archive location
   - Knowledge concepts updated
   - Capability specs removed or skipped
   - Note about any warnings (incomplete artifacts/tasks)

**Output On Success**

```
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Archived to:** the archive path derived from `planningHome.changesDir`/YYYY-MM-DD-<name>/
**Knowledge:** ✓ Current behavior merged
**Specs:** ✓ Sync skipped; matching current-state specs removed

All artifacts complete. All tasks complete.
```

**Guardrails**
- Always prompt for change selection if not provided
- Use artifact graph (openspec status --json) for completion checking
- Don't block archive on warnings - just inform and confirm
- Preserve .openspec.yaml when moving to archive (it moves with the directory)
- Show clear summary of what happened
- Never sync archived change specs into `openspec/specs/`; canonical knowledge is
  the sole current-state source of truth.
