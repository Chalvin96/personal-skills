# Stacked PRs

Load this reference for a GitHub PR or a branch with an associated PR.

Inspect the PR body and base/head refs for a declared stack layer or dependency.
Record the layer number, parent PR or branch, and requested review scope. Review
the requested layer's merge-base diff by default. Use later stack refs only to
verify that the layer does not depend on code added later in the stack; do not
include later-layer code in the requested diff.

Review the whole stack only when the user asks for it. Resolve the parent chain,
review each layer against its declared base, and check the cumulative diff from
the stack root. Report which scope each finding belongs to.
