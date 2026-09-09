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

### The three goals of this lab

| Goal | Across the lab |
|---|---|
| **Build shared intuition** | Develop a common engineering instinct for reasoning across repository, service, and agent boundaries. |
| **Standardize shared language** | Give recurring engineering situations a shared vocabulary so teams describe and reason about them consistently. |
| **Change engineering behavior** | Move from asking AI to solve a change end-to-end toward establishing evidence, defining boundaries, executing inside them, and verifying independently. |

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
 STAGE                              CONCEPT                           Takeaways
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

```
bash .claude/scripts/run scripts/verify_setup.py
```

Must end with **"Setup complete"**. If it does not, flag it now — not at minute forty.

### Update the workbench

Before running preflight, ensure your workbench plugin is on the version required for this lab:

```
/plugin marketplace update mastercard-workbench
```
To verify :
```
/reload-plugins
```
```
/plugin list
```

The final `/plugin list` confirms the update applied. If the list is empty or shows an unexpected version, ask the facilitator before continuing.

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

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | Establish authority and boundaries before asking AI to act. If authority is unclear, every downstream decision inherits that ambiguity. |
| **Standardize Language** | Use `context boundary`, `source authority`, `non-negotiable`, and `out of scope` consistently to distinguish what an agent may know, what governs the decision, and what it is not authorised to change. |
| **Behavior Change** | Before delegating work, explicitly establish what the agent may see, what it may change, and which source has authority when evidence conflicts. |

### 1 · Start the lab

Run:

```
/lab
```

`/lab` starts recording, prints the six objectives, and **stops**. That is all it should do. If
your session instead starts reading the two services or dispatching agents, stop it: Stage 1 is
yours to run, and a ledger handed to you finished is a ledger you did not reconcile.

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

Run:

```
/hand-off
```

---

```
┌─────────────────────────────────────────────────────────────── 17 min ──┐
│  STAGE 1  ·  AUDIT CONTEXT                                               │
│  Map the Seam                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

*Two repository audits can each be locally reasonable and still expose disagreement at the service
boundary.*

**Concept** — scoped sub-agents and parallel delegation
**You leave with** — two independent repository audits reconciled into one context ledger

> **Agents investigate locally. You reconcile across the service boundary.**

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | Local correctness does not establish correctness at a service boundary. Cross-repository conclusions require evidence from both sides. |
| **Standardize Language** | Use `scoped sub-agent`, `repository evidence`, `service boundary`, `context ledger`, and `UNKNOWN` consistently to distinguish local findings from cross-repository conclusions that have or have not been established. |
| **Behavior Change** | Investigate each repository in a bounded context, then reconcile the evidence across the boundary rather than asking one agent to infer the whole system. |

### Why

The evidence for the TTA → Payment Processor interaction is distributed across two repositories.

You will audit each repository independently, compare the evidence returned from both sides, and
make the cross-repository decisions yourself.

### ◆ Predict #2 — identify the blind spot

Before you begin:

> What are two things an auditor restricted to one repository could not establish about the other
> side of the service boundary?

Write them down. You will revisit this after both audits return.

### Step 1 · Parallel repository audit

The `repo-auditor` sub-agent comes from the workbench plugin — as does every agent, command and
skill this lab uses. There is nothing to install or author here. Its constraints are its own; you
supply only the two targets.

Run this once in the parent Claude session:

```
Spawn one instance of @"workbench:repo-auditor (agent)" for @pgs-tta/
and, in parallel, a second instance for @pgs-payment-processor/.

Return the two audit results separately. Do not reconcile them.
```

**⌂ You'll see** — two separate `repo-auditor` results return to the parent Claude session, one for
each repository. Wait until both have returned before moving on.

### Step 2 · Reconcile the two audits

[`docs/context-ledger.md`](docs/context-ledger.md) already exists in the starter repository. Use it
as it is — do not create a new ledger, and do not change its structure.

Once both audit results are available, update [`docs/context-ledger.md`](docs/context-ledger.md).

**The auditors provide the evidence. You make the cross-repository decision.**

If the available authority does not support a decision, keep it `UNKNOWN`. Do not replace missing
authority with a plausible assumption.

### Review the evidence

Confirm that:

```
  [ ] both repositories were audited independently
  [ ] each audit is supported by repository evidence
  [ ] reconciliation started only after both audit results were available
  [ ] every material disagreement is resolved by evidence or recorded as UNKNOWN
  [ ] docs/context-ledger.md reflects your decisions
