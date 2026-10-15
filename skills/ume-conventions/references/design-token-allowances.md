---
type: Coding Convention
title: Design-token allowances
description: How the UME-DS005 to UME-DS008 checker builds its token index and which values it deliberately allows.
tags: [coding-convention, mechanical, design-tokens]
status: active
---

# Design-token allowances

The detail behind `UME-DS005` through `UME-DS008` in
[mechanical.md](mechanical.md#design-tokens). Consult it when a hit looks
legitimate, before reporting or suppressing it.

## Token index

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

## Allowances

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
  Raw literal fallbacks in those arbitrary classes still fire `UME-DS005`.
- Test/spec files, test/e2e/fixture directories, Storybook host CSS, generated
  source with an explicit header, and build/dependency output are excluded
  from token checks. Authored `.stories.tsx` UI remains checked. Media headers
  and keyframe selectors are not CSS declarations; their bodies are checked.

## Tests

Run the token regression suite with `python3 -m pytest tests` from the
`ume-conventions` directory. Tests exercise the CLI, runtime CSS discovery,
all four rules, suppressions, and diff filtering in temporary repositories.
