---
name: ume-handover
description: Write a durable handover when work moves to another harness, repo, directory, machine, agent, or person, or forks into a side task while the session continues.
---

# Ume Handover

Use this when work must travel, including Claude to Codex and back. If work
stays in the same session and place, say that compaction is enough instead
of writing a file.

Tailor the brief to the next session's stated purpose. If it is missing,
ask in one line what the receiver needs to do.

Include:

- the purpose;
- repo, branch, worktree path, and base and head SHAs;
- what is done, in flight, and next;
- decisions already made and why;
- open questions;
- gates the receiver must run;
- files or areas to leave untouched;
- suggested skills to load, naming both ume-* and other relevant skills.

Mark every claim `verified` with an evidence pointer, or `unverified`.
Keep unchecked beliefs visibly unverified; the receiver relies on this
document. Link specs, issues, PRs, commits, diffs, and knowledge documents
by path or URL rather than copying their contents.

Redact secrets, tokens, credentials, and personal data. Name where the
receiver can obtain what they need instead.

Save the brief outside the working tree in a durable location the receiver
can read after a reboot. For a receiver working from the tracker, an issue
or PR comment also works when posting is authorized. Never rely on `/tmp`.
Return the path or URL and point the receiver there. Do not interpolate the
brief's text into a shell command; backticks and `$` can change its contents.