```

**Reveal:** return to your prediction — what could one auditor not have established from its
repository alone?

*That is the reason for separating the two audit contexts: each agent provides a local
evidence-backed view, while the cross-repository decision remains explicit.*

### ✓ Done when

Stage 1 is complete when:

- both repository audits have returned;
- material disagreements have been reconciled;
- unresolved items are explicitly recorded as `UNKNOWN`; and
- [`docs/context-ledger.md`](docs/context-ledger.md) reflects the evidence and your decisions.

Run:

```
/hand-off
```

---

```
┌─────────────────────────────────────────────────────────────── 16 min ──┐
│  STAGE 2  ·  AUTHOR & VALIDATE THE SPEC                                  │
│  Make the Spec Buildable                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

*Some of what you found in Stage 1 the available authority can settle. Some of it it cannot. Both
belong in the specification, stated differently.*

**Concept** — spec-as-context and readiness gates
**You leave with** — a build-ready specification for the resolved scope, with unresolved authority
kept explicit

> **A specification that says "we do not know this yet, and we are not building it" is more
> finished than one that guessed.**

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | A buildable specification separates what is known from what still requires authority. Unknown does not mean permission to choose. |
| **Standardize Language** | Use `acceptance criterion`, `observable`, `testable`, `open authority item`, `authorized scope`, and `READY_FOR_BOUNDED_BUILD` consistently to distinguish requirements that are ready to implement from decisions that remain unresolved. |
| **Behavior Change** | Convert evidence-backed decisions into observable, testable requirements. Keep unresolved authority explicit and outside implementation rather than allowing the model to fill the gap. |

### Why

Stage 1 established the evidence across TTA and Payment Processor.

Stage 2 turns the resolved evidence into explicit, observable, testable requirements. Items the
available authority cannot resolve remain open and are not authorised for implementation.

### Step 1 · Check the specification

Run:

```
/check-spec
```

The gate scores ten structural readiness checks against the rules in
[`docs/SPEC_COMPLETENESS_BAR.md`](docs/SPEC_COMPLETENESS_BAR.md). It checks structure — sections,
identifiers, observable outcomes, testable constraints, and whether what remains unknown is
recorded rather than quietly answered.

It does not decide domain correctness. A well-formed requirement can still be wrong.

The failing checks are your editing queue.

**⌂ You'll see** — a verdict, and separately, any authority the material does not settle:

```
  [PASS] required sections present                     all present
  [FAIL] acceptance criteria describe observable ...   unobservable phrasing: handled correctly
  [FAIL] idempotency is testable for the authorised    does not state: what carries the retry
         scope                                         identity; ...
  ...

  5/10 structural readiness checks  ->  DRAFT
```

Because the gate is deterministic, the same specification produces the same result. Model-generated
output varies; this does not.

### Step 2 · Harden the specification

Run:

```
Using @docs/context-ledger.md, the spec's source authority, and the latest
/check-spec failures, harden @specs/refund-seam-phase1.spec.md.

Make only resolved, evidence-backed requirements observable and testable.
Resolve conflicts only with authority; keep unresolved items open and out of
implementation scope.

Update only the specification.
```

The decision rule, for every item:

```
   Supported and resolved  ->  make it buildable
   Conflicting evidence    ->  resolve only with authority
   Unresolved              ->  keep it open
```

An unresolved item costs you nothing at the gate, provided it stays recorded and outside the
implementation boundary. Inventing an owner or a derivation to turn a check green is the one move
this stage exists to prevent.

**Optional — evaluate a requirement of your own**

If you want to add a requirement or constraint, test it against the authority first, in its own
turn:

```
Evaluate this requirement or constraint against @docs/context-ledger.md
and the source authority in @specs/refund-seam-phase1.spec.md:

"<add your requirement or constraint>"

If supported, add it as an observable, testable requirement.
If the available authority does not support it, leave the specification
unchanged and explain what is missing.

Update only @specs/refund-seam-phase1.spec.md.
```

