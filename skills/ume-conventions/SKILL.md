---
name: ume-conventions
description: Route implementation and review work to Ume's canonical coding-convention references for Python, FastAPI, Django, JavaScript, TypeScript, and React.
---

# Ume Conventions

This is a thin router. The files under references/ are the canonical coding
contract and are reusable by implementation and review skills. Link to those
references instead of copying their rules into another skill. A convention
finding must point to changed code and either a concrete impact or the named
rule. Do not report an undocumented preference as a defect.

For review requests, run [the mechanical checker](scripts/mechanical_check.py)
and read [the mechanical rules](references/mechanical.md) before the
model-based convention pass. Do not repeat a confirmed mechanical finding in
the model pass.

## Load the rules

Always read:

- [testing](references/testing.md)
- [simplicity](references/simplicity.md)
- [naming](references/naming.md)
- [security](references/security.md)

Read `testing.md` even when the diff does not add a test file. It determines
whether changed behavior has enough evidence. Do not demand tests for trivial
renames or changes with no behavior impact.

For each changed Python file, read [python](references/python.md). Then read every framework extension that matches that file's package and repository evidence:

- [FastAPI](references/fastapi.md) for `fastapi`, `FastAPI`, `APIRouter`, or equivalent project configuration.
- [Django](references/django.md) for `django`, `manage.py`, Django settings, or Django app layout.

For each changed JavaScript or TypeScript file, read [TypeScript](references/typescript.md). Then read [React](references/react.md) when the file imports or uses React, a React package or configuration, or other package-scoped repository evidence. JSX/TSX syntax alone does not select React. A monorepo can select FastAPI and Django, or backend and frontend, in one review.

Do not select a framework from a filename alone. If detection is ambiguous, state the ambiguity and use only the base language rules until the project context resolves it.

For file types outside this bundle, apply `testing.md`, `simplicity.md`, `naming.md`, and `security.md`, state that the type-specific lane is not covered, and do not infer language rules from the extension alone.

## Precedence

Apply rules in this order:

1. Security and data-loss protection.
2. Framework behavior and repository-local contracts.
3. Language rules.
4. Naming and simplicity.

An explicit repository rule overrides this bundle. If two explicit rules conflict, report the conflict instead of silently choosing one.

## Rule discipline

- Preserve safety controls, validation, error handling, accessibility, and required domain boundaries when simplifying code.
- Prefer the smallest clear design that satisfies the actual requirement.
- Use repository terminology from the glossary. Add a glossary term only after the user or repository explicitly approves it.
- Treat the references as review guidance, not a reason to rewrite unrelated code.
