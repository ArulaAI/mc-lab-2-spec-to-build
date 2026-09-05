# Lab 2 — One Refund Across a Service Boundary

**120 minutes.** Roughly 114 minutes of committed activity, ~6 minutes of float.

Lab 1 taught you to govern one AI-assisted change inside one repository. This lab is about what
happens when the change spans two, and the decisions that matter live in the space between them.

Before you start, confirm `python3 scripts/verify_setup.py` ended with **"Setup complete"**.

---

## How to read this guide

Each stage says what you are doing and why, and shows **one** worked example. It does not give you
a prompt to paste. That is deliberate: you will not have this guide at your desk next month, and a
prompt you copied teaches you nothing about how to write the next one.

Where you see **▶ Your turn**, you write the next one yourself. Where you see **◆ Predict**, write
your answer down before you find out — including when you turn out to be wrong, which is the part
that sticks.

Your agent's wording will differ from your neighbour's. That is expected. See
[`docs/ESSENTIAL_OUTCOMES.md`](docs/ESSENTIAL_OUTCOMES.md).

---

# Stage 0 — Ground the Work · *Frame the Boundary* · ~10 min

**Concept: context boundary and authority.** Before an agent acts, decide what it may see and which
document wins when two disagree.

1. **Start the lab.**
   ```
   /lab
   ```
   Confirm a journey event actually landed in `.claude/journey/` — not just that the command
   returned. A silent journey failure surfaces at Stage 6 otherwise, when it is too late to fix.

2. **Read the boundary.** Open [`docs/SCENARIO_GROUNDING.md`](docs/SCENARIO_GROUNDING.md). You are
   working on the TTA → Payment Processor seam only. CPC, injection, LCS, DCF and settlement are
   outside the runtime.

3. **Read the outcomes card.** [`docs/ESSENTIAL_OUTCOMES.md`](docs/ESSENTIAL_OUTCOMES.md). Eight
   outcomes, and two of them are things you *refuse* to do.

4. **Note the authority order.** `NON_NEGOTIABLES.md` → `OUT_OF_SCOPE.md` → `PGS_DECISIONS.md` →
   the specification. Higher wins. The first three are write-protected; if you try to edit them the
   write gate will stop you, which is the point.

5. **◆ Predict #1 — seal this before you look at any code.**

   > Two repositories must end up agreeing. **Which side should change first, and why?**

   Write it in your notes with your reasoning. You will reopen it twice. Do not go looking for the
   answer now — a prediction you have already researched teaches you nothing.

6. **Close the stage.**
   ```
   /hand-off
   ```

---

# Stage 1 — Audit Context · *Map the Seam* · ~18–20 min

**Concept: scoped sub-agents and parallel delegation.** Agents reason locally. You reconcile
globally.

You could hand one agent both repositories. Don't. An agent given everything spends its attention
on framework detail, reasons deeply about one side and shallowly about the other, and fills the
space between them with plausible invention. You will not be able to tell which parts it verified.

Instead: one agent per repository, read-only, each returning the same structured shape — so the
returns can be laid side by side and the disagreements become visible.

The `repo-auditor` agent is already defined for you at `.claude/agents/repo-auditor.md`. **The
capability is standardised. The brief is yours to write.**

### ◆ Predict #2

> The first agent will audit one repository and report confidently. **What will it be unable to
> know, that only the other repository can tell you?** Name two things before you dispatch it.

### The facilitator demonstrates: briefing the first auditor

Watch what the brief actually pins down, and what it deliberately refuses:

- which repository, and that it may read nothing else
- what to inspect: entry points, contract artifacts and their versions, outbound calls, business
  rules, boundary validations, error mappings, idempotency behaviour, correlation behaviour, tests
- that every claim cites a file and, where it applies, a line
- that anything requiring the other repository goes under **Unknowns**, not under a guess
- that it must report what the source material requires and the repository does *not* do — absence
  from code is not absence from authority
- the exact return headings, so two returns can be compared rather than read

### ▶ Your turn: brief the second auditor

Write the brief for the other repository yourself. Same return shape — that is what makes the
returns comparable — but the things worth inspecting are not identical on both sides of a seam.
One side translates and calls; the other decides and records.

Both auditors may run at the same time. They only read, so there is nothing to serialise.

### Then: reconcile, in [`docs/context-ledger.md`](docs/context-ledger.md)

| Claim | Asserted in | Evidence | Contradicted by | Human ruling | Status |

This is the stage's real work, and it is yours rather than the agents'. Every row gets a ruling.

Three things worth being deliberate about:

- **A claim is what a repository believes about the world beyond itself.** Those are the rows that
  matter: a claim can be entirely true locally and false at the seam.