### Step 3 · Re-run the readiness gate

Run:

```
/check-spec
```

Target:

```
  10/10 structural readiness checks  ->  READY_FOR_BOUNDED_BUILD

  OPEN AUTHORITY ITEMS
  - ownership undecided: Retry identity stability (OQ-3)

  These items are not authorised for implementation.
```

Open authority items do not reduce the score. They are reported so the boundary stays visible —
what is being built, and what is explicitly not. If items remain open, that is a finished outcome,
not an incomplete one.

`READY_FOR_BOUNDED_BUILD` means the resolved scope is well-formed enough to build against. It does
not mean a machine decided the payment behaviour is correct.

> **The gate validates structure. Engineers validate meaning.**

### Review the specification

Before moving on, confirm:

```
  [ ] every requirement being implemented is evidence-backed
  [ ] acceptance criteria are observable and testable
  [ ] unresolved authority items remain explicit
  [ ] unresolved items are outside the implementation scope
  [ ] you know whether each acceptance criterion needs evidence from TTA,
      Payment Processor, or both
```

That last one is what Stage 3 divides into repository-specific agent contracts, so it is worth
answering now rather than discovering it there.

### ◆ Reveal

Compare the specification you started with against the version that now reports
`READY_FOR_BOUNDED_BUILD`.

Where was the original wording forcing an implementation agent to make a decision the specification
had not actually made?

That gap is the reason for treating the specification as part of the agent's working context rather
than as documentation written after implementation.

### ✓ Done when

```
  [ ] /check-spec reports 10/10 READY_FOR_BOUNDED_BUILD
  [ ] resolved requirements are explicit, observable, and testable
  [ ] resolved requirements trace to available authority
  [ ] unresolved authority items remain explicitly open
  [ ] unresolved items are excluded from implementation scope
```

Run:

```
/hand-off
```

### ⏸ Q&A pause — 4 min

Use this pause for questions about the specification, authority, acceptance criteria, or the
readiness gate.

Environment-specific issues go to the **parking lot** so they do not consume the shared lab time.

---

```
┌─────────────────────────────────────────────────────────────── 16 min ──┐
│  STAGE 3  ·  PLAN ACROSS REPOSITORIES                                    │
│  Plan and Brief                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

*Turn the validated specification into an executable plan for two bounded implementation agents.*

**Concept** — cross-repository planning and bounded agent contracts
**You leave with** — one orchestration plan and two repository-specific implementation briefs

> **Plan only the scope authorised in Stage 2. Open authority items remain outside implementation.**

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | Cross-repository planning is not task decomposition alone. It must preserve responsibility, boundaries, dependencies, verification, and rollout constraints before implementation begins. |
| **Standardize Language** | Use `orchestration plan`, `implementation brief`, `acceptance criteria owned`, `working boundary`, `stop condition`, `NO_DIFF_EXPECTED`, and `rollout order` consistently to describe who is responsible for what, where an agent may act, and when it must stop. |
| **Behavior Change** | Turn the authorised specification into bounded repository-specific contracts before implementation begins. Do not turn an open authority item into an agent task. |

### What you carry forward

[`specs/refund-seam-phase1.spec.md`](specs/refund-seam-phase1.spec.md)

The specification defines what must be true. Stage 3 defines how that authorised work is divided,
bounded, verified, and sequenced across the two repositories.

### Produce three artifacts

```
   docs/plans/orchestration-plan.md
   docs/agent-briefs/tta-implementation-brief.md
   docs/agent-briefs/processor-implementation-brief.md
```

**The orchestration plan records:**

```
   in-scope acceptance criteria
   repository responsibility
   cross-repository dependencies
   rollout order and rationale
   Stage 2 open authority items that remain excluded
```

**Each implementation brief contains:**

```
   Repository                     Excluded areas
   Objective                      NO_DIFF_EXPECTED: true | false
   Acceptance criteria owned      Verification required
   Authoritative context          Stop conditions
   Allowed repository scope
