# Specification Completeness Bar

Ten structural readiness checks. A specification clears the bar for a **bounded build** when all
ten hold.

The deterministic gate — `bash .claude/scripts/run .claude/scripts/validate_spec.py` — runs every
check below. It tells you whether the *resolved* scope is well-formed enough to build from. It
cannot tell you whether the specification is *correct* — that judgement stays human, and the status
file says so rather than implying a machine blessed the content.

| # | Check | What it means in practice |
|---|---|---|
| 1 | **Required sections present** | Every section the gate expects exists in the document. A missing section is a missing concern. |
| 2 | **Metadata names an owner** | The specification has an assigned owner, not *(unassigned)*. The lab or the participant supplies this; the gate never infers it from session context. |
| 3 | **Acceptance criteria carry identifiers** | At least five criteria labelled AC-1 through AC-N. Unnamed criteria cannot be traced. |
| 4 | **Acceptance criteria describe observable outcomes** | No "handled correctly", "works correctly", "as expected" or similar. Each criterion names something a test can check. |
| 5 | **Idempotency is testable for the authorised scope** | States what carries the retry identity, what the caller observes on a retry, and what must be true of stored state afterwards. It does **not** require you to name an owner or a derivation the source material never settles. |
| 6 | **Compatibility constraints are testable** | Names which combinations of old and new must keep working, and which must be shown to fail. |
| 7 | **Out of scope references the authoritative document** | Points to `specs/OUT_OF_SCOPE.md`. Nothing excluded quietly reappears as in-scope. |
| 8 | **Unresolved items are recorded and held out of scope** | No *(unassigned)*, **Incomplete.**, **Vague.**, **Not yet testable.**, TBD or TODO markers; at least one open question retained; and every unresolved decision the document surfaces points at a recorded open question that no acceptance criterion depends on. |
| 9 | **Non-negotiables are referenced** | Points to `specs/NON_NEGOTIABLES.md`. The specification acknowledges the constraints it must satisfy. |
| 10 | **Negative requirements name settlement and Void** | Explicitly states that no settlement artifact is produced and no Void behaviour is implemented. |

## Open authority items are reported, not scored

Some questions cannot be settled from the material this lab supplies. Scoring them would reward the
one behaviour this stage exists to prevent: inventing an owner, a derivation or a threshold so a
gate turns green.

So the gate reports them separately instead:

```
  OPEN AUTHORITY ITEMS
  - ownership undecided: Retry identity stability (OQ-3)

  These items are not authorised for implementation.
```

An unresolved item costs nothing **provided the specification keeps it explicit and outside the
implementation boundary**. Concretely, the gate treats an item as genuinely deferred when it points
at an open question that actually has a row in the Open questions table, and no acceptance
criterion cites that question.

The three outcomes it distinguishes:

| Situation | Result |
|---|---|
| A structural defect in the resolved specification | **FAIL** |
| An explicitly recorded authority gap, held out of scope | **OPEN** — reported, non-blocking |
| An unresolved decision an acceptance criterion depends on | **FAIL** |

That last row is the one worth understanding. Calling something deferred does not defer it if
something is being built against it — an acceptance criterion that cites an open question is a
requirement waiting on an answer nobody has, and check 8 fails.

## Why 5 and 8 are the ones that matter most here

The other eight are the sort of thing a careful reviewer catches. These two are where an agent will
quietly close a gap for you, because a specification with no open questions *reads* finished. In
payments, an invented refund threshold, retry count or expiry window is a business decision made by
something with no authority to make it — and it will read as perfectly reasonable right up until it
moves the wrong amount of money.

A specification that says "we do not know this yet, and we are not building it" is more finished
than one that guessed.
