---
type: Coding Convention
title: FastAPI conventions
description: FastAPI-specific rules for route, dependency, schema, async, and service boundaries.
tags: [coding-convention, fastapi, python, backend]
status: active
---

# FastAPI

Load this extension with `python.md`. These are framework rules, not universal Python rules.

## Routes and schemas

- Group models, schemas, routers, and services by domain when the application
  has multiple domains.
- Keep route functions thin. They parse the request, apply dependencies, call an application/service boundary, and map the result to a response.
- Let services own write behavior and domain invariants. Keep ORM models
  declarative and do not put HTTP concerns in services.
- Use explicit Pydantic request and response models. Do not return internal ORM or domain objects directly when the response contract should be stable.
- Declare response models, status codes, and error responses when they are part of the API contract.
- Keep path, query, and body validation at the route boundary. Do not duplicate the same validation in every service caller.
- Use one canonical dependency for authentication and authorization. A route that omits a required dependency is a security finding, not a style preference.

## Async and side effects

- Do not call blocking I/O or CPU-heavy work directly from an async route. Use an async client, a worker, or an explicit thread boundary.
- Give outbound HTTP calls a timeout, bounded retry policy, and cancellation behavior.
- Keep transaction scope clear. Do not start a transaction around unrelated network calls.
- Make background work safe to retry. Pass stable IDs or serializable input, then re-read current state in the worker.
- Use an idempotency key or a guarded state transition when two requests can perform the same side effect.

For a provider used by several endpoints, split the client by responsibility
when the repository has enough surface to justify it: configuration and value
types, a typed exception hierarchy, an HTTP-only API layer, and a manager that
parses responses and applies classification or policy. Keep transport failure
translation at the layer that has a name for the failure.

## Persistence and migrations

- Keep exception classes for a module or nested package in its `exceptions.py`
  when the repository uses that boundary; do not scatter the error vocabulary
  beside individual raises.
- Treat an existing database uniqueness constraint as the concurrency boundary
  for check-then-write flows. A pre-read may optimize the common case, but the
  write must handle the race. Prefer absorbing an expected duplicate at the
  insert rather than catching an integrity error and retrying the whole unit of
  work.
- Generate Alembic migrations from model metadata when the repository uses
  Alembic. Do not hand-write generated migration bodies without a documented
  reason.

## Errors and operations

- Map domain errors to deliberate HTTP responses at one boundary. Do not leak stack traces, secrets, or internal model details.
- Preserve useful correlation identifiers in logs, but never log raw credentials or full sensitive payloads.
- Keep OpenAPI names and descriptions stable when clients depend on them.
- Test the endpoint contract, authorization, invalid input, dependency failures, and side-effect failure paths.

If the repository uses a specific DI, ORM, task queue, or response envelope, treat that project contract as higher priority than this general extension.
