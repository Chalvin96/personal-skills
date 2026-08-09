---
name: wayfinder
description: Resolve implementation uncertainty as local decision tickets inside an OpenSpec change. Use after proposal/specs when material implementation choices remain. Consolidates decisions into a TRD and dependency-safe cycles without GitHub issues.
---

# Local Wayfinder

Plan implementation; do not implement production code. The pull to just do the
work is the signal you have reached the edge of the map — hand off instead.

## Artifacts

Work only inside `openspec/changes/<change>/`:

- `tickets/index.md`: destination, decision index, status ledger, fog, out of scope.
- `tickets/D-*.md`: question, evidence, options, decision, consequences.
- `trd.md`: sole consolidated implementation design.
- `tasks.md`: sole cycle status ledger.
- `tasks/C-*.md`: stateless executor packets; no checkboxes.
- `artifacts/ui/<D-id>/`: accepted visual evidence.

Use stable IDs and requirement → decision → TRD → cycle traceability. Never use
GitHub issues. Do not create tickets for obvious mechanics.

`tickets/index.md` is an index, not a store: a decision lives in exactly one
place — its ticket — so the index gists it and links, never restates it.

## Refer by name

In everything the user reads, name a ticket by its title, never by a bare id. A
wall of `D-001, D-002, D-003` is illegible; names read at a glance. The id rides
inside the name and never stands in for it.

## Index sections

- **Destination** — what reaching the end of this map looks like. Name it first;
  it fixes the scope and shapes every ticket.
- **Decisions so far** — one line per CLOSED ticket, linked.
- **Open tickets** — id, name, type, status, blocking, depends_on.
- **Not yet specified** — in-scope fog.
- **Out of scope** — work ruled beyond the destination.

## Ticket types

Every ticket is **HITL** (worked with the user, who speaks for themselves) or
**AFK** (agent alone). Never answer the human's side of a HITL ticket.

| Type | Mode | Use when |
|---|---|---|
| `research` | AFK | A fact outside the working directory blocks a decision. Resolve in a subagent. |
| `prototype` | HITL | "How should it look or behave" is the question. Build a cheap artifact to react to and link it under `artifacts/`. |
| `grilling` | HITL | Conversation. The default case. Always invoke `$grill-me`. |
| `task` | either | Manual work unblocking a decision — provisioning access, moving data so its shape can be seen. Records what was done and the facts later tickets depend on. |

Record the type in ticket frontmatter `type:`.

## Fog of war

The map is deliberately incomplete. Beyond the live tickets lies fog: decisions
you can tell are coming but cannot yet pin down. Resolving a ticket clears the
fog ahead of it and graduates whatever is now specifiable into fresh tickets.

The test is whether you can state the question precisely **now** — not whether
you can answer it now.

- **Ticket** when the question is already sharp, even if blocked.
- **Not yet specified** when you cannot phrase it that sharply. Do not pre-slice
  fog into ticket-sized pieces; one patch may graduate into several tickets, or
  none.

## Out of scope

Fog gathers only toward the destination, so work past it is out of scope, not
fog. When an existing ticket turns out to sit past the destination, close it and
leave one line under **Out of scope** with the gist and why. It stays out of
**Decisions so far**, which records the route actually walked.

Out-of-scope work never graduates. It returns only if the destination is
redrawn, and then as a fresh change.

## Chart

1. Read proposal, specs, canonical knowledge, and relevant code.
2. Name the destination in `tickets/index.md`.
3. Map the frontier with `$grill-me`, **breadth-first** — fan out across the
   space rather than deep on one thread. If no fog surfaces, the way is already
   clear: stop and tell the user no map is needed.
4. Create only sharp material decisions: architecture, data, migration, rollout,
   security, performance, integration seams, or UI behavior.
5. Write `D-*.md` files from the schema template, then wire `depends_on` in a
   **second pass** — ids must exist before they can reference each other.
6. Sketch everything still vague into **Not yet specified**.
7. Fire the `research` tickets as parallel subagents.
8. Stop. Charting resolves nothing.

## Resolve one ticket

Never resolve more than one ticket per session — `research` excepted.

1. Select one unblocked, unclaimed ticket from `tickets/index.md`; claim it.
2. Investigate only enough to answer its question. Zoom on demand: read a
   related or closed ticket's body only when you need it.
3. Record evidence, rejected options, decision, and consequences in that ticket.
4. Mark it CLOSED and ready for integration, and append one line to **Decisions
   so far**. DEFERRED is allowed only when non-blocking and justified.
5. One integrator incorporates closed decisions into `trd.md` and marks them
   integrated. Parallel ticket agents must not edit overlapping TRD sections.
6. Graduate any fog the answer sharpened, clearing that patch from **Not yet
   specified**. Rule newly out-of-scope work out rather than resolving it. If
   the decision invalidates other tickets, update or delete them.

Expect concurrent sessions on unblocked tickets.

## UI decisions

Every UI ticket uses `$grill-me`. Read the project's design-system knowledge
first. Use `grill-me/visual-companion.md` for materially visual questions. Store
accepted assets under `artifacts/ui/<D-id>/`; express behavior, responsive
rules, accessibility, and components textually in the ticket and TRD.

## Consolidate and cycle

When all blocking tickets are CLOSED and integrated:

1. Consistency-check the TRD and its requirement/decision traceability.
2. Mark the TRD IMPLEMENTATION-READY, not frozen; new evidence may reopen a ticket.
3. Split work into dependency-safe, independently verifiable cycles.
4. Write `tasks/C-*.md` packets with outcome, scope, procedure, exact tests and
   commands, rollback, and stop conditions.
5. Generate `tasks.md` with one checkbox per cycle.
6. Run OpenSpec strict validation and `wayfinder-validate <change-dir>`.
7. Hand off to `openspec-apply-change`; do not implement here.
