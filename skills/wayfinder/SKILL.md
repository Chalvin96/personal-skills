---
name: wayfinder
description: Chart a large, uncertain engineering initiative as a small GitHub-issue decision map before implementation. Use when a destination spans multiple agent sessions, key decisions remain unknown, or the user asks to explore, map, or wayfind a broad effort. Routes resolved implementation work into OpenSpec and durable current state into the repository's canonical knowledge system.
---

# Wayfinder

Use Wayfinder to make an uncertain destination navigable. It is for discovery and
decisions, not for implementation. If the work is already concrete enough for a
single OpenSpec change, skip Wayfinder and use the OpenSpec workflow directly.

## Canonical artifacts

- Discover and read the repository's canonical knowledge source (for example
  `knowledge/`, `docs/`, or `AGENTS.md`) before charting or resolving a ticket.
- Use one GitHub issue labelled `wayfinder:map` as the map and child issues for
  its decision tickets. Use `gh issue`; names and links are clearer than bare
  issue numbers in user-facing text.
- Keep the map concise: destination, notes, closed decisions with links, unknown
  in-scope questions, and out-of-scope boundaries.
- When a decision is implementation-ready, create or update an OpenSpec change.
  Do not put proposals, task history, or investigations into `knowledge/`.
- After an implemented change is verified and archived, update only the
  repository's canonical current-state knowledge.

## Mechanical preferences

- Prefer mechanical, deterministic enforcement over review-only conventions.
- For a proposed rule, state its executable check, command, scope, exceptions,
  baseline, and failure behavior before calling it decided.
- Treat existing violations explicitly: migrate them, document a temporary
  ratchet, or rule them out. Do not silently grandfather them.
- Adopt repository-specific test naming only when it has a deterministic checker
  and a documented migration strategy.
- Keep one ticket to one answer that fits an agent session. Do not create tickets
  for foggy questions.

## Map template

```markdown
## Destination

<A concrete end state in one or two sentences.>

## Notes

<Relevant knowledge concepts, OpenSpec changes, constraints, and skills.>

## Decisions so far

- [<closed ticket title>](<link>) — <one-line durable answer>

## Not yet specified

<In-scope questions not yet sharp enough to ticket.>

## Out of scope

<Explicit exclusions and why.>
```

## Chart a map

1. Establish the destination. Use `$grill-me` when product, domain, or design
   choices are materially unresolved.
2. Read relevant knowledge and inspect the codebase for the current baseline.
3. Create the map issue and only the sharp, answerable child tickets. Label each
   `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or
   `wayfinder:task`; add dependency links after creation.
4. Record unknown but in-scope areas under **Not yet specified** rather than
   pretending they are ready tickets.
5. Stop after charting. Do not implement during the mapping session.

## Resolve one ticket

1. Load the map, choose one unblocked ticket, and assign it before starting.
2. Read the ticket, its relevant knowledge, and linked OpenSpec artifacts.
3. Investigate only enough to answer its question. For rule proposals, prove the
   baseline with the actual command or a deterministic audit.
4. Post the resolution as a GitHub comment, close the ticket, and add a one-line
   linked decision to the map.
5. Add only newly sharp questions as tickets; move genuine exclusions to **Out
   of scope**.
6. If the route is now clear, create a validated OpenSpec proposal. Do not
   implement in Wayfinder.

## Completion

The map is complete when no decision blocks a well-scoped OpenSpec change. Report
the destination, linked decisions, remaining exclusions, and the OpenSpec change
to apply next.
