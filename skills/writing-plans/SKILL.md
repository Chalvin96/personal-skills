---
name: writing-plans
description: Turn agreed intent into an OpenSpec proposal and behavioral specs, then use local Wayfinder tickets to produce a TRD and implementation cycles. Use before implementation when product requirements are sufficiently clear.
---

# Wayfinder-driven OpenSpec planning

1. Read canonical knowledge and existing change context. Use `$grill-me` when
   product behavior remains unresolved.
2. Create new changes with:
   `openspec new change <name> --schema wayfinder-driven`.
   Preserve existing changes on their current schema unless migration is explicit.
3. Follow `openspec status` and `openspec instructions` for every artifact.
4. Write proposal and behavioral specs first. Requirements own observable
   behavior; do not invent implementation details to make the change apply-ready.
5. Invoke `$wayfinder` for material implementation decisions. It creates local
   `tickets/`, integrates decisions into `trd.md`, and derives `tasks/C-*.md`
   cycle packets plus the `tasks.md` manifest.
6. UI tickets use `$grill-me`; materially visual decisions use its visual
   companion after reading the project design system.
7. End cycles with canonical knowledge updates and repository-specific validation.
8. Run:
   `openspec validate <name> --strict`
   and
   `wayfinder-validate <change-dir>`.
9. Report the change and first dependency-ready cycle. Do not implement here.

## Guardrails

- Split unrelated capabilities into separate changes.
- Specs own behavior; tickets own investigations; TRD owns implementation
  design; cycle packets own executor instructions; tasks.md alone owns status.
- Blocking tickets must be closed and integrated before cycles are created.
- Existing active changes are not bulk-migrated.
