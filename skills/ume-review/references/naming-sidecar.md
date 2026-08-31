# Naming sidecar

Read [the sidecar protocol](sidecar-protocol.md), then run this lane when the
diff adds or renames a production callable or changes its return or side-effect
contract.

Give the sidecar the changed production callables and the minimum direct context
needed to understand their behavior. Classify every callable as a predicate,
direct local retrieval, optional lookup, raising lookup, aggregation, pure
transformation, argument or self mutation, persistent-state write, or external
write.

Use [naming.md](../../ume-conventions/references/naming.md) as the authority.
Return only demonstrable mismatches between a name and its caller-visible
contract, with one candidate per line:

~~~text
path:line | callable | observed contract | violated naming promise | proposed correction | evidence
~~~

Return every mismatch without a line cap. If none exists, return exactly
`No candidates.` Keep syntax, declaration order, generic style, tests, severity,
and the final verdict outside this lane.

When delegation is unavailable, perform this checklist locally and record
`fallback — main reviewer`.
