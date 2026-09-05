# PGS_DECISIONS.md — decision register

Every behaviour represented in this lab is recorded here with its source and its layer. This
file is the authority participants reason against when the code and their assumptions
disagree.

**Layers**

| Layer | Meaning |
|---|---|
| `PGS FACT` | Supported by the supplied PGS source material, cited below |
| `LAB REPRESENTATION` | An intentional simplification or lab-chosen detail, explicitly labelled |
| `NOT MODELLED` | Deliberately excluded; the source is silent or the behaviour is out of scope |

**Rule this register exists to enforce**

> Inventing lab code is acceptable. Inventing PGS platform behaviour is not. Where the source
> is silent, the silence is recorded here rather than resolved by a plausible default.

Sources referenced: `pgs-lab-spec-pack.md` Spec 1 (*Support Refunds for S2I transactions*),
`pgs-epic-feature-story-examples.md`, `pgs-example-claude-md-for-labs.md`.

---

## 1. Request and response contract

| # | Decision | Source | Layer |
|---|---|---|---|
| 1.1 | Refund request field mapping WSAPI → Payment Processor, as tabulated in §2 below | Spec 1, "Request field mapping (WSAPI → Payment Processor API)" | `PGS FACT` |
| 1.2 | Response carries `order.totalCapturedAmount`, `order.totalRefundedAmount`, `order.status` (`REFUNDED`, `PARTIALLY_REFUNDED`), and `transaction.authorizationResponse.{responseCode,approvalCode}` | Spec 1, "Response fields (selection)" | `PGS FACT` |
| 1.3 | Currency cannot change on a refund; it is carried but not re-evaluated at the seam | Spec 1, mapping table note on `transaction.currency` | `PGS FACT` |

### 2. Field mapping (implemented verbatim)

| WSAPI field | Required | Payment Processor field |
|---|---|---|
| `merchantId` | Yes | `merchantWsApiId` |
| `transactionId` | Yes | `wsApiSupport.transactionWsApiId` |
| `orderId` | Yes | `wsApiSupport.orderWsApiId` |
| `version` | Yes | `wsApiSupport.wsApiVersion` |
| `transaction.amount` | Yes | `amounts.transactionAmount` |
| `transaction.currency` | Yes | `paymentCurrency` |
| `transaction.reference` | No | `merchantOrder.transactionReference` |
| `transaction.targetTransactionId` | Conditional | `wsApiSupport.targetTransactionWsApiId` |
| `action.refundAuthorization` | No | `wsApiSupport.refundAuthorization` |

---

## 3. Endpoint selection

| # | Decision | Source | Layer |
|---|---|---|---|
| 3.1 | Two refund endpoints exist, selected by which identifiers the caller supplies | Spec 1, "API contract" | `PGS FACT` |

| Caller supplies | Endpoint |
|---|---|
| Order ID + original transaction ID (payment) | `POST /card-payments/{card_payment_gateway_id}/refunds` |
| Payment gateway ID + capture transaction gateway ID | `POST /card-payments/{card_payment_gateway_id}/card-captures/{card_transaction_gateway_id}/refunds` |

| # | Decision | Source | Layer |
|---|---|---|---|
| 3.2 | **Representative lab case:** a request carrying `transaction.targetTransactionId` is the capture-target case and must use the capture-refund endpoint | Derived directly from 3.1 | `PGS FACT` (mapping) + `LAB REPRESENTATION` (choice of this case as the representative one) |
| 3.3 | **Explicit non-rule.** Endpoint choice is **not** online versus offline | Spec 1 treats these as separate concerns | `PGS FACT` |

> Online/offline is request-body state carried by `action.refundAuthorization` →
> `wsApiSupport.refundAuthorization`. Selecting an endpoint on the basis of online/offline
> would encode a PGS rule that does not exist.

---

## 4. Status codes and error semantics