```

Reference acceptance criteria by ID rather than rewriting them. The same criterion may appear in
both briefs when both repositories must provide local evidence for it. `NO_DIFF_EXPECTED: true`
still requires verification.

Every brief carries this stop condition:

> *If completing the assigned work requires behaviour that the validated specification does not
> authorise, stop and report it rather than choosing the behaviour.*

### Planning rules

```
   1  Plan only the resolved Stage 2 scope.
   2  Every in-scope acceptance criterion must be assigned.
   3  Open authority items must not become implementation work.
   4  Keep each implementation agent inside its assigned repository.
```

The orchestration plan must record the proposed rollout order and rationale based on the
compatibility constraints already established in the specification. Stage 3 records the plan;
Stage 5 verifies the pair.

### Optional — a planner assist

```
Using @specs/refund-seam-phase1.spec.md, propose a repository split and
rollout sequence for only the authorized implementation scope.

Keep Stage 2 open authority items excluded.

Return a planning proposal only. Do not write code or resolve authority gaps.
```

Use the proposal as input. The final plan and briefs remain yours.

### Validate the plan

```
/check-plan
```

It validates plan structure:

```
   both repositories are represented
   every in-scope AC is assigned
   no unsupported AC was introduced
   open Stage 2 authority items remain excluded
   repository boundaries are defined
   verification and stop conditions are present
   rollout order and rationale are recorded
```

**⌂ You'll see**

```
  [PASS] both repositories are represented
  [PASS] rollout order and rationale are present
  [FAIL] every in-scope acceptance criterion is assigned    missing: AC-4
  ...
  N/M structural checks  ->  DRAFT
```

Use any failures as the editing queue and rerun `/check-plan` until it reports `READY`.

> **The gate validates plan structure. Engineering judgment owns the plan.**

### ✓ Done when

```
  [ ] /check-plan reports READY
  [ ] every in-scope acceptance criterion is assigned
  [ ] Stage 2 open authority items remain outside implementation scope
  [ ] both briefs define scope, exclusions, verification, and stop conditions
  [ ] rollout order and rationale are recorded
```

Run:

```
/hand-off
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

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | Agent autonomy is useful only inside explicit scope and verification boundaries. The contract defines the authorised outcome and constraints; the agent determines the implementation. |
| **Standardize Language** | Use `bounded execution`, `repo-implementer`, `verification evidence`, `FILES_CHANGED`, and `STOP_REQUIRED` consistently to distinguish authorised execution, observed results, and conditions where the agent must stop rather than improvise. |
| **Behavior Change** | Dispatch one bounded implementation context per repository and judge the return against its contract and verification evidence, not against how convincing the agent sounds. |

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

### ⌂ You'll see — the return shape from each agent

```
   REPOSITORY:                       VERIFICATION_COMMAND:
   ACCEPTANCE_CRITERIA_ADDRESSED:    VERIFICATION_RESULT:
   FILES_CHANGED:                    UNRESOLVED:
                                     STOP_REQUIRED:
```

Read them side by side. The two questions worth asking: does each return only touch the repository
its contract named, and does `VERIFICATION_RESULT` match what the agent says it did? A green claim
that does not match its own build output is worse than a red one, because it removes the reason
anyone would look.

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

Run:

```
/hand-off
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

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | Two green repositories do not prove that the service boundary is correct. Repository verification and independent judgment answer different questions. |
| **Standardize Language** | Use `pair verification`, `fresh context`, `independent validator`, `PASS`, `FAIL`, `UNVERIFIED`, and `finding disposition` consistently to distinguish deterministic seam evidence from independent engineering judgment. |
| **Behavior Change** | Separate creation from judgment: verify the pair independently, then use fresh validators and disposition every finding rather than trusting the implementation context or individual green builds alone. |

### ◆ Predict #4 — what did you miss?

> Both repositories are green and you believe the work is done.
> **Name one thing a fresh validator or the pair harness will catch that your green builds did not.**

One thing, written down, before you run either. Be specific.

### 1 · Deterministic evidence first

Run:

```
/verify-pair
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

### 2 · Then independent judgment — two validators, two briefs

Run:

```
/build-validator-briefs
```

That writes **one brief per repository**. Each carries the specification, both scope documents,
that repository's contract, its diff and its verification evidence — and none of the other
repository's implementation.

Dispatch **two fresh validators in parallel**, one brief each. Each has read and test tools and
**no write tools**, so neither can quietly repair what it finds. Neither saw your session, so
neither can inherit your confidence in your own work.

