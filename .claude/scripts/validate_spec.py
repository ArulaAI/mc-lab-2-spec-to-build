#!/usr/bin/env python3
"""validate_spec.py -- structural readiness gate for the refund-seam specification.

What this proves, and what it deliberately does not
---------------------------------------------------
This checks that a specification is *structurally* build-ready: the sections exist, acceptance
criteria carry identifiers and observable outcomes, ownership is named, scope survives, unknowns
are recorded rather than quietly resolved, and no build-authorising field still contains a
placeholder.

It cannot tell you the specification is *correct*. A well-formed statement can still be wrong about
the domain, and no amount of structure detects a fabricated business rule. Semantic authority stays
human, and the status file says so out loud rather than implying a machine blessed the content.

Usage
-----
    python3 .claude/scripts/validate_spec.py
    python3 .claude/scripts/validate_spec.py --self-test

Exit codes: 0 = READY, 1 = DRAFT (not ready), 2 = the spec file is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import tempfile

SPEC_PATH = "specs/refund-seam-phase1.spec.md"
STATUS_PATH = "specs/spec.status.json"

REQUIRED_SECTIONS = [
    "Metadata",
    "Purpose",
    "System boundary",
    "Source authority",
    "In-scope behaviour",
    "Per-repo ownership",
    "Request and response contract",
    "Business rules",
    "Error semantics",
    "Idempotency",
    "Correlation and observability",
    "Compatibility and rollout constraints",
    "Acceptance criteria",
    "Negative requirements",
    "Out of scope",
    "Open questions",
    "Non-negotiables reference",
]

# A specification that still admits it is unfinished is not build-authorising. These markers are
# how the starter announces its own gaps, so their presence is exactly what must be cleared.
PLACEHOLDER_MARKERS = [
    "*(unassigned)*",
    "**Incomplete.**",
    "**Vague.**",
    "**Not yet testable.**",
    "**Unresolved.**",
    "is vague",
    "TBD",
    "TODO",
]

# An acceptance criterion has to describe something a test can observe. These are the words that
# tend to stand in for an observable outcome without being one.
UNOBSERVABLE_PHRASES = [
    "handled correctly",
    "works correctly",
    "behaves correctly",
    "as expected",
    "appropriately",
    "properly",
]

OWNERSHIP_DECISIONS = [
    ("remaining-refundable determination", ["remaining", "refundable"]),
    ("endpoint selection", ["endpoint"]),
    ("retry identity stability", ["identity", "idempotenc"]),
]


class Check:
    def __init__(self, name: str, passed: bool, detail: str):
        self.name = name
        self.passed = passed
        self.detail = detail


def sections(text: str) -> dict[str, str]:
    """Split into `##` sections, dropping blockquote lines.

    Blockquotes in the starter specification are the document's own admissions of what is still
    missing ("Vague.", "Not yet testable."). Counting them as content would let a section pass a
    completeness check on the strength of the note explaining that it is incomplete -- which is
    exactly the false pass this stripping prevents.
    """
    found: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        if line.startswith("## "):
            if current:
                found[current] = "\n".join(buf)
            current = line[3:].strip()
            buf = []
        elif current:
            buf.append(line)
    if current:
        found[current] = "\n".join(buf)
    return found


def table_rows(block: str) -> list[str]:
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|[\s:|-]+\|$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 2 and any(cells):
            rows.append(s)
    return rows


def validate(text: str) -> list[Check]:
    checks: list[Check] = []
    secs = sections(text)

    missing = [s for s in REQUIRED_SECTIONS if s not in secs]
    checks.append(Check("required sections present", not missing,
                        "all present" if not missing else "missing: " + ", ".join(missing)))

    meta = secs.get("Metadata", "")
    has_owner = bool(re.search(r"\|\s*Owner\s*\|\s*\S", meta)) and "unassigned" not in meta.lower()
    checks.append(Check("metadata names an owner", has_owner,
                        "owner named" if has_owner else "Owner is unset or marked unassigned"))

    ac_block = secs.get("Acceptance criteria", "")
    ac_ids = re.findall(r"\bAC-\d+\b", ac_block)
    checks.append(Check("acceptance criteria carry identifiers", len(set(ac_ids)) >= 5,
                        f"{len(set(ac_ids))} identified criteria (need at least 5)"))

    unobservable = [p for p in UNOBSERVABLE_PHRASES if p in ac_block.lower()]
    checks.append(Check("acceptance criteria describe observable outcomes", not unobservable,
                        "no unobservable phrasing" if not unobservable
                        else "unobservable phrasing: " + ", ".join(unobservable)))

    own_block = secs.get("Per-repo ownership", "")
    own_low = own_block.lower()
    unowned = [label for label, kws in OWNERSHIP_DECISIONS
               if not all(k in own_low for k in kws)]
    checks.append(Check("every contested decision has a named owner", not unowned,
                        "all owned" if not unowned else "no owner named for: " + "; ".join(unowned)))

    # An implementable idempotency statement answers four questions: what carries the retry
    # identity, which service keeps it stable, what the caller observes on a retry, and what must
    # be true of stored state afterwards. Each is checked for the thing that answers it rather than
    # by length -- a word count is both arbitrary and passable by padding.
    idem = secs.get("Idempotency", "").lower()
    idem_missing = []
    if "identity" not in idem and "idempotency key" not in idem:
        idem_missing.append("what carries the retry identity")
    if "pgs-tta" not in idem and "pgs-payment-processor" not in idem:
        idem_missing.append("which service is responsible")
    if "409" not in idem:
        idem_missing.append("what the caller observes on a retry")
    if not re.search(r"\b(one|single|no second|exactly one)\b", idem):
        idem_missing.append("what must be true of stored state afterwards")
    checks.append(Check("idempotency section is implementable", not idem_missing,
                        "names the identity, the responsible service, the retry status and the "
                        "resulting state" if not idem_missing
                        else "does not state: " + "; ".join(idem_missing)))

    compat = secs.get("Compatibility and rollout constraints", "")
    compat_rows = len(table_rows(compat))
    compat_ok = compat_rows >= 3 or ("must" in compat.lower() and len(compat.split()) > 60)
    checks.append(Check("compatibility constraints are testable", compat_ok,
                        f"{compat_rows} constraint row(s)" if compat_ok
                        else "states intent but names no combination that must hold or must fail"))

    oos = secs.get("Out of scope", "")
    oos_ok = "OUT_OF_SCOPE.md" in oos
    checks.append(Check("out of scope references the authoritative document", oos_ok,
                        "references specs/OUT_OF_SCOPE.md" if oos_ok else "does not reference it"))

    oq = secs.get("Open questions", "")
    oq_rows = len(table_rows(oq))
    checks.append(Check("open questions are recorded rather than resolved", oq_rows >= 1,
                        f"{oq_rows} open question(s) retained"))

    found_markers = [m for m in PLACEHOLDER_MARKERS if m in text]
    checks.append(Check("no unresolved placeholders remain", not found_markers,
                        "none" if not found_markers
                        else "still present: " + ", ".join(sorted(set(found_markers)))))

    nn = secs.get("Non-negotiables reference", "")
    nn_ok = "NON_NEGOTIABLES.md" in nn
    checks.append(Check("non-negotiables are referenced", nn_ok,
                        "references specs/NON_NEGOTIABLES.md" if nn_ok else "does not reference it"))

    neg = secs.get("Negative requirements", "")
    neg_ok = "settlement" in neg.lower() and "void" in neg.lower()
    checks.append(Check("negative requirements name settlement and Void", neg_ok,
                        "both named" if neg_ok else "must state that no settlement artifact is "
                                                    "produced and no Void behaviour is implemented"))

    return checks


def render(checks: list[Check]) -> str:
    width = max(len(c.name) for c in checks)
    lines = [f"  [{'PASS' if c.passed else 'FAIL'}] {c.name:<{width}}  {c.detail}" for c in checks]
    return "\n".join(lines)


def write_status(root: pathlib.Path, checks: list[Check]) -> dict:
    ready = all(c.passed for c in checks)
    status = {
        "valid": ready,
        "status": "READY" if ready else "DRAFT",
        "structural_checks": len(checks),
        "structural_checks_passed": sum(1 for c in checks if c.passed),
        # Said plainly so nobody reads a green structural gate as a correctness guarantee.
        "semantic_authority": "human-reviewed",
        "note": "Structural readiness only. This gate cannot determine whether the specification "
                "is correct about the domain, and does not attempt to.",
    }
    (root / STATUS_PATH).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status


def self_test() -> int:
    """A draft must fail and a hardened spec must pass, or the gate is decorative."""
    here = pathlib.Path(__file__).resolve().parents[2]
    draft = (here / SPEC_PATH).read_text(encoding="utf-8")

    results = []
    draft_checks = validate(draft)
    results.append(("the shipped DRAFT specification is refused",
                    not all(c.passed for c in draft_checks),
                    f"{sum(1 for c in draft_checks if not c.passed)} failing check(s)"))

    hardened = draft
    hardened = hardened.replace("| Owner | *(unassigned)* |", "| Owner | Coordinating engineer |")
    hardened = hardened.replace("| Status | DRAFT |", "| Status | READY |")
    for marker in ["**Incomplete.**", "**Vague.**", "**Not yet testable.**", "**Unresolved.**"]:
        hardened = re.sub(r"> \*\*" + re.escape(marker.strip("*.").strip()) + r"\.\*\*.*?(?=\n\n)",
                          "", hardened, flags=re.DOTALL)
    hardened = re.sub(r"^> .*$", "", hardened, flags=re.MULTILINE)
    hardened = hardened.replace("it is handled correctly",
                                "it is refused when it exceeds that capture's own amount")
    hardened = hardened.replace(
        "| Duplicate detection | `pgs-payment-processor` |",
        "| Duplicate detection | `pgs-payment-processor` |\n"
        "| Remaining refundable determination | `pgs-payment-processor` |\n"
        "| Endpoint selection | `pgs-tta` |\n"
        "| Retry identity stability, propagated unchanged | `pgs-tta` |\n"
        "| Deduplicating against the received idempotency identity | `pgs-payment-processor` |")
    hardened = hardened.replace(
        "Refunds are idempotent. Duplicate handling is covered by the error semantics above.",
        "The caller supplies a retry identity on the request. pgs-tta propagates that identity "
        "unchanged on every path, and pgs-payment-processor deduplicates against the identity it "
        "receives. A retry returns 409 to the caller and leaves exactly one refund record.")
    hardened = hardened.replace(
        "The change should be rolled out safely, without breaking anything that is already deployed.",
        "| Combination | Must |\n|---|---|\n"
        "| current consumer against current producer | succeed |\n"
        "| previous consumer against current producer | succeed |\n"
        "| current consumer against previous producer | fail, and be shown to fail |\n")

    hardened_checks = validate(hardened)
    failing = [c.name for c in hardened_checks if not c.passed]
    results.append(("a hardened specification is accepted", not failing,
                    "all checks pass" if not failing else "still failing: " + ", ".join(failing)))

    ok = True
    for label, passed, detail in results:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}  --  {detail}")
        ok = ok and passed
    print()
    print(f"validate_spec self-test: {sum(1 for _, p, _ in results if p)} passed, "
          f"{sum(1 for _, p, _ in results if not p)} failed")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = pathlib.Path(__file__).resolve().parents[2]
    spec_file = root / SPEC_PATH
    if not spec_file.is_file():
        print(f"specification not found at {SPEC_PATH}", file=sys.stderr)
        return 2

    checks = validate(spec_file.read_text(encoding="utf-8"))
    print(f"specification: {SPEC_PATH}\n")
    print(render(checks))
    status = write_status(root, checks)
    print(f"\n  {status['structural_checks_passed']}/{status['structural_checks']} structural "
          f"checks  ->  {status['status']}")
    print(f"  wrote {STATUS_PATH}")
    if status["status"] == "DRAFT":
        print("\n  Structural readiness only. Passing this gate does not mean the specification is "
              "correct;\n  it means it is well-formed enough to build against. That judgement "
              "stays human.")
    return 0 if status["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
