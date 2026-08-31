---
type: Coding Convention
title: Mechanical convention checks
description: Deterministic checks for Ume rules that can be proven from source syntax or file layout.
tags: [coding-convention, mechanical, ast, regex]
status: active
---

# Mechanical checks

Run `scripts/mechanical_check.py` before the model-based Ume rules pass. The
checker reads source text and Python ASTs. It does not import, execute, format,
or modify the target project.

For a review, give the checker the exact changed lines through `--diff-stdin`.
Report a finding only when its rule ID and line are in the changed diff. The
checker accepts `# noqa: UME-XXXX` or `# ume-ignore: UME-XXXX` with an explicit,
matching rule ID for a deliberate exception. A bare suppression does not hide a
Ume finding. Record the exception in the review when it affects a safety rule.
Rule IDs identify deterministic checks and are internal metadata, not
human-facing finding summaries. Keep the ID in mechanical-check evidence when
useful; use the checker's message and repository context to write a
plain-language finding title, assessment of why it applies and matters, and a
concrete fix.

## Rules enforced by the checker

| Rule | Mechanical check |
| --- | --- |
| `UME-PY001` | Mutable Python default values: list, dict, set, comprehensions, and direct `list()`/`dict()`/`set()` defaults. |
| `UME-PY002` | Cross-module import or access of a single-leading-underscore Python name. |
| `UME-PY003` | Public Python module functions and class methods placed after private helpers. |
| `UME-PY004` | Python function/class identifier shape: `snake_case` functions and `PascalCase` classes. |
| `UME-PY005` | Known blocking calls inside `async def`, including synchronous HTTP, `time.sleep`, and `subprocess.run`. |
| `UME-PY006` | Direct module-level Python constants in production code and `tests/integration` must start with `K_`; unit-test modules, class attributes, enum members, and migration output are exempt. |
| `UME-SA001` | SQLAlchemy `.query()` usage. |
| `UME-SA002` | Imported SQLAlchemy `Column` or `declarative_base()` constructors instead of the typed 2.x API. |
| `UME-FAPI001` | Database mutation calls directly inside a FastAPI-style route function. |
| `UME-FAPI002` | A `clients/<vendor>/` folder that contains one client layer but misses `api.py`, `manager.py`, or `config.py`. |
| `UME-FAPI003` | HTTP/SDK transport imports inside `clients/<vendor>/manager.py`. |
| `UME-FAPI004` | Local transaction operations inside `clients/<vendor>/manager.py`. |
| `UME-DJ001` | Direct Django settings-module imports when Django repository evidence exists. |
| `UME-NET001` | Known direct HTTP client calls or constructors without an explicit `timeout=` argument. |
| `UME-SEC001` | Direct `eval`, `exec`, unsafe pickle/dill loading, or unsafe YAML loading. |
| `UME-SEC002` | Obvious literal credentials assigned to Python credential-like names. |
| `UME-SEC003` | Obvious literal credentials in JavaScript or TypeScript source. |
| `UME-TS001` | Explicit TypeScript `any`. |
| `UME-TS002` | TypeScript non-null assertions. |
| `UME-TS003` | JavaScript/TypeScript function names containing underscores. |
| `UME-TS004` | JavaScript/TypeScript class, interface, or type names that are not `PascalCase`. |
| `UME-REACT001` | A hook call passed directly as another function's argument. |
| `UME-TOOL001` | Python syntax that cannot be parsed. |

The checker is intentionally conservative. It does not claim to prove
architecture or behavior from syntax. It does not replace repository formatters,
linters, type checkers, tests, or the model review.

`UME-SA002` does not inspect Alembic or migration paths because generated
migrations commonly use SQLAlchemy `Column` declarations.

## Keep these rules in model review

The following rules need repository context, runtime behavior, or human intent:

- whether a public boundary needs a type, response model, or authorization;
- whether a query is simple enough to stay near a route or needs a query module;
- service transaction scope, invariants, concurrency, retries, idempotency, and
  external side-effect ordering;
- relationship loading, N+1 behavior, serializer disclosure, migration safety,
  and error translation;
- whether a name is descriptive, a wrapper is load-bearing, a comment explains
  why, or knowledge belongs in a repository decision record;
- test oracles, independence, isolation, scenario coverage, and whether a
  generated test proves the changed behavior;
- accessibility, user-visible state, hook dependency completeness, and whether
  an array index is safe as a React key.

Do not repeat a confirmed mechanical finding in the model pass. Use the model
pass to interpret its impact only when the mechanical result alone cannot decide
the severity or fix.
