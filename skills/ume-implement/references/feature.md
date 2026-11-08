# Feature playbook

Before calling the work done, answer every question below — from the source,
not from the ticket.

- **Who invokes the change?** Every caller: API routers, background jobs,
  admin tooling, frontend code, anything else that reaches it.
- **What does each caller see afterwards?** The response, the output, the
  screen: one line per caller.
- **What is written where?** New or changed persisted records, and the
  fields each one gains.
- **What if it stops halfway?** Which writes survive a failure between two
  steps, and what a retry then does to them.
- **Which permission rules govern it?** The authorization each caller
  already passed must still hold on the new path.
- **What proves each caller?** A real scenario per caller: pytest on the
  backend, Vitest on frontend units, Playwright end to end, and a
  [visual-proof](../../visual-proof/SKILL.md) triptych whenever the UI
  changed. Proof on one caller says nothing about the rest.

Several callers, or a new kind of persisted record: post the
[change summary](change-summary.md) and wait for the reply before editing.
