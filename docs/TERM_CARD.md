# Term Card

Ten terms. Everything else is ordinary engineering vocabulary.

| Term | Meaning |
|---|---|
| **Context boundary** | What a given agent is allowed to see. Chosen deliberately, not by default. |
| **Seam** | The place two services meet — here, TTA → Payment Processor. Correctness at a seam lives in the relationship between two implementations, not inside either one. |
| **Repo brief** | The instruction you write for an agent auditing one repository: what to inspect, what evidence to return, and what it must not infer. |
| **Context ledger** | Your reconciliation of what the agents reported: claim, where it was asserted, evidence, what contradicts it, your ruling, and its status. |
| **Scoped sub-agent** | An agent deliberately given one repository and read-only tools, so its findings stay local and checkable. |
| **Agent brief** | The contract for an implementation agent: outcome, authoritative inputs, repository scope, allowed and excluded areas, tools, the acceptance criteria it owns, expected return shape, and stop conditions. |
| **Spec readiness** | Whether a specification is well-formed enough to build from. Structural readiness is machine-checkable; whether it is *correct* is not. |
| **Compatibility matrix** | The combinations of old and new that must work, and the one that must be shown to fail. It is what turns rollout order from an assertion into evidence. |
| **Fresh-context validator** | A judging agent that never saw the work being done, so it cannot inherit the builder's confidence. |
| **Hand-off** | The written checkpoint at a stage boundary: what we concluded, what evidence exists, what remains open, what the next context needs to know. |

## One deliberate naming choice

The human running the session is the **coordinating engineer**, not the "orchestrator". Two
reasons: "orchestration" already means something specific in payments platform work, and the human
role here is not to run more agents but to decide what each is allowed to know, and to rule on what
they come back with.

## Journey and hand-off are different things

**Journey** is automatic and machine-observable — *what actually happened*.
**Hand-off** is written by you at a stage boundary — *what we concluded and what remains open*.

Neither replaces the other. A journey with no hand-off is a trail nobody can act on; a hand-off
with no journey is a claim with nothing behind it.
