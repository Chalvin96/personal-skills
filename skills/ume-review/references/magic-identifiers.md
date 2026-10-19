# Magic domain identifiers

Use this lane to catch repeated finite domain values that should have one
source of truth. It complements the mechanical checker; it does not replace
reading the boundary and its callers.

## Admission gate

Report a warning only when all of these are true:

- changed production JavaScript or TypeScript hard-codes a finite domain
  identifier (provider/model ID, action or reason code, route anchor, event
  type, or status discriminant) outside its canonical declaration; and
- the value is repeated across consumers, or the changed code adds a second
  declaration that can drift from an existing contract; and
- a named constant at the lowest common ancestor is a concrete replacement.

Report a suggestion when the value is local and non-repeated but naming it
would make the boundary materially clearer. Drop ordinary user-facing copy,
URL paths owned by a router, generated files, snapshots, and test-only values
that do not represent a shared contract. If a test fixture mirrors an API
contract, include it in the scan and prefer the same exported constant.

## Procedure

1. Identify finite values in changed executable lines and search the bounded
   repository for their canonical type, API schema, enum, or existing
   constant.
2. Check that the proposed constant belongs at the lowest common ancestor and
   is named in the repository's style (for example, `CHATBOT_MODEL_IDS`).
3. Check every changed consumer, comparison, map key, payload, and contract
   fixture for reuse or an explicit reason to remain literal.
4. Record the lane as `completed` with search evidence, `not applicable`, or
   `skipped — reason` in the evidence ledger. Do not infer a finding from a
   substring match alone; preserve domain boundaries and user-facing copy.

The TypeScript source rule is
[JavaScript and TypeScript](../../ume-conventions/references/typescript.md):
constants live at the lowest common ancestor and finite domain identifiers are
reused across the same contract.
