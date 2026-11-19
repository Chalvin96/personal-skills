# Supporting principles

Use these to explain the five questions in the skill. They do not introduce
additional review passes or override project decisions.

- Nielsen's ten heuristics cover status feedback, familiar concepts, user
  control, consistency, error prevention, recognition, efficient use, minimal
  presentation, recovery, and help. Apply the relevant heuristic to a concrete
  task consequence. [Nielsen Norman Group](https://www.nngroup.com/articles/ten-usability-heuristics/).
- Gestalt grouping explains why nearby items seem related, similar treatments
  suggest similar roles, and a shared boundary implies a group. Check the
  relationship the screen communicates before adding another container.
  [Proximity](https://www.nngroup.com/articles/gestalt-proximity/),
  [similarity](https://www.nngroup.com/articles/gestalt-similarity/),
  [common region](https://www.nngroup.com/articles/common-region/).
- Progressive disclosure puts infrequent detail behind an intentional action.
  It must preserve what people need for their current decision, including
  first-use guidance. [Nielsen Norman Group](https://www.nngroup.com/articles/progressive-disclosure/).
- Hick's law relates decision time to the number and complexity of choices.
  Reduce competing choices when that helps the task; it does not justify
  removing needed information or impose a universal item limit.
  [Laws of UX](https://lawsofux.com/hicks-law/).
- WCAG 2.2 supplies testable accessibility requirements. Use
  [1.4.3 text contrast](https://www.w3.org/TR/WCAG22/#contrast-minimum),
  [1.4.11 non-text contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast),
  [1.4.1 use of colour](https://www.w3.org/TR/WCAG22/#use-of-color),
  [2.4.7 focus visible](https://www.w3.org/TR/WCAG22/#focus-visible),
  [2.4.11 focus not obscured](https://www.w3.org/TR/WCAG22/#focus-not-obscured-minimum),
  and [2.5.8 target size](https://www.w3.org/TR/WCAG22/#target-size-minimum).
  AA targets are 24 by 24 CSS pixels with the criterion's exceptions;
  [2.5.5's 44 by 44 requirement](https://www.w3.org/TR/WCAG22/#target-size-enhanced)
  is AAA. Normal text needs 4.5:1, large text 3:1. Large means at least 18pt,
  or 14pt bold. Applicable UI components and graphical objects need 3:1.
  The criteria define exceptions. Images alone cannot establish conformance;
  also test keyboard, semantics, focus, zoom, and reflow at runtime.
- Plain language helps people identify actions and recover from errors. Use
  familiar words, descriptive labels, useful headings, and direct instructions.
  [W3C writing guidance](https://www.w3.org/WAI/tips/writing/).
  Use the separately installed `simplified-technical-english` skill for prose
  when available; this skill does not own a writing workflow.
