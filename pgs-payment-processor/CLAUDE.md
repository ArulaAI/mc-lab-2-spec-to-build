# CLAUDE.md — pgs-payment-processor

The Payment Processor side of the represented refund seam. The workspace root `CLAUDE.md` applies
here too; this file adds only what is specific to this service.

## Role

This service exposes the represented refund API, decides refunds, and records them.

## Where behaviour is defined

Not here. This file carries engineering guardrails, not domain rules.

| Question | Answer lives in |
|---|---|
| What must this change do? | `specs/refund-seam-phase1.spec.md`, once it is READY |
| Is a behaviour PGS fact, lab representation, or not modelled? | `docs/PGS_DECISIONS.md` |
| What must never be built? | `specs/OUT_OF_SCOPE.md` |
| What holds regardless of anything else? | `specs/NON_NEGOTIABLES.md` |

If a rule is not in those documents, record the gap. Do not resolve it with a reasonable-looking
default — in a payment path that is a business decision you are not authorised to make.

## Engineering guardrails

- **Layering holds.** Controller → Service → Repository. Business refusals are structured
  outcomes, not exceptions.
- **Every interface is a trust boundary.** Validate every inbound request on its own merits.
- **Nothing sensitive reaches a log.** No PAN, PII, key, credential, token or authorization code,
  on any path.
- **Responses to callers are opaque.** No stack traces, no internal class names, no field values.
- **Configuration is externalised.** No hostname, URL or secret in source.
- **This service knows about refunds, not about its caller.** Do not add logic that is specific to
  the shape of whichever service happens to sit in front of it.

## Scope

Settlement, injection, LCS and DCF are downstream and outside this service. No Void flow is in
scope. Code near the refund path that looks like it belongs to that work is not an invitation —
`specs/OUT_OF_SCOPE.md` is authoritative and write-protected.
