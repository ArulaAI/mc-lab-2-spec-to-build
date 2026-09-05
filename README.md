# Lab 2 — One Refund Across a Service Boundary

A 120-minute hands-on lab on using AI safely when a money-moving change spans more than one
repository, and the decisions that matter live at the seam between them.

Lab 1 taught governing one AI-assisted change inside one repository. This lab is about
orchestrating several scoped AI contexts across a service boundary while the engineer keeps
authority over the seam.

**Participants start with [`LAB_ACTION_GUIDE.md`](LAB_ACTION_GUIDE.md).** This file covers
architecture and setup.

---

## The problem

A merchant refund crosses the **TTA → Payment Processor** boundary. Two repositories. Both build.
Both have passing tests. Neither is obviously broken.

They still do not agree with each other.

```
WSAPI  ->  TTA  ->  Payment Processor  ->  CPC  ->  Injection  ->  LCS API  ->  DCF
           |________________________|
                represented here          not implemented in this lab
```

Correctness across a service boundary lives in the relationship between two implementations, not
inside either one — which is why the central fact of the lab is:

> **Repo A green + Repo B green ≠ pair correct.**

---

## Prerequisites

- **JDK 17 or newer.** A 21 JDK compiling to the Java 17 target is the documented PGS pattern and
  is what this lab is built and tested against.
- **Maven 3.9+**
- **Python 3.9+**, with PyYAML for the grader (`python3 -m pip install pyyaml`)
- **Git**
- The `workbench` plugin, for `/lab`, `/journey`, `/hand-off`, the planner and the
  `code-to-spec-validator`
- A warm `~/.m2`. The lab makes no network calls at runtime, but a first Maven build on a cold
  cache resolves dependencies like any other.

## Setup — before session day, not during it

```bash
python3 scripts/verify_setup.py
```

This checks the toolchain, creates the two service repositories from `starter/` (each a real Git
repository with one committed starter commit), warms the Maven cache, and confirms the starting
state. It must end with **"Setup complete"**.

`--check` verifies without changing anything. `--reset` is destructive: it discards the working
copies and restores them from `starter/`, and asks for confirmation naming exactly what it will
delete.

---

## Layout

```
specs/          the specification, plus the write-protected authority documents
docs/           pre-read, term card, outcomes, grounding, decisions, ledger, tracker
starter/        pristine source for the two services; setup copies it out
lab-harness/    pair-verification harness -- readable, not writable
.claude/        lab config, write gate, auditor agent, validators, rubric, grader
scripts/        setup and pair verification
```

After setup, `pgs-tta/` and `pgs-payment-processor/` appear at the root as independent Git
repositories. They are gitignored here on purpose: nesting one repository's history inside
another's is how solution history leaks.

## The seven stages

| # | Stage | Focus | Min |
|---|---|---|---|
| 0 | Ground the Work | Frame the Boundary | 10 |
| 1 | Audit Context | Map the Seam | 18–20 |
| 2 | Author & Validate the Spec | Make the Spec Buildable | 18–20 |
| 3 | Plan Across Repositories | Design the Orchestration | 14–15 |
| 4 | Build & Validate | Build the Bounded Slice | 28–30 |
| 5 | Validate with Fresh Context | Prove the Pair | 20 |
| 6 | Review, Handoff & Close | Transfer the Learning | 5–6 |

---

## Commands

```bash
python3 scripts/verify_setup.py             # set up and verify the workspace
python3 scripts/run_pair_verification.py    # prove the seam
python3 scripts/run_pair_verification.py --explain   # what the compatibility matrix asks

python3 .claude/scripts/validate_spec.py    # Stage 2 readiness gate
python3 .claude/scripts/validate_plan.py    # Stage 3 plan gate
python3 .claude/scripts/build_validator_brief.py     # Stage 5 brief, assembled deterministically
python3 .claude/scripts/grade_repo.py       # deterministic grading
```

## Architecture notes

**The write gate.** `.claude/hooks/gate_guard.py` blocks writes to the harness, the out-of-scope
and non-negotiables documents, the outcomes card and the facilitator package. Reading them is
expected. A lab whose grading harness can be edited by the thing being graded is not measuring
anything. Run `--self-test` to confirm all four bypass classes are still covered.

**The generated client.** `pgs-tta/src/main/java/.../client/contract/` is generated from the
contract that service is pinned to:

```bash
cd pgs-tta && mvn -Pgenerate-client generate-sources
```

Generation runs at construction and remediation time only, never during an ordinary build, so the
lab needs no network. The same contract and configuration reproduce the committed output exactly —
regenerate rather than hand-editing.

**Determinism.** `grade_repo.py` produces the same score for the same workspace state every time.
Nothing samples, calls a model, or depends on the clock. Two people who reach the same outcome by
different routes score identically.

**A limitation, stated rather than papered over.** A journey event records that a tool ran, not what
it returned, so no rubric check can prove a build went green from the journey alone. Build outcomes
are graded from recorded results and repository state, and the facilitator's live spot-check covers
the rest.

## Grounding

`docs/SCENARIO_GROUNDING.md` separates grounded PGS behaviour from lab simplification from
deliberately seeded defect, and `docs/PGS_DECISIONS.md` records every decision with its source and
layer.

Seeded defects are teaching fixtures. **Their presence does not imply the same defect exists, or
ever existed, in a Mastercard production system.**

The lab proves the represented seam locally. It does not claim the wider PGS refund capability is
production-ready, and pair verification does not replace integration testing or release governance.
