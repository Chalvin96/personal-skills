---
name: ume-skill-authoring
description: Change or add skills in this repository safely — a five-line brief before editing, a reproduction gate for claimed defects, a new-skill-vs-enhancement ladder, and the mechanical-vs-judgment split. Use when editing any SKILL.md, reference, script, test, or agent file in this repository.
---

# Ume Skill Authoring

## Brief before editing

Write five lines before touching anything:

1. the requested behaviour;
2. the evidence behind it;
3. the observable result the change should produce;
4. the files allowed to change;
5. what must keep working afterwards.

Post the brief and stop for confirmation. Earlier approval of the overall task does not
cover this brief. When the reply alters it, repost the revised brief. Count as evidence: an actual user request, a run
that went wrong, a reviewer's remark, or a session transcript. When the evidence or the list of things that must
keep working is incomplete, ask the user for specific cases that went wrong; do
not ask how they would implement it.

## Reproduction gate

A claimed defect must be reproduced before any instruction changes: replay
the task or run the smallest isolated trial that shows the failure, and keep
the transcript outside git. An unreproduced claim leaves the instruction
change blocked; keep going on parts whose evidence already holds. Scope
the fix to what the trial showed; one reproduced symptom does not license a
wider rule. An explicit new capability needs no invented defect:
agree on the outcome and label any synthetic trial as synthetic.

## New skill or enhancement

Prefer fewer skills: each extra one is another candidate the router must rule
out. Take these steps in order and stop once one settles it:

1. Tighten the existing description. What looks like a missing skill is often
   a description that routes imprecisely.
2. Split only at a real workflow seam: sections whose triggers, consumers, or
   loading moments genuinely differ, or that must prove different evidence to
   be admitted.
3. If a parent skill always pulls in a child, every run pays for both; merge
   them.

If both parts serve the same reader, load at the same moment, and are never
wanted apart, extend the existing skill.

## Mechanical or judgment

A rule a machine can decide goes into a script, test, or config — never into
prose the model must re-derive by inspection. Each scripted rule needs a
test that triggers it, a near-miss test that must pass silently, and fixed
exit codes; deliberately invalid examples live inline in tests, not as browsable
fixtures. Judgment (intent, relevance, trade-offs, clarity) stays in prose.
Scripts run first; model judgment comes after.

## Runtime files and maintainer artifacts

Users install the skill directory; it should contain nothing except what the
skill runs: `scripts/` for checks and transformations, `references/` for
knowledge loaded while running. Tests and contributor documentation belong to
maintainers and live at repository level. Link only to paths that resolve
after installation.

## Validation

This repository has no evaluation harness yet; when one exists, its step
slots in here. Until then, validate every change with the repository's pytest
suite plus one manual trial of the affected workflow in an isolated worktree.
Keep transcripts and trial artifacts outside git. Report which layer each
check actually reached: a passing test file does not validate routing
behavior, and one trial is one trial, not a pattern.
