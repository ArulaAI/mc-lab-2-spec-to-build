# Specification Completeness Bar

Twelve structural checks. A specification clears the bar when all twelve hold.

The deterministic gate — `python3 .claude/scripts/validate_spec.py` — runs every check below.
It tells you whether the specification is well-formed enough to build from. It cannot tell you
whether the specification is *correct* — that judgement stays human, and the status file says so
rather than implying a machine blessed the content.

| # | Check | What it means in practice |
|---|---|---|
| 1 | **Required sections present** | Every section the gate expects exists in the document. A missing section is a missing concern. |
| 2 | **Metadata names an owner** | The specification has an assigned owner, not *(unassigned)*. |
| 3 | **Acceptance criteria carry identifiers** | At least five criteria labelled AC-1 through AC-N. Unnamed criteria cannot be traced. |
| 4 | **Acceptance criteria describe observable outcomes** | No "handled correctly", "works correctly", "as expected" or similar. Each criterion names something a test can check. |
| 5 | **Every contested decision has a named owner** | Remaining-refundable determination, endpoint selection, and retry identity stability each name exactly one owning service. |
| 6 | **Idempotency section is implementable** | States what carries the retry identity, which service keeps it stable, what the caller observes on a retry, and what must be true of stored state afterwards. |
| 7 | **Compatibility constraints are testable** | Names which combinations of old and new must keep working, and which must be shown to fail. |
| 8 | **Out of scope references the authoritative document** | Points to `specs/OUT_OF_SCOPE.md`. Nothing excluded quietly reappears as in-scope. |
| 9 | **Open questions are recorded rather than resolved** | At least one open question is retained. Closing one by picking a plausible answer is the failure this check exists for. |
| 10 | **No unresolved placeholders remain** | No *(unassigned)*, **Incomplete.**, **Vague.**, **Not yet testable.**, TBD, or TODO markers. |
| 11 | **Non-negotiables are referenced** | Points to `specs/NON_NEGOTIABLES.md`. The specification acknowledges the constraints it must satisfy. |
| 12 | **Negative requirements name settlement and Void** | Explicitly states that no settlement artifact is produced and no Void behaviour is implemented. |

## Why 6 and 9 are the ones that matter most here

The other ten are the sort of thing a careful reviewer catches. These two are the ones an agent
will quietly close for you, because a specification with no open questions *reads* finished. In
payments, an invented refund threshold, retry count or expiry window is a business decision made by
something with no authority to make it — and it will read as perfectly reasonable right up until it
moves the wrong amount of money.

A specification that says "we do not know this yet" is more finished than one that guessed.
