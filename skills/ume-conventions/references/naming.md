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
4. Make the name promise the behavior. `get_` reads, `update_` writes, `sync_` pushes state outward, and `is_`/`has_` returns a boolean unless the project has an established different contract.
5. Avoid unrelated rename churn. Rename when the current name is misleading, unsafe, or part of the requested change; do not rename only for taste.
6. Use one term for one concept. Do not rotate synonyms for style.

## Language rules

| Language | Convention |
| --- | --- |
| Python | `snake_case` values and functions; `PascalCase` classes; `_private` helpers; `UPPER_SNAKE_CASE` constants only when module-level constants are justified. |
| TypeScript | `camelCase` values and functions; `PascalCase` classes, components, and types; `UPPER_SNAKE_CASE` constants only for true constants. |
| React | Component names are nouns; event props use `on<Event>`; coordinating handlers use `handle<Event>`; imperative actions use `action<DoSomething>` when that distinction is useful. |
| Collections | Use plural nouns for collections and `valuesByKey`/`values_by_key` for maps. |
| Methods | Keep public methods and functions before private helpers unless framework lifecycle order requires another arrangement. |

Do not invent abbreviations. Keep an established domain abbreviation when the repository already uses it consistently, and add no new abbreviation without a glossary entry.

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
