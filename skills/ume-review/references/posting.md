# Post a PR review

Post the completed review for a PR target. A branch target uses the associated
PR when one exists. A working-tree review has terminal output only.

## Resolve the PR

Use the repository and PR number from the target. Resolve the current head
commit and both GitHub users before posting:

```bash
REPO=<owner>/<repo>
PR=<number>
HEAD_SHA=$(gh pr view "$PR" --repo "$REPO" --json headRefOid --jq .headRefOid)
PR_AUTHOR=$(gh pr view "$PR" --repo "$REPO" --json author --jq .author.login)
VIEWER=$(gh api user --jq .login)
```

Use `HEAD_SHA` for every comment. Do not post against an old commit.

## Prepare comments

- Post one finding per comment.
- Anchor an inline comment only to a changed line on the right side of the
  current PR diff. Use a general PR comment when no changed line can carry the
  finding.
- Omit the file and line from an inline header. GitHub shows the anchor beside
  the comment.
- Post only confirmed findings. Do not post candidates, questions, or secrets.
- Keep the finding format: header, assessment, and fix, separated by `---`.

## Submit

Build the review JSON in memory and send it to GitHub. Do not write a review
payload into the repository:

```json
{
  "commit_id": "<HEAD_SHA>",
  "body": "<summary and check status>",
  "event": "<REQUEST_CHANGES or COMMENT>",
  "comments": [
    {
      "path": "src/example.py",
      "line": 42,
      "side": "RIGHT",
      "body": "<one finding>"
    }
  ]
}
```

Submit it with:

```bash
jq -n ... | gh api "repos/$REPO/pulls/$PR/reviews" --method POST --input -
```

Use `REQUEST_CHANGES` when at least one confirmed `critical` or `warning`
finding exists and `VIEWER` is not `PR_AUTHOR`. Use `COMMENT` for suggestions,
no findings, or a self-authored PR. GitHub rejects `REQUEST_CHANGES` from the
PR author.

For no findings, use an empty `comments` array and a body that contains
`No findings.`. For a general finding, omit `comments` or use a separate issue
comment endpoint. Never post a candidate secret.

Verify the response contains the review URL, then report the URL and the
submitted state. If GitHub rejects an inline anchor, do not move it to an
unchanged line; post it as a general comment and record that change.
