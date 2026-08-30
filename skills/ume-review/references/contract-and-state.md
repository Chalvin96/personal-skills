# Contract & State

Use this check only when changed code modifies a public contract, persistent or
shared state, a transaction boundary, or an external effect. Trace callers and
callees one level outward. Skip private and pure helpers.

Record these four answers in the review notes:

1. What caller-visible result does the operation promise?
2. What durable or external effects occur, and who commits or owns them?
3. If each later step fails, what state survives and how is it recovered?
4. Does the name describe the promised outcome, or hide another independently
   useful operation?

When durable state is written before later fallible work, require a targeted
failure test. Force the later work to fail and assert that the surviving state
is safe or that the documented recovery occurs.

For retries, background work, cancellation, or external resources, include
repeated calls, overlapping calls, cancellation, cleanup, and recovery in the
failure question. For shared state, identify the resource, competing paths,
plausible interleaving, and synchronization or serialization point.

Treat multiple writes as one operation only when they produce one atomic domain
outcome with one failure and recovery policy. Report a finding when a caller can
reasonably need a subset, sequencing is broken, or the name hides a separate
caller-visible operation. Cite the caller or path and the impact.

Report only a concrete defect with a trigger and impact. A method over 40
nonblank lines is an investigation prompt for multiple responsibilities, not a
finding by itself. Do not report length, effect count, or design preference
without a concrete caller-visible or state-integrity impact.
