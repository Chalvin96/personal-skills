# Publishing

## Before the first mutation

Confirm `gh` is present and logged in. Stacks additionally need the `gh-stack`
skill plus the `gh stack` extension; when a prerequisite is absent, name it
and stop before publishing.

## New PRs

Push the requested branch, then create the PR as a draft with the prepared
body:

~~~bash
gh pr create --draft --base <base> --head <branch> \
  --title "<title>" --body-file "<body>"
~~~

Re-read the new PR: still a draft, with head, base, title, and body as
prepared. Publishing a draft with pending proof is allowed; the Proof section
carries the gap, and a Pending claim names its next action.

## Existing PRs

Pin before editing: head ref and SHA, base ref and SHA, title, body, and
state. Re-read all of them immediately before each mutation. Preserve
concurrent human edits: when the body changed since it was read, recompute the
scoped edit against the current body; when the change conflicts with the
requested edit or the target moved, ask instead of overwriting.

- Branch content lands first: push requested branch changes before editing
  the PR, so its text is never rewritten around a stale head.
- A Proof-only update swaps the body in via `gh pr edit <pr> --body-file <body>`
  and alters nothing else; the other three sections and all metadata hold as
  pinned.
- Anything wider than Proof goes through
  `gh pr edit <pr> --title ... --body-file ... --base ...`, setting the
  requested title, body, and base together.
- The head ref sits beyond `gh pr edit`'s reach; moving a head needs the
  requester to choose the supported route.
- Draft state and review state stay as found unless the request says to
  change them.

## History rewrites

Rewriting published history needs explicit approval naming the branch. Push
with the pinned head so a concurrent update cannot be destroyed:

~~~bash
git push --force-with-lease=<branch>:<pinned-head-sha>
~~~

Never force-push blind. A rebase that only adds commits still pushes
normally.

## Verify

After every mutation, re-read the PR and confirm head, base, title, body, and
state match the request. Report the PR URL.