**Why not one validator holding both diffs.** A reviewer given the whole change stops judging *this*
repository against *its* criteria and starts reviewing the change as a whole — which is the pair
harness's job, and the harness already answered it deterministically in step 1. Splitting the
evidence is what keeps the two judgements independent, and it is why each contract had to own
acceptance criteria back in Stage 3.

**⌂ You'll see** — findings in this shape, from each validator:

```
REPOSITORY: <the repo that brief covered>
AC:         <a criterion that repository's contract owns>
VERDICT:    PASS | FAIL | UNVERIFIED
FINDING:
EVIDENCE:
```

Three verdicts, not two. **`UNVERIFIED` is a real answer** — it means the validator could not settle
the criterion from what it was given, usually because judging it would require the other side. That
is the correct outcome, not a softer way of saying FAIL, and treating it as a failure would teach
exactly the guessing this lab exists to prevent.

> **`FILES_CHANGED: none` is not automatically a failure.** Where a contract declared
> `NO_DIFF_EXPECTED: true`, the question is whether the owned criteria were already satisfied. A
> validator that marks that FAIL has judged the diff rather than the repository.

### 3 · Disposition every finding

In `docs/finding-dispositions.md`:

| Finding | Evidence | In scope? | Material? | Disposition | Rationale |
|---|---|---|---|---|---|

> ⚠ **A validator finding does not authorise a code change.**
>
> Some findings are correct and out of scope. Some are simply wrong. Some are right but
> immaterial. Sorting them is the judgment this stage exists to build — and you are graded on the
> disposition, **not** on agreeing with the validator.

### 4 · If something material is broken — the facilitator decides whether to repair

Core Stage 5 ends after the pair proof, the two validators, and your dispositions. **Remediation is
not part of it.**

If a finding is material and marked `FIX_NOW`, repair only when the room is on time *and* the
facilitator opens the path. One targeted cycle, maximum:

```
  re-launch the implementer for that repository only, with its existing contract,
  the finding, and the relevant pair evidence
        │
  it makes the targeted repair and runs that repository's verification
        │
  re-run the pair proof, then re-run only the affected repository's validator
        │
  update the disposition
```

Otherwise: record the finding, use the facilitator's checkpoint, and go to Stage 6 with it open.

**An open finding you understood and recorded is a better outcome than a rushed fix you did not
verify.** Stage 5 is the judgment anchor; it does not become a repair queue because Stage 4 ran
long.

**Reveal:** compare against Prediction #4.

### ✓ Done when

```
  [ ] run_pair_verification.py has been run and you know its result
  [ ] the validator brief was generated and a fresh validator judged it
  [ ] every finding has a disposition AND a rationale
  [ ] you can say what the harness proves and what it does not
```

Run:

```
/hand-off
```

### ⏸ Q&A pause — 4 min

---

```
┌──────────────────────────────────────────────────────────────── 6 min ──┐
│  STAGE 6  ·  REVIEW, HANDOFF & CLOSE                                     │
│  Transfer the Learning                                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

*You made a prediction blind, revised it informed, and now have evidence. How wrong were you?*

**Concept** — context handoff, evidence, and the learning loop

| Engineering lens | This stage establishes |
|---|---|
| **Build Intuition** | The reusable asset is the evidence-backed workflow, not the prompt or model conversation that produced one implementation. |
| **Standardize Language** | Use `handoff`, `evidence trail`, `workflow tracker`, `open item`, and `reusable practice` consistently to describe what must survive beyond the current agent session. |
| **Behavior Change** | Preserve decisions, evidence, verification results, and unresolved items so the next engineer or agent can continue from an explicit handoff instead of reconstructing reasoning from conversation history. |

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

Run:

```
/hand-off
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
| The pair harness cannot resolve `pgs-tta` or `pgs-payment-processor` | The services were not installed to your local Maven repository, or only one was | Use `bash .claude/scripts/run scripts/run_pair_verification.py` rather than calling Maven in the harness directly — it installs both, in the required order |
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
  commit. `bash .claude/scripts/run scripts/verify_setup.py --reset` rebuilds both from scratch, and will tell you
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
