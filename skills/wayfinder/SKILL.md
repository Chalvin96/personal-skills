---
name: wayfinder
description: Map a large uncertain product or implementation effort as decision tickets. Use explicitly to find the next evidence, settle one decision at a time, and plan implementation only after the product direction is supported.
---

# Wayfinder

Wayfinder finds the route to a named decision or build. It is planning work. Do
not change production code while using it. First decide which stage the effort
is in. Keep an untested product idea out of implementation cycles.

## Choose the stage

- **Product discovery:** The user, problem, value, or demand is still uncertain.
  Make an ignored local map under `plans/<effort>/`. Its destination is a product
  decision and the evidence needed to make it. Do not create OpenSpec behavior
  specs, a TRD, or build cycles from an untested product guess.
- **Implementation planning:** The intended user behavior is agreed, but material
  implementation choices remain. Use the repository's OpenSpec
  `wayfinder-driven` change. Read the proposal and behavioral specs first. The
  destination is a technical design and dependency-safe implementation cycles.

Read the target repository's `AGENTS.md` and canonical knowledge first. Put the
map in the repository that owns the planned behavior. If that repository has a
stricter planning location, follow it. Link prior research instead of copying
its conclusions into several files.

## The map and tickets

The map is an index. Give it a short **Destination**, **Notes**, **Decisions so
far**, **Open tickets**, **Not yet specified**, and **Out of scope**. A decision
lives in its ticket; the map links to it with a one-line summary. Refer to a
ticket by its linked title in anything the user reads, not by a bare ID.

Use stable `D-001`, `D-002`, ... IDs. A ticket records its question, type,
status, blockers, evidence needed, and decision rule. Once resolved, record the
evidence, options, decision, and consequences in that same ticket. Mark a
deferred ticket nonblocking and say why. Do not ticket obvious mechanics.

Ticket types are:

- `research`: inspect code, data, documents, or outside sources to answer a
  factual question. An agent can do this alone.
- `prototype`: make a cheap artifact that a real user can react to. The user's
  reaction is evidence; the agent cannot invent it.
- `grilling`: settle a choice that requires the user's preference or authority.
  Use `$grill-me` when its interview method helps. Never answer for the user.
- `task`: perform specific work that unlocks a decision, such as a data audit or
  a recruited user session. Name who must do it and the completion evidence.

Blocking means the destination cannot be reached until this ticket is resolved.
For product discovery, make each gate observable. State what a failed result
changes. Counts from a small pilot are decision aids, not proof of learning or
market size. Contacting participants or publishing material still needs the
authorization required by the host and repository.

## Chart a map

1. Read the prior plan, relevant knowledge, current product behavior, and any
   existing map. Name one destination. If the owner or destination is unclear,
   ask only the decision that cannot be inferred from those sources.
2. List the sharp questions that block the destination. Put vague future areas
   under **Not yet specified**. Put work beyond the destination under **Out of
   scope**. A sharp question is a ticket even if another ticket blocks it.
3. Create ticket files, then add dependencies. Keep the frontier small enough
   to see what can be done now. Do not create a task for every possible feature.
4. Stop after charting. Show the user the map, the first unblocked decision, and
   the evidence that will settle it. Charting does not count as a product win.

## Resolve a ticket

Choose one unblocked ticket and mark it claimed before work. Research tickets
can be resolved together when their work is independent. Inspect only the
evidence needed for the question. Record sources and limitations. For a human
ticket, wait for the actual human input or observed use. Record the answer in
the ticket, close it, and add one linked line to **Decisions so far**. Move any
newly sharp questions out of **Not yet specified** into tickets. Revisit the
destination if the evidence changes the product direction.

## Product discovery handoff

After every blocking discovery ticket closes, write a short decision record:
what was observed, what failed, what passed, and the next action. If the product
bet passes, start a separate implementation plan in the consuming product's
OpenSpec workflow. If it fails, record the stop or change of direction. Do not
turn a failed pilot into more feature work by default.

## Implementation planning in OpenSpec

Work inside the selected `openspec/changes/<change>/`:

- `tickets/index.md` holds the destination, status, fog, and decision links.
- `tickets/D-*.md` holds material implementation decisions with stable IDs.
- `trd.md` is the one consolidated technical design.
- `tasks/C-*.md` are independently verifiable implementation cycle packets.
- `tasks.md` alone tracks cycle status with checkboxes.
- `artifacts/ui/<D-id>/` holds accepted visual evidence when relevant.

Use the installed `wayfinder-driven` schema templates. Trace behavioral
requirement → decision → TRD → cycle. Chart only material choices: data,
architecture, migration, rollout, security, performance, integration, and UI
behavior. For UI tickets, read the project's design system and use `$grill-me`
for human decisions. After all blocking tickets are closed, integrate their
decisions into the TRD, write dependency-safe cycles with tests, rollback, and
stop conditions, then run OpenSpec strict validation and
`wayfinder-validate <change-dir>`. Hand off to `openspec-apply-change`; do not
implement within Wayfinder.
