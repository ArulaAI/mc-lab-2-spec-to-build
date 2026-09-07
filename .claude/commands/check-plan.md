---
name: check-plan
description: "Stage 3 readiness gate. Checks the orchestration plan and both agent contracts, including acceptance-criteria ownership."
---

Run the deterministic plan readiness gate and report its result.

1. Execute: `python3 .claude/scripts/validate_plan.py`
2. Report every check with its outcome, then `READY` or `DRAFT`.
3. Give particular attention to the acceptance-criteria ownership checks, because Stage 5 depends
   on them:
   - every validated criterion is owned by at least one contract;
   - each repository contract owns at least one criterion;
   - no contract references a criterion the specification does not contain;
   - each contract declares `NO_DIFF_EXPECTED`.

   A repository owning no criteria leaves its Stage 5 validator with nothing to judge. Expecting no
   code change is `NO_DIFF_EXPECTED: true`, which is a different statement and does not remove
   ownership.

Do not ask the participant any question, and do not write or amend the plan or the contracts. Report
what is missing and stop.
