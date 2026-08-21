---
type: Coding Convention
title: Django conventions
description: Django-specific rules for views, ORM, serializers, admin, transactions, and migrations.
tags: [coding-convention, django, python, backend]
status: active
---

# Django

Load this extension with `python.md`. These rules do not apply to FastAPI code.

## Views and services

- Keep views thin. Put query composition and business rules in a service or domain boundary.
- Serialize data before logging a success event. A serialization failure must not produce a false success log.
- Log exception class and useful identifiers, not raw request bodies or sensitive payloads.
- Use `django.conf.settings`, not direct settings-module imports, when accessing configured values.

## ORM and concurrency

- Trace concurrent writers. `transaction.atomic` alone does not prevent two requests from passing the same check; use row locking, conditional updates, or an idempotent transition where required.
- Fire external side effects after commit when the database state must exist first.
- Pass stable IDs to queues and reload current state in the worker. Do not enqueue mutable model objects.
- Use narrow updates when saving a model so unrelated concurrent changes are not overwritten.
- Check query count and relation loading for list, admin, and serializer paths.

## Models, admin, and migrations

- Give status fields explicit choices and preserve model metadata that the project relies on.
- Review serializer fields as disclosure decisions. Check every legacy, versioned, staff, vendor, and customer path that exposes the same object.
- Protect custom admin URLs with the admin authorization wrapper and log material changes through the project audit path.
- Treat migrations as deployable behavior. Review backward compatibility, data volume, locking, and rollout order. Do not hand-edit generated migration bodies without a clear reason.

## Tests

Cover permission scope, serializer exposure, query behavior, transaction boundaries, concurrent transitions, and migration safety when the change touches those surfaces.
