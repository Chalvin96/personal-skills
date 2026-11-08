---
type: Coding Convention
title: Domain data and its owners
description: One authoritative representation per domain state, validation at the boundary, typed compound service inputs, code placed with its owner, and effects owned by the operation that causes them.
tags: [coding-convention, data-modeling, pydantic, placement]
status: active
---

# Data shape and ownership

These rules decide what a piece of data is, who is allowed to check it, and
which module owns what happens because of it. They apply across the stack:
a Pydantic schema, an ORM model, a service signature, or a TypeScript type can
each be the place a mistake lands.

## Domain shape

- Keep one authoritative representation of each domain state. A status stored
  once, with its meaning in one place, beats two boolean columns that must be
  kept in sync by every writer.
- Prefer an enum (a Python `enum`, a typed SQLAlchemy enum, or a check
  constraint) over loose strings compared in scattered conditionals, and over
  flag pairs whose invalid combinations are representable. Invalid states
  should be hard to construct or hard to persist.
- Derive values at read time when persisting them would add a consistency
  rule nobody wants to maintain (a total computed from quantity and unit
  price, a display name assembled from parts).
- Reuse the repository's existing models, enums, and vocabulary before adding
  a parallel representation. A second representation of the same state is a
  defect waiting for its first drift.
- Reach for a state machine, a registry, or a new abstraction layer only when
  the simple representation has actually failed; otherwise keep the shape
  ordinary and the change inside the task.

## Boundary validation

- Validate untrusted input once, at the edge, with Pydantic request models at
  the route. Services receive typed, already-validated objects.
- Inside the boundary, trust the types and do not re-validate in every layer.
  When a service genuinely must defend itself, that is a signal it serves two
  kinds of callers; make the split explicit instead of copying checks.
- A static type is never a reason to drop a runtime check the behavior depends
  on: authorization, persisted-state checks, and framework validation stay
  even when the types line up.
- Fix the representation instead of silencing it: `Any`, narrowing casts, and
  non-null assertions that hide a mismatch are findings, not conveniences.

## Service inputs

- When an operation needs compound input, pass a named typed object (a Pydantic
  model or a dataclass) with one field per input. Routers, adapters, and job
  runners construct it from their own payload; the operation reads its
  declared fields and never a transport dictionary or raw request body.
- A wrapper that accepts an arbitrary payload is not a contract; the fields
  are the contract, and each one should be visible in the signature.
- Partial updates are explicit. An update operation states which fields it
  changes and treats "not provided" as different from "explicitly cleared"
  when both are meaningful; it writes only the intended fields, which is also
  the rule in [state written by more than one writer](reliability.md#state-written-by-more-than-one-writer).
- An optional field must behave correctly when a real caller omits it, not
  only when the one current adapter always supplies a value. Construct the
  minimal input directly and check what the operation does with the omission.

## Placement

- Code lives with the owner of the behavior it implements. Domain rules,
  writes, and invariants belong in the domain service; request parsing and
  response mapping in the router; payload shape in the schema. The backend
  specifics are in
  [FastAPI routes and schemas](fastapi.md#routes-and-schemas) or
  [Django](django.md).
- A new module is justified by a cohesive responsibility with its own tests,
  not by a wish to keep files small. A one-function module beside the service
  that should own the function is a placement finding.
- On the frontend, shared types and constants live with the API layer or the
  module that owns the concept; component-local state stays in the component.
  Do not create a shared module for one consumer.

## Effect ownership

- The service operation owns its side effects: notifications, jobs, cache
  invalidations, and external calls that the operation's name promises.
  Several features calling the same helper does not make that helper the
  owner of a new effect.
- Give an ORM event, a model hook, or a shared helper a side effect only
  when every path through it should fire that effect, and decide whether the
  effect's failure should stop the operation. An effect that belongs to one
  action stays with that action's operation, not with the shared plumbing.
- Views and routers stay thin: they do not own writes, notifications, or
  external calls; they hand off to the operation that does. A write buried in
  a read path is an ownership defect regardless of where the code sits.
- When reviewing, report a concrete misplaced effect or duplicate source of
  truth with its caller-visible impact; do not demand a subsystem redesign
  for a working scoped change.
