---
name: wayfinder
description: Resolve implementation uncertainty as local decision tickets inside an OpenSpec change. Use after proposal/specs when material implementation choices remain. Consolidates decisions into a TRD and dependency-safe cycles without GitHub issues.
---

# Local Wayfinder

Plan implementation; do not implement production code.

## Artifacts

Work only inside `openspec/changes/<change>/`:

- `tickets/index.md`: sole ticket status ledger.
- `tickets/D-*.md`: evidence, options, decision, consequences.
- `trd.md`: sole consolidated implementation design.
- `tasks.md`: sole cycle status ledger.
- `tasks/C-*.md`: stateless executor packets; no checkboxes.
- `artifacts/ui/<D-id>/`: accepted visual evidence.

Use stable IDs and requirement → decision → TRD → cycle traceability. Never use
GitHub issues. Do not create tickets for obvious mechanics.

## Chart

1. Read proposal, specs, canonical knowledge, and relevant code.
2. Name the destination: the TRD and cycles are implementation-ready.
3. Create only sharp material decisions: architecture, data, migration, rollout,
   security, performance, integration seams, or UI behavior.
4. Write `tickets/index.md`, then `D-*.md` files using the schema template.
5. Add dependencies after ticket IDs exist. Stop after charting.

## Resolve one ticket

1. Select one unblocked, unclaimed ticket from `tickets/index.md`; claim it.
2. Investigate only enough to answer its question.
3. Record evidence, rejected options, decision, and consequences in that ticket.
4. Mark it CLOSED and ready for integration. DEFERRED is allowed only when
   non-blocking and justified.
5. One integrator incorporates closed decisions into `trd.md` and marks them
   integrated. Parallel ticket agents must not edit overlapping TRD sections.
6. Add newly sharp decisions; keep vague future questions out of the ticket set.

## UI decisions

Every UI ticket uses the Superpowers brainstorming loop through `$grill-me`.
Read the project's design-system knowledge first. Use
`grill-me/visual-companion.md` for materially visual questions. Store accepted
assets under `artifacts/ui/<D-id>/`; express behavior, responsive rules,
accessibility, and components textually in the ticket and TRD.

## Consolidate and cycle

When all blocking tickets are CLOSED and integrated:

1. Consistency-check the TRD and its requirement/decision traceability.
2. Mark the TRD IMPLEMENTATION-READY, not frozen; new evidence may reopen a ticket.
3. Split work into dependency-safe, independently verifiable cycles.
4. Write `tasks/C-*.md` packets with outcome, scope, procedure, exact tests and
   commands, rollback, and stop conditions.
5. Generate `tasks.md` with one checkbox per cycle.
6. Run OpenSpec strict validation and the mechanical Wayfinder validator.
7. Hand off to `openspec-apply-change`; do not implement here.
