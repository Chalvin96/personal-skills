---
type: Coding Convention
title: Mechanical convention checks
description: Deterministic checks for Ume rules that can be proven from source syntax or file layout.
tags: [coding-convention, mechanical, ast, regex]
status: active
---

# Mechanical checks

Run `scripts/mechanical_check.py` before the model-based Ume rules pass. The
checker reads CSS, JavaScript/TypeScript source text, and Python ASTs. It does not import, execute, format,
or modify the target project.

For a review, give the checker the exact changed lines through `--diff-stdin`.
Report a finding only when its rule ID and line are in the changed diff. The
checker accepts `# noqa: UME-XXXX` or `ume-ignore: UME-XXXX` in a `#`, `//`, or
`/* ... */` comment on the same or preceding line with an explicit,
matching rule ID for a deliberate exception. A bare suppression does not hide a
Ume finding. Record the exception in the review when it affects a safety rule.
Keep the rule ID in mechanical-check evidence and cite it in house-rule
findings. Use the checker's message and repository context to write a
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
| `UME-REACT002` | `createContext` with a usable default value instead of `null` or `undefined`, so a consumer rendered without its provider silently gets the default. Requires React evidence; skips test and story files. A meaningful fallback, such as a default theme, stays with `// ume-ignore: UME-REACT002` and a reason. |
| `UME-DS001` | A `!`-forced Tailwind utility inside a `className`, which wins over a component's own recipe. |
| `UME-DS002` | `eslint-disable` of `no-restricted-syntax` or `no-restricted-imports`, switching off the project's own policy at the call site it would have caught. |
| `UME-DS003` | A cast inside a JSX `className` or `style` prop; confirm that the target component's API excludes the prop before reporting. |
| `UME-DS004` | A `toHaveClass` assertion, or a read of `className`/`classList`, in a test, spec, or story outside `packages/ui`. |
| `UME-DS005` | A raw literal in a Tailwind arbitrary value or property, including lengths, colours, and numeric values. Scans class candidates in quoted attributes, recipe/helper strings, nested template literals, and CSS `@apply`. Names the nearest known scale/token utility when resolvable. |
| `UME-DS006` | An arbitrary `var(--token)` class whose token has an equivalent named utility, a background class that reads a role with a different named utility, or a token absent from repository CSS. Discovers `@theme` namespaces and direct `@utility` wrappers. |
| `UME-DS007` | A raw colour or non-scale length in a CSS declaration outside token definitions. Includes component-local custom properties. Exempts the layout and scale values below. |
| `UME-DS008` | A discovered palette variable or palette utility read outside the theme layer. Falls back to numbered `--primary-*`, `--secondary-*`, `--accent-*`, `--warning-*`, `--destructive-*`, `--black-*`, and `--white-*` steps. Components read semantic roles. |
| `UME-TOOL001` | Python syntax that cannot be parsed. |

The checker is intentionally conservative. It does not claim to prove
architecture or behavior from syntax. It does not replace repository formatters,
linters, type checkers, tests, or the model review.

Framework-specific checks require evidence from the repository or source: a
recognized dependency manifest or an import of the relevant framework. This
keeps names such as `app.get()`, `builder.query()`, and `useValue()` from being
treated as framework code in otherwise generic projects.

`UME-SA002` does not inspect Alembic or migration paths because generated
migrations commonly use SQLAlchemy `Column` declarations.

## Design tokens

Build the token index from all hand-written repository CSS, including unchanged
files during a diff review. Custom-property declarations supply defined names;
palette/primitives sheets supply palette names; `@theme` supplies Tailwind
namespaces. `@utility` rules with one direct `var()` declaration supply named
wrappers. Do not infer a utility from a variable's spelling. For example,
`--border-color-strong: var(--border-strong)` proves `border-strong`, while
`--color-paper` supplies background, text, ring, and other colour utilities.
Specialized border/background mappings do not prove ring utilities. Valid
`ring-[var(--border-focused)]` and ring-offset role reads stay when no equivalent
ring utility exists. A background reading a border role is reported with the
available utility and a request to choose a background role, without claiming
that a border utility preserves the paint.

Token definitions are declarations in palette/primitives or theme CSS files,
`@theme` blocks, and custom properties in `:root`, `:host`, theme attributes,
or `.theme-*`/`.dark`/`.light` selectors. Ordinary declarations in a `tokens.css`
file remain checked. Adding a raw custom property to a component selector does
not make it a token definition.

