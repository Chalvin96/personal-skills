# Proof gate

List every material claim about what the PR fixes or adds. Each needs an
observed result from a test, recipe run, or UI proof tied to the final head
revision. Record the command or scenario, result, revision, and evidence path.
Source inspection and planned checks do not verify behaviour. After a head
change, rerun the affected proof and required gates; evidence from an earlier
head remains historical until the final-head run establishes the claim.

UI changes require real-app or Storybook before/after captures and inspected
diffs through [visual-proof](../../visual-proof/SKILL.md), one set per applicable
state at mobile and desktop widths, plus an
[ume-ui-review](../../ume-ui-review/SKILL.md) pass. Record exclusions and missing
states. Captures show the rendered result; observed actions and outcomes
support behaviour claims. A pixel diff alone proves neither correctness nor
quality.

Use [ume-verification](../../ume-verification/SKILL.md) for reusable runtime
recipes in `knowledge/runtime.md` and `knowledge/scenarios/`. A small one-off
check needs no recipe. Blocked proof may ship in a draft with its exact gap
labelled Pending, Failed, or Skipped as appropriate, but never as verified.
Do not mark the work verified or clear a merge gate with a named gap.
