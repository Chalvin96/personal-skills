# Comment audit

Load this reference for every changed production file. Read the Comments and
knowledge section of
[simplicity.md](../../ume-conventions/references/simplicity.md) as the policy
authority.

Inspect added or modified comments and comments immediately governing changed
behavior. Do not audit unrelated comments only because their file was touched.
Apply the keep, flag, and delete-or-move decisions from
[simplicity.md](../../ume-conventions/references/simplicity.md). Classify the
audit in the review ledger, including the no-finding case.

Search knowledge/ before naming a destination. Delete a comment when a clearer
name, type, test, or structure expresses the reason. Move durable content to
the relevant knowledge concept or decision record. If no concept fits, identify
the missing concept.

Cite [simplicity.md](../../ume-conventions/references/simplicity.md), the
comment line when changed, or the nearest changed line when the comment is
adjacent to changed behavior. Use suggestion for placement or deletion. Use
warning only when a stale or misleading comment can cause an incorrect
implementation.
