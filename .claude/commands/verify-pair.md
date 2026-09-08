---
name: verify-pair
description: "Prove the seam. Runs deterministic pair verification across both services and reports PASS or FAIL with evidence."
---

Run the deterministic pair-verification harness and report its result.

1. Execute: `bash .claude/scripts/run scripts/run_pair_verification.py`
2. Report, in this shape:

   ```
   PAIR_VERIFICATION: PASS | FAIL
   EVIDENCE:
   ```

   For `EVIDENCE`, give the harness's own test summary and, on failure, the assertion message of
   each failing test. Those messages name the disagreement in domain terms; that is the whole value
   of them, so quote rather than summarise.

Do not launch the fresh-context validators. This command produces deterministic system-level
evidence only. The independent model judgements are a separate step, and keeping them separate is
the point: one tells you whether the two services agree, the other tells you whether a reviewer who
never saw your work believes the criteria are met.

Do not ask the participant any question, and do not attempt a repair. Whether a failure is material,
and whether to fix it now, is the coordinating engineer's ruling.
