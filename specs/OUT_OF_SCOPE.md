# Out of scope

**Write-protected.** This document is authority, not a worksheet. The deterministic write gate
blocks edits to it.

Everything below is excluded from this change. Implementing any of it is a hard fail regardless
of how well the rest of the work is done — not because the behaviour is wrong in general, but
because it is not this change, and a payment-grade change that quietly grows is the failure mode
this lab exists to prevent.

## Excluded by the source specification

| Item | Source |
|---|---|
| **All Void flows** — Void-Auth, Void-Capture, Void-Pay, Void-Refund | Spec 1, "Out of scope" |
| Pre-settlement reversals | Spec 1, "Out of scope" |
| Unsettled transactions | Spec 1, "Out of scope" |
| Non-card refunds | Spec 1, "Out of scope" |
| DCF and settlement data generation — handled downstream, not in this service | Spec 1, "Out of scope" |
| Pre-risk assessment on subsequent refunds — **there is none**; inventing a risk or fraud call fabricates a dependency | Spec 1, "Out of scope" |
| Excessive refund (`EXCESSIVE_REFUNDS`) — a later phase | Spec 1, Phase 1.1 |
| Partial refund, scheme-token and device-payment cases — a later phase | Spec 1, Phase 2 |

## Outside the lab runtime

Represented in the wider flow, deliberately not implemented here:

- CPC behaviour and ownership beyond the online/offline state supplied at the seam
- Refund injection, LCS API, DCF generation and the settlement lifecycle
- A3RS, BECS, BPSS and surrounding platform components
- ISO 8583 and DE48 mapping, settlement-specific field processing
- Production routing, regional and blue-green topology
- The production CI/CD, integration-environment and release-governance path
- Merchant-privilege enforcement — the source establishes the privileges but does not assign
  enforcement to a component in this slice. See `docs/PGS_DECISIONS.md` open question 12.3.

## Nearby code is not authorisation

Code adjacent to the refund path may look reusable, may compile, and may appear to be waiting to
be finished. Adjacency is not permission. If you believe something out of scope genuinely must
change, the correct action is to record it and escalate — not to implement it and mention it
afterwards.
