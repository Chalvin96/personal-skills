# Post a PR review

Use this reference only after the user explicitly authorizes posting. A request
to review a PR does not by itself authorize a GitHub write.

Post the completed review for a PR target or for a branch with an associated PR.
A branch without an associated PR and a working-tree review have terminal output
only.

## Resolve the PR

Use the repository and PR number from the target. Resolve the current head
commit and both GitHub users before posting:

~~~bash
REPO=<owner>/<repo>
PR=<number>
HEAD_SHA=$(gh pr view "$PR" --repo "$REPO" --json headRefOid --jq .headRefOid)
PR_AUTHOR=$(gh pr view "$PR" --repo "$REPO" --json author --jq .author.login)
VIEWER=$(gh api user --jq .login)
~~~

Use HEAD_SHA for every inline comment. Do not post against an old commit.

## Prepare comments

- Post one inline comment for each confirmed finding that can anchor to a changed line.
- Anchor an inline comment only to a changed line on the right side of the current PR diff.
- Put confirmed findings without a changed-line anchor in the review body under a
  General findings heading. Do not use a separate issue-comment endpoint for them.
- Omit the file and line from an inline header because GitHub shows the anchor beside the comment.
- Post only confirmed findings. Do not post candidates, questions, or secrets.
- Keep the finding format: header, assessment, and fix, separated by ---.

## Submit

Build the review JSON in memory and send it to GitHub. Do not write a review
payload into the repository:

~~~json
{
  "commit_id": "<HEAD_SHA>",
  "body": "<summary, general findings, and check status>",
  "event": "<REQUEST_CHANGES, APPROVE, or COMMENT>",
  "comments": [
    {
      "path": "src/example.py",
      "line": 42,
      "side": "RIGHT",
      "body": "<one finding>"
    }
  ]
}
~~~

Submit it with:

~~~bash
jq -n ... | gh api "repos/$REPO/pulls/$PR/reviews" --method POST --input -
~~~

Use REQUEST_CHANGES when at least one confirmed critical or warning finding
exists and VIEWER is not PR_AUTHOR. Use APPROVE when there are no findings and
VIEWER is not PR_AUTHOR. Use COMMENT for suggestions, unresolved questions, or
any self-authored PR, including a self-authored no-findings review. GitHub
rejects REQUEST_CHANGES and APPROVE from the PR author.

For no findings, use an empty comments array and a body that contains
No findings. For general findings, put the finding blocks in the review body
under General findings and keep comments for inline findings only. Never post a
candidate secret.

Verify the response contains the review URL, then report the URL and the
submitted state. If GitHub rejects an inline anchor, do not move it to an
unchanged line; put that finding in the review body under General findings and
record the change.
