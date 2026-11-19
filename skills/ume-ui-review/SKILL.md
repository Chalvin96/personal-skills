---
name: ume-ui-review
description: Judge screenshots for clear tasks, truthful claims, minimal content, grouping, and accessibility. Use on screenshots alone or as the separate UI pass for components, styles, or user-facing copy changed in a diff.
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
the screen look thorough, report it and propose the simpler screen. Do not
replace removed clutter with a new explanation of the same clutter. A misleading
headline does not finish the removal test: examine its chart, supporting
breakdown, legend, and metadata too. Name which of those stay or disappear
and the task consequence, even when removing the whole panel.

Keep accessible names and semantic headings. Removing visible text may require
an accessible equivalent. Keep labels on unfamiliar controls, field labels,
necessary error instructions, and guidance needed at first use. Record why
these earn their place; minimalism is not a text-count target. Do not delete
something merely because you cannot tell what it is for. Investigate or leave
a question. A taste-only choice remains `suggestion`.

## Answer five questions

Use these as the spine of one review. The supporting
[principles](references/principles.md) explain judgments, not extra passes.

1. **Truthfulness.** Does each claim match what the data actually proves?
   Counts must name unit and scope; distinguish occurrences from distinct
   items. Label estimates. A stored status does not prove comprehension or
   learning. Do not present a metric driven mostly by account age as feedback
   on the current task. If the definition is unavailable, flag the ungrounded
   claim and ask for it rather than asserting how it was calculated.
2. **Task and action.** Can this audience identify the task and one primary
   next action? Completion states lead with what was completed and one next
   action. Recording that someone finished or saved something does not prove
   they read, understood, or learned it. Keep one name per concept across this
   screen and related screens. Empty-state copy must name the empty collection
   and remain true beside populated collections.
3. **Necessity.** Carry forward the removal test. For each proposed removal,
   explain what the retained content lets the user do. A completion screen
   often needs only a completion line, task-relevant items such as looked-up
   words, and one primary action. In a completion-screen proposal, name the
   completion line, the task-relevant result, and the primary action explicitly.
   If result data such as looked-up words is absent, say it is unavailable and
   propose showing it only when backed by that data. Never invent items or counts.
4. **Grouping and emphasis.** Is there one focal point appropriate to the task?
   Keep related things together. Use consistent styling for the same meaning.
   Underlines or other cues that promise tapping belong only on interactive
   elements. When interaction is unknown, request a runtime check rather than
   claim a screenshot proves that a control is inert.
5. **Perception and operation.** Check readable contrast, meaning beyond colour,
   visible focus when shown, and usable targets. WCAG 2.2 AA requires 4.5:1
   for normal text, 3:1 for large text and applicable UI boundaries or states.
   Pointer targets under 2.5.8 need at least 24 by 24 CSS pixels or a qualifying
   spacing, equivalent-control, inline, user-agent, or essential exception.
   The 44 by 44 CSS pixel threshold is AAA 2.5.5, not AA. Use the linked WCAG
   criteria for scope and exceptions. Screenshots cannot prove keyboard access,
   focus order, zoom/reflow, or screen-reader behaviour. Say what was not checked.

## Cover states and widths

For each applicable state, review mobile and desktop captures: empty,
first-use/new account, sparse, typical, crowded/long text, loading, and error.
Record capture IDs and actual widths, or unknown. Name why each state or width
is excluded. Missing captures are `not reviewed`, never a pass or an assumed
exclusion. Continue the bounded review of supplied captures; request missing
captures through visual-proof when they are needed to complete UI proof.

## Report

Open with findings, or `No findings.` Use the shared
[finding format](../ume-review/references/comment-format.md):

```markdown
**warning** · ui-review / truthfulness · capture-id.png, mastery panel → the headline does not describe this task

Name the element, audience, state, observed evidence, and consequence.
Distinguish visible evidence from supplied facts and unresolved questions.

---

Propose a concrete simplification and explain what the retained screen supports.
```

Use `critical`, `warning`, or `suggestion` as defined in that format. Origin is
`ui-review` plus the rule, such as removal test, truthfulness, task and action,
grouping, or perception and operation. A screenshot region is a valid location
without a diff; add file and line only when known. Every finding names the
element, screenshot, audience, consequence, and proposed simplification.
Deduplicate findings with the parent review. Keep uncertain intent as a question.

End with states and widths reviewed/not reviewed, exclusions with reasons,
checks and their limits, and one verdict: Approve, Request changes, or Comment.
A bounded screenshot review can have no findings while full UI proof remains
incomplete. Never turn absent captures or runtime checks into verification.
