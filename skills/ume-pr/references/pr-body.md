# PR body format

Exactly these four sections, in this order, with nothing added.

```markdown
## Problem

<The user-visible failure or the technical constraint, in a sentence or two.>

## Solution

<What this change does. Name dependencies and rollout or rollback conditions
when they matter. Name every behaviour decision taken without asking the
requester, and why it was taken.>

## Behaviour Changes

<Observable changes, one bullet each, specific enough to check later.>

## Proof

<One claim per line, each labeled Proven, Failed, Pending, or Skipped, with
the evidence actually observed for it.>
```

## Labels

- **Proven**: observed on this change; name the exact command or scenario that
  produced the recorded result.
- **Failed**: attempted, and the observed result contradicts the claim; report
  the observed result.
- **Pending**: not yet observed. Name the scenario, the expected result, and
  the next action that would produce the observation.
- **Skipped**: deliberately not attempted; name why.

Reading the code, or an agent's summary of a run, is never an observation. A
claim stays inside what its evidence exercised: a unit test proves its unit,
not the endpoint around it; a service check proves the service, not the
route in front of it.

## Evidence

Local evidence is first-class because CI may not run. Results from the
repository's gate (`local-ci` when installed, otherwise the repository's
documented checks) are valid proof when they ran against this exact head.
Name the base revision for any before/after comparison, and keep the
conditions comparable. UI changes link the `visual-proof` triptych for the
changed stories. Link reviewer-accessible artifacts only; label local-only
paths as local-only and never invent a URL.

In a stack, a layer's Proof covers only what that layer itself introduces or
verifies; evidence that belongs to several layers sits on the layer that owns
it.
