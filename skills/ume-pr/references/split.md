# Splitting a large change

Propose a split when the range is too large or mixed for one review. Leave every
branch, commit, and PR untouched until the user agrees to the proposed layers.

Propose independently verifiable layers, not mechanical file groupings: each
layer must carry a claim that can be shown true or false on that layer alone.
For each layer, record:

- **Claim**: what the layer says it does.
- **Proof**: the check that demonstrates the claim on the layer by itself.
- **Depends on**: the lower layers that must merge first.
- **Merge and deploy order**: the order to merge and any deployment stage a
  layer needs before the next one lands.
- **Migration compatibility**: old code must tolerate the new schema until the
  layer that stops using it merges. Prefer expand, then migrate callers, then
  contract: add the new shape, move readers and writers, remove the old shape
  in a later layer. Put destructive or data-losing migrations in front of a
  human for the rollout call; just because a migration can be reversed does
  not mean the data comes back with it.

Each layer becomes one PR whose base is the layer below it; the bottom layer
targets the real merge branch. Use the `gh-stack` skill when installed to link
the stack. A slice that cannot be verified on its own (a route stub without
its handler, a migration without the code that fills the column) is not a
layer.
