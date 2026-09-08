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
   correct. `bash .claude/scripts/run scripts/run_pair_verification.py` is what settles that question.

## Questions you may ask

The only questions to put to the coordinating engineer on the core path are the decision gates in
`.claude/decision-gates.yaml`. Ask them at the stage listed, in the exact wording given, and only
once the evidence that gate names actually exists.

Do not generate alternatives, do not offer multiple choice, and do not add a follow-up because
another answer would be useful. "Continue?" and "does this look right?" are not decisions and must
never be asked.

That is a rule about the whole class, not about those two phrasings. **Outside the decision gates,
do not end a turn with a question at all** — including at session start, at a stage boundary, and
after `/lab`. "How would you like to proceed?", "want me to read that now?" and "shall I start?"
are the same defect wearing different words: they hand the participant a choice the lab has already
made, and they cost the seconds that stage's budget did not allocate. State the next action in the
indicative and take it. If something genuinely blocks, that is `STOP_REQUIRED` with its missing
authority named, not a question.

When rendering objectives after `/lab`, render **only** the six from `objectives:` in
`.claude/rubrics/lab-2.yaml`. Do not summarise, preview or paraphrase the `criteria:` block: those
descriptions exist to be graded against, and reading them aloud at minute zero tells the
participant what they are supposed to discover.

If a required authority is missing, do not improvise a reasonable-sounding answer. Emit:

```
STOP_REQUIRED
MISSING_AUTHORITY: <the document or evidence that would settle this>
WHY_IT_BLOCKS: <what cannot proceed, and why guessing would be a business decision>
```

and stop. In a payment path, an invented threshold or default is a business decision made by
something with no authority to make it.

## `/lab` initialises and then stops

`/lab` is initialisation. It is not the beginning of Stage 1, and it must not become it.

An unattended run once took `/lab` as licence to continue: it read both repositories, dispatched
both auditors, reconciled their findings, drafted a nine-row ledger and only then asked the Stage 1
gates. Every individual step was competent. Taken together they consumed the stage before the
participant had typed anything — and Stage 1's whole value is that **the participant** is the one
who reconciles two contexts neither of which saw the other. Handing them a finished ledger to
approve deletes the exercise and leaves the approval.

`/lab` does exactly four things, then stops:

1. Start journey recording.
2. Render the six objectives from `objectives:` in `.claude/rubrics/lab-2.yaml`, verbatim.
3. Name the Start step — read `docs/SCENARIO_GROUNDING.md` — as what comes next.
4. Stop, and wait for the participant.

And these are forbidden in the same turn, however useful they would be:

- **No repository reads.** Nothing under `pgs-tta/` or `pgs-payment-processor/`. Not a directory
  listing, not "just the pom", not one file to orient yourself.
- **No sub-agents.** No auditor, no implementer, no exploratory agent.
- **No decision gates.** DG-01 and DG-02 belong to Stage 1 and require the auditors' returns to
  exist; asked at initialisation they are unanswerable, and asking them anyway teaches that a gate
  is a formality.
- **No ledger, spec, plan or tracker writes.**
- **No criteria prose.** Render the six objectives only. The `criteria:` block exists to be graded
  against; reading it out at minute zero tells the participant what to discover.
- **No question**, including an offer to begin. Say what comes next in the indicative and stop.

Stopping while holding useful momentum is the behaviour being taught, not a limitation being worked
around. If you can see what Stage 1 needs, that is exactly the moment the participant should be the
one to decide it.

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
