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

- Keep route functions thin. They parse the request, apply dependencies, call an application/service boundary, and map the result to a response.
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

## Errors and operations

- Map domain errors to deliberate HTTP responses at one boundary. Do not leak stack traces, secrets, or internal model details.
- Preserve useful correlation identifiers in logs, but never log raw credentials or full sensitive payloads.
- Keep OpenAPI names and descriptions stable when clients depend on them.
- Test the endpoint contract, authorization, invalid input, dependency failures, and side-effect failure paths.

If the repository uses a specific DI, ORM, task queue, or response envelope, treat that project contract as higher priority than this general extension.
