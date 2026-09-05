# CLAUDE.md — Lab 2: One Refund Across a Service Boundary

Guidance for any AI agent working in this workspace.

## What this workspace is

A controlled simulation of one slice of the Mastercard PGS refund flow: the **TTA → Payment
Processor** seam. Two service repositories, one pair-verification harness, and the documents that
say what is true.

`docs/SCENARIO_GROUNDING.md` explains which parts are grounded PGS behaviour, which are lab
simplifications, and which defects are deliberate teaching fixtures. Read it before you reason
about the domain.

## The rules that decide arguments

1. **Source silence is not permission.** Where the supplied material does not say, it does not say.
   Record the gap in the specification's Open Questions and stop. Do not resolve it with a
   plausible default — inventing a threshold, a field, an endpoint, a default or a dependency is a
   business decision you are not authorised to make.

2. **A generated summary is a claim until it is verified.** That includes yours. Anything you
   report about a repository cites a file and, where it applies, a line. A claim you cannot point
   at is an unknown, and saying so is worth more than a confident inference.

3. **The human owns the seam.** Cross-repository authority, which service owns which decision,
   contract version choices, rollout order and the disposition of any review finding are the
   coordinating engineer's rulings. Propose, evidence, and wait. A finding does not authorise a
   change.

4. **No sensitive payment data in logs.** No PAN, PII, key, credential, token or authorization
   code, ever, on any path. Do not add debug logging that prints a request, a response, or a card
   object.

5. **Do not expand the scope.** No CPC behaviour, no settlement or DCF generation, no Void flows.
   `specs/OUT_OF_SCOPE.md` is authoritative and write-protected. Code sitting next to the refund
   path is not authorisation to use it.

6. **Pair-level evidence before completion.** Two green repositories are not evidence the seam is
   correct. `python3 scripts/run_pair_verification.py` is what settles that question.

## Authority, in order

| Document | Answers |
|---|---|
| `specs/NON_NEGOTIABLES.md` | What holds regardless of anything else |
| `specs/OUT_OF_SCOPE.md` | What must not be built |
| `docs/PGS_DECISIONS.md` | Whether a behaviour is PGS fact, lab representation, or not modelled |
| `specs/refund-seam-phase1.spec.md` | What to build, once it is READY |

When they disagree, the higher row wins.

## Working across the two repositories

Work in one repository at a time, with only that repository's context. An agent given both spends
its attention on framework detail, reasons deeply about one side and shallowly about the other, and
fills the gaps in between with invention. Read-only auditing may run in parallel because it changes
nothing; writes follow the rollout order the coordinating engineer has decided.

## Before you hand anything back

- Did I log anything sensitive? (Must be no.)
- Does every claim I made cite evidence?
- Did I stay inside the specification's scope, and record anything it left undecided?
- Did every changed line trace back to an acceptance criterion?
- Did I leave any placeholder, TODO or ambiguous handoff behind? (Must be none.)
