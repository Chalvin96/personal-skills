# Review sidecars

Load this reference only when a delegated review lane applies.

## Shared protocol

Use a fresh context for each sidecar. Give it only the target diff,
specification, and minimum direct context needed for its lane. Do not give it
the implementer's reasoning, prior findings, or final conclusions.

A sidecar is read-only. It must not edit files, execute target code, run checks,
post comments, or decide the final severity or verdict. The main reviewer
verifies every candidate against the diff, repository, and specification,
drops duplicates and speculation, and records the lane status.

Select an available low-cost reviewer by capability; do not require a named
model. If delegation is unavailable, perform the naming or specification lane's
same narrow checklist locally and record "fallback — main reviewer". If an
elevated-risk independent reviewer is unavailable, record
"skipped — independent reviewer unavailable"; the main review is not independent
evidence.

## Naming lane

Run this lane when the diff adds or renames a production callable, or changes
its return or side-effect contract. Skip it for tests-only, documentation-only,
and configuration-only changes.

Give the sidecar only the changed production callables and the minimum direct
context needed to understand their behavior. Ask it to classify every callable
as a predicate, direct local retrieval, optional lookup, raising lookup,
aggregation, pure transformation, argument or self mutation, persistent-state
write, or external write.

Use [naming.md](../../ume-conventions/references/naming.md) as the authority for
behavior verbs, Boolean prefixes, effect names, and failure-visible names.
Report only a demonstrable mismatch between a name and its caller-visible
contract. Require a changed-line citation and the observed behavior for every
candidate. Return one line per candidate in this
format:

~~~text
path:line | callable | observed contract | violated naming promise | proposed correction | evidence
~~~

Classify every in-scope callable, but return only mismatches. Return all
candidates; there is no line cap. If no grounded mismatch exists, return exactly
"No candidates." The sidecar must not review syntax, declaration order,
generic style, tests, severity, or the final verdict.

## Elevated-risk independent lane

Run one fresh-context independent reviewer in addition to the main review for
changes involving persistence, transactions, authorization, shared state,
concurrency, public contracts, migrations, or external effects.

Give it the diff, requirements, and relevant files. Ask it for grounded defects,
missing failure paths, and contract/state risks only. Verify each result against
the repository before reporting it. Do not report its unverified candidates.

## Specification lane

When a task, issue, PR body, acceptance-criteria document, ADR, or other
explicit specification exists, give the sidecar the specification and target
diff. Ask it to:

1. list every explicit requirement;
2. mark each requirement met, missing, contradicted, or ambiguous;
3. cite the requirement and changed file and line for every non-met item.

It must not review style, invent requirements, edit files, execute untrusted
code, post comments, or give the final verdict. Verify every candidate against
the specification, diff, and repository. Put unresolved items in questions.
