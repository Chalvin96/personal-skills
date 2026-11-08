# Personal Skills

This is a personal engineering workflow that combines Matt Pocock's Wayfinder
with OpenSpec.

- **Wayfinder** maps large, uncertain work as a small set of GitHub decision
  tickets. It resolves the unknowns without pretending implementation is ready.
- **OpenSpec** starts when the route is clear. It records the proposal, design,
  behavioral requirements, tasks, implementation progress, and archive.
- **Knowledge** receives only verified, durable current-state facts after the
  change is implemented, excluding planning history.

The result is a deliberate handoff: `wayfinder` for discovery → `grill-me` for
pressure-testing decisions → OpenSpec for planned and implemented change. The
skills favor mechanical checks wherever a convention can be made executable.

Install every skill globally for supported agents with `npx skills`:

```bash
npx skills add Chalvin96/personal-skills --global --all
```

OpenSpec is optional. If you use the OpenSpec workflow, install its CLI
separately and initialize it inside a project:

```bash
npm install --global @fission-ai/openspec
openspec init
```

## Skills

| Skill | Invocation | Dependency | Purpose |
| --- | --- | --- | --- |
| `wayfinder` | Automatic | `gh`, OpenSpec when available | Chart large uncertain initiatives. |
| `grill-me`, `writing-plans` | Automatic | OpenSpec | Resolve decisions and create plans. |
| `openspec-explore` | Automatic | OpenSpec | Investigate without implementation. |
| `openspec-propose`, `openspec-apply-change`, `openspec-sync-specs`, `openspec-to-knowledge`, `openspec-archive-change` | Explicit command | OpenSpec | Propose, implement, distill knowledge, synchronize, or archive a change. |
| `ume-conventions` | Automatic | None | Route implementation and review work to the canonical Python, FastAPI, Django, TypeScript, React, testing, simplicity, naming, and security references, plus shared reliability, data-modeling, and comments rules. |
| `ume-review` | Automatic | `gh` for PR posting | Review changes and test evidence against the conventions, trace real risks, and post PR reviews after explicit authorization. Changed lines are also checked against the repository's own pre-commit hooks in a throwaway worktree. |
| `ume-implement` | Automatic | git | Execute scoped features, bug fixes, refactors, and performance changes on a fresh branch in their own worktree, with per-kind proof and an honest final report. |
| `ume-handover` | Automatic | None | Carry work to another session, place, or receiver with a durable brief and explicit evidence. |
| `ume-pr` | Explicit command | `gh` to publish | Draft and publish PR descriptions with labeled, local-first proof; update existing PRs safely; split large changes into verifiable layers. |
| `ume-verification` | Automatic | pstack optional | Write and maintain runtime recipes in the target repo's knowledge area, with Draft/Verified status that only an actual run changes. |
| `ume-skill-authoring` | Explicit command | pytest | Change or add skills in this repository behind a confirmed five-line brief. |

Every skill falls back to the host's native question and task mechanisms. OpenSpec
skills require the globally installed `openspec` command.

Reviews do not edit target source. PR targets post the finished review only after
explicit authorization; working-tree reviews produce terminal output.

The issue workflow skills (`setup-matt-pocock-skills`, `triage`, `to-spec`, and
`to-tickets`) use the repository's configured GitHub, GitLab, or local Markdown
tracker. Run `/setup-matt-pocock-skills` once per product repository.

`ume-conventions` is a thin router. Its `references/` files are the canonical
rules that future implementation and review skills can reuse directly.

## With pstack

`ume-implement`, `ume-verification`, and `ume-pr` layer on
[pstack](https://github.com/michael-denyer/pstack-claude) when it is installed:
pstack's `how`, `why`, `blast-radius`, `tdd`, verification and PR-tidying skills
do the generic work, and the ume skills add repository rules (worktrees, local
gates, proof labels, knowledge placement). Without pstack, each ume skill falls
back to a short inline step.

## Agents

`npx skills` installs skills only; it does not install agents. To use the
read-only source-lookup agent from a clone of this repository:

```bash
mkdir -p ~/.claude/agents ~/.codex/agents
ln -s "$PWD/agents/claude/ume-source-reader.md" ~/.claude/agents/
ln -s "$PWD/agents/codex/ume-source-reader.toml" ~/.codex/agents/
```

## Attribution

- `skills/ume-handover` draws ideas from Matt Pocock's MIT-licensed `handoff` skill in [mattpocock/skills](https://github.com/mattpocock/skills). Its wording is original.
- `skills/wayfinder` is adapted from [Matt Pocock's Wayfinder skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder), licensed under [MIT](https://github.com/mattpocock/skills/blob/main/LICENSE).
- `skills/openspec-*` are derived from [OpenSpec](https://github.com/Fission-AI/OpenSpec) generated workflow skills, available under [MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE).
- The UI visual-companion behavior in `skills/grill-me` is adapted from
  [Superpowers brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming).
