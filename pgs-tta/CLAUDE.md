# CLAUDE.md — pgs-tta

The translation side of the represented refund seam. The workspace root `CLAUDE.md` applies here
too; this file adds only what is specific to this service.

## Role

This service accepts the WSAPI-facing refund request, maps it onto the Payment Processor contract,
calls that service, and maps the answer back to its caller.

## Where behaviour is defined

Not here. This file carries engineering guardrails, not domain rules.

| Question | Answer lives in |
|---|---|
| What must this change do? | `specs/refund-seam-phase1.spec.md`, once it is READY |
| Is a behaviour PGS fact, lab representation, or not modelled? | `docs/PGS_DECISIONS.md` |
| What must never be built? | `specs/OUT_OF_SCOPE.md` |
| What holds regardless of anything else? | `specs/NON_NEGOTIABLES.md` |

If you cannot find a rule in those documents, that is a finding to record — not a gap to fill
with something plausible.

## Engineering guardrails

- **Layering holds.** Controller → Service → Repository. Controllers carry HTTP concerns only.
- **Every interface is a trust boundary**, including a call from another internal service.
  Validate what you receive; do not displace trust onto the caller.
- **Nothing sensitive reaches a log.** No PAN, PII, key, credential, token or authorization code,
  on any path. Do not add debug logging that prints a request, a response, or a card object.
- **Configuration is externalised.** No hostname, URL or secret in source.
- **Generated code is not edited by hand.** Anything under `client/contract/` is produced from
  `src/main/openapi/payment-processor.yaml`:

  ```bash
  mvn -Pgenerate-client generate-sources
  ```

  A hand-patched client no longer matches any contract, and the next regeneration discards the
  patch silently. If the generated result is wrong, the contract or the generator configuration is
  what needs to change.

## Scope

Work only inside the seam this lab represents. Code sitting next to the refund path is not
authorisation to use it, and `specs/OUT_OF_SCOPE.md` is authoritative and write-protected.
