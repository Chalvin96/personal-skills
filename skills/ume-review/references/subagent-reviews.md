# Subagent reviews

Use only these two read-only subagent roles. The host orchestrator owns
dispatch: at the start of Pass 3, dispatch each applicable role exactly once.
Do not dispatch either role from Pass 2. Give each reviewer the target diff and
only the direct context needed for its role.

Use fresh contexts and keep the implementer's reasoning, prior findings, and
final conclusions out of the inputs. Select available low-cost reviewers by
capability. Subagents return candidates without editing files, executing target
code, running checks, posting comments, assigning final severity, or deciding
the verdict.

## Convention and specification reviewer

Use one subagent for either or both applicable lanes when the orchestrator's
pre-Pass-3 trigger collection marks either lane applicable:

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

Use one independent subagent when the changed diff includes a public or
integration boundary involving persistence, transactions, authorization,
shared state, concurrency, public contracts, migrations, or external effects.
Give it only the changed boundary files and the direct context needed to answer
the four numbered questions in [Contract & State](contract-and-state.md).
Request grounded defects, missing failure paths, and contract or state risks
within those questions. This is not a second general review: do not ask it to
review unrelated changed files, style, naming, specification compliance, or
the final verdict.

If this subagent is unavailable, record
`skipped — independent reviewer unavailable`; do not use
`fallback — main reviewer` for this lane because the main review is not
independent evidence.

Verify every returned candidate against the diff, repository, and
specification. Drop duplicates and speculation before reporting it. Record each
applicable lane separately.
