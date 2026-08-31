# Specification sidecar

Read [the sidecar protocol](sidecar-protocol.md), then run this lane when a task,
issue, PR body, acceptance-criteria document, ADR, or other explicit
specification exists.

Give the sidecar the specification and target diff. Require it to:

1. list every explicit requirement;
2. mark each requirement `met`, `missing`, `contradicted`, or `ambiguous`;
3. cite the requirement and changed file and line for every non-met item.

Keep style review and invented requirements outside this lane. Verify every
candidate against the specification, diff, and repository. Put unresolved
items in questions.

When delegation is unavailable, perform this checklist locally and record
`fallback — main reviewer`.
