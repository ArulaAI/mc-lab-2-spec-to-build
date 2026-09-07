```
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   L A B   2                                                                ║
║                                                                            ║
║   ONE REFUND ACROSS A SERVICE BOUNDARY                                     ║
║   ─────────────────────────────────────                                    ║
║                                                                            ║
║   Two repositories. Both green. They still disagree.                       ║
║                                                                            ║
║   120 minutes · 6 stages · 2 services · 1 seam                             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## The 90-second version

A merchant took a payment. Now they want it refunded.

That refund crosses a boundary: **TTA** translates it, **Payment Processor** decides it. Two
services, two repositories, two teams, two release cadences.

Here is the situation you are walking into:

```
       pgs-tta                              pgs-payment-processor
   ┌───────────────┐                        ┌───────────────┐
   │  mvn verify   │                        │  mvn verify   │
   │               │                        │               │
   │   ✓  GREEN    │                        │   ✓  GREEN    │
   └───────┬───────┘                        └───────┬───────┘
           │                                        │
           └──────────────►  ?????  ◄───────────────┘
                        the two do not agree
```

Nobody's tests are failing. Nobody's build is red. No linter is complaining. And the refund
still does the wrong thing, because **correctness across a service boundary does not live inside
either service** — it lives in the relationship between them, and neither repository can see it.

> ### The one line to take away
> **Repo A green + Repo B green ≠ pair correct.**

Lab 1 taught you to govern one AI-assisted change inside one repository. This lab is about what
happens when the change spans two, and the decisions that actually matter live in the space
between them — where no single agent, and no single test suite, is looking.

---

## Your job, stated plainly

You are not here to fix bugs. You are here to **establish what is true across a boundary where
neither witness can see the whole picture** — and then to direct AI safely inside that picture.

By minute 120 you will have:

```
  ▸ audited both repositories with scoped agents that cannot see each other
  ▸ reconciled their conflicting claims yourself, with evidence
  ▸ turned a vague specification into one you can build from
  ▸ written the contracts that bound what each agent may do
  ▸ let AI implement only inside those bounds
  ▸ proved the pair with evidence a fresh context produced
```

---

## The map

The whole lab on one screen. Each stage teaches one agentic-engineering concept, and each hands
the next stage something concrete.

```
 STAGE                              CONCEPT                            YOU LEAVE WITH
 ────────────────────────────────────────────────────────────────────────────────────────
  ~  Start: Ground the Work        context boundary & authority       a sealed prediction
        │
  1  Audit Context                  scoped agents, parallel            the context ledger
        │                           delegation
  2  Author & Validate the Spec     spec-as-context, readiness gates   a buildable spec
        │
       ⏸  Q&A
        │
  3  Plan Across Repositories       planning, briefing &               plan + 2 agent briefs
        │                           rollout sequencing
  4  Build & Validate               bounded execution, deterministic   a remediated seam
        │                           guardrails
  5  Validate the Pair              independent judgment               evidence you didn't write
        │
       ⏸  Q&A
        │
  6  Review, Handoff & Close        context handoff, learning loop     a practice worth reusing
```

### Where the time goes

```
  Start ████                              6 min   Ground the Work
  S1  ██████████                        17 min   Audit Context
  S2  █████████                         16 min   Author & Validate the Spec
  Q&A ██                                 4 min   ⏸
  S3  █████████                         16 min   Plan Across Repositories
  S4  ███████████████                   25 min   Build & Validate
  S5  ████████████                      20 min   Validate the Pair
  Q&A ██                                 4 min   ⏸
  S6  ███                                6 min   Review, Handoff & Close
      ─────────────────────────────────────────
                                       114 min   committed, leaving 6 minutes of float
```

Six minutes of float, and it is float rather than slack you can spend twice. Something always
runs long; when it does the trade comes out of Stage 4, never Stage 5. Stage 5 is the judgment
anchor and is the reason the whole exercise is worth doing.

---

## How to read this guide

This guide shows you **one** worked example per technique and then asks you to write the next one
yourself. It deliberately does not hand you prompts to paste. You will not have this document at
your desk next month, and a prompt you copied teaches you nothing about how to write the one you
will actually need.

### The markers

```
  ◆ Predict     Write your answer down BEFORE you find out. Including — especially —
                when you turn out to be wrong. That is the part that sticks.

  ▶ Your turn   The facilitator demonstrated one. You write the next one.

  ⚠ Trap        A place rooms reliably lose time or reach for the wrong instinct.

  ⏸ Q&A pause   Scheduled, so questions land somewhere instead of derailing the room.

  ⌘ Run         A command to actually execute.

  ⌂ You'll see  Real output from a real run, so you can tell "different" from "wrong".
                Yours will differ in wording. It should not differ in shape.

  ✓ Done when   The self-check that closes a stage. If you can tick these, move on.
