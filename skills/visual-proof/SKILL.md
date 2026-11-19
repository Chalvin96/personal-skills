---
name: visual-proof
description: Visual proof. Use for UI changes, baseline updates, or requested screenshots and comparisons.
---

# Visual proof

`<skill>` below is the directory holding this file.

Choose the capture source before starting. For a running app, follow
[real-app capture](references/real-app.md). For Storybook, use the steps below.
Both paths reuse this skill's diff and review page; neither a pixel diff nor
an unchanged image establishes UI quality. Pair captures with the observed
action and outcome, then run [ume-ui-review](../ume-ui-review/SKILL.md).

1. Once per machine, install the capture browser: `pnpm install --dir <skill>`.
2. From the target repository, capture, diff, and serve the review page. For
   Flyt, read [references/flyt.md](references/flyt.md) first for its flags.

   ```bash
   node <skill>/scripts/visual-proof.mjs \
     --stories story-id,another-story --widths 320,768 \
     --env KEY=VALUE --out visual-proof --serve
   ```

3. Open the printed URL. Give every **change** capture a verdict, intended or
   not, by the rules under **Judging a change**, then scan the noise list. The step is done when every change capture
   has a verdict.
4. Send the owner the page link with those verdicts before asking them to
   choose anything.

## Judging a change

Establish the intended target before judging. Confirm that the two captures are
comparable in viewport, DPR, route, state, data, fonts, and assets. Inspect the
boundaries of each changed effect before judging the whole frame. Metrics locate
differences; they never decide correctness.

## Running one step

Run one step alone with `scripts/capture.mjs`, `scripts/diff.mjs`, or
`scripts/page.mjs` when the preceding artifacts already exist. The page server
uses port 8790 by default.
