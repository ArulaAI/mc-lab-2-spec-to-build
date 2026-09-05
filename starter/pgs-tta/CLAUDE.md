# CLAUDE.md — pgs-tta

The translation side of the represented refund seam. The workspace root `CLAUDE.md` applies here
too; this file adds what is specific to this service.

## What this service is responsible for

- accepting the WSAPI-shaped refund request
- validating the request **it** receives
- mapping it onto the Payment Processor contract
- propagating the retry identity it was given
- calling Payment Processor and mapping the answer back
- preserving the meaning of what comes back

## What it is not responsible for

**This service does not make authoritative refund-state decisions.** Anything that depends on
stored order or transaction state — how much of an order remains refundable, whether a target
transaction is refundable at all — belongs to Payment Processor, because that is where the state
lives.

Boundary validation here is legitimate and expected: every interface is a trust boundary, and this
service validates what it receives. The line is between *validating the request* and *deciding the
refund*. A domain rule independently re-encoded on both sides of a seam does not stay in step; the
two services simply become able to disagree about the same refund, and nothing tells you when that
starts.

## Contract handling

`src/main/openapi/payment-processor.yaml` is the Payment Processor contract this consumer is pinned
to, and everything under `client/contract/` is generated from it:

```
mvn -Pgenerate-client generate-sources
```

**Regenerate; do not hand-edit generated code.** A hand-patched client is a client that no longer
matches any contract, and the next regeneration silently discards the patch. If the generated
result is wrong, the contract or the generator configuration is what needs to change.

## Things to preserve

- **The retry identity crosses unchanged**, on every path. Deriving, replacing or regenerating it
  breaks end-to-end idempotency even though this service still looks correct on its own.
- **Downstream failure semantics survive translation.** A duplicate answered with 409 must not
  reach the caller as a generic 500: the caller would retry a request that was correctly refused.
- **Correlation context propagates.**

## Out of scope here

No settlement artifacts. No Void behaviour. No dependency the source material does not establish.
