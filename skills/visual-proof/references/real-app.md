# Capture a running app

Use this path when the changed screen needs the app's routes, navigation, or
real interactions. The Storybook capture CLI remains specific to Storybook;
for an app, use its existing browser driver or a small Playwright scenario.
Reuse this skill's diff and page commands below.

## Set the scenario before capture

Confirm a concrete scenario from the request, project recipe, or owner before
running it. Record:

- page/route and the user's task;
- role and data state, including prerequisites and isolated test data;
- actions in order and the expected visible result after each;
- base and head commit IDs, browser/version, viewport width and height, DPR;
- locale, time, motion, fonts, and assets that affect the result;
- applicable states and mobile/desktop widths, with reasons for exclusions.

Use [ume-verification](../../ume-verification/SKILL.md) recipes in
`knowledge/runtime.md` and `knowledge/scenarios/` to start and drive the app
when present. Record drift there. A one-off capture does not need a new recipe.
Use synthetic or approved local test data. Never seed production data.

## Capture both revisions

1. Resolve the PR's actual base and final head. Use isolated worktrees or
   builds for each; record how you confirmed each running revision. Do not
   capture the same server twice and label it two different revisions.
2. Prepare the same role and data snapshot independently for both revisions.
   Reset between runs when actions mutate state. Keep browser/version,
   viewport, DPR, route, locale, fonts, assets, and timing comparable. Wait for
   explicit readiness and the expected result, not an arbitrary delay.
3. Execute the scenario on base, observe each action's outcome, and capture
   the relevant region. Repeat on head. Record failed expectations as failures.
   Use one capture set per applicable state and width: empty, first-use/new
   account, sparse, typical, crowded/long text, loading, and error. Exclude
   states only with a reason; unavailable states remain proof gaps.
4. Store matching PNG filenames under `before/` and `after/`, for example
   `library-sparse@390.png`. Keep an evidence manifest beside them with the
   scenario, revisions, environment, observed outcomes, and capture paths.
   Inspect images for personal data, secrets, and unrelated account controls;
   crop to the relevant region without hiding task context. Keep raw captures
   local unless they are safe and explicitly intended for publication.
5. Reuse the existing comparison tools:

   ```bash
   node <skill>/scripts/diff.mjs --before <out>/before --after <out>/after --out <out>
   node <skill>/scripts/page.mjs --out <out> --serve
   ```

6. Inspect before, after, and diff at native scale, including the noise list.
   Record a verdict for every change and pair it with the observed action and
   outcome. A pixel diff proves a rendered change, not its quality or that an
   interaction worked. Run [ume-ui-review](../../ume-ui-review/SKILL.md) on the
   captures and retain its state coverage and limits with the proof.

A new route or state may have no base equivalent. Capture the actual base
outcome at the same entry point, explain that limitation, and keep it separate
from directly comparable pairs. Do not manufacture a baseline. Correct a
mistaken capture and rerun the pair instead of explaining away a mismatch.

## When preparation is blocked

Name what cannot be prepared and ask the owner for the exact missing captures:
base and head revisions, page, role/data state, actions, expected visible
result, viewport/DPR, and matching browser conditions. Request both sides and
any missing states. Never invent an image, substitute an older image, or reuse
a capture as if it came from another revision or state. Continue independent
work, but leave this proof Pending or Failed as appropriate. A draft can carry
that gap; a verified claim cannot.
