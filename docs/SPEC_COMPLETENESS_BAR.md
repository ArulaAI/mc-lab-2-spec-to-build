# Specification Completeness Bar

Eight checks. A specification clears the bar when all eight hold.

The deterministic gate — `python3 .claude/scripts/validate_spec.py` — checks the structural half.
The rest is a human judgement, and the status file says so rather than implying a machine blessed
the content.

| # | Check | What it means in practice |
|---|---|---|
| 1 | **Ownership is named** | Every contested decision has exactly one owning service. A decision with two owners is a decision that will drift. |
| 2 | **Acceptance criteria are executable** | Each criterion describes something a test can observe. "Handled correctly" is not an outcome. |
| 3 | **Out-of-scope survives intact** | Nothing excluded quietly reappears as in-scope because it was convenient. |
| 4 | **Unknowns remain explicit** | Open questions are still recorded as open. Closing one by picking a plausible answer is the failure this check exists for. |
| 5 | **Error semantics are named where source-backed** | Which condition produces which status, where the source says so. |
| 6 | **No invented field, default, service or endpoint** | Every named thing traces to source material or is labelled a lab representation. |
| 7 | **Source silence is surfaced, not guessed** | Where the material does not say, the specification says that it does not say. |
| 8 | **Compatibility impact is identified** | Which combinations of old and new must keep working, and which must be shown to fail. |

## Why 4 and 7 are the ones that matter most here

The other six are the sort of thing a careful reviewer catches. These two are the ones an agent
will quietly close for you, because a specification with no open questions *reads* finished. In
payments, an invented refund threshold, retry count or expiry window is a business decision made by
something with no authority to make it — and it will read as perfectly reasonable right up until it
moves the wrong amount of money.

A specification that says "we do not know this yet" is more finished than one that guessed.
