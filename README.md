# Personal Skills

Reusable Codex skills for engineering discovery and OpenSpec change management.

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
| `openspec-propose`, `openspec-apply-change`, `openspec-sync-specs`, `openspec-archive-change` | Explicit command | OpenSpec | Propose, implement, synchronize, or archive a change. |

Every skill falls back to the host's native question and task mechanisms. OpenSpec
skills require the globally installed `openspec` command.

## Attribution

- `skills/wayfinder` is adapted from [Matt Pocock's Wayfinder skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder), licensed under [MIT](https://github.com/mattpocock/skills/blob/main/LICENSE).
- `skills/openspec-*` are derived from [OpenSpec](https://github.com/Fission-AI/OpenSpec) generated workflow skills, available under [MIT](https://github.com/Fission-AI/OpenSpec/blob/main/LICENSE).
- The UI visual-companion behavior in `skills/grill-me` is adapted from
  [Superpowers brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming).
