# Maintainer evals

These are synthetic or cropped, non-personal fixtures approved for this public
repository. Case A is the supplied Flyt completion crop. Case B crops the
supplied library capture to the reading content, excluding account navigation
and the recorder overlay. Case C is original static HTML and a Playwright PNG.
The fixtures contain no personal names, emails, tokens, or account pages.

For each case, start a fresh agent with `skills/ume-ui-review/SKILL.md`, references it requests, that case’s task and inputs. Keep the expectations file available only to the evaluator.
Attach the PNG or use the runner's image-viewing tool. Keep raw prompts,
transcripts, and outputs outside git and identify the tested revision/tree.
Read each output and mark every expectation met or missed. When a case misses,
fix only a general principle the skill lacks; never write a case's answer,
fixture nouns, or app-specific wording into the skill. If the expectation
demands what the inputs cannot show, fix the expectation instead and say so.
Rerun at most two rounds; retain every round and report remaining misses.
These trials exercise judgment, not a deterministic pass/fail script or a
guarantee for other screens.
