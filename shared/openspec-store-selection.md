# OpenSpec store selection

If the work is in a registered OpenSpec store, run `openspec store list --json`,
select the applicable store, and retain its `--store <id>` flag on OpenSpec
commands that accept it. Otherwise, use the nearest local `openspec/` root.
