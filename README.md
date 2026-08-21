# Personal Skills

This is a personal engineering workflow that combines Matt Pocock's Wayfinder
with OpenSpec.

- **Wayfinder** maps large, uncertain work as a small set of GitHub decision
  tickets. It resolves the unknowns without pretending implementation is ready.
- **OpenSpec** starts when the route is clear. It records the proposal, design,
  behavioral requirements, tasks, implementation progress, and archive.
- **Knowledge** receives only verified, durable current-state facts after the
  change is implemented—not planning history.

The result is a deliberate handoff: `wayfinder` for discovery → `grill-me` for
pressure-testing decisions → OpenSpec for planned and implemented change. The
skills favor mechanical checks wherever a convention can be made executable.

Clone the private repository, then install every skill globally for Codex, Claude
Code, OpenCode, and Droid/Factory:

```bash
gh repo clone Chalvin96/personal-skills
cd personal-skills
./setup.sh
```

`setup.sh` installs the OpenSpec CLI globally. Initialize it inside a project
with `openspec init`.

Re-run `./setup.sh` after pulling updates; it replaces only the personal skill
folders in these locations:

- Codex: `$CODEX_HOME/skills` (default `~/.codex/skills`)
- Claude Code: `~/.claude/skills`
- OpenCode: `~/.config/opencode/skills`
- Droid/Factory: `~/.factory/skills`

## Skills

| Skill | Invocation | Dependency | Purpose |
| --- | --- | --- | --- |
| `wayfinder` | Automatic | `gh`, OpenSpec when available | Chart large uncertain initiatives. |
| `grill-me`, `writing-plans` | Automatic | OpenSpec | Resolve decisions and create plans. |
| `openspec-explore` | Automatic | OpenSpec | Investigate without implementation. |
| `openspec-propose`, `openspec-apply-change`, `openspec-sync-specs`, `openspec-to-knowledge`, `openspec-archive-change` | Explicit command | OpenSpec | Propose, implement, distill knowledge, synchronize, or archive a change. |
| `ume-conventions` | Automatic | None | Apply Python, FastAPI, Django, TypeScript, React, testing, simplicity, naming, and security conventions. |
| `ume-review` | Automatic | None | Review changes and test evidence against the conventions, trace real risks, and rewrite findings in ASD-STE100-informed English. |

Every skill falls back to the host's native question and task mechanisms. OpenSpec
skills require the globally installed `openspec` command.

Reviews are local and read-only by default; PR posting requires an explicit request.

## Attribution

- `skills/wayfinder` is adapted from [Matt Pocock's Wayfinder skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder), licensed under [MIT](https://github.com/mattpocock/skills/blob/main/LICENSE).
- `skills/openspec-*` are derived from [OpenSpec](https://github.com/Fission-AI/OpenSpec) generated workflow skills, available under [MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE).
- The UI visual-companion behavior in `skills/grill-me` is adapted from
  [Superpowers brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming).
