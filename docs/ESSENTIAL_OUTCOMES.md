# Essential Outcomes Card

**Write-protected.** Keep this open during the session.

## What is graded

Engineering outcomes and evidence. Not whether your screen matches the facilitator's.

> Model wording, ordering and formatting will differ between people, and between two runs by the
> same person. That is normal and expected. We grade what you concluded, what you can show for it,
> and what you refused to do — never whether your response looks like anyone else's.

If your agent phrases something differently, finds the same problem by another route, or returns
its findings in a different order, you are not behind.

## The eight outcomes

By the end of the session your workspace should show:

1. **The context ledger identifies the contract drift** between the two repositories, with evidence.
2. **The context ledger identifies the divergent business rule**, and names which service owns it.
3. **At least one unknown remains unresolved** rather than filled in with a plausible default.
4. **The specification preserves its out-of-scope list** — nothing excluded got built.
5. **The plan defines repository boundaries and a compatibility rationale**, not just a task list.
6. **The retry identity is stable across the seam** — what one side sends is what the other
   deduplicates against.
7. **Duplicate semantics survive the seam** — a duplicate reaches the caller as a duplicate.
8. **Pair verification is green**, and you can say what that does and does not prove.

## Two things that are outcomes, not failures

**A "no diff" result, with evidence, is a real outcome.** Deciding that a repository is correct and
proving it is engineering work. So is refusing to change something because it is out of scope, and
recording why.

**An unresolved question left visible beats a plausible answer invented to close it.** In payments,
guessing a threshold or a default is a business decision you were not authorised to make. Surfacing
it is the correct move, and it is scored as such.

## What this lab does not claim

The lab proves the represented seam locally. It does not claim the wider PGS refund capability is
production-ready, and pair verification does not replace integration testing or release governance.
