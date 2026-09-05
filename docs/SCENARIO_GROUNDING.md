# Scenario grounding — what is real, what is simplified, what is planted

This lab sits in the PGS refund domain and uses real PGS terminology. That makes it worth being
exact about which parts are grounded behaviour, which are simplifications made so the exercise fits
in two hours, and which are deliberate teaching fixtures.

**The rule the lab authors worked to:** inventing lab code is acceptable; inventing PGS platform
behaviour is not. A failure mechanism may be simulated. The engineering principle it demonstrates
may not be made up.

---

## The three layers

### Layer 1 — PGS fact

Behaviour supported by the supplied PGS material, recorded decision by decision in
[`PGS_DECISIONS.md`](PGS_DECISIONS.md) with its citation.

Examples: the wider refund flow and where TTA and Payment Processor sit in it; the request field
mapping; the two refund endpoints and the identifiers that select between them; the status codes,
including `409` for a duplicate; refunds not exceeding the captured amount, per order and per
capture; idempotency being required on money-moving paths; correlation IDs propagating end to end;
Void being out of scope; settlement being downstream.

### Layer 2 — Lab representation

Deliberate simplifications, each labelled as such in `PGS_DECISIONS.md`.

Examples: two editable repositories; only the TTA → Payment Processor seam being executable;
online/offline supplied as an input rather than modelling CPC's decision; in-memory stores instead
of Oracle; a deterministic authorization stub with no network; the contract version numbers; the
specific transport field carrying the retry identity; the correlation header name; a local
compatibility harness standing in for a deployment pipeline.

### Layer 3 — Seeded failure

Defects introduced deliberately by the lab authors to create the exercise.

**Their presence does not imply that the same defect exists, or ever existed, in a Mastercard
production system.** They are teaching fixtures. What is grounded is the *principle* each one
demonstrates and the behaviour that correcting it restores.

This document does not say where they are. Finding them is the work.

---

## What the lab deliberately does not model

CPC behaviour beyond the state supplied at the seam · refund injection · LCS API · DCF generation
and the settlement lifecycle · ISO 8583 and DE48 mapping · A3RS, BECS, BPSS and surrounding
platform components · production routing, regional and blue-green topology · the production CI/CD,
integration-environment and release-governance path · the real team-ownership and merge-approval
model across repositories · merchant-privilege enforcement.

These are scope reductions for the exercise. **They are not architectural claims.** Nothing here
says the real system lacks them.

---

## What "success" means, precisely

The represented TTA → Payment Processor slice is internally consistent, contract-compatible,
tested, and independently validated against the supplied technical authority.

That is narrower than "the refund capability works". The lab proves the represented seam locally.
It does not claim the wider PGS refund capability is production-ready, and pair verification does
not replace PGS integration testing or release governance.

---

## Why the grounding discipline is the point, not the paperwork

The habit this lab is trying to build is the one that matters when the AI is confident and the
source is silent. An agent asked to finish a refund path will produce something plausible for a
threshold nobody specified, an endpoint nobody published, or a dependency nobody built. It will
read well. In payments it will also be a business decision made by something with no authority to
make it.

Separating fact from representation from fixture — here, and in your own work — is what makes that
difference visible before it ships.
