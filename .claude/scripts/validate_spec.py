#!/usr/bin/env python3
"""validate_spec.py -- bounded-build readiness gate for the refund-seam specification.

What this proves, and what it deliberately does not
---------------------------------------------------
This checks that the *resolved, authorised* scope of a specification is structurally build-ready:
the sections exist, acceptance criteria carry identifiers and observable outcomes, ownership is
named, scope survives, idempotency is stated well enough to test, and every unresolved item is
recorded rather than quietly answered.

It cannot tell you the specification is *correct*. A well-formed statement can still be wrong about
the domain, and no amount of structure detects a fabricated business rule. Semantic authority stays
human, and the status file says so rather than implying a machine blessed the content.

Bounded build, not total certainty
----------------------------------
Some questions cannot be settled from the material this lab supplies. Forcing them green would
teach the opposite of the lesson: it would reward inventing an owner or a derivation to satisfy a
gate. So an unresolved authority question does not reduce the score *provided the specification
keeps it explicit and outside the implementation boundary*. Those items are reported separately, as
OPEN AUTHORITY ITEMS, and they are not authorised for implementation.

The distinction the gate enforces:

  * a structural defect in the resolved specification            -> FAIL
  * an explicitly recorded authority gap, held out of scope      -> OPEN, non-blocking
  * an unresolved decision the implementation still depends on   -> FAIL

An open question that an acceptance criterion depends on is not deferred, whatever the document
calls it -- something has to build against it. That case fails.

Usage
-----
    python3 .claude/scripts/validate_spec.py
    python3 .claude/scripts/validate_spec.py --spec path/to/other.spec.md
    python3 .claude/scripts/validate_spec.py --self-test

Exit codes: 0 = ready for a bounded build, 1 = DRAFT (not ready), 2 = the spec file is missing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

SPEC_PATH = "specs/refund-seam-phase1.spec.md"
STATUS_PATH = "specs/spec.status.json"

# The participant-facing verdict. The machine-readable "status" stays READY so downstream
# scripts and grading that already key on it keep working.
READY_LABEL = "READY_FOR_BOUNDED_BUILD"

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

# How a document says "this one is not settled". Matched against a single table cell or paragraph,
# never against the whole document, so an unrelated sentence elsewhere cannot mark an item open.
UNRESOLVED_PHRASES = [
    "open",
    "not settled",
    "unsettled",
    "not decided",
    "undecided",
    "unresolved",
    "to be decided",
]

OQ_ID = re.compile(r"\bOQ-\d+\b")


class Check:
    def __init__(self, name: str, passed: bool, detail: str):
        self.name = name
        self.passed = passed
        self.detail = detail


class AuthorityItem:
    """An unresolved decision the specification has surfaced.

    `recorded` means it points at an open question that actually exists in the Open questions
    table. `depended_on` means an acceptance criterion cites that same open question -- which is
    the case where deferral is not real, because something is being built against it.
    """

    def __init__(self, label: str, refs: list[str], recorded: bool, depended_on: bool):
        self.label = label
        self.refs = refs
        self.recorded = recorded
        self.depended_on = depended_on

    @property
    def deferred(self) -> bool:
        return self.recorded and not self.depended_on

    def describe(self) -> str:
        refs = f" ({', '.join(self.refs)})" if self.refs else ""
        return f"{self.label}{refs}"


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


def row_cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip("|").split("|")]


def looks_unresolved(fragment: str) -> bool:
    low = fragment.lower()
    return any(p in low for p in UNRESOLVED_PHRASES)


def recorded_question_ids(secs: dict[str, str]) -> set[str]:
    """Open-question identifiers that genuinely have a row in the Open questions table."""
    ids: set[str] = set()
    for row in table_rows(secs.get("Open questions", "")):
        cells = row_cells(row)
        if cells:
            ids.update(OQ_ID.findall(cells[0]))
    return ids


def authority_items(secs: dict[str, str]) -> list[AuthorityItem]:
    """Unresolved decisions the specification itself surfaces.

    Two structural sources, both explicit rather than inferred: an owner cell that says the
    decision is open, and an idempotency paragraph that says a part of it is not settled. Nothing
    here encodes which decisions those are -- the document names them.
    """
    known = recorded_question_ids(secs)
    ac_block = secs.get("Acceptance criteria", "")
    ac_refs = set(OQ_ID.findall(ac_block))
    items: list[AuthorityItem] = []

    for row in table_rows(secs.get("Per-repo ownership", "")):
        cells = row_cells(row)
        if len(cells) < 2:
            continue
        concern, owner = cells[0], cells[1]
        if concern.lower() in ("concern", "decision") or not looks_unresolved(owner):
            continue
        refs = OQ_ID.findall(owner)
        items.append(AuthorityItem(
            f"ownership undecided: {concern}",
            refs,
            bool(refs) and all(r in known for r in refs),
            any(r in ac_refs for r in refs),
        ))

    for para in [p for p in secs.get("Idempotency", "").split("\n\n") if p.strip()]:
        if not looks_unresolved(para) or "|" in para:
            continue
        refs = OQ_ID.findall(para)
        summary = " ".join(para.split())
        if len(summary) > 90:
            summary = summary[:87].rstrip() + "..."
        items.append(AuthorityItem(
            f"idempotency: {summary}",
            refs,
            bool(refs) and all(r in known for r in refs),
            any(r in ac_refs for r in refs),
        ))

    return items


def validate(text: str) -> tuple[list[Check], list[AuthorityItem]]:
    checks: list[Check] = []
    secs = sections(text)
    items = authority_items(secs)

    # 1
    missing = [s for s in REQUIRED_SECTIONS if s not in secs]
    checks.append(Check("required sections present", not missing,
                        "all present" if not missing else "missing: " + ", ".join(missing)))

    # 2
    meta = secs.get("Metadata", "")
    has_owner = bool(re.search(r"\|\s*Owner\s*\|\s*\S", meta)) and "unassigned" not in meta.lower()
    checks.append(Check("metadata names an owner", has_owner,
                        "owner named" if has_owner
                        else "Owner is unset or marked unassigned -- the lab or the participant "
                             "supplies this; the gate does not infer it"))

    # 3
    ac_block = secs.get("Acceptance criteria", "")
    ac_ids = re.findall(r"\bAC-\d+\b", ac_block)
    checks.append(Check("acceptance criteria carry identifiers", len(set(ac_ids)) >= 5,
                        f"{len(set(ac_ids))} identified criteria (need at least 5)"))

    # 4
    unobservable = [p for p in UNOBSERVABLE_PHRASES if p in ac_block.lower()]
    checks.append(Check("acceptance criteria describe observable outcomes", not unobservable,
                        "no unobservable phrasing" if not unobservable
                        else "unobservable phrasing: " + ", ".join(unobservable)))

    # 5 -- the authorised scope only. What carries the retry identity, what a caller observes on a
    # retry, and what must be true of stored state afterwards are all supported by the source
    # material, so they are required. Who owns the derivation is not, so it is not.
    idem = secs.get("Idempotency", "").lower()
    idem_missing = []
    if "identity" not in idem and "idempotency key" not in idem and "idempotency-key" not in idem:
        idem_missing.append("what carries the retry identity")
    if "409" not in idem:
        idem_missing.append("what the caller observes on a retry")
    if not re.search(r"\b(one|single|no second|exactly one)\b", idem):
        idem_missing.append("what must be true of stored state afterwards")
    checks.append(Check("idempotency is testable for the authorised scope", not idem_missing,
                        "names the retry identity, the duplicate response and the resulting state"
                        if not idem_missing else "does not state: " + "; ".join(idem_missing)))

    # 6
    compat = secs.get("Compatibility and rollout constraints", "")
    compat_rows = len(table_rows(compat))
    compat_ok = compat_rows >= 3 or ("must" in compat.lower() and len(compat.split()) > 60)
    checks.append(Check("compatibility constraints are testable", compat_ok,
                        f"{compat_rows} constraint row(s)" if compat_ok
                        else "states intent but names no combination that must hold or must fail"))

    # 7
    oos = secs.get("Out of scope", "")
    oos_ok = "OUT_OF_SCOPE.md" in oos
    checks.append(Check("out of scope references the authoritative document", oos_ok,
                        "references specs/OUT_OF_SCOPE.md" if oos_ok else "does not reference it"))

    # 8 -- the merged unresolved-items check. Placeholders, recorded open questions, and the
    # boundedness of every authority gap are one concern: is what remains unknown stated plainly
    # and held outside the build?
    found_markers = [m for m in PLACEHOLDER_MARKERS if m in text]
    oq_rows = len(table_rows(secs.get("Open questions", "")))
    unrecorded = [i for i in items if not i.recorded]
    depended = [i for i in items if i.depended_on]
    faults = []
    if found_markers:
        faults.append("unresolved placeholders remain: " + ", ".join(sorted(set(found_markers))))
    if oq_rows < 1:
        faults.append("no open question is retained")
    if unrecorded:
        faults.append("not recorded as an open question: "
                      + "; ".join(i.label for i in unrecorded))
    if depended:
        faults.append("an acceptance criterion depends on an unresolved decision: "
                      + "; ".join(i.describe() for i in depended))
    checks.append(Check("unresolved items are recorded and held out of scope", not faults,
                        f"{oq_rows} open question(s) retained; "
                        f"{len([i for i in items if i.deferred])} authority item(s) deferred"
                        if not faults else " | ".join(faults)))

    # 9
    nn = secs.get("Non-negotiables reference", "")
    nn_ok = "NON_NEGOTIABLES.md" in nn
    checks.append(Check("non-negotiables are referenced", nn_ok,
                        "references specs/NON_NEGOTIABLES.md" if nn_ok else "does not reference it"))

    # 10
    neg = secs.get("Negative requirements", "")
    neg_ok = "settlement" in neg.lower() and "void" in neg.lower()
    checks.append(Check("negative requirements name settlement and Void", neg_ok,
                        "both named" if neg_ok else "must state that no settlement artifact is "
                                                    "produced and no Void behaviour is implemented"))

    return checks, items


def render(checks: list[Check]) -> str:
    width = max(len(c.name) for c in checks)
    return "\n".join(
        f"  [{'PASS' if c.passed else 'FAIL'}] {c.name:<{width}}  {c.detail}" for c in checks)


def render_open_items(items: list[AuthorityItem]) -> str:
    deferred = [i for i in items if i.deferred]
    if not deferred:
        return ""
    lines = ["  OPEN AUTHORITY ITEMS"]
    lines += [f"  - {i.describe()}" for i in deferred]
    lines.append("")
    lines.append("  These items are not authorised for implementation.")
    return "\n".join(lines)


def build_status(checks: list[Check], items: list[AuthorityItem]) -> dict:
    ready = all(c.passed for c in checks)
    return {
        # Preserved internal contract: downstream scripts and grading key on these two.
        "valid": ready,
        "status": "READY" if ready else "DRAFT",
        # Participant-facing verdict, said out loud so the bound is not lost in translation.
        "readiness": READY_LABEL if ready else "DRAFT",
        "structural_checks": len(checks),
        "structural_checks_passed": sum(1 for c in checks if c.passed),
        "open_authority_items": [i.describe() for i in items if i.deferred],
        "semantic_authority": "human-reviewed",
        "note": "Structural readiness for the resolved scope only. This gate cannot determine "
                "whether the specification is correct about the domain, and does not attempt to. "
                "Open authority items are recorded, not authorised for implementation.",
    }


def self_test(draft_path: str | None = None) -> int:
    """The starter must fail, a bounded-ready spec must pass, and a fake deferral must not.

    `draft_path` overrides the baseline, so the suite can be run against the committed starter
    when the working copy has already been hardened.
    """
    here = pathlib.Path(__file__).resolve().parents[2]
    source = pathlib.Path(draft_path) if draft_path else here / SPEC_PATH
    draft = source.read_text(encoding="utf-8")
    results = []

    def scored(text):
        checks, items = validate(text)
        return checks, items, [c.name for c in checks if not c.passed]

    checks, _, failing = scored(draft)
    results.append(("the shipped starter specification is refused", bool(failing),
                    f"{len(failing)} failing check(s)"))
    results.append(("exactly ten checks are scored", len(checks) == 10,
                    f"{len(checks)} checks"))

    # A specification hardened only where authority supports it: the retry-identity owner stays
    # open, deliberately, and must not cost a point.
    hardened = draft
    hardened = hardened.replace("| Owner | *(unassigned)* |", "| Owner | Coordinating engineer |")
    hardened = hardened.replace("| Status | DRAFT |", "| Status | READY |")
    hardened = re.sub(r"^> .*$", "", hardened, flags=re.MULTILINE)
    hardened = hardened.replace("it is handled correctly",
                                "it is refused when it exceeds that capture's own amount")
    hardened = hardened.replace(
        "| Duplicate detection | `pgs-payment-processor` |",
        "| Duplicate detection | `pgs-payment-processor` |\n"
        "| Remaining-refundable determination | `pgs-payment-processor` |\n"
        "| Endpoint selection | `pgs-tta` |\n"
        "| Retry identity stability | Open -- see OQ-3 |")
    # Surfacing a question means recording it, which is what makes the deferral real.
    hardened = hardened.replace(
        "| OQ-1 | Production derivation of the idempotency key |",
        "| OQ-3 | Retry identity stability on the online path | Open |\n"
        "| OQ-1 | Production derivation of the idempotency key |")
    hardened = hardened.replace(
        "Refunds are idempotent. Duplicate handling is covered by the error semantics above.",
        "The `Idempotency-Key` header carries the retry identity. A retry returns 409 to the "
        "caller and leaves exactly one refund record.\n\n"
        "The derivation of the key value, and which service keeps it stable across retries on the "
        "online path, is not settled from available source material. See OQ-3.")
    hardened = hardened.replace(
        "The change should be rolled out safely, without breaking anything that is already deployed.",
        "| Combination | Must |\n|---|---|\n"
        "| current consumer against current producer | succeed |\n"
        "| previous consumer against current producer | succeed |\n"
        "| current consumer against previous producer | fail, and be shown to fail |\n")

    checks, items, failing = scored(hardened)
    results.append(("a bounded-ready specification is accepted", not failing,
                    "all checks pass" if not failing else "still failing: " + ", ".join(failing)))
    results.append(("the deferred authority item is reported, not scored",
                    len([i for i in items if i.deferred]) >= 1 and not failing,
                    f"{len([i for i in items if i.deferred])} open authority item(s)"))

    # The same document, except an acceptance criterion now builds against the open question.
    # Calling it deferred does not make it deferred.
    depends = hardened.replace(
        "| AC-5 |", "| AC-5 | Retry identity behaviour per OQ-3 |", 1)
    _, _, failing_dep = scored(depends)
    results.append(("an open question an AC depends on still fails",
                    "unresolved items are recorded and held out of scope" in failing_dep,
                    "blocked" if failing_dep else "NOT blocked"))

    # An unresolved owner that points at no recorded question is a gap, not a deferral.
    dangling = hardened.replace("| Retry identity stability | Open -- see OQ-3 |",
                                "| Retry identity stability | Open |")
    _, _, failing_dangle = scored(dangling)
    results.append(("an unrecorded authority gap still fails",
                    "unresolved items are recorded and held out of scope" in failing_dangle,
                    "blocked" if failing_dangle else "NOT blocked"))

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
    parser.add_argument("--spec", default=None,
                        help="validate another specification file; the status file is only "
                             "written for the lab's own specification")
    args = parser.parse_args()

    if args.self_test:
        return self_test(args.spec)

    root = pathlib.Path(__file__).resolve().parents[2]
    rel = args.spec or SPEC_PATH
    spec_file = pathlib.Path(rel) if args.spec else root / SPEC_PATH
    if not spec_file.is_file():
        print(f"specification not found at {rel}", file=sys.stderr)
        return 2

    checks, items = validate(spec_file.read_text(encoding="utf-8"))
    status = build_status(checks, items)

    print(f"specification: {rel}\n")
    print(render(checks))
    print(f"\n  {status['structural_checks_passed']}/{status['structural_checks']} structural "
          f"readiness checks  ->  {status['readiness']}")

    open_block = render_open_items(items)
    if open_block:
        print()
        print(open_block)

    if not args.spec:
        (root / STATUS_PATH).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        print(f"\n  wrote {STATUS_PATH}")

    if not status["valid"]:
        print("\n  Structural readiness only. Passing this gate does not mean the specification is "
              "correct;\n  it means the resolved scope is well-formed enough to build against. "
              "That judgement stays human.")
    return 0 if status["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
