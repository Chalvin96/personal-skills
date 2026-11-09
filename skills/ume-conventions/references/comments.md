---
type: Coding Convention
title: Comment discipline
description: Comments only for the non-obvious why; suppressions carry the exact rule and a reason; durable rationale moves to knowledge docs.
tags: [coding-convention, comments, suppressions]
status: active
---

# Comments and suppressions

[simplicity.md](simplicity.md#comments-and-knowledge) owns comment discipline
and knowledge placement. This file adds suppression rules.

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
