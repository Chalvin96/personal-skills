# Independent-review sidecar

Read [the sidecar protocol](sidecar-protocol.md), then run one independent
reviewer for changes involving persistence, transactions, authorization, shared
state, concurrency, public contracts, migrations, or external effects.

Give it the diff, explicit requirements, and directly relevant files. Ask for
grounded defects, missing failure paths, and contract or state risks. Verify
every candidate against the repository before reporting it.

When an independent reviewer is unavailable, record
`skipped — independent reviewer unavailable`; the main review is not independent
evidence.
