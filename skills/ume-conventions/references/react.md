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

When repository evidence shows a Vite/TanStack-style frontend, keep the feature
flow legible: a plain API wrapper owns transport, a query or mutation hook owns
server-state behavior, and a page or component owns rendering. Keep file-based
routes thin and do not edit generated route trees directly.

Keep server state in the query library, URL state in router search parameters,
and page-local interaction state local. Do not add global state without a real
shared consumer.

## Context

Context is a dependency-injection channel, not a default way to share data.
Prefer, in order: props, composition with `children` or slots, a decision made
by the parent or a registry entry, URL state, the query library for server
state, and a client store for frequently changing shared state.

Use a context only when all of these hold:

- Props or `children` cannot reasonably carry the value: readers are many
  levels down or across router outlets, not one or two levels below a single
  mount.
- The value is genuinely shared by that subtree: theme, locale, current
  account, an injected service or store instance, or state a compound
  component shares with its own children.
- It is not server state and not URL state.

When a context is justified:

- **Mechanical (`UME-REACT002`):** Give it a `null` or `undefined` default and
  read it through a hook that throws when the provider is missing. A usable
  default turns a forgotten provider into silent wrong behaviour.
- Do not nest a provider to switch behaviour for a subtree, such as an inner
  `allowRetry={false}` overriding an outer `allowRetry`. Behaviour that varies
  by caller is a prop or a registry entry, so the rule is visible where it is
  decided.
- Keep the provider value referentially stable. Memoize it from its real
  inputs; an object rebuilt every render re-renders every consumer, and
  `React.memo` does not stop a context-driven re-render. Split stable actions
  from fast-changing state when consumers only need one of them.
- Encapsulate the context object. Export the provider and the reading hook;
  only those two touch the raw context. Callers and tests never call
  `useContext(fooContext)` directly.
- For state that changes often and is read in many places, put a stable store
  instance in context and let consumers subscribe to slices through selectors,
  instead of putting the changing values in context. Context has no selectors.
  A second or third state context for the same feature is a signal to use a
  store.
- On React 19, render `<FooContext value={...}>` instead of
  `<FooContext.Provider>`, which React plans to deprecate. Read with
  `use(FooContext)` when the read must happen after an early return or inside
  a condition; otherwise the custom hook is enough.
- Tests render the consumer inside the real provider, or a provider built from
  explicit test values. Do not rely on the default to make a test pass.

## Hooks and effects

- Keep hooks unconditional and preserve complete dependency arrays.
- **Mechanical (`UME-REACT001`):** Do not pass a hook call directly as another
  function's argument. Assign it to a named value first.
- Use `useMemo` and `useCallback` only when they protect a dependency identity, a memoized consumer, or a meaningful computation cost. Do not memoize primitive values or stable module constants.
- Use effects for synchronization with an external system. Prefer a mutation's success/error callback for work that only reacts to that mutation.
- A custom hook should earn its boundary. Do not wrap a bundle of selectors or a single forwarding call without a behavior reason.

## Data and accessibility

- Keep query and mutation names honest and distinguish reads from writes.
- Verify pagination, cache invalidation, loading, empty, and error states at the endpoint boundary.
- Preserve keyboard access, semantic elements, labels, focus behavior, and useful error messages.
- Do not put secrets in browser-delivered configuration. Treat media and download URLs as untrusted until the project validates their origin.