- **`UNKNOWN` is a finish state.** If neither repository can settle something, it stays `UNKNOWN`.
  Do not resolve it because an empty cell looks unfinished.
- **When the two disagree, you rule.** Not the agent that sounded more certain.

**Reveal:** compare the ledger against your Prediction #2. What could the first agent not have
known?

```
/hand-off
```

---

# Stage 2 — Author & Validate the Spec · *Make the Spec Buildable* · ~18–20 min

**Concept: spec-as-context and readiness gates.** The validated specification becomes the bounded
authority every agent builds from. Whatever is vague here becomes an invention later.

Open [`specs/refund-seam-phase1.spec.md`](specs/refund-seam-phase1.spec.md) and run the gate:

```bash
python3 .claude/scripts/validate_spec.py
```

It will refuse the specification and tell you which checks fail. The checks map to
[`docs/SPEC_COMPLETENESS_BAR.md`](docs/SPEC_COMPLETENESS_BAR.md).

### The facilitator demonstrates: one weak requirement becoming testable

> **Weak:** "Handle duplicate refunds correctly."
>
> **Buildable:** "When Payment Processor identifies a duplicate logical refund, the TTA boundary
> preserves the duplicate-conflict semantics, and the downstream repository contains no second
> refund record."

Notice what changed. The second version names who decides, what the caller observes, and what must
be true of stored state afterwards — three things a test can check. The first names none of them,
and "correctly" is doing all of the work.

### ▶ Your turn: harden the rest

The specification carries several more weaknesses of the same kind. Work through them with your
agent, then re-run the gate until it reports **READY**.

Three rules while you do it:

1. **Do not close an open question by answering it.** `OQ-1` asks how the idempotency key is
   derived in production. The source states the duplicate rule and the status code and never states
   the derivation. It stays open. An agent will offer you a reasonable-sounding answer; that is the
   single most important thing to refuse in this lab.
2. **Do not weaken the out-of-scope list to make something fit.** It is write-protected, so the
   gate will stop you, but the instinct is what to notice.
3. **Everything you add traces to `PGS_DECISIONS.md`** — as a PGS fact, or as an explicitly
   labelled lab representation.

The gate is structural. It checks that the specification is well-formed, not that it is *right*.
The status file says `"semantic_authority": "human-reviewed"` for exactly that reason.

**Human gate before you move on:** read your hardened specification once more and ask — did we
invent any PGS behaviour to get here? If yes, take it out and put the question back.

```
/hand-off
```

### ⏸ Q&A pause — ~3 min

Questions about the domain, the spec or the gate. Deep environment problems go on the **parking
lot** rather than into the room.

---

# Stage 3 — Plan Across Repositories · *Design the Orchestration* · ~14–15 min

**Concept: agent orchestration and context isolation.** Orchestration is not launching more agents.
It is deciding who knows what, who does what, and who decides what.

Produce three artifacts:

```
docs/plans/orchestration-plan.md
docs/agent-briefs/tta-implementation-brief.md
docs/agent-briefs/processor-implementation-brief.md
```

Each implementation brief states:

```
Outcome                     Tools allowed
Authoritative inputs        Acceptance criteria owned
Repository scope            Dependencies on the other repository
Allowed areas               Expected return shape
Excluded areas              Stop conditions
```

**Stop conditions matter more than they look.** "If the specification is silent on X, stop and
report rather than choosing" is the line that prevents an agent inventing a business rule at minute
twenty-two when nobody is watching it closely.

You may use the planner to propose a decomposition. It does not own the rulings: **which service is
authoritative, which contract version is targeted, and what order things happen in are yours.**

### The rollout question

Derive a sequence in which old and new can coexist safely.

Note what the question is not: it is not "which side is more important". It is "which combinations
of deployed versions are safe while the change is in flight" — and a change can be perfectly
correct in its final state and still be unsafe halfway through.

```bash
python3 scripts/run_pair_verification.py --explain
```

### ◆ Predict #3 — reopen Prediction #1

You sealed an answer in Stage 0 before seeing any code. You now know the seam and the
specification.

> **Would you change your answer? What did you not know when you made it?**

Write the revision next to the original. Keep both.

Validate the plan:

```bash
python3 .claude/scripts/validate_plan.py
```

```
/hand-off
```

---

# Stage 4 — Build & Validate · *Build the Bounded Slice* · ~28–30 min

**Concept: bounded agent execution and deterministic guardrails.** AI generates inside tests,
rules, gates, tool permissions and contract checks — not inside a conversation.

One scoped implementation context per repository. Each agent receives **only**:

- the validated specification
- its repository brief and implementation brief
- the acceptance criteria it owns
- that repository's `CLAUDE.md`

