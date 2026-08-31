---
name: ume-review
description: Review PRs, branches, commit ranges, and working trees for grounded defects and Ume convention violations, prepare clear findings, and post PR reviews only after explicit authorization. Use for code review; use an implementation skill for fixes.
---

# Ume Review

Review the change as a careful maintainer. Every finding must be grounded in the
changed code, the repository, or an explicit specification. "No findings." is a
valid result.

Use these admission gates:

- Defect: changed code plus a concrete trigger and production impact.
- House rule: changed code plus the cited Ume rule.
- Spec gap: changed behavior plus an explicit requirement that is missing or contradicted.

Drop preferences, ungrounded claims, and theoretical risks without a plausible
trigger. Do not edit the target source. Post to GitHub only after the user
explicitly authorizes posting; otherwise keep the review in the terminal. If the
user asks for a fix, use an implementation skill.

## Evidence ledger

Keep a review ledger in the review notes. Record:

- target provenance, base and head, diff source, trust status, and generated-file exclusions;
- one convention-reference entry for every changed source file;
- one entry for every applicable risk surface: "traced", "not applicable", or "skipped — reason";
- every applicable lane in the single subagent review as "completed",
  "fallback — main reviewer", "skipped — reason", or "not applicable".

A pass is incomplete until every item in its ledger has a status and evidence.

## Pass 1 — mechanical checks

### Get the diff

Accept a PR, branch, explicit commit range, or working tree. If no target is
supplied, ask what to review. Do not assume main or master; resolve the PR base
or ask.

- For a branch, use its merge base: git diff --no-color <base>...HEAD.
- For a PR, use gh pr diff <number> or the resolved merge-base diff.
- For a commit range, require literal endpoints OLD and NEW (or an explicit
  OLD..NEW) and compare them with git diff --no-color OLD NEW. Do not infer a
  base, replace an endpoint with HEAD, or use merge-base semantics.
- For a working tree, use git diff --no-color HEAD and git status --short.

Inspect every untracked source file directly as an addition. Do not concatenate
separate staged and unstaged diffs. Do not create an aggregate-diff helper or
write the review input to diff.txt.

### Stacked PRs

For a PR, or for a branch with an associated PR, load
[stacked-PR guidance](references/stacked-prs.md) and record the requested scope
before reviewing. A branch without an associated PR remains a terminal-only
review target.

Review hand-written source. Exclude generated files only when the repository
identifies them as generated. A generated migration may still require review of
the model change, deploy safety, and compatibility.

### Run checks

Inspect the target provenance, base and head, and changed executable or
configuration files before running commands. Do not execute untrusted branch or
fork code. Run the repository's read-only format, lint, type, and test checks.
Do not run auto-fix formatters or hooks that write to the checkout. Record
material working-tree changes and skipped checks. Report each exact tool result
once; do not re-derive it as a second finding.

Run the Ume mechanical convention checker from the canonical
ume-conventions references on the exact changed lines before the Ume-rules
pass:

~~~bash
git diff --no-color -U0 <base>...HEAD \
  | python <ume-conventions>/scripts/mechanical_check.py \
      --root <repository> --diff-stdin
~~~

For a working tree, use git diff --no-color -U0 HEAD. Check untracked source
files separately by passing their paths to the checker. A status of 1 means
that the checker found convention violations. Record rule IDs, paths, lines,
and messages in mechanical-check evidence, then translate each confirmed
finding into the normal format with a plain-language summary. Explain why the
rule applies and matters, and give a concrete fix. Do not report a mechanical
finding again in the Ume-rules or model pass. Read
[the mechanical rule table](../ume-conventions/references/mechanical.md) to
interpret scope and suppression rules. If the checker cannot run, record
not run — checker unavailable and do not treat a model scan as equivalent
deterministic evidence.

For changed Python files, discover the repository's documented Ruff command
from package configuration, task-runner files, CI, or repository documentation.
Run that read-only command against the changed files when it supports
file-scoped checks; otherwise run the documented project check. If no configured
Ruff command exists, record not run — no repository Ruff command. Record
whether C901 or PLR rules are enabled when complexity is relevant. Ruff
complexity rules do not enforce a physical line-count limit, so keep the
40-line review prompt separate from Ruff evidence.

The mechanical pass is complete when the target, provenance, base, diff source,
trust status, generated-file exclusions, repository check results, mechanical
checker result, Ruff status, and skipped checks all have ledger entries.

## Pass 2 — Ume rules

Follow [Ume Conventions](../ume-conventions/SKILL.md) to select the canonical
references for every changed source file. Record a required reference that is
unavailable as skipped.

Apply only conventions supported by repository evidence. Cite the convention
file and changed file and line for a finding. A house-rule finding does not need
a separate failure scenario, but it must point to changed code and the named
rule. Do not turn an undocumented preference into a finding.

When the diff adds or renames a production callable, or changes its return or
side-effect contract, include the naming lane in the single
[subagent review](references/subagent-review.md). Skip it for tests-only,
documentation-only, and configuration-only changes.

For every changed production file, run
[the comment audit](references/comment-audit.md).

