# Context ledger

<!--
Stage 1. Your reconciliation of what the scoped repository auditors reported.

Each agent sees one repository. Neither sees the seam. This table is where their local findings
become one view, and where you rule on the disagreements -- that ruling is yours, not theirs.

OWNERSHIP -- who may write what
  Auditors            return claims and evidence. They never touch this file.
  You                 make the rulings.
  The parent session  writes your rulings into this table, after you have given them, and only
                      once BOTH auditor returns exist.

Nothing is written here before both returns are in. A ledger populated from one audit is a summary
of one repository, not a reconciliation of two -- and it will read exactly like the real thing.

The Human ruling column is never filled in on your behalf. If a row has no ruling, the row is not
finished, and the grader counts populated cells for that reason.

Status values:
  VERIFIED           evidence supports it
  CONTRADICTED       the two repositories disagree; your ruling says which is authoritative
  UNKNOWN            cannot be settled from what we have. Leave it UNKNOWN. Do not fill it in.
  LAB_SIMPLIFICATION true of the lab, not a claim about production

Keep this schema. Do not replace it with a differently-shaped table.
-->

| Claim | Asserted in | Evidence | Contradicted by | Status |
|---|---|---|---|---|
| | | | | |
