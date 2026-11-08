---
name: ume-pr
description: Draft and publish pull-request descriptions from the full commit range with labeled proof and local-first evidence; update existing PRs without clobbering human edits; split changes or squash-merge PRs on request. Use when the user asks to write, publish, update, or merge a PR.
---

# Ume PR

Turn the finished change into a PR description whose claims match observed
evidence, and publish it only on request.

pstack's `make-pr-easy-to-review` can tidy commit history and add reviewer
notes first. When it touches the description, the format below replaces its
own.

## Authorization

A request to publish authorizes the push and draft-PR creation for that
branch; the prepared body needs no second approval. With a prepare-only
request, hand back the drafted text and the plan for publishing, and touch
nothing on the remote. Updating an existing PR follows
[publishing](references/publishing.md). Rewriting published history always
needs its own explicit approval.

## Read the whole range first

Fetch, then read the entire `origin/<base>...HEAD` diff and every commit in
the range before writing. Summarize all commits, not just the latest. Inspect
changed filenames first. Decide whether the range is one independently
verifiable change; when it is large or mixed, follow [split](references/split.md)
and wait for confirmation before dividing anything.

## Write the body

Follow [the PR body format](references/pr-body.md).

## Publish

Follow [publishing](references/publishing.md): create new PRs as drafts; pin
an existing PR's head, base, and body before editing and re-read before each
mutation; never overwrite a concurrent human edit. A Proof-only update touches
only the body. A missing or blocked proof does not hold up the requested
draft; publish it with the gap stated honestly in Proof.

The commit message convention lives in the user's rules; this skill does not
restate it.

## Merge

Merge only when asked, using `gh pr merge --squash`; never use a merge commit
or rebase merge. Fix review findings, then run [ume-review](../ume-review/SKILL.md)
again on the new head. Require passing gate evidence for the head being merged.
When CI cannot run, local checks count, using `local-ci` when installed. State
which evidence cleared the gates. Follow the user's commit convention for the
squash title; summarize the whole PR range in its body.

After merging, delete the remote branch and remove the local worktree only
if each was created for this PR. For "merge all", merge in dependency order,
rebase the remaining PRs onto the new base, and rerun their gates before each
merge. Review any changed head again before merging it.