```

### Before anything else

> **Your agent's output will not match your neighbour's.** Different wording, different ordering,
> the same problem found by a different route. Running the same prompt twice will not give you
> the same text either.
>
> None of that means you are behind. If you catch yourself trying to make your output *look like*
> the demonstration, stop and ask what the demonstration was actually showing you.
>
> See [`docs/ESSENTIAL_OUTCOMES.md`](docs/ESSENTIAL_OUTCOMES.md) — we grade what you concluded and
> what you can show for it, never whether your screen matches anyone else's.

### Preflight

```bash
python3 scripts/verify_setup.py
```

Must end with **"Setup complete"**. If it does not, flag it now — not at minute forty.

---

```
┌───────────────────────────────────────────────────────────────── 6 min ──┐
│  START  ·  GROUND THE WORK                                               │
│  Frame the Boundary            not a numbered stage -- the six begin next │
└──────────────────────────────────────────────────────────────────────────┘
```

*You are about to commit to an answer you cannot take back. You have ten minutes.*

**Concept** — context boundary and authority
**You leave with** — a sealed prediction, and knowing which document wins an argument

Before an agent does anything, two questions have to be settled: what is it allowed to see, and
when two documents disagree, which one wins? Skip these and every later decision inherits the
ambiguity.

### 1 · Start the lab

```
⌘  /lab
```

**Once `/lab` has run**, confirm a journey event actually landed — not merely that the command
returned. A silent journey failure surfaces at Stage 6, which is far too late to fix it.

The directory does not exist until `/lab` creates it, so run this *after* the command above, in a
form that tells you which of the two situations you are in:

```bash
ls .claude/journey/*.jsonl 2>/dev/null || echo "no journey file yet - /lab did not start recording"
```

**⌂ You'll see** — one or more `.jsonl` paths. If you get the fallback message instead, re-run
`/lab` now rather than discovering it at Stage 6.

### 2 · Read the boundary

Open [`docs/SCENARIO_GROUNDING.md`](docs/SCENARIO_GROUNDING.md).

```
   WSAPI ─► TTA ─► Payment Processor ─► CPC ─► Injection ─► LCS ─► DCF
            └──────────┬─────────────┘  └──────────┬──────────────────┘
              you work here              not implemented in this lab
```

That document also separates three things you must keep apart all session: what is **grounded PGS
behaviour**, what is **lab simplification**, and what is a **deliberately planted defect**. The
planted ones are teaching fixtures. They do not imply anything about real Mastercard systems.

### 3 · Note the authority order

```
   specs/NON_NEGOTIABLES.md     ◄── highest. Holds regardless of anything else.
   specs/OUT_OF_SCOPE.md        ◄── what must not be built
   docs/PGS_DECISIONS.md        ◄── fact vs. lab representation vs. not modelled
   specs/refund-seam-phase1.spec.md   ◄── what to build, once it is READY
```

Higher wins. `NON_NEGOTIABLES.md`, `OUT_OF_SCOPE.md` and `ESSENTIAL_OUTCOMES.md` are
**write-protected** — try to edit one and the write gate stops you. That is deliberate: a lab
whose rules can be edited by the thing being graded is not measuring anything.

### 4 · ◆ Predict #1 — seal it, you cannot change it later

> Two repositories have to end up agreeing.
> **Which side should change first, and why?**

Write it down now, with your reasoning, before you look at a single line of code.

You will reopen this twice — once when you understand the seam, and once when you have hard
evidence. Do not go researching it now. A prediction you have already looked up teaches you
nothing.

### 5 · Close the stage

### ✓ Done when

```
  [ ] /lab ran and .claude/journey/ contains at least one event
  [ ] you can name which document wins if the spec and NON_NEGOTIABLES disagree
  [ ] Prediction #1 is written down, with reasoning, before you opened any code
```

```
⌘  /hand-off
```

---

```
┌─────────────────────────────────────────────────────────────── 17 min ──┐
│  STAGE 1  ·  AUDIT CONTEXT                                               │
│  Map the Seam                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

*Two agents will each tell you the truth. They will contradict each other.*

**Concept** — scoped sub-agents and parallel delegation
**You leave with** — a context ledger you reconciled yourself

> **Agents reason locally. You reconcile globally.**

### Why not just hand one agent both repositories?

You could. Someone in the room will. Here is what happens:

```
   ONE AGENT, BOTH REPOS              TWO AGENTS, ONE REPO EACH
   ─────────────────────              ─────────────────────────
   spends attention on                each finding is local
   framework detail                   and checkable

   reasons deeply about one           neither can guess across
   side, shallowly about the          the boundary — so it says
   other                              so instead

   fills the gap between them         the gaps stay visible,
   with plausible invention           and YOU close them

   you cannot tell which parts        the disagreements show up
   it actually verified               as disagreements
```

The second shape is not more work. It is the only shape where the seam becomes visible, because
a disagreement can only appear when two independent accounts are laid side by side.

### ◆ Predict #2

> The first agent will audit its repository and report with total confidence.
> **Name two things it cannot possibly know** — things only the *other* repository can tell you.

Write them down before you dispatch it.

### The facilitator demonstrates — the repo-brief pattern

The `repo-auditor` agent already exists at `.claude/agents/repo-auditor.md`. **The capability is
standardised; the brief is yours.** The facilitator walks through the pattern **without launching
anything** — you launch both, together, in a moment.

What a brief has to pin down:

```
   the absolute repository root, and that globs and greps are rooted there
   what to inspect: entry points, contract artifacts and versions, outbound
     calls, business rules, boundary validations, error mappings, idempotency,
     correlation, tests
   that every claim cites a file, and a line where one applies
   that anything needing the other repository goes under UNKNOWNS, not a guess
   that it must report what the source requires and the repo does NOT do --
     absence from code is not absence from authority
   the six required return headings, verbatim
```

Two of those are load-bearing for reasons that are not obvious.

**The absolute root.** The agent has Read, Glob and Grep. A broad glob will happily return matches
from outside the repository you meant. Scope has to come from the brief; the tooling will not
supply it.

**The six headings, in the brief itself.** The agent returns whatever shape the brief asks for — it
does not enforce its own. Ask for the wrong shape and you get the wrong shape, politely.

```
REPOSITORY:      CONTRADICTIONS:
CLAIMS:          UNKNOWNS:
EVIDENCE:        STOP_REQUIRED:
```

### ▶ Your turn — write both briefs, then launch both at once

Write both repo briefs yourself. Same return shape, because that is what makes two reports into one
comparison. But the two sides are not mirror images: one **translates and calls**, the other
**decides and records**, so what is worth inspecting differs.

Then dispatch **both auditors in a single action**, before reading either result.

That ordering is the whole technique. Launch one, read it, then brief the second and you have
contaminated the second brief with the first agent's conclusions — and you will not be able to tell
which of its findings were independent. Two agents launched blind to each other produce two
accounts that can genuinely disagree.

**⌂ You'll see** — two returns, each naming its own repository, each with its own `UNKNOWNS`. A
return that answers a question about the *other* repository is a finding about your brief, not a
gift: it means the scope did not hold.

### Then the real work — reconcile

In [`docs/context-ledger.md`](docs/context-ledger.md):

| Claim | Asserted in | Evidence | Contradicted by | Human ruling | Status |
|---|---|---|---|---|---|

**⌂ You'll see** — the *shape* of a reconciled row. The content is yours to find; what matters is
that every column carries weight:

| Claim | Asserted in | Evidence | Contradicted by | Human ruling | Status |
|---|---|---|---|---|---|
| what one repository believes about the other | which repository asserts it | a file and line you can open | what the other repository actually shows | your decision, and the reason for it | `CONTRADICTED` |

That example is deliberately not telling you what the claim is, and it is not a row you can copy.

**The evidence column has to resolve.** If you cite a file and line, open it first — a citation
that points at nothing is worse than no citation, because it looks like work. A row with three
empty cells is a note to yourself, not a finding, and the grader counts populated cells for
exactly that reason.

### The rulings are yours — and only yours

The auditors return claims and evidence. **They do not touch this file.** Nothing is written into
the ledger until both returns exist and you have ruled, and the `Human ruling` column is never
filled in on your behalf.

Two questions decide what goes in it. They are the same for everyone in the room, and they are
asked once both returns are on the table:

> **DG-01** — The two audits disagree about at least one behaviour at the seam. For each
> disagreement, which repository is authoritative, and what is your evidence for that ruling?
>
> **DG-02** — Which of the auditors' unknowns can be settled from the material you have, and which
> stay `UNKNOWN`?

If answering either one would require authority nobody has, that is not a stalemate to break with
a reasonable guess. Say so, record what is missing, and move on — the specification has an Open
questions section for exactly this.

This part is yours, not the agents'. Three things to be deliberate about:

**A claim is what a repository believes about the world beyond itself.** Those are the rows that
matter. A claim can be entirely true locally and false at the seam — that is precisely the failure
mode you are hunting.

**`UNKNOWN` is a finish state.** If neither repository can settle something, it stays `UNKNOWN`.
Do not resolve it because an empty cell looks unfinished.

**When the two disagree, you rule.** Not the agent that sounded more certain. Confidence is not
evidence, and an agent has no way to signal the difference.

> ⚠ **Trap** — the tempting move here is to accept whichever account is more detailed. Detail is
> a property of how much the agent had to say, not of how much it verified.

**Reveal:** compare your ledger against Prediction #2. What could the first agent not have known?

*What you just proved: two independent accounts of a seam produce disagreements that one combined
account would have hidden with plausible invention.*

### ✓ Done when

```
  [ ] both repositories were audited by separate agents, not one agent twice
  [ ] the ledger has a row for the contract situation and a row for the business rule
  [ ] every row has a ruling — none left blank
  [ ] at least one row is still UNKNOWN, because you could not settle it honestly
```

If every row came back VERIFIED and nothing is UNKNOWN, you have probably accepted an agent's
confidence as evidence. Go back and ask which repository actually *proved* each claim.

```
⌘  /hand-off
```

---

```
┌─────────────────────────────────────────────────────────────── 16 min ──┐
│  STAGE 2  ·  AUTHOR & VALIDATE THE SPEC                                  │
│  Make the Spec Buildable                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

*The spec is broken. The gate will prove it. Your job is to fix it without inventing anything.*

**Concept** — spec-as-context and readiness gates
**You leave with** — a specification an agent can build from without guessing

> **Whatever stays vague here becomes an invention later.** Not might. Does.

The validated specification is the bounded authority every agent in Stage 4 will build from. It
is the highest-leverage document in the lab, and right now it is not good enough.

```
⌘  python3 .claude/scripts/validate_spec.py
```

It will refuse the specification and name the failing checks.

The twelve checks it runs are the twelve in
[`docs/SPEC_COMPLETENESS_BAR.md`](docs/SPEC_COMPLETENESS_BAR.md), one for one. They are all
structural — is a section present, does a criterion carry an identifier, is an owner named. None
of them can tell you the specification is *correct*, which is why the status file records
`"semantic_authority": "human-reviewed"` instead of implying a machine approved the content.

**⌂ You'll see** — the shipped specification fails six of the twelve:

```
  [PASS] required sections present                           all present
  [FAIL] metadata names an owner                             Owner is unset or marked unassigned
  [FAIL] acceptance criteria describe observable outcomes    unobservable phrasing: handled correctly
  [FAIL] every contested decision has a named owner          no owner named for: ...
  [FAIL] idempotency section is implementable                does not state: ...
  ...
  6/12 structural checks  ->  DRAFT
```

By the end of this stage that last line reads `12/12 structural checks  ->  READY`. It is a
deterministic script, not a model, so that number is the same for everyone in the room. If yours
says READY and your neighbour's says DRAFT, you have a real difference — not a formatting one.

Run the gate before you start editing — the failing check names are your editing queue. Work
through them with your agent and re-run until all twelve pass.

### The facilitator demonstrates — one weak requirement becoming testable

```
   ✗  WEAK
      "Handle duplicate refunds correctly."

   ✓  BUILDABLE
      "When Payment Processor identifies a duplicate logical refund, the TTA
       boundary preserves the duplicate-conflict semantics, and the downstream
       repository contains no second refund record."
```

Look at what actually changed. The second version names **who decides**, **what the caller
observes**, and **what must be true of stored state afterwards**. Three things a test can check.

The first names none of them. The word "correctly" was carrying the entire requirement, and
"correctly" is exactly where an agent inserts its own judgement.

### ▶ Your turn — harden the rest

The specification carries several more weaknesses of the same shape. Work through them with your
agent and re-run the gate until it reports **READY**.

Three rules while you do:

**1 · Do not close an open question by answering it.**

`OQ-1` asks how the idempotency key is derived in production. The source material states the
duplicate rule and the status code, and never states the derivation.

> ⚠ **Trap — the strongest one in this lab.** Your agent will offer you a reasonable-sounding
> derivation. It will look like diligence. In payments, an invented key derivation is a business
> decision made by something with no authority to make it — and it will read as perfectly sensible
> right up until it moves the wrong amount of money.
>
> It stays open. Refusing to answer it is the single most important thing you do today.

**2 · Do not weaken the out-of-scope list to make something fit.** It is write-protected, so the
gate will stop you. The instinct is the thing worth noticing in yourself.

**3 · Everything you add traces to `docs/PGS_DECISIONS.md`** — as a PGS fact, or as an explicitly
labelled lab representation. Nothing gets invented into existence.

### Human gate before you move on

Two fixed questions close this stage. Same wording for everyone, asked once the gate reports
READY so the criteria are stable:

> **DG-03** — For each open question the specification carries, does the supplied source material
> answer it? Name the source you checked, and say what you are recording.
>
> **DG-04** — Which acceptance criteria need evidence from both repositories, and which belong to
> exactly one?

DG-04 is not bookkeeping. That assignment becomes the `Acceptance criteria owned` field in each
Stage 3 contract, and it is what lets Stage 5 judge each repository against its own criteria
instead of reviewing one combined diff.

Then read your hardened specification once more and ask:

> **Did we invent any PGS behaviour to get here?**

If yes, take it out and put the question back.

The gate is structural. It tells you the specification is well-formed, never that it is *right* —
which is why the status file records `"semantic_authority": "human-reviewed"` rather than quietly
implying a machine approved the content.

*What you just built: the single document every agent in Stage 4 will treat as truth. Everything
vague you left in it will become an invention you did not authorise.*

### ✓ Done when

```
  [ ] validate_spec.py reports READY
  [ ] OQ-1 is still listed as open — you did not answer it
  [ ] every ownership row names exactly one service
  [ ] anything you added traces to a line you can point at in PGS_DECISIONS.md
```

```
⌘  /hand-off
```

### ⏸ Q&A pause — 3 min

Domain, spec, or gate questions. Environment problems go to the **parking lot** instead of into
the room.

---

```
┌─────────────────────────────────────────────────────────────── 16 min ──┐
│  STAGE 3  ·  PLAN ACROSS REPOSITORIES                                    │
│  Plan and Brief                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

*The agents you are about to dispatch are only as good as what you write in the next 14 minutes.*

**Concept** — planning, briefing, and rollout sequencing
**You leave with** — an orchestration plan and two agent briefs

No agents are dispatched here — that is Stage 4. Your job now is to write the contracts they will
work from. Deciding who knows what, who does what, and who decides what.

### Produce three artifacts

```
   docs/plans/orchestration-plan.md
   docs/agent-briefs/tta-implementation-brief.md
   docs/agent-briefs/processor-implementation-brief.md
```

Each implementation brief is a contract:

| Each contract settles | And also |
|---|---|
| Repository | Tools allowed |
| Objective | **Acceptance criteria owned** |
| Authoritative context | **NO_DIFF_EXPECTED: true \| false** |
| Allowed repository scope | Verification required |
| Excluded areas | Expected return shape |
| | Stop conditions |

Two of those decide what Stage 5 can even do.

**Acceptance criteria owned** is the per-repository split. Stage 5 judges each repository against
*its own* criteria rather than reviewing one combined diff, so a criterion nobody owns is a
criterion nobody validates. The plan gate enforces it: every criterion owned by at least one
contract, each contract owning at least one, and no contract inventing a criterion the
specification does not contain.

**NO_DIFF_EXPECTED** is a separate statement from owning nothing. A repository can legitimately own
criteria and expect to change no code — in which case the contract says so, and the job becomes
proving those criteria are already satisfied. Owning no criteria at all is not the same claim, and
leaves that repository's validator with nothing to judge.

**Stop conditions matter far more than they look.** A line like *"if the specification is silent
on X, stop and report rather than choosing"* is what prevents an agent inventing a business rule
at minute twenty-two, in a file nobody is watching closely, with complete confidence.

You may use the planner to propose a decomposition. It does not own the rulings. **Which service
is authoritative, which contract version you target, and what order things land in are yours.**

### The rollout question

Derive a sequence in which old and new can coexist safely.

Notice what that question is *not*. It is not "which side matters more". It is "which combinations
of deployed versions are safe **while the change is in flight**" — and a change can be perfectly
correct in its final state while being unsafe halfway there.

```
⌘  python3 scripts/run_pair_verification.py --explain
```

### ◆ Predict #3 — reopen Prediction #1

You sealed an answer at the Start step, blind. You now know the seam and the specification.

> **Would you change your answer? What did you not know when you made it?**

Write the revision next to the original. Keep both — the gap between them is the lesson.

*What you just decided: who changes first, what each agent may touch, and when it must stop.
Every boundary you drew here is a boundary the agents cannot cross in Stage 4.*

### ✓ Done when

```
  [ ] validate_plan.py reports READY
  [ ] each brief names its repository, its ACs, its excluded areas and its stop conditions
  [ ] the rollout order is written down WITH the reason it is safe in that order
  [ ] Prediction #3 sits next to Prediction #1, both still legible
```

```
⌘  python3 .claude/scripts/validate_plan.py
⌘  /hand-off
```

---

```
┌─────────────────────────────────────────────────────────────── 25 min ──┐
│  STAGE 4  ·  BUILD & VALIDATE                                            │
│  Build the Bounded Slice                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

*Now the AI touches code. Everything you decided in Stages 0–3 is about to be tested.*

**Concept** — bounded agent execution and deterministic guardrails
**You leave with** — a remediated seam, built inside boundaries you set

> AI generates inside **tests, rules, gates, tool permissions and contract checks** — not inside a
> conversation.

### What each agent receives — and what it does not

```
   ✓  GIVEN                              ✗  NOT GIVEN
   ─────────                             ────────────
   the validated specification           the other repository
   its agent contract                    this action guide
   the criteria that contract owns       your reasoning about the seam
   that repository's CLAUDE.md           the other agent's return
```

One scoped implementation context per repository. The exclusions are the design, not an oversight.

### You do not write an implementation prompt

The contracts you wrote in Stage 3 *are* the instruction. A prebuilt agent —
`repo-implementer` — executes one contract against one repository. You authorise; you do not
re-describe the work in prose.

That is the point of having written a contract. A prompt that also specifies the diff is a slower,
more expensive way of writing the diff yourself: you are buying the agent's ability to find an
implementation, and if you hand it one you have bought nothing and still have to review it.

### ▶ Your turn — authorise both, then read what comes back

Dispatch both implementers, one per repository, each with only its own contract.

**The agent runs the verification, not you.** Its contract requires it to run that repository's
full Maven build before returning, and to report the command and the result it actually saw. You
are not asked to re-run the same command by hand — you are asked to read two returns and judge
whether they are consistent with each other and with the contracts.

If you want to audit an agent rather than trust it, re-run its command deliberately and say that is
what you are doing. That is a different activity from mechanical repetition.

> **A return with `FILES_CHANGED: none` is a real outcome, not a failed one.** Where a contract
> declared `NO_DIFF_EXPECTED: true`, the job was to establish that the owned criteria are already
> satisfied and show the evidence. Some of the best returns you get today will contain no diff.

### Expected return from each agent

```
   Files changed         Verification run
   ACs addressed         Open concern
   Tests added           No-scope-expansion confirmation
```

### Three things that will actually happen

> ⚠ **You will be tempted to dispatch one agent for both repositories.** Don't. The moment you
> give one agent both repos, you have re-created the visibility problem you spent Stage 1 avoiding.
> One agent per repository, in the rollout order you decided in Stage 3.

> ⚠ **An agent will offer to fix something in the other repository.** Refuse it. That is the seam,
> and the seam is yours. An agent that can reach across the boundary has no way to know what it
> would break, because it cannot see the other side.

> ⚠ **An agent will find nearby code that looks reusable and unfinished.** It compiles. It shares
> infrastructure with the refund path. It looks abandoned mid-change.
>
> **Adjacency is not authorisation.** If it is out of scope, the correct action is no diff plus a
> recorded reason.

### Verify as you go

```bash
cd pgs-tta && mvn verify
cd ../pgs-payment-processor && mvn verify
```

```
   ╭──────────────────────────────────────────────────────────────╮
   │  Both green does not mean done.                              │
   │  That is the entire premise of this lab.                     │
   ╰──────────────────────────────────────────────────────────────╯
```

Writes follow the rollout order you decided in Stage 3.

*Both repos are green. You are about to find out if that means anything.*

### ✓ Done when

```
  [ ] both returns carry a verification command AND the result the agent observed
  [ ] every changed file traces to a criterion its contract owns
  [ ] no agent was given both repositories
  [ ] nothing out of scope was implemented — and where you refused, you wrote down why
```

Both green is the *entry* condition for Stage 5, not the finish line.

```
⌘  /hand-off
```

---

```
┌──────────────────────────────────────────────────────────────── 20 min ──┐
│  STAGE 5  ·  VALIDATE THE PAIR                                           │
│  Prove the Pair                                        ★ NEVER CUT       │
└──────────────────────────────────────────────────────────────────────────┘
```

*Something that has never seen your work is about to judge it. You do not get to argue back.*

**Concept** — fresh-context validation and independent judgment
**You leave with** — evidence you did not produce, and rulings on what it found

> **Separate creation from judgment.**

If Stage 4 runs long, the facilitator will apply a checkpoint and move the room here anyway.
Arriving with part of the work done and seeing what independent judgment catches is a far
better session than finishing the code and never finding out. Nobody is counting your fixes.

### ◆ Predict #4 — what did you miss?

> Both repositories are green and you believe the work is done.
> **Name one thing a fresh validator or the pair harness will catch that your green builds did not.**

One thing, written down, before you run either. Be specific.

### 1 · Deterministic evidence first

```
⌘  python3 scripts/run_pair_verification.py
```

This answers the only question that matters: **are the two services actually in agreement?** Each
failure names the disagreement in its own message.

```
   THE COMPATIBILITY MATRIX

   previous consumer ──► previous producer     baseline. The world before this change.
   previous consumer ──► current producer      MUST SUCCEED
   current consumer  ──► previous producer     MUST BE SHOWN TO FAIL
   current consumer  ──► current producer      the intended final state
```

That third row is the interesting one. The test **passes by detecting the incompatibility** — it
is diagnostic, not permanently red. It is how the rollout order stops being an assertion
somebody made and becomes something you can point at.

### 2 · Then independent judgment

```
⌘  python3 .claude/scripts/build_validator_brief.py
```

The brief is assembled **mechanically** from an allowlist: the specification, both diffs, the
ledger, the pair results, the plan, the scope documents.

It contains no chat history and no builder rationale — **not because the script is careful about
leaving them out, but because it has no way to reach them.** That is a structural guarantee rather
than an instruction to be discreet, which is exactly why it is a script and not a prompt.

Dispatch the fresh `code-to-spec-validator` against it. It has read and test tools and **no write
tools**, so it cannot quietly repair what it finds. It never saw your session, so it cannot
inherit your confidence in your own work.

> **Expect the validator to report FAIL even when the harness is green.** The validator works
> from the diff — it can only see what *changed*. Any behaviour that was already correct before
> you started is invisible to it, so it will report criteria as unmet that are in fact
> satisfied by code you never touched.
>
> That is not a bug in the validator; it is the cost of judging from a diff, and knowing it is
> part of reading any review honestly. Where the validator and the harness disagree about a
> criterion, the harness is the ground truth — it executes the behaviour, the validator only
> reads the change. Disposition those as `PRE-EXISTING`, and say which harness test is your
> evidence.

### 3 · Disposition every finding

In `docs/finding-dispositions.md`:

| Finding | Evidence | In scope? | Material? | Disposition | Rationale |
|---|---|---|---|---|---|

> ⚠ **A validator finding does not authorise a code change.**
>
> Some findings are correct and out of scope. Some are simply wrong. Some are right but
> immaterial. Sorting them is the judgment this stage exists to build — and you are graded on the
> disposition, **not** on agreeing with the validator.

### 4 · If the harness is RED and findings are material — loop back

Return to Stage 4: fix the defect, re-run `mvn verify`, then come back here and restart from
step 1. Watch the harness count — if the number of failing tests goes down, you are converging.
If it stays flat or the validator produces new material findings, something real is still broken.

**Reveal:** compare against Prediction #4.

### ✓ Done when

```
  [ ] run_pair_verification.py has been run and you know its result
  [ ] the validator brief was generated and a fresh validator judged it
  [ ] every finding has a disposition AND a rationale
  [ ] you can say what the harness proves and what it does not
```

```
⌘  /hand-off
```

### ⏸ Q&A pause — 3 min

---

```
┌──────────────────────────────────────────────────────────────── 6 min ──┐
│  STAGE 6  ·  REVIEW, HANDOFF & CLOSE                                     │
│  Transfer the Learning                                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

*You made a prediction blind, revised it informed, and now have evidence. How wrong were you?*

**Concept** — context handoff, evidence, and the learning loop

### 1 · Reopen Prediction #1

You have now answered the rollout question three times:

```
   the Start step   blind        ─────►   Stage 3   informed   ─────►   Stage 5   evidenced
```

Compare all three. What made the difference — and would you have found it without the
compatibility matrix?

### 2 · Record one reusable practice

One sentence in `docs/workflow-tracker.md`: something about multi-repository AI work you would do
again on Monday, on your own code, with your own team.

### 3 · Close out

### ✓ Done when

```
  [ ] Predictions #1, #3 and your Stage 5 answer are all visible together
  [ ] one reusable practice is written in docs/workflow-tracker.md
  [ ] the journey trail exists
```

```
⌘  /hand-off
```

Then confirm `.claude/journey/` holds a real event trail.

### What you should be able to say at the end

> When an AI-assisted change spans repositories, I first establish the authority and the seam. I
> scope agents to local evidence instead of giving one context everything. I reconcile their claims
> myself, make the specification buildable, define agent contracts and rollout constraints, let AI
> execute only inside those boundaries, and then prove the pair with independent evidence before I
> accept the change.

### And what it does not mean

The lab proves the represented seam **locally**. It does not claim the wider PGS refund capability
is production-ready, and pair verification does not replace integration testing or release
governance.

---

## The parking lot

Environment problems, deep domain questions, and anything that would derail thirty people go
here. The facilitator picks them up at the Q&A pauses or after the session.

Nothing is lost by parking something. A room of thirty loses a great deal by debugging one laptop
together.

## If you fall behind

Say so, early.

Stage 5 is the payoff and there are facilitator checkpoints for exactly this situation. There is
no prize for finishing the code — there is a great deal of value in reaching independent
validation and finding out what it catches.

```
   ╭──────────────────────────────────────────────────────────────────────╮
   │  Two outcomes that are wins, not failures:                           │
   │                                                                      │
   │    ▸ "No diff, and here is the evidence it was already correct."     │
   │    ▸ "We do not know, and we refused to invent an answer."           │
   ╰──────────────────────────────────────────────────────────────────────╯
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `verify_setup.py` does not end with "Setup complete" | A prerequisite is missing, or the first Maven build has not resolved yet | Read the first `[FAIL]` line — it names the tool. A cold Maven cache can take several minutes; let it finish before concluding anything |
| `mvn verify` fails in a repository you have not touched | You are mid-edit, or an earlier agent left the tree inconsistent | `git -C <repo> diff` to see what changed. `git -C <repo> checkout -- .` returns that repository to its starter commit |
| The pair harness cannot resolve `pgs-tta` or `pgs-payment-processor` | The services were not installed to your local Maven repository, or only one was | Use `python3 scripts/run_pair_verification.py` rather than calling Maven in the harness directly — it installs both, in the required order |
| `validate_spec.py` stays at DRAFT and you cannot see why | A failing check is worded generally | Every `[FAIL]` line states what is missing. Fix them one at a time and re-run; the count moves |
| The write gate blocked a file you believe you need | It is authority rather than workspace | Read it instead. If you are convinced the change is genuinely required, that is a finding to raise, not a file to force |
| An agent asks to change the other repository | Its brief did not bound it, or it is guessing across the boundary | Refuse, and tighten the brief's excluded areas. The seam is yours |
| The validator reports FAIL while the harness is green | The validator judges from the diff and cannot see code that was already correct | Disposition it `PRE-EXISTING` and name the harness test that is your evidence |
| `.claude/journey/` is empty after `/lab` | Journey recording did not start | Re-run `/lab`. Do this at the Start step — it cannot be reconstructed later |

## If you run out of time

Time-boxes, so a stall does not cost you the stage that matters:

- **Stage 2 will not reach READY.** Take the best specification you have, write the remaining gaps
  into Open Questions, and move on. A specification with honest gaps is workable; a stage you
  never left is not.
- **Stage 4 is unfinished.** Stop where you are and go to Stage 5 anyway. Partial work judged
  independently teaches more than complete work nobody checked.
- **A repository is beyond recovery.** `git -C <repo> checkout -- .` returns it to the starter
  commit. `python3 scripts/verify_setup.py --reset` rebuilds both from scratch, and will tell you
  exactly what it is about to discard before it does it.
- **You are simply behind.** Say so. There are facilitator checkpoints for this and using one
  costs you nothing.

## If you finish early

Two things worth your time, in this order.

**1 · Break the write gate.** [`docs/CHALLENGE.md`](docs/CHALLENGE.md)

You have met the gate by now — it stopped you from editing something. So break it. It is
breakable, and finding out how is more instructive than being told. When you have a bypass, the
question that matters is not the technique but this one: *if a control can be routed around, what
is actually protecting the thing it guards?*

Revert anything you actually change. A protected file left modified fails the grading checks and
shows up in the anti-gaming report — which is the point, but you would rather demonstrate it
deliberately than by accident.

**2 · Write the brief you would use on Monday.** Take one of your Stage 3 agent briefs and rewrite
it against a seam in a repository you actually own. That is the artifact worth leaving with.

## Reference

| Document | What it answers |
|---|---|
| [`docs/ESSENTIAL_OUTCOMES.md`](docs/ESSENTIAL_OUTCOMES.md) | What is graded |
| [`docs/TERM_CARD.md`](docs/TERM_CARD.md) | The ten terms |
| [`docs/SPEC_COMPLETENESS_BAR.md`](docs/SPEC_COMPLETENESS_BAR.md) | When a spec is good enough |
| [`docs/SCENARIO_GROUNDING.md`](docs/SCENARIO_GROUNDING.md) | Real PGS vs. lab vs. planted |
| [`docs/PGS_DECISIONS.md`](docs/PGS_DECISIONS.md) | Every decision and its source |
| [`specs/OUT_OF_SCOPE.md`](specs/OUT_OF_SCOPE.md) | What must not be built |
| [`specs/NON_NEGOTIABLES.md`](specs/NON_NEGOTIABLES.md) | What holds regardless |
| [`docs/CHALLENGE.md`](docs/CHALLENGE.md) | Bonus: break the gate |
