# Review finding format

Use one finding per block. Keep three blocks in this order: header, assessment,
and fix. Separate the blocks with `---` and keep a blank line on both sides of
each separator.

For terminal output, include the file and line in the header. For an inline PR
comment, omit the location because GitHub shows the file and line beside the
comment.

````markdown
**warning** · `security.md` · `app/routes.py:42` → missing authorization at the route boundary

The new route accepts an object ID but does not apply the dependency that checks the caller's access to that object. The endpoint can return another user's data when the caller knows the ID.

---

Apply the existing authorization dependency or document the public audience.

```suggestion
@router.get("/{item_id}", dependencies=[Depends(require_item_access)])
```
````

Use these origins:

- `security.md` for security or data-exposure rules;
- `simplicity.md` for a verified, concrete simplification or a comment/knowledge-placement rule;
- `naming.md` for naming or glossary rules;
- `python.md`, `fastapi.md`, `django.md`, `typescript.md`, or `react.md` for language/framework rules;
- `testing.md` for test-evidence, oracle, isolation, or boundary rules;
- `state trace` for a behavior finding;
- `tooling` for an exact formatter, linter, test, or deterministic-check result.

Rules:

- Use exactly one severity: `critical`, `warning`, or `suggestion`.
- Include a changed file and line when the finding has a location. Use a general finding only when no line can carry it.
- Quote only the minimum changed code needed to identify the issue. Keep quoted code, identifiers, paths, commands, URLs, and raw excerpts byte-for-byte unchanged through the STE pass, except mask secret-shaped values before output or posting.
- Severity means: `critical` for an exploitable issue, data loss, or production break; `warning` for a probable defect or security/framework rule with concrete impact; `suggestion` for a convention or simplification with no direct impact.
- Only confirmed `critical` and `warning` findings force `Request changes`. Keep unresolved candidates as questions.
- Explain why the code is wrong or why the convention applies. Do not write a vague “consider” suggestion.
- Give a concrete fix when one is known. Use prose when the fix requires an architecture or product decision.
- Keep a question as a question. Do not assign severity to an unresolved intent question.
- Do not add praise, a generic checklist, or a diff summary before the findings.
