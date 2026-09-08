---
name: check-spec
description: "Stage 2 readiness gate. Reports whether the specification is structurally build-ready, and names every gap."
---

Run the deterministic specification readiness gate and report its result.

1. Execute: `bash .claude/scripts/run .claude/scripts/validate_spec.py`
2. Report the outcome exactly as the script gives it: the pass/fail line for every check, the
   `N/M structural checks` total, and `READY` or `DRAFT`.
3. Say which checks failed and what each one is asking for. Do not paraphrase a failure into a
   suggestion, and do not offer to fix the specification yourself.

Do not ask the participant any question. This command reports a deterministic result; the human
decisions for this stage are the decision gates in `.claude/decision-gates.yaml`, and they are the
coordinating engineer's to answer, not yours to invent.

State plainly what the gate does and does not establish: it checks the specification is well-formed
enough to build from. It cannot tell anyone the specification is *correct* about the domain, which
is why the status file records `"semantic_authority": "human-reviewed"`.
