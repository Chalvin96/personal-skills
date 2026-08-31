# Sidecar protocol

Read this shared protocol before running a naming, independent-review, or
specification sidecar.

Use a fresh context. Give the sidecar only the target diff and the minimum
direct context required by its lane. Keep the implementer's reasoning, prior
findings, and final conclusions out of its input.

The sidecar is read-only: it returns candidates without editing files, executing
target code, running checks, posting comments, assigning final severity, or
deciding the verdict. Verify every candidate against the diff, repository, and
specification; drop duplicates and speculation; then record the lane status.

Select an available low-cost reviewer by capability.
