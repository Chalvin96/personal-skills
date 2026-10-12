---
name: ume-design
description: Route any repo's design work to Ume's self-hosted Penpot — where the design goes, how an agent connects, and where the bot credentials live. Use when a task needs to put, read, or update a design in Penpot ("put the design in Penpot", "where's our Penpot", "Penpot login", "design this screen"), before any penpot-* skill runs.
---

# Ume Design

Thin router to Ume's internal Penpot. It answers three questions, then hands
off to the `penpot-*` skills for the actual design work.

## Setup lives in the environment

This skill holds no hosts, accounts, or paths. Read them from the shell
environment (exported in `~/.bashrc`):

| Variable | Meaning |
| --- | --- |
| `PENPOT_URL` | Penpot UI base URL |
| `PENPOT_AGENT_ENV` | Agent credentials |
| `PENPOT_BOT_DIR` | Directory of the agent keepalive (`keepalive.mjs`, `.pid`, `.log`) |
| `PENPOT_FLYT_FILE` | Workspace URL of Flyt's Design System file |

If a variable is unset, stop and ask the owner. Do not guess or search for
values.

- MCP: the server named `penpot` in your agent config. Its URL carries a user
  token. Never print, log, or paste it.
- Credentials: get them from the env, only inside the process that logs in.
  Never echo, commit, or screenshot them. Humans log in with their own
  account.

## Where the design goes

| Repo | Team | File | Page |
| --- | --- | --- | --- |
| `norsk` (Flyt app) | Flyt | Design System | `Foundations` (tokens), `Components`, `Screens` (one board per screen) |
| `norsk-lesson-factory` (Flyt lesson producer) | Flyt | Design System | `Screens`. Lessons render in Flyt, so build them from Flyt's components and tokens. |

- Any other repo may also use the Flyt team. It can add pages to the Design
  System file or create a new file there, with no approval needed.
- Flyt's own work stays in the one Design System file until Penpot ships live
  library-token sync (penpot#9334, 2.19). Penpot 2.15 does not share tokens
  across files, so a new file that should reuse Flyt's tokens copies them with
  Tokens → Tools → Export, then Import.
- Add a row above for any new repo once its design has a home.

## How to connect

The MCP acts on whichever file is open and focused in the browser tab the
plugin is connected to.

1. **Agent keepalive (default for Flyt).** `$PENPOT_BOT_DIR/keepalive.mjs`
   keeps `$PENPOT_FLYT_FILE` open in headless Chromium as the agent account.
   If the PID in `$PENPOT_BOT_DIR/keepalive.pid` is alive, the MCP is already
   connected to that file. It holds only that one file, so do not repoint it
   at another file without asking. Flyt work depends on it.
2. **Human tab (any other file).** Open the file in a browser, choose File →
   MCP Server → Connect, and keep that tab visible. A backgrounded tab makes
   calls time out.

Check the connection: your first Penpot call is always `high_level_overview`.
Then confirm the open file's name before writing anything.

## Then hand off

1. Read `~/.penpot-ai-kit/AGENTS.md` and follow it: tokens first, never
   one-shot, suggest then apply with review.
2. Use `penpot-router` to pick exactly one `penpot-*` skill. For example,
   `penpot-build-from-code` for code → screen, and `penpot-build-screen` for
   a brief → screen.
3. For Flyt designs, the `norsk` frontend's CSS custom properties are the source of truth for tokens. Snap
   values to the nearest existing token and never add a token just to match
   a measurement.

## Penpot 2.15 traps

- Open the page (`penpot.openPage`) before building on it. Text built
  off-page stays 1×1.
- Build in batches of 5–10 shapes. On a 30 s timeout, re-read the state
  before redoing anything, because the work usually landed.
- Shadow tokens are broken. Set `shape.shadows` directly.
- `font.applyToText` corrupts `fontId`. Set `fontId`, `fontFamily`,
  `fontVariantId`, and `fontWeight` directly.
- Shapes inside a variant set ignore writes. Move the main out, edit it, move
  it back, then re-set its variant props.
- Library components and pages cannot be deleted through the API. Delete
  them through the UI.
- `export_shape` can drop fresh text. For visual proof, select the shape,
  press Shift+2, and take a screenshot instead.
- The plugin API cannot move shapes between pages, and clipboard paste
  fails in a headless tab. To split a page:
  1. Duplicate the page in the UI.
  2. Open the copy with `penpot.openPage`.
  3. `remove()` the boards you don't want.

  A duplicated page shares shape ids with the original, and `remove()` acts
  on the current page, so open the copy first.
