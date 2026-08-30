---
type: Coding Convention
title: Security conventions
description: Review trust boundaries, authorization, sensitive data, and secure failure behavior.
tags: [coding-convention, security]
status: active
---

# Security

Security findings have priority over style findings. Pursue a narrow trigger when the impact is high, but verify the trigger in the repository before reporting it.

## Review the boundary

- Identify who can call the endpoint, command, job, or tool. Authentication proves identity; authorization limits action.
- Check object-level access, tenant or account scope, ownership checks, and sibling paths that expose the same data.
- Validate untrusted input at the boundary. Check path traversal, injection,
  unsafe deserialization, SSRF, open redirects, unsafe file handling, and
  untrusted origins. Direct `eval`, `exec`, unsafe pickle/dill/YAML loads are
  mechanically checked as `UME-SEC001`; the model must still trace the input
  and impact.
- Treat frontend configuration as public. Never place secrets, signing keys,
  private URLs, or credentials in browser-delivered code. Obvious literal
  credentials are mechanically checked as `UME-SEC003`.
- Keep secrets in environment or a secret manager. Do not log tokens, passwords,
  raw request bodies, or unnecessary personal data. Obvious Python literal
  credentials are mechanically checked as `UME-SEC002`; logging and data-flow
  decisions remain model review.
- Use approved cryptography. Do not add a custom hash, encryption scheme, token format, or random-number source.
- Check error handling. Do not turn security or data failures into success responses, empty values, or silent catches.
- Bound external work with timeouts, size limits, rate limits, cancellation, and safe retry behavior.
- Review new dependencies for necessity, provenance, version constraints, and exposure before accepting them.

## Evidence rule

Do not report “this may be exposed” without tracing the consumer or permission path. Cite the changed line and the repository file that proves the audience, data flow, or missing control. If the repository cannot answer the question, state the exact missing artifact and ask.

Never remove validation, authorization, logging needed for incident response, or secure defaults for the sake of simplicity.
