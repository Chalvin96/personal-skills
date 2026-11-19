# Maintainer evals

These are synthetic or cropped, non-personal fixtures approved for this public
repository. Case A is the supplied Flyt completion crop. Case B crops the
supplied library capture to the reading content, excluding account navigation
and the recorder overlay. Case C is original static HTML and a Playwright PNG.
The fixtures contain no personal names, emails, tokens, or account pages.

For each case, start a fresh agent with only SKILL.md, its linked references,
that case's task.md, and inputs. Do not expose expectations.md to the runner.
Attach the PNG or use the runner's image-viewing tool. Keep raw prompts,
transcripts, and outputs outside git and identify the tested revision/tree.
Read each output and mark every expectation met or missed. Improve the skill
and rerun missed cases, at most two rounds; retain both rounds and report any
remaining misses. These trials exercise judgment, not a deterministic pass/fail
script or a guarantee for other screens.
