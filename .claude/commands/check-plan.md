---
name: check-plan
description: "Stage 3 readiness gate. Checks the orchestration plan and both agent contracts, including acceptance-criteria ownership."
---

Run the deterministic plan readiness gate and report its result.

1. Execute: `bash .claude/scripts/run .claude/scripts/validate_plan.py`
2. Report every check with its outcome, then `READY` or `DRAFT`.
3. Give particular attention to the acceptance-criteria ownership checks, because Stage 5 depends
   on them:
   - every validated criterion is owned by at least one contract;
   - each repository contract owns at least one criterion;
   - no contract references a criterion the specification does not contain;
   - each contract declares `NO_DIFF_EXPECTED: true` or `false`.

   A repository owning no criteria leaves its Stage 5 validator with nothing to judge. Expecting no
   code change is `NO_DIFF_EXPECTED: true`, which is a different statement and does not remove
   ownership. The same criterion appearing in both contracts is valid when each repository has to
   produce its own local evidence for it — do not report that as a conflict.

4. Report an open authority item assigned as implementation work as the failure it is. Stage 2 left
   those unresolved deliberately; a plan that hands one to an agent has authorised work the
   specification does not.

The gate validates plan structure, not whether the chosen rollout order is correct. Say so rather
than letting `READY` read as approval of the sequencing.

Do not ask the participant any question, and do not write or amend the plan or the contracts. Report
what is missing and stop.
