---
type: Coding Convention
title: Test design and review
description: Evaluate test evidence, independent oracles, isolation, boundary coverage, and AI-assisted testing.
tags: [coding-convention, testing, ai]
status: active
---

# Testing

Treat a test as evidence about a behavior. A passing test is useful only when the
scenario matters, the expected result is trustworthy, and the test can fail when
the behavior is wrong. Review the changed production code and changed tests as one
diff.

## Admission gate

Report a test finding only when it has one of these forms:

- **Defect:** changed code, a concrete scenario, and a production impact that the
  test misses or incorrectly accepts;
- **Convention:** changed code or changed test code, plus this named rule.

Do not demand a new test for every line or for a trivial rename. Ask for test
evidence when the change alters behavior, a public contract, a trust boundary,
state, persistence, an external side effect, or a failure mode.

## Review sequence

### 1. Define the behavior

Start with the issue, acceptance criteria, public contract, bug report, or
repository knowledge. State what must be true after the change. Do not infer the
expected behavior from the implementation alone.

### 2. Build a small scenario matrix

Check only the rows that apply:

| Area | Questions |
| --- | --- |
| Normal path | Does the intended result occur for a valid input? |
| Boundary | What happens for empty, null, minimum, maximum, duplicate, expired, or malformed values? |
| Permission | Can an unauthenticated, unauthorized, cross-tenant, or wrong-owner caller reach the behavior? |
| Failure | What happens on timeout, dependency failure, invalid state, partial work, or retry? |
| State | Are transactions, concurrency, idempotency, cache state, and queue delivery correct? |
| User experience | Are loading, empty, error, keyboard, focus, and accessible-name states correct? |

Map each applicable scenario to a meaningful assertion. A test that only executes a
line is not evidence for a result.

### 3. Check the oracle

The oracle is the rule that decides whether the result is correct.

- Derive expected values from the requirement, a trusted fixture, a simple
  reference implementation, or an invariant. Do not calculate the expected value
  with the same logic as the code under test.
- Assert the returned value and important side effects. Do not assert only that a
  function was called when the user-visible or persisted result is the contract.
- Mock external systems at a boundary. Do not mock the function or branch that the
  test is meant to verify.
- For refactors, compare old and new behavior only when the old behavior is a
  trusted contract. Do not preserve a known bug as the expected result.

### 4. Check isolation and repeatability

Tests must not depend on test order, shared mutable data, a developer's clock,
random seed, environment, network, or local credentials. Clean up database rows,
files, queues, patches, and temporary resources. Prefer a controllable clock and
explicit dependency injection to broad global patches.

Treat sleeps, real external network calls, unbounded retries, and hidden global
state as candidates for flakiness. Replace them with a controllable boundary or a
condition that the test can observe.

### 5. Choose the right boundary

Use the smallest test that proves the behavior, but test at the real boundary when
the risk is at that boundary:

- pure transformations and rules: unit or property-based tests;
- database, transactions, queues, and external clients: integration tests with
  controlled dependencies;
- HTTP routes: request, authorization, status, response, and side-effect tests;
- browser behavior: user-visible interaction and accessibility tests;
- service-to-service payloads: contract tests.

Do not test framework behavior or private structure when a public behavior test can
prove the same contract.

## Stronger evidence

Coverage shows which code ran. It does not show that the assertions can detect a
wrong result. Use these techniques when the change is risky or the oracle is weak:

- **Regression test:** reproduce the original bug before asserting the fix.
- **Negative implementation:** run the tests against a deliberately incorrect
  implementation and require a failure.
- **Mutation testing:** inspect surviving mutants in changed or high-risk code;
  classify equivalent mutants instead of forcing a score.
- **Property-based testing:** use invariants, round trips, parser rules, and state
  laws when examples do not cover the input space.
- **Contract testing:** verify the shape and meaning of messages at a boundary.

Do not use a universal coverage or mutation-score threshold as a substitute for
reading the changed behavior.

## AI-assisted testing

AI-generated tests are drafts. Do not report their origin as a defect, but do not
treat their presence as proof of quality.

- If one agent wrote both the implementation and its tests, treat the tests as
  correlated evidence. Identify this from the user statement, the current session,
  PR or commit text, or signals such as `Co-Authored-By` and `Generated with`. If
  origin is unknown, record it as unknown and start with a requirement-first pass.
  For high-risk changes, require a black-box, negative-implementation, mutation,
  or independent human review pass. A reviewer can create independence by deriving
  expected behavior from the requirement before reading the test; use a subagent
  only when the user explicitly requests one or the skill is being validated.
- Check for test gaming: disabled assertions, test-only branches, altered
  production behavior under a test flag, expected values copied from the current
  implementation, and tests that pass without exercising the changed behavior.
- Require the actual test command and raw result before accepting a claim that the
  tests pass. An agent summary is not execution evidence.
- Re-run important tests after code changes. Generated tests can become stale when
  code changes even if their line coverage remains high.
- Keep prompts, fixtures, logs, and test data free of secrets and personal data.

When the repository tests an AI feature, use a separate evaluation mode. Keep the
model and prompt versions, fixed examples, expected behavior, adversarial cases,
tool permissions, output schema, latency, cost, and fallback behavior explicit.
Use deterministic assertions where possible. An LLM judge can provide a labeled
signal, but it must not be the only binary oracle. Include model testing,
red-team testing, and field monitoring when the risk requires it.

## Framework notes

- **Python:** name tests by behavior and failure mode. When the repository uses
  the stricter house style, use
  `test_<what>_given_<scenario>_expect_<result>` for new or renamed tests. Use controlled clocks,
  explicit fixtures, and scoped patches. Test exceptions and external-call
  failures, not only successful return values.
- **FastAPI:** test the HTTP contract, dependency and object authorization,
  validation, status and response models, dependency failures, timeouts, and
  background side effects. Use factories and savepoint-isolated sessions when
  the repository provides them. Use `TestClient` for normal endpoint tests and
  an async test boundary when the code under test requires it. Test concurrency
  with independent sessions and explicit synchronization when a database race
  is part of the contract.
- **Django:** use the Django client for route behavior. Check permissions and
  serializer disclosure. Use transaction-aware tests when transaction behavior,
  locking, or commit hooks are part of the change.
- **TypeScript and React:** name new static Vitest tests with the repository's
  behavior pattern when it has one; prefer user-visible behavior, semantic roles, labels,
  stable contracts, and explicit async states. Avoid tests that assert component
  instances, private helpers, CSS structure, or hook call order.

## Review record

Include this evidence in the review when tests are relevant:

```text
Test evidence:
- Changed behavior:
- Scenarios covered:
- Scenarios not covered:
- Oracle and independence:
- Isolation and determinism:
- Commands run and raw results: (or `not run — not authorized` / `not run — untrusted source`)
- Mutation, negative, property, or contract evidence:
```

### Sources

- [NIST GenAI Code Challenge](https://ai-challenges.nist.gov/code) and its
  [evaluation plan](https://ai-challenges.nist.gov/uassets/GenAI_Test_Code_Pilot_Evaluation_Plan.pdf)
- [NIST agent-evaluation findings](https://www.nist.gov/caisi/cheating-ai-agent-evaluations)
- [Stryker mutation-testing metrics](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/)
- [Hypothesis property-based testing](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html)
- [Testing Library guiding principles](https://testing-library.com/docs/guiding-principles/)
- [Playwright best practices](https://playwright.dev/docs/best-practices)