Not the other repository. Not this guide. Not your reasoning about the seam.

### The facilitator demonstrates: the shape of one implementation prompt

You will see the structure — outcome, authoritative inputs, scope, exclusions, expected return —
and how it refuses to describe the fix. It states the outcome and the boundary, and leaves the
implementation to the agent, because a prompt that specifies the diff is just a slower way of
writing the diff yourself.

### ▶ Your turn: write the brief for the other repository

Adapt it to what that repository actually owns. The two are not symmetric, and one of them may
correctly conclude that it needs **no production change at all** — in which case its job is to say
so and prove it. That is a real outcome, not a failed one.

### Expected return from each agent

```
Files changed        Verification run
ACs addressed        Open concern
Tests added          No-scope-expansion confirmation
```

### Two things to watch for, because they are the ones that will actually happen

- **An agent will offer to fix something outside its repository.** Refuse it. That is the seam, and
  the seam is yours.
- **An agent will find nearby code that looks reusable and unfinished.** Adjacency is not
  authorisation. If it is out of scope, the correct action is no diff plus a recorded reason.

### Verify as you go

```bash
cd pgs-tta && mvn verify
cd ../pgs-payment-processor && mvn verify
```

**Both green does not mean done.** That is the entire premise of the lab. Writes follow the rollout
order you decided in Stage 3.

```
/hand-off
```

---

# Stage 5 — Validate with Fresh Context · *Prove the Pair* · ~20 min

**Concept: fresh-context validation and independent judgment.** Separate creation from judgment.

**This stage is never cut.** If Stage 4 runs long, the facilitator will apply a checkpoint and move
the room here. Finishing the coding is worth less than seeing what independent judgment catches.

### ◆ Predict #4

> Both repositories are green. **What will a fresh validator, or the pair harness, catch that your
> green builds did not?** Write down one thing before you run either.

### 1. Deterministic evidence first

```bash
python3 scripts/run_pair_verification.py
```

This is the answer to "are the two services actually in agreement". Each failure names the
disagreement in its message.

### 2. Then independent judgment

```bash
python3 .claude/scripts/build_validator_brief.py
```

The brief is assembled mechanically from the specification, both diffs, the ledger, the pair
results, the plan and the scope documents. It contains **no chat history and no builder
rationale** — not because the script is careful, but because it has no access to them.

Dispatch the fresh `code-to-spec-validator` against it. It has read and test tools and **no write
tools**, so it cannot quietly fix what it finds. It never saw your session, so it cannot inherit
your confidence in your own work.

### 3. Disposition every finding — `docs/finding-dispositions.md`

| Finding | Evidence | In scope? | Material? | Disposition | Rationale |

**A validator finding does not authorise a code change.** Some findings are correct and out of
scope. Some are wrong. Some are right but immaterial. Deciding which is which is the judgment this
stage exists to exercise, and it is graded on the disposition — not on agreeing with the validator.

**Reveal:** compare against Prediction #4.

```
/hand-off
```

### ⏸ Q&A pause — ~3 min

---

# Stage 6 — Review, Handoff & Close · *Transfer the Learning* · ~5–6 min

**Concept: context handoff, evidence and the learning loop.**

1. **Reopen Prediction #1.** You have now answered the rollout question three times: blind, informed
   and evidenced. Compare all three. What made the difference — and would you have discovered it
   without the compatibility matrix?

2. **Record one reusable practice.** One sentence, in `docs/workflow-tracker.md`: something about
   multi-repository AI work you would do again on Monday, on your own code.

3. **Close out.**
   ```
   /hand-off
   ```

4. **Confirm the journey exists.** `.claude/journey/` should hold a real event trail.

### What you should be able to say at the end

> When an AI-assisted change spans repositories, I first establish the authority and the seam. I
> scope agents to local evidence instead of giving one context everything. I reconcile their claims
> myself, make the specification buildable, define agent contracts and rollout constraints, let AI
> execute only inside those boundaries, and then prove the pair with independent evidence before I
> accept the change.

### And what it does not mean

The lab proves the represented seam locally. It does not claim the wider PGS refund capability is
production-ready, and pair verification does not replace integration testing or release governance.

---

## Parking lot

Environment problems, deep domain questions and anything that would derail the room goes here.
The facilitator picks these up at the Q&A pauses or after the session. Nothing is lost by parking
it, and a room of thirty loses a lot by debugging one laptop together.

## If you fall behind

Say so. Stage 5 is the payoff and there are facilitator checkpoints for exactly this. Arriving at
independent validation having done four of five fixes is a far better session than finishing the
coding and never seeing what fresh context catches.
