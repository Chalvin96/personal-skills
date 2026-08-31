# Single subagent review

Use at most one subagent for the entire review. Give that reviewer the target
diff, explicit requirements, and only the direct context needed for every
applicable lane below. Combine the lanes in one prompt; never spawn a separate
subagent for each lane.

Use a fresh context and keep the implementer's reasoning, prior findings, and
final conclusions out of the input. Select an available low-cost reviewer by
capability. The subagent is read-only: it returns candidates without editing
files, executing target code, running checks, posting comments, assigning final
severity, or deciding the verdict.

## Applicable lanes

Include only lanes triggered by the change:

- **Naming:** when production callables are added, renamed, or change their
  return or side-effect contract. Use
  [naming.md](../../ume-conventions/references/naming.md) as the authority.
  Classify caller-visible behavior and return only demonstrable mismatches
  between a name and its contract.
- **Specification:** when an explicit task, issue, PR body, acceptance criteria,
  ADR, or other specification exists. List each explicit requirement, mark it
  `met`, `missing`, `contradicted`, or `ambiguous`, and cite the requirement and
  changed line for each non-met item. Do not invent requirements.
- **Elevated risk:** when the change involves persistence, transactions,
  authorization, shared state, concurrency, public contracts, migrations, or
  external effects. Look for grounded defects, missing failure paths, and
  contract or state risks.

Verify every returned candidate against the diff, repository, and
specification. Drop duplicates and speculation before reporting it. Record the
status of each applicable lane separately even though one subagent handles them
together.

If no subagent is available or authorized, perform the naming and specification
checklists locally and record `fallback — main reviewer`. An elevated-risk lane
is not independent evidence when performed by the main reviewer; record
`skipped — independent reviewer unavailable` for that lane.
