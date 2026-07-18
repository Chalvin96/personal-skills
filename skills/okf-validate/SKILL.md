---
name: okf-validate
description: Use when you need to validate an OKF (Open Knowledge Format) knowledge bundle — a directory of markdown files with YAML frontmatter, plus optional reserved index.md and log.md — after editing knowledge docs, before committing knowledge changes, or when a repo says to run "the OKF validator" but names no command. Not for OpenSpec change validation (use openspec validate).
---

# OKF validate

## Overview

OKF is an open knowledge format (spec by Google Cloud, Apache 2.0,
[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog);
community stewardship via the Holon group). A bundle is a directory of markdown
files with YAML frontmatter, plus optional reserved `index.md` and `log.md`. Drive a
real validator — do not hand-roll one.

## Conformance rules

A bundle conforms on three rules (OKF v0.1):

1. Every non-reserved `.md` file has a parseable YAML frontmatter block.
2. Every frontmatter block has a non-empty `type` field.
3. Reserved `index.md` and `log.md`, when present, follow their documented structure.
   The bundle-root `index.md` MAY declare `okf_version` (optional, not required).

## Run the validator

There is no single official CLI. Prefer, in order:

1. A validator already vendored in the repo — check `package.json` scripts,
   `pyproject.toml`, Makefile, and pre-commit config first.
2. A community CLI on PATH, e.g. `openknowledge` (Python) or `okf` (Go). Confirm the
   subcommand and flags with `--help` before trusting them — do not assume flags like
   `--format json` or `--strict` exist.
3. The client-side validator at [okf.md/validator](https://okf.md/validator).

Run from the bundle root (the dir holding `index.md`). Fix every failure; re-run
until clean.

## If no validator is available

Do not fake it. Either install a community CLI, or fall back to a manual pass against
the three rules above — and **say which you did**. Report a manual pass as a "manual
conformance check", never as "validated".

## Common mistakes

- Confusing OKF validation with `openspec validate` — different systems, different
  bundles.
- Running from the wrong directory (must be the bundle root).
- Assuming `log.md` freshness is enforced. Rule 3 only checks its *structure* when
  present; a stale-but-well-formed log passes. Appending to it is good hygiene the
  validator will not catch, not a validation requirement.
