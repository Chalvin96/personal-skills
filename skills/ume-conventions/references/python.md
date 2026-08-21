---
type: Coding Convention
title: Python conventions
description: Language-level rules for readable, typed, safe Python code.
tags: [coding-convention, python]
status: active
---

# Python

These rules apply to Python regardless of web framework.

## Boundaries and errors

- Type public function inputs and outputs when the project supports typing. Keep types honest; do not use `Any` to hide an unclear boundary.
- Raise or translate errors at a clear boundary. Do not catch `Exception` unless the code logs enough context and has a deliberate recovery path.
- Use context managers for files, locks, and resources that need cleanup.
- Use timezone-aware UTC values for instants. Compute one current time per flow and reuse it when consistency matters.
- Give external network calls an explicit timeout and bounded retry behavior.
- Avoid mutable default arguments and hidden global state.
- Use a bare `*` in a function signature when parameters should be keyword-only, especially when positional order would be unclear or future optional parameters should not break callers. Use `*args` or `**kwargs` only when arbitrary arguments are part of the contract; prefer explicit parameters otherwise.
- Represent expected domain outcomes with explicit typed values when callers must
  distinguish them. Reserve exceptions for failure paths, and use a typed
  project exception hierarchy instead of several boolean or `None` sentinels.

## Structure and naming

- Put public module functions before private helpers.
- Inside a class, put the constructor and public methods before `_private` helpers. Keep private helpers at the bottom unless a framework lifecycle requires another order.
- Name a function for the value it returns, not for a vague action. Avoid
  `get_`, `handle_`, `process_`, `manage_`, and `do_` when a value name is
  clearer. Use question- or adjective-shaped names for predicates.
- Make exception behavior visible: use `_or_raise` for a value-or-exception
  helper and `find_` for a helper that may return `None`. Do not hide a raise
  behind an innocuous accessor name.
- Prefer small composable functions, unabbreviated names, and clear control
  flow over cleverness or needless mutation.
- Encode stable invariants in types, enums, dataclasses, relationships, or
  database constraints when possible. Do not use several sentinel values for
  distinct outcomes when a typed result or exception can make them explicit.
- Keep one responsibility per function. Extract only when the new boundary makes behavior easier to understand or test.
- Prefer the standard library and existing project utilities before adding a dependency.

## Tests

- Name tests by behavior: `test_<case>_given_<state>_expect_<outcome>` when the project uses this convention.
- Test behavior and failure modes, not private implementation details.
- Use factories or fixtures for setup when the project provides them. Keep scenario-specific mutation close to the test.
- Cover authorization, invalid input, retries, concurrency, and external-call failures when the code changes those boundaries.
