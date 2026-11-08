# Performance playbook

## Before touching code

A usable measurement runs the reported workload against the same data every
time, repeats several times, and keeps every number raw, spread included —
not one rounded figure. Write down the revision, the environment, and the
exact command so the run can be recreated.

Agree the target with the requester first: which number, moving from what to
what. When none is on offer, ask; a target the implementer invented proves
nothing to anyone.

## Changing it

Spend the first change on waste the profile actually shows, for example:

- One query per loop iteration (N+1). Under SQLAlchemy's `lazy="raise"`
  setting the ORM refuses implicit relationship loads, so add explicit
  loading (`selectinload`, `joinedload`) where the loop walks relationships.
- Round trips that pile up: a remote service called once per item when one
  batched request would do.
- React components re-rendering far more often than their data changes.

Caching, concurrency, and new infrastructure each add failure modes; go
there only with the requester's agreement.

## Claiming it

Re-run the identical measurement on the new head and put its raw numbers
beside the baseline. A result carries a claim only when the workload, data,
machine, and run count all match; anything else is an observation.

Missed the target? Lay out the remaining options and what each one costs,
then stop; the requester picks.
