---
name: visual-proof
description: "Before | after | pixel-diff triptychs of Storybook stories across widths, with real changes split from anti-aliasing noise on one review page. Use when a change is visible in the UI, a visual baseline moves, or the owner asks for screenshots, a diff, or proof before choosing."
---

# Visual proof

Use the entry point from the target repository:

```bash
node /path/to/visual-proof/scripts/visual-proof.mjs \
  --stories story-id,another-story --widths 320,768 \
  --env KEY=VALUE --out visual-proof
```

Open the generated `index.html`. Review every **change** capture by eye, then
the noise list, and report what moved and whether it was intended. The owner
always gets the triptych page before being asked to choose.

Establish the intended target before judging. Confirm that the two captures are
comparable in viewport, DPR, route, state, data, fonts, and assets. Inspect the
boundaries of each changed effect before judging the whole frame. Metrics locate
differences; they never decide correctness.

For Flyt, read [references/flyt.md](references/flyt.md) before capturing.

Run one step alone with `scripts/capture.mjs`, `scripts/diff.mjs`, or
`scripts/page.mjs` when the preceding artifacts already exist. The page server
uses port 8790 by default.
