# Pre-read — Lab 2

**10–15 minutes, before session day.** Setup takes longer than reading this, so start with the
setup step and read while Maven downloads.

---

## 1. Setup first

```bash
bash .claude/scripts/run scripts/verify_setup.py
```

This checks your toolchain, creates the two service repositories, warms the Maven cache and
confirms the starting state. It must end with **"Setup complete"**. If it does not, bring the
output to the facilitator before the session rather than during it.

A cold Maven cache is the single most common way a room loses fifteen minutes. Run this at your
desk, on the machine you will use.

---

## 2. The situation, in plain terms

A merchant took a payment. Now they need to refund it.

The refund request arrives in a WSAPI-facing shape, is translated by **TTA**, and is sent to
**Payment Processor**, which decides it and records it.

```
Merchant refund request
        |
        v
      WSAPI
        |
        v
       TTA                  translation boundary
        |
        v
Payment Processor           refund decision
        |
        v
wider PGS flow continues    CPC / Injection / LCS / DCF
                            -- not implemented in this lab --
```

You work on the **TTA → Payment Processor** portion only.

**Your task:** bring that portion into agreement — across contract, implementation, tests and
technical requirements — without expanding into the rest of the flow.

---

## 3. The thing that makes it interesting

Both repositories build. Both have passing tests. Neither is obviously broken.

They still do not agree with each other.

That is the whole point of the exercise. Correctness across a service boundary lives in the
*relationship* between two implementations, not inside either one, and no amount of testing one
repository in isolation will show you a disagreement with the other.

Two examples of the shape of the problem, neither of which is a hint about where to look:

- A service answers a duplicate refund with "this is a duplicate". The service in front of it turns
  that into "the system failed". The caller retries a request that was correctly refused.
- Both sides implement retry protection. They protect against *different* retry identities. Each
  looks correct alone; together, the operation is not idempotent.

---

## 4. Lab versus real PGS

The lab uses real PGS terminology and real refund behaviour, simplified deliberately so the
exercise fits in two hours.

Read [`SCENARIO_GROUNDING.md`](SCENARIO_GROUNDING.md) — it separates grounded PGS behaviour from
lab simplification from deliberately planted defect. The planted defects are teaching fixtures and
do not imply anything about real Mastercard systems.

The one rule worth carrying into the room: **inventing lab code is fine; inventing PGS platform
behaviour is not.**

---

## 5. Vocabulary

Skim [`TERM_CARD.md`](TERM_CARD.md). Ten terms. You will use *seam*, *context ledger* and
*agent brief* constantly.

---

## 6. What is graded

Read [`ESSENTIAL_OUTCOMES.md`](ESSENTIAL_OUTCOMES.md).

The short version: **engineering outcomes and evidence, never whether your screen matches the
facilitator's.**

---

## 7. Model output will vary — plan for it

Your agent will word things differently from the person next to you, find the same problem by a
different route, and return findings in a different order. Running the same prompt twice will not
give you the same text.

None of that means you are behind. If you find yourself trying to make your output *look like* the
demonstration, stop and ask what the demonstration was showing you instead.

---

## 8. What this lab assumes you already have

From Lab 1: fresh-context review, sub-agents, human gates, deterministic checks, journey and
hand-off. These are not re-taught. If any of them is hazy, say so early — the Start step is the moment for
it, not Stage 4.

You do **not** need to know anything new about payments. You need to be willing to say "the source
does not tell us that" and leave it unanswered.
