---
type: Coding Convention
title: JavaScript and TypeScript conventions
description: Language-level rules for typed, explicit, and maintainable frontend code.
tags: [coding-convention, javascript, typescript, frontend]
status: active
---

# JavaScript and TypeScript

These rules apply before a framework extension.

- Prefer TypeScript for new application code when the repository supports it.
- Type public boundaries: API responses, component props, event payloads, and shared utilities.
- Model meaningful variants with discriminated unions or explicit result types. Do not hide uncertainty behind `any`, broad casts, or non-null assertions.
- Distinguish `null`, `undefined`, empty values, and absent fields at the boundary. Do not add optional chaining that hides a broken contract.
- Handle rejected promises and cancellation where the caller can observe failure.
- Keep exported functions and components before module-private helpers where practical. Keep private class methods after the public API.
- Prefer existing utilities and platform features before adding a dependency or a wrapper.
- Keep constants at the lowest common ancestor that uses them. Do not create a global constant for a one-call value.
- Keep error objects and response shapes explicit. Do not assume every caught value has the same fields.
