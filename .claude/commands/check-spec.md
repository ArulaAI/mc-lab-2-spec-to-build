---
name: check-spec
description: "Stage 2 readiness gate. Reports whether the specification is structurally build-ready, and names every gap."
---

Run the deterministic specification readiness gate and report its result.

1. Execute: `bash .claude/scripts/run .claude/scripts/validate_spec.py`
2. Report the outcome exactly as the script gives it: the pass/fail line for every check, the
   `N/10 structural readiness checks` total, the verdict — `READY_FOR_BOUNDED_BUILD` or `DRAFT` —
   and the `OPEN AUTHORITY ITEMS` block whenever the script prints one.
3. Say which checks failed and what each one is asking for. Do not paraphrase a failure into a
   suggestion, and do not offer to fix the specification yourself.
4. Never report an open authority item as a failure, and never propose an answer for one. They are
   listed precisely because the available material does not settle them, and they are not
   authorised for implementation.

Do not ask the participant any question. This command reports a deterministic result; the human
decisions for this stage belong to the coordinating engineer, not to you.

State plainly what the gate does and does not establish: it checks that the *resolved* scope is
well-formed enough to build from. It cannot tell anyone the specification is *correct* about the
domain, which is why the status file records `"semantic_authority": "human-reviewed"`.
