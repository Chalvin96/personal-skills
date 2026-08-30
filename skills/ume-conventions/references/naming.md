---
type: Coding Convention
title: Naming and glossary
description: Use informative, stable names and one approved vocabulary across the codebase.
tags: [coding-convention, naming, glossary]
status: active
---

# Naming and Glossary

Use names that reduce the next reader's memory load. The Jane Street principles apply to systems, modules, services, shared helpers, queues, and constants. They do not justify renaming a local loop variable without a reason.

## Principles

1. Reuse an existing name when the concept already exists. A duplicate implementation is also a duplicate name.
2. Make names carry information. Prefer descriptive names inside code. Mnemonic names are acceptable only when the project has already paid for them and uses them consistently.
3. Spend longer names on concepts that are rare or far from their definition. Frequent local values can be shorter when their meaning is clear at the call site.
4. Make the name promise the behavior. Every ordinary function and method
   begins, after any visibility marker such as `_`, with a behavior verb. Use
   `get_` for direct in-memory reads, `collect_` for traversal or aggregation,
   `build_` for derived structures, `load_` or `fetch_` for external reads,
   `find_` for optional lookups, `validate_` or `check_` for validation, and
   `populate_`, `update_`, or `write_` for effects. Properties, protocol and
   entry-point names, and other externally constrained callables are exceptions.
   The examples are guidance, not a closed verb allowlist.
5. Avoid unrelated rename churn. Rename when the current name is misleading, unsafe, or part of the requested change; do not rename only for taste.
6. Use one term for one concept. Do not rotate synonyms for style.
7. Pick the verb for the action and the noun for the value or target. Avoid
   vague verbs such as `handle_`, `process_`, `manage_`, and `do_`; a callable
   should reveal whether it reads, derives, searches, validates, loads, or
   changes data.
8. Make failure behavior visible: use `find_` for an optional result and
   `_or_raise` for a value-or-exception helper. A name such as `authorize_`
   should not hide an accessor that raises instead of granting anything.
9. Prefer unabbreviated names unless the repository has an established domain
   abbreviation. Make illegal states unrepresentable when the name alone
   cannot express an important invariant.

Noun-only names are reserved for properties, fields, and declarative values.
An ordinary function that reads, derives, aggregates, validates, loads, or
mutates data must expose that operation in its name. Do not add a verb merely
to satisfy grammar when the verb contradicts the caller-visible contract.

### Callable verbs

| Contract | Preferred verb | Caller-visible meaning |
| --- | --- | --- |
| Direct in-memory read | `get_` | Return an already-held or directly indexed value. |
| Optional lookup | `find_` | Search and represent absence as `None`; use `_or_raise` when absence raises. |
| Traversal or aggregation | `collect_` | Gather existing values into a collection or summary without mutating inputs. |
| In-process derivation | `build_`, `parse_`, `render_`, `project_` | Return a value derived from supplied data. |
| Persistent or external read | `load_`, `fetch_` | Read from storage, a file, a database, or a network service. |
| Validation | `validate_`, `check_` | Check an invariant and return findings, a result, or raise. |
| Fill an existing target | `populate_` | Mutate an incomplete caller-owned target. |
| Change existing state | `update_`, `set_` | Modify an established object or state value. |
| Persistent or external write | `write_`, `save_`, `publish_` | Emit or persist data to an external sink. |

### Boolean callables

Every function, method, or property whose caller-visible contract returns a
boolean begins, after any visibility marker such as `_`, with `is_` or `has_`.
This includes async callables. Do not use `should_`, `can_`, `supports_`,
`needs_`, or an unprefixed predicate name for a boolean contract. Protocol,
entry-point, and other externally constrained names are exceptions.

## Language rules

| Language | Convention |
| --- | --- |
| Python | `snake_case` values and functions; `PascalCase` classes; single-leading-underscore helpers are file-local; `K_` + `UPPER_SNAKE_CASE` for direct module-level constants in production code and integration tests. |
| TypeScript | `camelCase` values and functions; `PascalCase` classes, components, and types; `UPPER_SNAKE_CASE` constants only for true constants. |
| React | Component names are nouns; event props use `on<Event>`; coordinating handlers use `handle<Event>`; imperative actions use `action<DoSomething>` when that distinction is useful. |
| Collections | Use plural nouns for collections and `valuesByKey`/`values_by_key` for maps. |
| Methods | Keep public methods and functions before private helpers unless framework lifecycle order requires another arrangement. |

Do not invent abbreviations. Keep an established domain abbreviation when the repository already uses it consistently, and add no new abbreviation without a glossary entry.

Identifier shape and public/private ordering are mechanical checks where the
language parser can prove them (`UME-PY003`, `UME-PY004`, `UME-PY006`, `UME-TS003`, and
`UME-TS004`). Whether a name is descriptive, truthful, or the approved glossary
term remains a model judgment.

The `K_` constant rule is a diff-aware ratchet: do not rename untouched legacy
declarations. It applies to direct module-level assignments in production
modules and `tests/integration`; unit-test modules, class attributes, enum
members, and migration output are exempt.

## Glossary

This is the single source of truth for approved personal and domain terms. Add a row only when the user or repository explicitly approves it.

| Term | Meaning | Preferred form | Avoid | Scope | Status |
| --- | --- | --- | --- | --- | --- |
| ASD-STE100 | Simplified Technical English standard | `ASD-STE100` | `ASD STE`, `STE100` when the standard is meant | Documentation and agent output | approved |
| FastAPI | Python web framework | `FastAPI` | `Fast API` | Python backend | approved |
| Django | Python web framework | `Django` | `django` in prose | Python backend | approved |
| TypeScript | Typed JavaScript language | `TypeScript` | `Typescript` | Frontend and tooling | approved |
| React | UI library | `React` | `react` in prose | Frontend | approved |
| knowledge | Durable repository context | `knowledge` | storing durable facts only in comments | Repository documentation | approved |

Personal project terms must be added with their meaning, preferred form, scope, and status. Do not infer them from one isolated identifier.
