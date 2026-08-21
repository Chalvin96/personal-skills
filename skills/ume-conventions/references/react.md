---
type: Coding Convention
title: React conventions
description: React-specific rules for component boundaries, hooks, state, data fetching, and accessibility.
tags: [coding-convention, react, frontend]
status: active
---

# React

Load this extension with `typescript.md` when the project uses React.

## Components and state

- Use function components for new code unless the repository has a deliberate class boundary.
- Keep one responsibility per component. Separate data loading, state coordination, and presentation when the combined component becomes difficult to trace.
- Put state at the narrowest owner that needs it. Do not lift state or add global state without a real shared consumer.
- Use stable, genuinely unique keys for lists. Do not use array indexes when items can reorder, insert, or delete.
- Keep public components and hooks before module-private helpers where practical.

## Hooks and effects

- Keep hooks unconditional and preserve complete dependency arrays.
- Do not pass a hook call directly as another function's argument. Assign it to a named value first.
- Use `useMemo` and `useCallback` only when they protect a dependency identity, a memoized consumer, or a meaningful computation cost. Do not memoize primitive values or stable module constants.
- Use effects for synchronization with an external system. Prefer a mutation's success/error callback for work that only reacts to that mutation.
- A custom hook should earn its boundary. Do not wrap a bundle of selectors or a single forwarding call without a behavior reason.

## Data and accessibility

- Keep query and mutation names honest and distinguish reads from writes.
- Verify pagination, cache invalidation, loading, empty, and error states at the endpoint boundary.
- Preserve keyboard access, semantic elements, labels, focus behavior, and useful error messages.
- Do not put secrets in browser-delivered configuration. Treat media and download URLs as untrusted until the project validates their origin.
