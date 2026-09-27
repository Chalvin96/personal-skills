# Corner-bleed review

Inspect children whose fill or border reaches a rounded corner. Report only when
painted pixels cover that corner despite clipping and radius rules; cite the
container, child, affected corner, and evidence. A painted child reaching a
straight edge alone is not enough.

Check the rendered result or trace the container's clipping and the child's
radius and painted bounds in code. When the repository has an automated
corner-bleed check, name it in the evidence, for example Flyt's Storybook
`cornerBleed` check.
