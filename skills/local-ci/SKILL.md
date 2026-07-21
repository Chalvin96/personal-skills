---
name: local-ci
description: Use when GitHub Actions cannot run for infrastructure reasons (billing/spending-limit block, runner outage) and you need to verify a PR's CI locally and reflect the result on the PR. Reads a repo-local `.local-ci.json`, runs each declared job locally, posts a checklist comment, and (optionally) sets commit statuses. Repo-agnostic — no project is hardcoded.
---

# Local CI

Runs a project's CI checks locally when GitHub Actions is unavailable, then reflects the
outcome on the PR. It is **config-driven**: the job list lives in the target repo's
`.local-ci.json`, so this skill hardcodes nothing.

## When to use

- Actions is blocked ("recent account payments have failed / spending limit"), the
  runner is down, or CI otherwise can't trigger.
- You want the PR's check list / commit statuses to reflect a verified-locally result.

## Prerequisites

- `gh` authenticated with **commit-status write** on the repo, plus `git`, `python3`.
- Whatever runtimes the configured jobs need (uv/pnpm/etc.) and any services (e.g. a
  local Postgres) they assume. If a job needs a disposable DB/env that isn't present
  locally, put it in `skip` — do not let it report a possibly-false result.

## Config: `.local-ci.json` at the repo root

```jsonc
{
  "context_prefix": "ci / ",           // prepended to each job name for the status context
  "env": { "ADMIN_SESSION_SECRET": "development-admin-session-secret" },
  "jobs": [                            // each RUNS locally; its result drives the status
    { "name": "Backend Tests", "run": "cd backend && uv run pytest -q" }
  ],
  "skip": [                            // reported as "not run", NEVER set green
    { "name": "Flyt E2E", "reason": "needs the full-stack runner" }
  ]
}
```

- Job `name` MUST match the GitHub check name (minus `context_prefix`) so `--status`
  aligns with any branch-protection required contexts.
- Put every **gating** CI job in `jobs`, or in `skip` with a reason. Anything omitted is
  silently unverified — don't omit gating checks.

## Run it

```bash
<skill>/run.sh            # run jobs + post the checklist comment
<skill>/run.sh --status   # also set a commit status per job on HEAD
```

## Honesty guards (why a green status here is trustworthy)

- Refuses a **dirty working tree** and requires local **HEAD == the PR head SHA** (checked
  before running and again before publishing) — a status can't attach to a commit you
  didn't test.
- `--status` sets each status to the **actual local result**; a failed check is set
  `failure`. Skipped jobs get **no** status.
- Any comment/status API failure makes the run exit non-zero.
- Uses `bash -o pipefail` per job so a `failing | succeeding` command can't read green.

## Caveats

- Not a substitute for CI. It verifies only what the config runs; `skip` jobs (e2e,
  container scans, anything needing infra) are unverified.
- Commit statuses are separate from Actions check-runs; they satisfy branch-protection
  rules that require *status contexts* by name, but they don't erase failed Actions runs.
- Re-run after every push (statuses/comment are per-commit).
