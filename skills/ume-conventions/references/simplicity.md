---
type: Coding Convention
title: Simplicity and comments
description: Prefer the smallest clear design and keep production comments rare.
tags: [coding-convention, simplicity, comments, ponytail]
status: active
---

# Simplicity

Be a lazy senior developer: remove work that does not need to exist, but understand the full problem before simplifying it.

Keep code terse and clear. Production comments are exceptional. A comment earns
its place only when the code would otherwise be misleading and the reason is
local, precise, and impossible to express with a name, type, test, or structure.

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

Default to no explanatory comment in production code. A comment is not
automatically acceptable just because it explains **why**. Keep one only for:

- public API documentation that defines a caller contract or generated documentation;
- a concise local invariant or compatibility, security, accessibility, or
  correctness constraint that cannot be expressed in code; or
- an unavoidable local workaround whose failure mode is not otherwise visible.

Comments that describe domain behavior, product decisions, architecture,
operational policy, external-system behavior, thresholds, calibration, history,
or tradeoffs belong in the repository's canonical `knowledge/` or decision
records. Comments that narrate control flow, restate a function name, describe
an obvious line, or record untracked future intent should be deleted. Improve
the name, structure, test, or knowledge placement first.

When a comment contains durable rationale, update or create the relevant
knowledge concept instead of keeping the rationale beside the code. Do not add
a code comment merely to point at knowledge; make the code and knowledge
discoverable through their normal names and indexes.

Keep public API documentation only when it defines a caller contract or
generated documentation. Do not repeat the signature or implementation. Remove
or update stale comments when behavior changes.

## Safety boundary

Never simplify away input validation at a trust boundary, error handling that prevents data loss, authorization, security controls, accessibility behavior, or a load-bearing domain boundary. Mark a deliberate shortcut with its known ceiling and upgrade path when the project accepts the tradeoff.
