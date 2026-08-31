# Subagent reviews

Use only these two read-only subagent roles. Run a role only when its trigger
applies and delegation is available and authorized. Give each reviewer the
target diff and only the direct context needed for its role.

Use fresh contexts and keep the implementer's reasoning, prior findings, and
final conclusions out of the inputs. Select available low-cost reviewers by
capability. Subagents return candidates without editing files, executing target
code, running checks, posting comments, assigning final severity, or deciding
the verdict.

## Convention and specification reviewer

Use one subagent for either or both applicable lanes:

- **Naming:** when production callables are added, renamed, or change their
  return or side-effect contract. Use
  [naming.md](../../ume-conventions/references/naming.md) as the authority.
  Classify caller-visible behavior and return only demonstrable mismatches
  between a name and its contract.
- **Specification:** when an explicit task, issue, PR body, acceptance criteria,
  ADR, or other specification exists. List each explicit requirement, mark it
  `met`, `missing`, `contradicted`, or `ambiguous`, and cite the requirement and
  changed line for each non-met item. Do not invent requirements.

If this subagent is unavailable, perform its applicable checklists locally and
record `fallback — main reviewer` for each lane.

## Independent elevated-risk reviewer

Use one independent subagent when the change involves persistence,
transactions, authorization, shared state, concurrency, public contracts,
migrations, or external effects. Ask for grounded defects, missing failure
paths, and contract or state risks.

If this subagent is unavailable, record
`skipped — independent reviewer unavailable`; the main review is not independent
evidence.

Verify every returned candidate against the diff, repository, and
specification. Drop duplicates and speculation before reporting it. Record each
applicable lane separately.
