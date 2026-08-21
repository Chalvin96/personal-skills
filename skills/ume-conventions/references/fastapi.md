---
type: Coding Convention
title: FastAPI conventions
description: FastAPI-specific rules for routes, SQLAlchemy 2.x, CQRS-style reads, services, and external clients.
tags: [coding-convention, fastapi, python, backend]
status: active
---

# FastAPI

Load this extension with `python.md`. These are framework rules, not universal Python rules.

## Routes and schemas

- Group models, schemas, routers, and services by domain when the application
  has multiple domains.
- Keep route functions thin. They parse the request, apply dependencies, call a
  service for writes or a read/query function for reads, and map the result to a
  response.
- Put every database mutation—create, update, delete, and state transition—behind
  an application or domain service. The service owns write behavior, domain
  invariants, and the transaction boundary. Routes and read paths must not
  commit writes as a side effect.
- Treat CQRS as a simple read/write boundary, not as a reason to add a framework.
  Read-only queries may live wherever they are clearest: in a route for a small
  query, or in a query module, repository, or service for a larger one. A query
  must not mutate state, commit a transaction, or perform an unrelated side
  effect. Do not add command buses, query buses, or generic repositories only to
  satisfy this rule.
- Keep ORM models declarative and do not put HTTP concerns in services.
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

## SQLAlchemy 2.x

- Use the SQLAlchemy 2.x typed declarative API for new models: the repository's
  `DeclarativeBase`, `Mapped[...]`, `mapped_column()`, and typed
  `relationship()` declarations. Follow the repository's existing base and
  naming conventions instead of introducing a second model base.
- Use `select()` with `Session.scalars()` or `Session.execute()` for reads, and
  `Session.get()` for primary-key lookup. With `AsyncSession`, await the
  corresponding operations. Do not use `session.query()`, `Query`, or other
  legacy SQLAlchemy 1.x query patterns in new code.
- Make relationship loading explicit for collection and list endpoints. Use
  `selectinload()` or `joinedload()` when appropriate, and check for accidental
  lazy-loading and N+1 queries. Do not load a large collection implicitly from
  a serializer.
- Keep persistence writes in the service layer. Use the session to add, change,
  or delete entities there, and make flush/commit/rollback behavior explicit at
  the service or unit-of-work boundary used by the repository.

## Third-party clients

Use one folder per vendor with this layout:

```text
clients/<vendor>/
├── api.py
├── manager.py
└── config.py
```

- `config.py` contains typed vendor settings, such as the base URL, API key,
  timeout, and feature options. Read secrets from environment configuration or
  a secret manager. Do not put credentials or vendor defaults that contain
  secrets in source code.
- `api.py` is the transport layer. It owns the HTTP or SDK client connection,
  endpoint paths, authentication headers/API-key placement, serialization,
  timeouts, and transport-level error translation. Expose typed methods for
  vendor operations. Do not put domain decisions or database writes here.
- `manager.py` is the application-facing vendor layer. It calls `api.py`
  methods, coordinates provider calls, normalizes provider responses, and maps
  provider failures to application-level errors. It must not construct the
  HTTP/SDK client or duplicate endpoint and header details.
- A manager may return data needed by a write service, but it must not commit
  local database changes. The service remains responsible for local mutations
  and transaction rules.
- Wire `config.py` → `api.py` → `manager.py` through a dependency/provider and
  inject the manager into routes or services. Tests should replace the API or
  manager with a fake; they must not call a live vendor by default.

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