| # | Decision | Source | Layer |
|---|---|---|---|
| 4.1 | `200` processed, `400` validation failure, `403` missing refund privilege, `405` invalid method, `409` idempotency conflict, `500` system error | Spec 1, "HTTP status codes" | `PGS FACT` |
| 4.2 | A repeated request carrying the same idempotency key returns `409` and creates no second refund | Spec 1, "Error scenarios" and acceptance criteria | `PGS FACT` |
| 4.3 | Client errors (4xx) are distinguished from server errors (5xx); responses to callers never leak stack traces, internal class names, or sensitive data | `pgs-example-claude-md-for-labs.md`, "Error handling" | `PGS FACT` |
| 4.4 | `403` for missing `REFUNDS` privilege is a real source-backed status. **Merchant-privilege enforcement is `NOT MODELLED` in this lab slice** — the represented seam covers contract, idempotency and error-semantic correctness. Entitlement remains a legitimate downstream concern and must not be invented into the seam. | Spec 1, "Merchant privileges" | `NOT MODELLED` |

---

## 5. Business rules

| # | Decision | Source | Layer |
|---|---|---|---|
| 5.1 | A refund must not exceed the total captured amount unless `EXCESSIVE_REFUNDS` is granted; per-capture refunds must not exceed each capture's amount | Spec 1, "Business rules" | `PGS FACT` |
| 5.2 | The remaining-refundable determination therefore depends on stored transaction state (`totalCapturedAmount`, `totalRefundedAmount`), which the Payment Processor holds. **Payment Processor is authoritative for it.** | Derived from 5.1 and 1.2 | `PGS FACT` |
| 5.3 | `EXCESSIVE_REFUNDS` itself is `NOT MODELLED`; the lab represents the base rule only, and the excessive-refund path is out of scope for this slice | Spec 1 lists excessive refund as Phase 1.1 | `NOT MODELLED` |
| 5.4 | Boundary validation may legitimately exist in more than one service. What must not exist twice is an independently-encoded authoritative domain decision. | Scenario Document §7 | `PGS FACT` |

---

## 6. Idempotency

| # | Decision | Source | Layer |
|---|---|---|---|
| 6.1 | Every money-moving path is idempotent; a repeated request must never double-refund | `pgs-example-claude-md-for-labs.md`, non-negotiable 2 | `PGS FACT` |
| 6.2 | Duplicate detection produces `409` | Spec 1 | `PGS FACT` |
| 6.3 | **Transport of the identity.** The source states the rule and the status but never names a transport field. This lab carries the identity as the WSAPI body field `idempotencyKey`, propagated across the seam as the HTTP header `Idempotency-Key`. | Source silent | **`LAB REPRESENTATION`** |
| 6.4 | **Key derivation is `NOT MODELLED` and is not graded.** The incoming, caller-supplied key is used unchanged. Only propagation and stability across the seam are assessed. Inventing a composition rule would manufacture a requirement the source does not state. | Source silent | `NOT MODELLED` |

---

## 7. Online and offline

| # | Decision | Source | Layer |
|---|---|---|---|
| 7.1 | Refunds may be offline (against an existing PAYMENT or CAPTURE) or online (authorization plus a settlement leg handled downstream); the flag is controlled by CPC | Spec 1, "In scope (Phase 1)" | `PGS FACT` |
| 7.2 | **The lab treats online/offline state as an input supplied to the seam.** CPC's ownership of that decision is not modelled, and neither TTA nor Payment Processor is presented as owning it. | Scenario Document §4 | **`LAB REPRESENTATION`** |
| 7.3 | The online path performs represented authorization-facing behaviour via a deterministic lab stub with no network dependency | Lab construct | **`LAB REPRESENTATION`** |
| 7.4 | **No settlement artifact is ever created.** Settlement, injection, LCS and DCF are downstream and outside this service. | Spec 1, "Out of scope" | `PGS FACT` |

---

## 8. Correlation and observability

