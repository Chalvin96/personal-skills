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

## Design tokens

Components consume semantic roles and named scale utilities. Palette steps
belong in the theme layer, which must be replaceable without changing component
classes. `UME-DS005` through `UME-DS008` in
[mechanical.md](mechanical.md#design-tokens) check arbitrary literals, unnecessary
or undefined token classes, CSS literals, and palette reads.

Keep the token set small and give each token a reusable purpose. Review the
cases the checker cannot prove: a new token duplicating an existing token,
a role named after a colour rather than its use, and a component inventing a
one-off size. Compare the existing scale and role definitions before accepting
a new token. Collapsing duplicate values needs a meaning check because two
roles can happen to share a value in one theme. Use role names in the style of
Atlassian's background, text, border, and state vocabulary. Preserve a swappable
theme layer for dark mode. Warm accents use amber or a cooler red; orange is
excluded from Ume's design system.

## Context

These rules cover contexts the project defines in production code.
Third-party providers, and providers mounted only in tests or stories, are out
of scope.

Context is a dependency-injection channel, not a default way to share data.
Prefer, in order: props, composition with `children` or slots, a decision made
by the parent or a registry entry, URL state, the query library for server
state, and a client store for frequently changing shared state.

Use a context only when all of these hold:

- Props or `children` cannot reasonably carry the value, because readers are
  many levels down or across router outlets, or the context is a compound
  component's private channel to its own parts.
- The value is genuinely shared by that subtree: theme, locale, current
  account, an injected service or store instance, or state a compound
  component shares with its own children.
- It is not server state and not URL state.

When a context is justified:

- **Mechanical (`UME-REACT002`):** When the provider is required, give the
  context a `null` or `undefined` default and read it through a hook that
  throws when the provider is missing. A usable default turns a forgotten
  provider into silent wrong behaviour. A context with a meaningful fallback,
  such as a default theme, may keep it; mark the line with
  `// ume-ignore: UME-REACT002` and the reason. The checker reads one line, so
  it misses a default on the next line and an aliased `createContext` import.
- Pass behaviour that varies by caller as a prop or a registry entry, so the
  rule is visible where it is decided. A nested provider of the same context
  supplies different data of the same kind: a nested theme, a second instance
  of a compound component, a form section. An inner `allowRetry={false}`
  overriding an outer `allowRetry` is behaviour, so it is a prop.
- Mount the provider at the level that matches the state's intended lifetime.
  A provider under a layout route resets when the user crosses to another
  layout; mount it above the layouts when the state must survive that
  navigation.
- Keep the provider value referentially stable. Build it with `useMemo` from
  its real inputs and check that those inputs are themselves stable; a memo
  that depends on an object rebuilt every render still rebuilds every render.
  A new value re-renders every consumer, and `React.memo` does not stop a
  context-driven re-render. Split stable actions from fast-changing state when
  consumers only need one of them.
- Encapsulate the context object. Callers and tests use the provider and the
  reading hook, not `useContext(FooContext)`. The raw context is imported only
  by its provider, its hook, and the exception below.
- A custom hook cannot be called after an early return or inside a condition.
  When a read must happen there, move it into a child component; if that is
  worse, read `use(FooContext)` at that site and check for `null`. That is the
  one allowed direct read.
- For state that changes often and is read in many places, put a stable store
  instance in context and let consumers subscribe to slices through selectors,
  instead of putting the changing values in context. Context has no selectors.
  Several state contexts that must stay consistent for one feature suggest a
  store; the count alone is not a finding.
- On React 19, new code renders `<FooContext value={...}>`.
  `<FooContext.Provider>` still works, and React plans to deprecate it in a
  future version.
- Tests render the consumer inside the real provider, or a provider built from
  explicit test values.

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
