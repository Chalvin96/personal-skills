---
name: visual-proof
description: "Before | after | pixel-diff triptychs of Storybook stories across widths, with real changes split from anti-aliasing noise on one review page. Use when a change is visible in the UI, a visual baseline moves, or the owner asks for screenshots, a diff, or proof before choosing."
---

# Visual proof

`<skill>` below is the directory holding this file.

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
