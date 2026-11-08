# Refactor playbook

Answer each question before starting, and again before calling it done.

- **What stays identical?** Behaviour, exactly as it was: outputs, errors,
  public contracts. A refactor that alters any of them is two changes
  wearing one commit.
- **What will demonstrate that?** Name the equivalence evidence first and
  get it green against the old code: existing tests, plus characterization
  checks for anything uncovered. Compiling and linting cleanly prove
  nothing about behaviour.
- **How does the old path die?** Move each caller onto the new shape, then
  delete the old path inside the same change when nothing outside the
  repository can still reach it. An independently deployed consumer keeps
  compatibility until
  [removing a shared interface](../../ume-conventions/references/reliability.md#removing-a-shared-interface)
  has run its course.
- **What else snuck in?** Nothing. A drive-by behaviour change belongs to
  its own task; this diff moves structure only.
