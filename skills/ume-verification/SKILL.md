---
name: ume-verification
description: Ume layer over pstack's create-verification-skill and maintain-verification-skill — keeps runtime recipes and the feature map in the repo's knowledge area for every agent, with Draft/Verified status that only an actual run can change. Use when implementation needs a runtime check, a recipe or feature entry is missing or has drifted, or the user asks how to exercise a feature locally.
---

# Ume Verification

One skill owns both creating recipes and keeping them true, because whoever
observes drift during a task is the right person to record it in the same
diff.

## With pstack

When pstack is installed, its `create-verification-skill` builds the driver
(launch, readiness, how to drive each feature) and its
`maintain-verification-skill` audits it. Use them for that work, with these
Ume overrides:

- Write their output into the knowledge area below, not `.claude/skills/verify/`,
  and point `AGENTS.md` at it. Codex and other agents read the repository's
  knowledge; a Claude-only skill folder hides the recipes from them.
- Keep the status rules below on every recipe and feature entry.
- Feature entries list every entry point (route, job, admin action, UI path).
  A check that drives one entry point leaves the others Draft.

Without pstack, write the recipes directly from the fields below.

## Where recipes live

In the target repository's knowledge area: `knowledge/runtime.md` for shared
run and connect guidance, `knowledge/scenarios/README.md` as the feature map
(one row per feature, its entry points, and its status), and
`knowledge/scenarios/<feature>.md` per feature.
Follow the repository's existing knowledge format and validator when it has
either; use these defaults only when it has none. Link new recipes from the
knowledge index. Include the edit in the task's diff — no separate
documentation approval — and preserve existing linked documents.

## Recipe fields

Fill only the fields this feature uses, and point to configuration files
rather than duplicating them.

| Field | Content |
| --- | --- |
| Run/connect commands | Exact commands to start or reach the target, with required tools and revisions. |
| Auth/data prerequisites | Roles, environment key names (never values), and the data conditions the scenario needs. |
| Readiness check | A cheap read-only observation proving the target is reachable and at the intended revision. |
| Steps | Ordered, each with its observable effect. |
| Observable expectations | What the observer sees when the feature works, per entry point the recipe claims to cover. |
| Evidence limits | What this recipe does not exercise, and what a pass here does not prove. |
| Status | Draft or Verified, per the rules below. |

## Status

A recipe starts Draft. Reading the source, however carefully, never verifies
one; only running it does. When a recipe runs successfully, record on the
entry the revision it ran against, the date, and a pointer to the evidence;
the entry becomes Verified for exactly that revision and scenario. Steps that
changed since the verified run go back to Draft until rerun. Keep prior
provenance when updating rather than erasing it.

## Keeping recipes true

When a task observes drift — a command changed, a route moved, an expectation
wrong — update the recipe and its status in the same diff as the change that
caused it, not in a later cleanup. A failing expectation is a product signal:
report it, and never rewrite the expectation to make a broken run pass. The
same goes for a step that fails on permissions: that is a defect to surface,
not a reason to sign in as an admin and step around it.

## Safety

Never record secrets, credentials, or personal data; name environment keys,
not values. Named sample records are hints to recheck, not fixtures: confirm
they still exist and still qualify before relying on them. Keep run artifacts
out of source control; a Verified entry points to evidence, it does not embed
it.