The Ume-rules pass is complete when every changed source file has its selected
reference entry, every applicable rule has been considered, every in-scope
comment has been classified, and every naming candidate has been
verified, deduplicated, admitted, or dropped.

## Pass 3 — model review

Read the diff yourself. Do not delegate the general code review. Use at most
one subagent for the entire review. When delegation is available and authorized,
combine every applicable naming, specification, and elevated-risk lane into the
single [subagent review](references/subagent-review.md). Never spawn one
subagent per lane.

### Trace behavior

Trace values that carry state across the repository: permissions, status,
caches, URLs, IDs, transactions, retries, persistence, and external side
effects. Find other readers and writers before claiming a race, exposure,
stale state, missing reuse, or a broken contract.

For a changed handler, service operation, job, factory, command, consumer, or
other integration boundary, trace one level outward to callers and callees.
Record the caller-visible result, material effects, ownership of commits or
external calls, and failure or retry behavior.

When the patch changes a public, stored, or published contract, compare its
producers, consumers, exports, serialized fields, schemas, migrations,
configuration, generated artifacts, docs, and examples. Skip this check for a
private internal change with no stored or published contract.

When the change modifies a public or integration boundary, persistent or shared
state, a transaction boundary, or an external effect, read
[Contract & State](references/contract-and-state.md). That reference defines
the required trace, concurrency admission gate, atomic-outcome rule, and
reporting threshold.

Expand the trace only across applicable risk surfaces: data integrity and
stored-data or message migrations, concurrency and idempotency, security and
privacy, backward and forward compatibility, performance and resource use,
and observability, deployment, and rollback.

Use production-function size as a triage signal, not a defect rule. Exclude
test modules. For each changed production function over 40 nonblank physical
lines, check whether it contains multiple responsibilities or an independently
useful caller-visible subset. Report an issue only when that inspection finds a
concrete defect or supported house-rule violation.

Treat complexity, coupling, design smells, and metrics as investigation signals.
Do not infer a defect from a metric or a SOLID label. Apply the admission gates
above. Use the single Ponytail simplicity pass for confirmed,
concrete over-engineering findings.

### Review tests

Review changed production code and tests together. Use
[testing](../ume-conventions/references/testing.md) to check
normal and boundary scenarios, independent oracles, isolation, the smallest
useful test boundary, and the exact command and result. Treat coverage as
context, not proof. Treat AI-generated tests as drafts: check for copied
expected values, disabled assertions, test-only branches, and tests that do not
exercise the changed behavior. If origin is unknown, treat the evidence as
correlated until an independent oracle exists.

Prefer assertions on observable outcomes and domain invariants. Assert internal
collaboration or call order only when it is necessary to prove an observable
contract, invariant, or failure-safety property.

If the repository tests an AI feature, use the AI section in
[testing](../ume-conventions/references/testing.md) for
fixed examples, model and prompt version, adversarial cases, tool permissions,
output schema, fallback behavior, and cost or latency evidence.

### Spec review

When a task, issue, PR body, acceptance-criteria document, ADR, or other
explicit specification is available, include the specification lane in the
single [subagent review](references/subagent-review.md). If no explicit
specification exists, record Spec review: not applicable.

The model pass is complete when every applicable risk surface has a ledger
status and trace, every applicable test scenario has evidence or a reason it is
not covered, and every spec candidate is confirmed, dropped, or moved to
questions.

## Pass 4 — simplicity

Run the Ponytail ladder in
[simplicity](../ume-conventions/references/simplicity.md) after the model pass. Report a
simplification only when the changed code violates that file, the replacement
is concrete and smaller, and a bounded repository search shows that the
construct is not load-bearing. If the search is inconclusive, ask a question.
Respect the safety boundary in
[simplicity](../ume-conventions/references/simplicity.md). Report each duplicate
only once.

This pass is complete when every added abstraction, option, wrapper, dependency,
memoization call, validation branch, serializer field, route, or configuration
value has a status of finding, question, or no finding with bounded search
evidence.

## Output

Read [the finding format](references/comment-format.md). Open with findings. Do
not add praise, a generic checklist, or a diff summary. Order findings by
critical, warning, then suggestion.

Then include:

1. checks run and checks not run;
2. the spec-review result;
3. selected convention references;
4. test evidence when behavior changed;
5. questions about invisible intent or unresolved requirements;
6. one verdict: Approve, Request changes, or Comment.

Use Request changes only for confirmed critical or warning findings and only
when the authenticated GitHub user is not the PR author. GitHub rejects a
self-authored Request changes review; submit COMMENT instead and state that
limitation. Use Comment for suggestions, unresolved questions, or no findings.
State checks that did not run, including not run — not authorized, not run —
untrusted source, and not applicable.

After the user explicitly authorizes posting for a PR target or a branch with an
associated PR, follow [posting.md](references/posting.md). Without that
authorization, return terminal output only.

Before handoff, confirm that every changed file appears in the ledger, every
candidate is admitted, dropped, or recorded as a question, findings are
deduplicated and grounded, all check and subagent-review statuses are explicit, the
output follows the finding format, and any authorized post is verified.
