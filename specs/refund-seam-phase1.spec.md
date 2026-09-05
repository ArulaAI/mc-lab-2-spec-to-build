# Refund seam, phase 1 — specification

## Metadata

| Field | Value |
|---|---|
| Spec ID | REFUND-SEAM-P1 |
| Status | DRAFT |
| Owner | *(unassigned)* |
| Source authority | `docs/PGS_DECISIONS.md`, `specs/OUT_OF_SCOPE.md`, `specs/NON_NEGOTIABLES.md` |
| Applies to | `pgs-tta`, `pgs-payment-processor` |

## Purpose

A merchant has taken a payment and now needs to refund it. The refund request arrives in a
WSAPI-facing shape and must cross the TTA → Payment Processor boundary correctly, so that what the
caller is told matches what actually happened downstream.

## System boundary

```
WSAPI  ->  TTA  ->  Payment Processor  ->  CPC  ->  Injection  ->  LCS API  ->  DCF
           |________________________|
                represented here
```

Only the TTA → Payment Processor interaction is implemented. Everything downstream of Payment
Processor is outside this change.

## Source authority

Behaviour traces to the PGS decision register at `docs/PGS_DECISIONS.md`, which records for each
decision whether it is a PGS fact, a labelled lab representation, or deliberately not modelled.

Where the register marks something unresolved, it stays unresolved. It is not settled by choosing
a reasonable-looking default.

## In-scope behaviour

1. A refund request enters TTA in the WSAPI-facing shape.
2. TTA validates the request it receives and maps it onto the Payment Processor contract.
3. TTA calls Payment Processor and maps the response back to the caller.
4. Payment Processor decides the refund and records it.
5. Duplicate submissions do not produce a second refund.
6. Refunds may be offline or online; the online path performs the represented authorization step.

## Per-repo ownership

| Concern | Owner |
|---|---|
| Request-boundary validation of the WSAPI request | `pgs-tta` |
| Field mapping onto the Payment Processor contract | `pgs-tta` |
| Recording the refund | `pgs-payment-processor` |
| Duplicate detection | `pgs-payment-processor` |

> **Incomplete.** Several decisions in this change have no owner named above: which service is
> authoritative for the remaining-refundable determination, which service selects the endpoint,
> and which service is responsible for the retry identity remaining stable. Ownership must be
> settled before implementation, because a decision with two owners is a decision that will drift.

## Request and response contract

Field mapping is given in `docs/PGS_DECISIONS.md` section 2 and is implemented verbatim.

Two refund endpoints exist, selected by the identifiers the caller supplies
(`docs/PGS_DECISIONS.md` section 3).

> **Unresolved.** The consumer's generated client and the contract the producer publishes are not
> currently on the same version. Which version this change targets, and what that means for
> anything already deployed, is not yet decided here.

## Business rules

- A refund must not exceed the total captured amount on the order.
- A refund targeting a specific capture must not exceed that capture's own amount.
- Currency is carried across the seam and is not re-evaluated.
- Amounts are positive.

## Error semantics

| Condition | Status |
|---|---|
| Processed | 200 |
| Validation failure | 400 |
| Duplicate submission | 409 |
| System error | 500 |

Error responses carry no internal detail — no stack traces, no internal class names, no field
values.

## Idempotency

Refunds are idempotent. Duplicate handling is covered by the error semantics above.

> **Vague.** "Refunds are idempotent" is not implementable as written. It does not say what carries
> the retry identity, which service is responsible for keeping it stable, what a caller observes on
> a retry, or what must be true of stored state afterwards. This needs to become a statement that
> can fail.

## Correlation and observability

A correlation context is propagated across the seam. No sensitive value is written to any log.

## Compatibility and rollout constraints

The change should be rolled out safely, without breaking anything that is already deployed.

> **Not yet testable.** This is a statement of intent, not a constraint. It does not say which
> combinations of old and new must keep working, which combination is unsafe, or how any of that
> is demonstrated.

## Acceptance criteria

| ID | Given | When | Then |
|---|---|---|---|
| AC-1 | a valid refund request | it is submitted through TTA | it is processed and the caller receives the result |
| AC-2 | a refund that exceeds what remains refundable | it is submitted | it is refused |
| AC-3 | the same refund submitted twice | the second submission arrives | the caller is told it is a duplicate and no second refund exists |
| AC-4 | a refund targeting a specific capture | it is submitted | it is handled correctly |
| AC-5 | an online refund | it is submitted | the represented authorization step is performed and no settlement artifact is produced |

> **AC-4 is vague.** "Handled correctly" is not observable. It needs to state what distinguishes a
> capture-targeted refund from an order-level one, in terms of something a test can assert.

## Negative requirements

- No settlement artifact is produced by either service.
- No Void behaviour is implemented.
- No dependency is introduced that the source does not establish.

## Out of scope

See `specs/OUT_OF_SCOPE.md`, which is authoritative and write-protected.

## Open questions

| # | Question | Status |
|---|---|---|
| OQ-1 | Production derivation of the idempotency key | Open — source defines the duplicate rule and the status code, never the derivation |

## Non-negotiables reference

See `specs/NON_NEGOTIABLES.md`, which is authoritative and write-protected. Nothing in this
specification overrides it.
