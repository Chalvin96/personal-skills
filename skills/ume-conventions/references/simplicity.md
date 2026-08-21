---
type: Coding Convention
title: Simplicity and comments
description: Prefer the smallest clear design and keep comments focused on why.
tags: [coding-convention, simplicity, comments, ponytail]
status: active
---

# Simplicity

Be a lazy senior developer: remove work that does not need to exist, but understand the full problem before simplifying it.

## Ponytail ladder

Stop at the first rung that solves the real problem:

1. Does this need to exist at all?
2. Does the repository already have the behavior or abstraction?
3. Can the standard library solve it?
4. Can the platform or framework solve it?
5. Can an already-installed dependency solve it?
6. Can the design be smaller without losing clarity?
7. Write the minimum code that remains.

Deletion is preferred to addition. Reuse is preferred to a second name and a second implementation. Do not add an interface with one implementation, a factory for one product, configuration for a value that never changes, or scaffolding for a future need.

## Comments and knowledge

Comments explain **why**, not **how**. Use them for:

- intent that is not visible in the code;
- an invariant or compatibility constraint;
- a non-obvious failure mode;
- a deliberate tradeoff and its known limit; or
- a security, performance, or correctness reason that a future maintainer must not remove.

Do not use a comment to narrate control flow, restate a function name, or describe an obvious line. Improve the name, structure, or extraction first.

Durable system behavior, architecture, operational knowledge, and decisions belong in the repository's canonical knowledge or decision records. Edit that knowledge instead of adding a local comment when the fact applies beyond the line or file. Keep a local comment only when the explanation is local and the code cannot express it clearly.

Keep public API documentation when it defines a caller contract or generated documentation. Do not repeat the signature or implementation. Remove or update stale comments when behavior changes.

## Safety boundary

Never simplify away input validation at a trust boundary, error handling that prevents data loss, authorization, security controls, accessibility behavior, or a load-bearing domain boundary. Mark a deliberate shortcut with its known ceiling and upgrade path when the project accepts the tradeoff.
