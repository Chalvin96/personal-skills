#!/usr/bin/env bash
# local-ci: run a repo's PR CI checks locally, post a checklist comment, and
# optionally set commit statuses — for when GitHub Actions can't run.
#
# Generic + config-driven: reads `.local-ci.json` at the repo root. It hardcodes
# nothing about any project. See SKILL.md for the config schema.
#
#   run.sh            # run checks + post checklist comment on the current PR
#   run.sh --status   # also set commit statuses on HEAD (only for checks that ran)
#
# Honesty guards (a green status must mean the check actually passed on this commit):
#   - refuses a dirty working tree
#   - verifies local HEAD == the PR's head SHA, before checks AND before publishing
#   - only sets a status for a check that RAN; skipped checks are reported, never green
#   - any publish (comment/status) failure makes the script exit non-zero
set -uo pipefail

fail() { echo "local-ci: $*" >&2; exit 1; }
for bin in gh git python3; do command -v "$bin" >/dev/null || fail "missing dependency: $bin"; done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "not in a git repo"
cd "$REPO_ROOT"
CONFIG="$REPO_ROOT/.local-ci.json"
[ -f "$CONFIG" ] || fail "no .local-ci.json at repo root (see the local-ci SKILL.md schema)"

SET_STATUS=0
[ "${1:-}" = "--status" ] && SET_STATUS=1

# --- guards: clean tree, real PR, HEAD == PR head ---------------------------------
[ -z "$(git status --porcelain)" ] || fail "working tree is dirty — commit/stash first (a status would attach to a commit that isn't what you tested)"
git symbolic-ref -q HEAD >/dev/null || fail "detached HEAD is not supported"
SHA="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"

PR_JSON="$(gh pr view --json number,headRefOid,baseRefOid,headRepository,headRepositoryOwner 2>/dev/null)" \
  || fail "no PR for the current branch (open/push a PR first)"
PR="$(python3 -c 'import sys,json;print(json.load(sys.stdin)["number"])' <<<"$PR_JSON")"
PR_HEAD="$(python3 -c 'import sys,json;print(json.load(sys.stdin)["headRefOid"])' <<<"$PR_JSON")"
PR_BASE="$(python3 -c 'import sys,json;print(json.load(sys.stdin)["baseRefOid"])' <<<"$PR_JSON")"
OWNER="$(python3 -c 'import sys,json;print(json.load(sys.stdin)["headRepositoryOwner"]["login"])' <<<"$PR_JSON")"
NAME="$(python3 -c 'import sys,json;print(json.load(sys.stdin)["headRepository"]["name"])' <<<"$PR_JSON")"
SLUG="$OWNER/$NAME"
[ -n "$PR" ] && [ -n "$PR_HEAD" ] && [ -n "$PR_BASE" ] && [ -n "$OWNER" ] && [ -n "$NAME" ] || fail "could not resolve PR metadata"
[ "$SHA" = "$PR_HEAD" ] || fail "local HEAD ($SHORT) != PR head (${PR_HEAD:0:9}) — push, then re-run"
git cat-file -e "${PR_BASE}^{commit}" 2>/dev/null || git fetch -q origin "$PR_BASE" 2>/dev/null || true
# Available to job commands (e.g. diff-range ratchets): the PR's base and head SHAs.
export LOCAL_CI_BASE_SHA="$PR_BASE" LOCAL_CI_HEAD_SHA="$SHA" LOCAL_CI_SLUG="$SLUG" LOCAL_CI_PR="$PR"

# --- parse config -----------------------------------------------------------------
# Emits: PREFIX<TAB>..  / ENV<TAB>k=v  / JOB<TAB>name<TAB>cmd  / SKIP<TAB>name<TAB>reason
mapfile -t CFG < <(python3 - "$CONFIG" <<'PY'
import json,sys
c=json.load(open(sys.argv[1]))
print("PREFIX\t"+c.get("context_prefix",""))
for k,v in (c.get("env") or {}).items(): print(f"ENV\t{k}={v}")
for j in c.get("jobs",[]): print("JOB\t"+j["name"]+"\t"+j["run"])
for s in c.get("skip",[]): print("SKIP\t"+s["name"]+"\t"+s.get("reason",""))
PY
) || fail "invalid .local-ci.json"

PREFIX=""; declare -a JN JC SN SR
for line in "${CFG[@]}"; do
  IFS=$'\t' read -r kind a b <<<"$line"
  case "$kind" in
    PREFIX) PREFIX="$a" ;;
    ENV) export "${a?}" ;;
    JOB) JN+=("$a"); JC+=("$b") ;;
    SKIP) SN+=("$a"); SR+=("$b") ;;
  esac
done
[ "${#JN[@]}" -gt 0 ] || fail "no jobs in .local-ci.json"

# --- run checks -------------------------------------------------------------------
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT INT TERM
declare -a STATE
for i in "${!JN[@]}"; do
  printf '  %-38s ' "${JN[$i]}" >&2
  if bash -o pipefail -c "${JC[$i]}" >"$TMP/log" 2>&1; then
    STATE+=("success"); echo "PASS" >&2
  else
    STATE+=("failure"); echo "FAIL" >&2; tail -6 "$TMP/log" | sed 's/^/    /' >&2
  fi
done

# Re-verify HEAD did not move under us before we publish anything.
[ "$(git rev-parse HEAD)" = "$SHA" ] || fail "HEAD moved during the run — aborting publish"

# --- checklist comment ------------------------------------------------------------
{
  echo "## Local CI verification (\`$SHORT\`)"
  echo; echo "GitHub Actions unavailable — ran the \`.local-ci.json\` jobs locally on this commit:"
  echo; echo "| Check | Result |"; echo "|---|---|"
  for i in "${!JN[@]}"; do
    [ "${STATE[$i]}" = success ] && r="✅ pass" || r="❌ **FAIL**"
    echo "| ${JN[$i]} | $r |"
  done
  for i in "${!SN[@]}"; do echo "| ${SN[$i]} | ⏳ not run (${SR[$i]}) |"; done
  echo; echo "_Not a substitute for CI. Skipped checks were not verified._"
} > "$TMP/body.md"

PUB_FAIL=0
gh pr comment "$PR" --repo "$SLUG" --body-file "$TMP/body.md" >/dev/null \
  && echo "posted checklist to $SLUG#$PR" >&2 || { echo "local-ci: failed to post comment" >&2; PUB_FAIL=1; }

# --- statuses (only for checks that ran) ------------------------------------------
if [ "$SET_STATUS" = 1 ]; then
  for i in "${!JN[@]}"; do
    gh api -X POST "repos/$SLUG/statuses/$SHA" \
      -f state="${STATE[$i]}" -f context="${PREFIX}${JN[$i]}" \
      -f target_url="https://github.com/$SLUG/pull/$PR" \
      -f description="Verified locally (GH Actions unavailable)" >/dev/null \
      && echo "  status: ${PREFIX}${JN[$i]} = ${STATE[$i]}" >&2 \
      || { echo "local-ci: failed to set status ${JN[$i]}" >&2; PUB_FAIL=1; }
  done
fi

# --- exit code: nonzero if any check failed OR any publish failed -----------------
[ "$PUB_FAIL" = 0 ] || exit 1
for s in "${STATE[@]}"; do [ "$s" = failure ] && exit 1; done
exit 0
