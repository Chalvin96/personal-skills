---
type: Coding Convention
title: Reliability under repetition and sharing
description: Rules for work that can run twice, crash halfway, or race with other writers, and for removing shared interfaces without breaking consumers.
tags: [coding-convention, reliability, idempotency, concurrency, compatibility]
status: active
---

# Reliability

These rules follow failure, not file type. A queue consumer, a webhook
handler, a background task, or a state transition can carry a repeat or a race
even though nothing else in the diff looks concurrent. Load the section that
matches the changed behavior.

## Work that can arrive twice or stop midway

Treat any job, callback, or retryable request as if it can arrive more than
once and can stop between any two of its effects.

- Name the guard that makes a repeated run safe: an idempotency key, a
  guarded state transition, or a uniqueness constraint that absorbs the
  duplicate. A transaction around the work is not itself the answer, because
  the transaction may commit before the process dies, and a retry starts a
  new one.
- State what a second delivery of the same request leaves behind: the same
  visible result and no duplicate effect, or a rejected duplicate. Write the
  answer down in the change, not only in someone's head.
- A database rollback does not reverse an HTTP response already sent, a
  message already published, or a cache already invalidated. When a partial
  failure around such an external effect matters, choose and name the
  boundary: emit the effect only after local state commits, or make the
  receiving side idempotent on a stable key.
- When a crash can land between two durable writes, say which write survives
  alone and what a retry or reconciliation step does to finish the operation.
- When the change creates or widens this risk (a new consumer, a new
  transition, a new external call in a flow that retries), add one focused
  regression check for the duplicate delivery or the partial state. Do not
  attach concurrency or retry tests to ordinary edits that never expose the
  risk.

## State written by more than one writer

Start by naming the writers that can actually run at the same time. Rules
follow from that list, not from a general worry about concurrency.

- When two writers produce independent results, give them separate owned
  rows, keys, or files instead of one shared record they both overwrite.
- When one canonical record is a real invariant, enforce it with a mechanism
  the repository already uses: `SELECT ... FOR UPDATE`, an optimistic version
  column with a conditional `UPDATE ... WHERE version = :expected`, or a
  uniqueness constraint that makes the race lose cleanly. A comment asking
  callers not to race is not synchronization.
- Write only the fields the caller intends to change. In SQLAlchemy, assign
  the changed attributes on a freshly loaded instance; re-attaching or merging
  a whole stale object flushes every field it carries and silently reverts a
  concurrent writer's unrelated update.
- When concurrent writers really share this path, verify through the real
  caller that somebody else's newer value is still there after the intended
  edit writes its fields.
- Keep a lock only as long as the invariant needs it, and keep required locks;
  partitioning one writer's data is an option only when the domain genuinely
  permits it.

## Removing a shared interface

Before replacing or deleting an interface other code consumes, inventory the
consumers: modules in this repository, sibling services, stored records and
payloads, public API clients, and deployed frontends. A name search that
returns nothing is weak evidence, not proof of zero consumers.

- Migrate in three steps: expand (add the new shape), migrate callers, then
  contract (remove the old shape). Never delete the shared interface before
  the consumers that matter have moved.
- Consumers that deploy independently cannot be migrated atomically. Keep both
  shapes working for the overlap window, name the rollout assumption (every
  consumer at or past revision X before removal), and check it against
  reality rather than hoping.
- Stored records outlive deploys: a renamed payload field needs a reader that
  still accepts old records, or a migration that rewrites them first.
- Do not weaken or delete tests to make the removal look complete, and do not
  keep a compatibility shim the repository no longer needs without a stated
  consumer.
