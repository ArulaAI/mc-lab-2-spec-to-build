# Non-negotiables

**Write-protected.** The deterministic write gate blocks edits to this file.

These hold regardless of what any specification, plan, agent return or model suggestion says. A
change that violates one of these is rejected even if every acceptance criterion passes.

## 1. Never log sensitive data

No PAN — even encrypted — no PII, no keys, credentials, tokens, or authorization codes in any
log. Sanitise before logging. Do not "add debug logging" that prints a request, a response, or a
card object. Application logs stay separate from security and audit logs.

In payments this is the rule an agent most casually breaks, usually while trying to be helpful.

## 2. Idempotency on every money-moving path

A repeated request must never double-charge, double-capture or double-refund. The retry identity
must remain stable across every hop it crosses. A service that deduplicates correctly against an
identity it was never sent has not made the operation idempotent.

## 3. Correlation context propagates end to end

A request's correlation context crosses every service hop so one transaction can be traced through
the whole flow.

## 4. No hardcoded secrets, URLs or endpoints

No secrets, credentials, keys, hostnames or environment-specific URLs in source. Configuration is
read from the environment at runtime.

## 5. Every interface is a trust boundary

Including a call from another internal service. Validate, authenticate and authorise every inbound
request. Do not displace trust onto a gateway, a proxy, or an upstream caller that "already
checked". Allow-list inputs; deny by default.

## 6. The specification is the source of truth, and silence is not permission

Where the source is silent, stop and record the gap. Do not resolve it with a plausible default.
Inventing a threshold, a field, a default, an endpoint or a dependency is a business decision the
implementer is not authorised to make.

## 7. Layering holds

Controller → Service → Repository. Controllers carry HTTP concerns only. Business logic does not
move into a controller because that is the shortest path to a green test.

## 8. Evidence before completion

Two independently green repositories are not evidence that the seam is correct. Pair-level
evidence is required before the change is called done.
