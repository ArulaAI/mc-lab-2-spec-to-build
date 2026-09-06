# CLAUDE.md — pgs-payment-processor

The Payment Processor side of the represented refund seam. The workspace root `CLAUDE.md` applies
here too; this file adds what is specific to this service.

## What this service is responsible for

- exposing the represented refund API
- the **authoritative** refund decisions in this slice, because they depend on state only this
  service holds:
  - how much of an order remains refundable, from the total captured amount less what has already
    been refunded
  - whether a refund targeting a specific capture fits within that capture's own amount
  - whether this refund duplicates one already accepted
- the represented online authorization step
- returning correct response and error semantics

## What it must never do

- **Create a settlement artifact.** Settlement, injection, LCS and DCF are downstream and outside
  this service. There is no exception to this.
- **Hold WSAPI or TTA-specific logic.** This service knows about refunds, not about the shape of
  the caller that happens to be in front of it today.
- **Implement any Void flow.** Void-Auth, Void-Capture, Void-Pay and Void-Refund are all out of
  scope. Code near the refund path that looks like it belongs to that work is not an invitation.

## Idempotency

Deduplicate on the identity **as received**. Do not derive, normalise or reconstruct it: a service
that deduplicates against an identity it invented for itself is not deduplicating anything the
caller can rely on. If the identity arriving here looks wrong, that is a finding about the seam, to
be raised — not repaired locally.

## Error semantics

`200` processed, `400` validation failure, `409` duplicate, `500` system error. Responses to the
caller are opaque: no stack traces, no internal class names, no field values. Business refusals are
structured outcomes, not exceptions.