| # | Decision | Source | Layer |
|---|---|---|---|
| 8.1 | A correlation ID is propagated across every service hop | `pgs-example-claude-md-for-labs.md`, non-negotiable 3 | `PGS FACT` (principle) |
| 8.2 | **The specific header used on the represented refund seam is a lab choice.** The correlation headers named in the supplied material (`X-Client-Correlation-Id`, `X-Mc-Correlation-Id`, `X-Mc-Correlation-Request-ID`, `X-Mc-Tns-Logging-Id`, `X-Mc-Toggle-Version`) belong to the Retrieve Payer Authentication API, not the refund path. They are **not** presented here as the PGS refund-path correlation header. | Source establishes the principle, not the refund-path header | **`LAB REPRESENTATION`** |
| 8.3 | No PAN, PII, key, credential, token, or authorization code is written to any log on any path | `pgs-example-claude-md-for-labs.md`, non-negotiable 1 | `PGS FACT` |

---

## 9. Scope boundaries

| # | Decision | Source | Layer |
|---|---|---|---|
| 9.1 | All Void flows (Void-Auth, Void-Capture, Void-Pay, Void-Refund) are out of scope and must not be implemented | Spec 1, "Out of scope" | `PGS FACT` |
| 9.2 | Pre-settlement reversals, unsettled transactions, and non-card refunds are out of scope | Spec 1, "Out of scope" | `PGS FACT` |
| 9.3 | There is **no pre-risk assessment** on subsequent refund transactions; inventing a risk or fraud call in the refund path fabricates a dependency | Spec 1, "Out of scope" | `PGS FACT` |
| 9.4 | CPC, injection, LCS API, DCF, A3RS, BECS, BPSS, ISO 8583 / DE48 mapping, regional routing and blue-green topology are outside the lab runtime | Scenario Document §12 | `NOT MODELLED` |
| 9.5 | The wider PGS flow is `WSAPI → TTA → Payment Processor → CPC → Injection → LCS API → DCF`. Only `TTA → Payment Processor` is executable here. | Spec 1 context; Scenario Document §4 | `PGS FACT` (flow) + `LAB REPRESENTATION` (slice) |

---

## 10. Contract evolution

| # | Decision | Source | Layer |
|---|---|---|---|
| 10.1 | APIs are contract-first; the OpenAPI document is the source of truth and a non-breaking change updates the spec rather than forking a version | `pgs-example-claude-md-for-labs.md`, "APIs" | `PGS FACT` |
| 10.2 | Production deployments are incremental, reversible and version-tolerant across instances | `pgs-epic-feature-story-examples.md`, "Controlled Production Deployments" | `PGS FACT` |
| 10.3 | The lab contract version numbers (`v1`, `v2`) and the specific additive delta between them are a lab construct | Lab construct | **`LAB REPRESENTATION`** |
| 10.4 | The rollout order derived in this lab belongs to the specific additive change represented here. **Producer-first is not presented as a universal PGS rule.** | Scenario Document §8 | `PGS FACT` (principle) |

---

## 11. Layering and architecture

| # | Decision | Source | Layer |
|---|---|---|---|
| 11.1 | Controller (API) → Service (business logic) → Repository (persistence). Controllers hold HTTP concerns only. | `pgs-example-claude-md-for-labs.md`, "Architecture and code shape" | `PGS FACT` |
| 11.2 | Configuration is externalised; no secrets, hostnames or environment-specific URLs in source | `pgs-example-claude-md-for-labs.md` | `PGS FACT` |
| 11.3 | In-memory stores replace Oracle/H2 persistence for the lab | Lab construct | **`LAB REPRESENTATION`** |

---

## 12. Open questions

Recorded rather than resolved. An implementation that silently answers one of these has
encoded an unresolved question as production fact, which is a hard-fail condition.

| # | Question | Why it is open |
|---|---|---|
| 12.1 | Exact production idempotency-key derivation | Source defines the duplicate rule and the `409`, never the derivation |
| 12.2 | The production correlation header on the refund path | Named headers in source belong to a different API |
| 12.3 | Whether merchant-privilege enforcement belongs at this seam or downstream | Source establishes the privileges; it does not assign them to a component in this slice |

---

## Change log

| Date | Change |
|---|---|
| 2026-09-04 | Initial register. Phase A. SEED-05 endpoint mapping recorded and gated; SEED-06 candidate testing completed. |