The final allowances are:

- `UME-DS005` keeps arbitrary selectors, data/group variants, breakpoint
  variants, keyword/property-list payloads, SVG paths, and zero-only layout
  values. Layout `%`, `fr`, viewport units, and intrinsic `ch`/`em` dimensions
  stay. Percentages inside gradients and colour mixing are positions or mix
  weights. Raw colours inside those expressions still fire. A token-based
  `calc()` stays. Layout `calc()`/`min()`/`max()` with viewport/intrinsic units or
  `env()` stay only when their fixed dimensions are on the CSS scale below.
  Standalone arbitrary pixel/rem values still fire even if a named scale value
  would match them exactly.
- `UME-DS007` allows zero in any unit, signed `1px` hairlines, and spatial
  lengths in half spacing steps. The default `0.25rem` spacing unit gives
  `2px`/`0.125rem` increments; a discovered `--spacing` overrides the unit for
  CSS allowances and utility suggestions. Border/outline widths and underline
  thickness have the narrower pixel scale `0, 1, 2, 3, 4, 8`; `3px` has existing
  integer border/decoration utilities, while `2.5px` is excluded. Font sizes and line heights
  use the default Tailwind text scale `12, 14, 16, 18, 20, 24, 30, 36, 48, 60,
  72, 96, 128px` plus discovered type/leading utilities. Pixel/rem comparisons
  use a `16px` root. Layout percentages, fractional tracks, viewport units
  (`vh`, `vw`, `vi`, `vb`, `vmin`, `vmax` and small/large/dynamic variants),
  and intrinsic `ch`/`em` measures stay on layout properties. Gradient stops
  and mix percentages stay. `transparent`, `currentColor`, and `inherit` stay;
  all CSS named colours, hex colours, and literal colour functions fire.
  A variable alpha does not exempt raw colour channels. Token-supplied channels
  stay.
  Token-based `calc()` is exempt only within that expression; raw sibling
  colours and lengths still fire. Quoted content/font names and URLs are data.
- `UME-DS006` allows defined tokens with no equivalent utility. `--radix-*`
  and `--tw-*` are external runtime variables, not missing repository tokens.
- Test/spec files, test/e2e/fixture directories, Storybook host CSS, generated
  source with an explicit header, and build/dependency output are excluded
  from token checks. Authored `.stories.tsx` UI remains checked. Media headers
  and keyframe selectors are not CSS declarations; their bodies are checked.

Every `UME-DS` finding uses the existing changed-line and explicit-ID
suppression filter. CSS findings point at the literal, including a changed
channel in a multiline colour. Full mode inspects every in-scope line.

Run the token regression suite with `python3 -m pytest tests` from the
`ume-conventions` directory. Tests exercise the CLI, runtime CSS discovery,
all four rules, suppressions, and diff filtering in temporary repositories.

## Component API escapes

The existing `UME-DS001` through `UME-DS004` retain their meanings and
explicit-ID suppressions. Token escapes use `UME-DS005` through `UME-DS008`.

`UME-DS001` through `UME-DS003` flag candidate escapes from a closed component API.
A cast, forced utility, or disabled lint rule can indicate that a call site
reached past a declared styling boundary. Confirm the component API and
repository policy before reporting.

They flag syntax that warrants checking a declared component boundary. Token
escapes have their own deterministic checks and allowances above.

`UME-DS004` is the same boundary seen from the test file. A class string in a
feature test pins the recipe rather than the contract: it survives a token
rename that changed nothing, and it fails on a class rename that changed
nothing. Inside the design-system package a `cva` recipe's output genuinely is
the unit under test, so those assertions stay — the exemption is the package
path `packages/ui/`, not a list of permitted files, so a new feature test cannot
opt itself in by picking a filename. What the assertion was protecting decides
the replacement: assert the `data-state`, the role, `aria-checked`/
`aria-pressed`, or the accessible name when the learner can perceive the state,
and delete the assertion when nothing does — appearance belongs to the visual
suite, not to a class name matched in a unit test. Reading `className` or
`classList` is the same assertion in another spelling and is reported the same
way, except in the design-system package, where a test may legitimately compare
rendered markup to prove a closed surface rejected injected props.

These checks flag candidate escapes. Confirm the declared boundary and call
site before reporting; review allowlist expansions against the repository's
stated policy.

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
