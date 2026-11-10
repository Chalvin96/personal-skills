---
name: ume-implement
description: Execute a scoped feature, bug fix, refactor, or performance change on a fresh branch in its own worktree, with proof matched to the task kind and an honest final report. Use when the user asks to build, fix, restructure, or speed up something.
---

# Ume Implement

This skill adds Ume's repository workflow on top of pstack. When pstack's
`poteto-mode` is active, it still sets the working style and its principles
apply; this skill decides where the work happens, what proof each kind of
change needs, and how it is reported. Where both speak, the repository's
`AGENTS.md` wins, then this skill, then pstack defaults.

## Start

1. Fetch `origin`, work out its default branch, and cut the task branch from
   that branch as just fetched. A base the request names, or a request to
   continue work already begun, overrides this.
2. Carry out the task in a git worktree, placed wherever the repository's
   worktree convention puts worktrees. The user's own checkout is not yours
   to touch: never switch its branch, never stash, reset, or discard its
   uncommitted files.
3. Read the repository's `AGENTS.md`, then the knowledge documents covering
   the area the task changes. A missing document does not stall the work;
   name the gap in the report.
4. A question that only needs explaining gets an answer, not an edit.

## Select the playbook

With pstack installed, run its `poteto-mode` playbook for the task kind
(Feature, Bug fix, Refactoring, Perf issue) and apply this skill's Start,
Route, Choices, and Final report rules on top. A repository can add its own
differences as pstack project playbooks under `.agents/playbooks/`.

Without pstack (for example a delegate that has no pstack skills), use the
short fallback playbooks:

| Task | Fallback playbook |
| --- | --- |
| New or changed behavior | [feature](references/feature.md) |
| Reported defect | [bug fix](references/bug-fix.md) |
| Same behavior, different structure | [refactor](references/refactor.md) |
| Measured slowness | [performance](references/performance.md) |

All code follows [Ume Conventions](../ume-conventions/SKILL.md).

When a feature has several entry points, or starts writing a new kind of
persisted record, stop at the [change summary](references/change-summary.md)
checkpoint before editing.

## Token budget

pstack's fan-out skills spawn several subagents each. Spend them only where
they change the outcome:

- Do a step inline when the session can; spawn at most one subagent per step,
  on the cheapest model that can do it. Never spawn a subagent on the
  session's own top-tier model just to hold a second copy of the work.
- Panels (`architect`, `interrogate`, `arena`) run a single runner unless the
  user asks for a panel.

- `how`: take its single-agent path; spawn parallel explorers only when the
  flow crosses services or packages.
- `why`: search git history, PRs, and issues; widen to other sources only
  when the user asks for the full investigation.
- `architect`, `interrogate`, `arena`, `swarm`: only for a new module or a
  changed cross-package interface, or when the user asks.
- Principles: read only the leaf skills that changed a decision, and name
  only those.
- Implementation itself goes to the delegate the user's rules name, not to
  extra subagents of the planning session.
- A delegate brief states the problem, evidence, constraints, and the
  placement decision with its reason. It names a file or line only after that
  decision is recorded.
- If that delegate is down or out of quota, report it and stop that step,
  or use the next delegate the user named. Never substitute Opus or another
  top-tier subagent. When the user says the delegate is back, restart the
  stopped step from its brief, not from an unchecked partial result.

## Route

| Need | Use |
| --- | --- |
| Any code edit | [Ume Conventions](../ume-conventions/SKILL.md) |
| Runtime observation; missing or drifted recipe | [Ume Verification](../ume-verification/SKILL.md) |
| PR description or publication | [Ume PR](../ume-pr/SKILL.md) |
| Unfamiliar flow or placement | pstack `how` when installed; otherwise trace the flow from its real entry points and callers in source |
| Unexplained constraint | pstack `why` when installed; otherwise read decision records, then the constraint's history in git |
| Symptom in data another system produces | Decide the owner before choosing a file: the system where the fact is first known publishes it as a field, and the consumer maps published fields. Consumer code that derives meaning from the producer's content (label text, "all segments are X", guessing a missing field) is a stop: propose the producer change instead. Existing inference of that kind is debt, not precedent. |
| Changed shared contract | pstack `blast-radius` when installed; otherwise list every consumer of the changed name, field, or payload and name the assumption that clears each risk |
| Cheap regression path or requested TDD | pstack `tdd` when installed; otherwise write the failing check, fix, keep it green |
| Local gate | `local-ci` when installed; otherwise the repository's documented checks |
| Visual evidence for UI changes | [visual-proof](../visual-proof/SKILL.md) |
| Stacked layers for a split change | `gh-stack` when installed |

## Choices and blocks

Record every behaviour choice the request did not settle — including defaults
inherited from existing code and fallbacks added for failure paths — in the
final report and the PR Solution. Never leave a choice only in code.
Interrupt with a question only when the answer would change the contract the
requester asked for or lock in a decision that is expensive to undo;
otherwise take the option nearest existing behavior, write it down, and move
on.

When proof is blocked, say exactly what blocked it, ask one direct question
naming the missing input, and continue with independent work. Installing
dependencies, starting services, and preparing data need the human's
go-ahead. A missing check is a reported gap, not a silently skipped one;
reuse evidence the user supplies when it matches the current diff.

## Final report

- changed behaviour and changed files;
- base and final head, by SHA or tree identity;
- checks actually run, each with its raw result; unrun or blocked checks,
  each with its reason;
- behaviour choices made, including inherited defaults and fallbacks;
- remaining gaps.

Call the task done only when every item maps to a place in the code and to a
check result or a named gap — and the diff holds the requested change and
nothing else.
