# Change summary

Post this checkpoint before editing when a feature has several entry points
or starts writing a new kind of persisted record. The one-caller, one-sentence
skip applies only when neither trigger applies. Also skip when the requester
has already said to go ahead without a checkpoint.

Use this summary in the [ume-handover](../../ume-handover/SKILL.md) brief when
delegating implementation, so the receiver can follow the same proof plan.

Trace every entry point from source before posting. Write `not traced` rather
than guessing. Omit sections with nothing to say, keep the summary to about
one screen, and end with the final line exactly as written.

```markdown
**Change summary** (base <sha>)

Questions to settle
1. <question> — recommended answer: <answer> (<why you recommend it>).

Approaches (include this section only if a genuine alternative exists)
- **A (recommended):** <approach>; <what it costs>.
- **B:** <approach>; <what it costs>; <the concrete difference from A>.

Changes
- `<file or operation>`: <what changes>.

Entry points
| Entry point | What changes there | Traced from |
| --- | --- | --- |
| <caller> | <behavior, writes, output> | <file:line, or `not traced`> |

Conventions that apply
- <ume-conventions reference#section>: <how the change satisfies it>.

Proof plan
- <check> → demonstrates <observable result>.

Reply with answers, or with "go" to accept the recommendations.
```

Wait once. After the reply, implement without further pauses except the
blocked-proof and consequential-choice rules in [SKILL.md](../SKILL.md).
Answers given in that reply are agreed choices; record any later departure
from them, with the alternative considered and the reason.
