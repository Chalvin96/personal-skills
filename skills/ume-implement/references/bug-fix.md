# Bug fix playbook

Answer each question before the fix is called done.

- **Does it reproduce?** Write the smallest failing test and confirm it
  fails for the reported reason, not for a broken fixture or environment.
  Where no reproduction is possible, say so plainly, run the strongest
  check available, and report the gap.
- **What is the actual cause?** Watch it happen — logs, a debugger, a
  probe — before believing a theory, and patch the cause rather than the
  symptom.
- **Does the reproduction pass now?** The test from the first question
  turns green after the fix, without weakening it.
- **Where else does this pattern live?** Search the codebase for the same
  shape of bug; fix the copies or file them.
- **What is known to have failed before?** Only what was watched failing.
  When the original breakage was never observed, "broken then, fixed now"
  stays unknown; report what was actually seen.
