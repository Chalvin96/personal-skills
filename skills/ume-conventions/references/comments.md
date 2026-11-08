---
type: Coding Convention
title: Comment discipline
description: Comments only for the non-obvious why; suppressions carry the exact rule and a reason; durable rationale moves to knowledge docs.
tags: [coding-convention, comments, suppressions]
status: active
---

# Comments and suppressions

The test for every comment: would a competent reader with the code in front of
them reach a wrong conclusion without it? If not, delete it.
[simplicity.md](simplicity.md) owns the wider comment and knowledge-placement
policy; this file adds the suppression rules and the shared dispositions.

## What a comment may keep

- A constraint the code cannot state: why this value, this order, or this
  awkward call is required by something outside the file (a protocol quirk, a
  provider limit, a platform behavior, a security or accessibility
  requirement).
- A deliberate trade-off with a known ceiling, kept short, when no name, type,
  test, or structure can carry it.
- Public API documentation that defines a caller contract, and links to a
  decision record or issue that explains a constraint.

## What must go

- Narration: restating what the next statement obviously does.
- Commented-out code, section banners, and TODOs with no owner or action.
- Domain behavior, product rules, thresholds, history, and operational policy
  written as comments; these belong in the repository's knowledge area. Move
  them there instead of leaving them beside the code, per
  [simplicity.md](simplicity.md#comments-and-knowledge).
- A comment that a better name, type, or test would make redundant. Improve
  the code first; keep the comment only when that is genuinely unavailable.

Before deleting a comment that claims to protect something, check nearby code
and recorded rationale: if the constraint is real, encode it in a test or
knowledge doc rather than silently removing both the comment and the safety
it described.

## Suppressions

A suppression is a comment too, and a stronger one: it turns a tool off.

- Every suppression names the exact rule it suppresses and why:
  `# noqa: UME-SEC001  # expression comes from the reviewed fixture file`,
  `// eslint-disable-next-line no-restricted-imports -- mirrors the vendor entry point`,
  `# type: ignore[attr-defined]  # the C extension does not ship stubs`.
- A bare suppression (`# noqa`, `# type: ignore`, `// eslint-disable` with no
  rule) is itself a finding. The mechanical checker already refuses bare
  suppressions for `UME-` rules; reviewers apply the same standard to every
  tool.
- Match the change to the suppression: one rule, one line, the narrowest form
  available (`noqa: UME-XXX`, not `noqa`; disable-next-line, not disable).
- Remove the suppression together with the fix when the underlying problem is
  corrected. Keep tool-required directives that are part of the file's
  contract (pragma statements a tool needs to function are configuration, not
  suppressions).
- If the same suppression appears repeatedly, that is a signal about the rule
  or the code; raise it instead of propagating it.
