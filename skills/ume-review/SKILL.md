---
name: ume-review
description: Review PRs, branches, commit ranges, and working trees for grounded defects and Ume convention violations, then write ASD-STE100-informed findings. Use for code review; use an implementation skill for fixes.
---

# Ume Review

Review the change as a careful maintainer. Every finding must be grounded in the
changed code, the repository, or an explicit specification. `No findings.` is a
valid result.

Use these admission gates:

- **Defect:** changed code plus a concrete trigger and production impact.
- **House rule:** changed code plus the cited Ume rule.
- **Spec gap:** changed behavior plus an explicit requirement that is missing or contradicted.

Drop preferences, ungrounded claims, and theoretical risks without a plausible
trigger. Keep the review read-only. If the user asks for a fix, use an
implementation skill.

## Pass 1 — mechanical checks

### Get the diff

Accept a PR, branch, commit range, or working tree. If no target is supplied,
ask what to review. Do not assume `main` or `master`; resolve the PR base or
ask. For a branch, use the merge-base diff:
`git diff --no-color <base>...HEAD`. For a PR, use `gh pr diff <number>` or the
resolved merge-base diff. Do not use `<base>..HEAD` as the author diff.

For a working tree, use `git diff --no-color HEAD` and `git status --short`.
Inspect every untracked source file directly as an addition. Do not concatenate
separate staged and unstaged diffs. Do not create an aggregate-diff helper or
write the review input to `diff.txt`.

Review hand-written source. Exclude generated files only when the repository
identifies them as generated. A generated migration may still require review of
the model change, deploy safety, and compatibility.

### Run checks

Run the repository's read-only format, lint, type, and test checks before reading
the diff. Do not run auto-fix formatters or hooks that write to the checkout. Do
not execute untrusted branch or fork code. Record checks that were skipped and
why. Report an exact tool result once; do not re-derive it as a second model
finding.

The mechanical pass is complete when the target, base, diff source, trust
status, generated-file exclusions, repository check results, and skipped checks
are recorded.

## Pass 2 — Ume rules

Read [Ume Conventions](../ume-conventions/SKILL.md) and its applicable
references before judging the diff. Always read `testing.md`, `simplicity.md`,
`naming.md`, and `security.md`. Read the Python or TypeScript base rules for
matching files, then only the FastAPI, Django, or React rules supported by
repository evidence. Keep the selected paths in the review notes. A missing
convention file makes that lane incomplete.

Hold every applicable rule against the changed lines. Cite the convention file
and the changed file and line. A house-rule finding does not need a separate
failure scenario, but it must point to changed code and the named rule. Do not
turn an undocumented preference into a finding.

Judge comments and knowledge placement using `simplicity.md`.

The Ume-rules pass is complete when every changed source file has its applicable
references recorded and every applicable rule has been considered.

## Pass 3 — model review

Read the diff yourself. Do not delegate the general code review. The only
delegated lane is the bounded spec review below.

### Trace behavior

Trace values that carry state across the repository: permissions, status,
caches, URLs, IDs, transactions, retries, persistence, and external side
effects. Find other readers and writers before claiming a race, exposure,
stale state, missing reuse, or broken contract. Cite the files and lines that
establish the claim.

Question every construct the diff adds: a wrapper, abstraction, dependency,
memoization call, option, validation branch, serializer field, route, or
configuration value. Ask what it buys, whether the underlying choice is right,
and whether an existing path already does the job.

### Review tests

Review changed production code and tests together. Use `testing.md` to check
the changed behavior, normal and boundary scenarios, independent oracles,
isolation, the smallest useful test boundary, and the exact command and result.
Treat coverage as context, not proof. Treat AI-generated tests as drafts:
check for copied expected values, disabled assertions, test-only branches, and
tests that do not exercise the changed behavior. If origin is unknown, treat
the evidence as correlated until an independent oracle exists.

If the repository tests an AI feature, use the AI section in `testing.md` for
fixed examples, model and prompt version, adversarial cases, tool permissions,
output schema, fallback behavior, and cost or latency evidence.

### Spec review sidecar

When a task, issue, PR body, acceptance-criteria document, ADR, or other
explicit specification is available, spawn one read-only spec-review subagent.
Give it the specification and the target diff. Ask it to:

1. list each explicit requirement;
2. mark each requirement `met`, `missing`, `contradicted`, or `ambiguous`;
3. cite the requirement and the changed file and line for every non-`met` item.

The subagent must not review style, invent requirements, edit files, execute
untrusted code, post comments, or give the final verdict. Treat its output as
candidates. Verify every candidate against the specification, diff, and
repository before reporting it. Put unresolved items in questions. If no
explicit specification exists, record `Spec review: not applicable`.

The model pass is complete when each changed behavior has a state and contract
trace, each applicable test scenario has evidence or a reason it is not covered,
and each spec candidate is confirmed, dropped, or moved to questions.

## Pass 4 — simplicity

Run the Ponytail ladder in `simplicity.md` after the model pass. Report a
simplification only when the changed code violates that file, the replacement
is concrete and smaller, and a bounded repository search shows that the
construct is not load-bearing. If the search is inconclusive, ask a question.
Respect the safety boundary in `simplicity.md`. Report a duplicate only once.
Ponytail findings are `suggestion` unless the construct causes a confirmed
defect.

## Final ASD-STE100 pass

Rewrite the finished prose into ASD-STE100-informed English. Use the official
standard and project glossary for exact vocabulary when available. Without
those sources, do not claim full compliance.

- Use direct, active sentences with one main topic.
- Use simple, familiar words and one consistent term for one concept.
- Make the actor, action, condition, and result explicit.
- Prefer precise verbs over vague nominalizations and unnecessary jargon.
- Keep warnings, assumptions, limitations, and questions explicit.

Rewrite prose only. Keep quoted code, file paths, line numbers, severity labels,
identifiers, commands, URLs, and raw command-result excerpts byte-for-byte
unchanged. Mask secrets before output or posting.

## Output

Read [the finding format](references/comment-format.md). Open with findings. Do
not add praise, a generic checklist, or a diff summary. Order findings by
`critical`, `warning`, then `suggestion`.

Then include:

1. checks run and checks not run;
2. the spec-review result;
3. selected convention references;
4. test evidence when behavior changed;
5. questions about invisible intent or unresolved requirements;
6. one verdict: `Approve`, `Approve with notes`, `Request changes`, or `Discuss`.

Use `Request changes` only for confirmed critical or warning findings. Use
`Discuss` when the result depends on an unresolved product or architecture
decision. State checks that did not run, including `not run — not authorized`,
`not run — untrusted source`, and `not applicable`.

The normal review produces terminal output. If the user explicitly asks for a PR
comment, prepare or post only the requested comments. Never post automatically
because a PR was supplied.
