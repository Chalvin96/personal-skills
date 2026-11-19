---
name: ume-ui-review
description: UI review. Use for supplied screenshots or the separate UI pass on components, styles, or user-facing copy changed in a diff.
---

# Ume UI review

Review the screen for the person using it, their task, and the current state.
Screenshots are enough to begin; a diff is optional. Do not edit the target app.
Capture and comparison belong to [visual-proof](../visual-proof/SKILL.md).
Runtime recipes belong to [ume-verification](../ume-verification/SKILL.md).

## Establish the context

Identify the audience, task, state, capture ID, revision if known, and viewport.
Read the target repository's `knowledge/design-system/` and similar design,
glossary, and metric documents when available. Use their vocabulary, metric
units and scope, and recorded decisions. Project rules override generic advice;
name any conflict with an accessibility requirement rather than silently waiving it.
For screenshots alone, name missing context and keep conclusions within what
is visible. An unfamiliar element calls for investigation, not deletion.

Run available deterministic checks first, such as measured contrast or target
bounds. Report their evidence once. Do not estimate precise ratios or CSS
sizes from image pixels, or invent tool results. Judgment follows those checks.

## Apply the removal test first

The house preference is a minimalist screen. Before scoring other concerns,
apply this question to the whole screen, then to every heading, label,
caption, helper line, count, number, and control:

> For this user, doing this task, in this state, what becomes harder if this disappears?

A reason to keep it must help someone identify something, find it, decide the
next step, orient themselves, avoid or recover from an error, or operate with
assistive technology. If nothing becomes harder and the element only makes
the screen look thorough, propose removing it. Apply the removal test to
replacement explanations too. For a group of related elements, assess its
contents together; name what stays or disappears and the task consequence.

Keep accessible names and semantic headings. Removing visible text may require
an accessible equivalent. Keep labels on unfamiliar controls, field labels,
necessary error instructions, and guidance needed at first use. Record why
these earn their place; minimalism is not a text-count target. Do not delete
something merely because you cannot tell what it is for. Investigate or leave
a question. A taste-only choice remains `suggestion`.

## Answer five questions

Apply the removal test and all five questions to every supplied capture. Before reporting, record an outcome for each: finding, no finding, or not checked with a reason. Consult [principles](references/principles.md) when explaining a judgment.

1. **Truthfulness.** Does each claim match what the data actually proves?
   Counts must name unit and scope; distinguish occurrences from distinct
   items. Label estimates. Describe stored status and recorded activity only
   as what they measure;
   claim comprehension or outcomes only with evidence for them. Do not present
   a metric driven mostly by account or history age as feedback on the current
   task. If the definition is unavailable, flag the ungrounded
   claim and ask for it rather than asserting how it was calculated.
2. **Task and action.** Can this audience identify the task and one primary
   next action? For completion states, consult
   [completion states](references/principles.md#completion-states). Keep one
   name per concept across this screen and related screens. Empty-state copy
   must name the empty collection and remain true beside populated collections.
3. **Necessity.** For every removal, explain what the retained screen lets the user do.
4. **Grouping and emphasis.** Is there one focal point appropriate to the task?
   Keep related things together. Use consistent styling for the same meaning.
   Visual cues that signal interactivity belong only on interactive elements.
   When interaction is unknown, request a runtime check rather than claim a
   screenshot proves that a control is inert.
5. **Perception and operation.** Check readable contrast, meaning beyond colour, visible focus when shown, and usable targets. Use the WCAG entry in [principles](references/principles.md) for thresholds, scope, and exceptions. Record which runtime checks remain untested, including keyboard access, focus order, zoom/reflow, and screen-reader behaviour.

## Cover states and widths

For each applicable state, review mobile and desktop captures: empty,
first-use/new account, sparse, typical, crowded/long text, loading, and error.
Record capture IDs and actual widths, or unknown. Name why each state or width
is excluded. Missing captures are `not reviewed`, never a pass or an assumed
exclusion. Continue the bounded review of supplied captures; request missing
captures through visual-proof when they are needed to complete UI proof.

## Report

Open with findings, or `No findings.` Follow the shared [finding format](../ume-review/references/comment-format.md), using `ui-review / <rule>` as the origin. Locate screenshot findings by capture ID and region; add file and line when known.

Each assessment names the audience, state, evidence, and consequence. Distinguish visible evidence, supplied facts, and unresolved questions. Each fix proposes a concrete simplification and explains what the retained screen supports.

Deduplicate findings with the parent review. Keep uncertain intent as a question.

End with states and widths reviewed/not reviewed, exclusions with reasons,
checks and their limits, and one verdict: Approve, Request changes, or Comment.
A bounded screenshot review can have no findings while full UI proof remains
incomplete. Never turn absent captures or runtime checks into verification.
