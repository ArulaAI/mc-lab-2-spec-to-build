#!/usr/bin/env python3
"""validate_plan.py -- structural gate for the cross-repository orchestration plan.

A plan that names tasks but not boundaries is a task list, not an orchestration design. This checks
that the plan and its agent briefs actually decide the things that have to be decided before agents
are let loose: which repository owns what, what each agent may see and touch, which acceptance
criteria it owns, when it must stop, and in what order the changes can safely land.

Like the specification gate, this is structural only. It cannot tell you the rollout order is
*right* -- only that one was chosen and a reason was given.

    python3 .claude/scripts/validate_plan.py
    python3 .claude/scripts/validate_plan.py --self-test

Exit codes: 0 = plan is structurally ready, 1 = not ready, 2 = the plan is missing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

PLAN_PATH = "docs/plans/orchestration-plan.md"
STATUS_PATH = "docs/plans/plan.status.json"
BRIEFS = {
    "pgs-tta": "docs/agent-briefs/tta-implementation-brief.md",
    "pgs-payment-processor": "docs/agent-briefs/processor-implementation-brief.md",
}

# What a participant-authored brief must decide. Deliberately excludes anything the
# repo-implementer agent already fixes for every task: its tool grant is frontmatter, and its
# return shape is the six headings in its own definition. Restating an invariant in a brief invites
# the two to drift, and the brief is the one that wins.
# Each entry is (label, accepted keywords). "Objective" and "Outcome" are the same field under two
# reasonable names; failing a brief over which one the author picked would be pedantry, not a gate.
BRIEF_SECTIONS = [
    ("outcome or objective", ["outcome", "objective"]),
    # A contract that does not require the agent to verify its own repository leaves verification
    # to the participant, which is the duplication Stage 4 exists to remove -- and leaves the
    # Stage 5 brief with no verification evidence to carry. The command varies per repository, so
    # it is the brief's to name.
    ("verification required", ["verification"]),
    ("authoritative inputs", ["authoritative"]),
    ("repository scope", ["repository"]),
    ("allowed areas", ["allowed"]),
    ("excluded areas", ["excluded"]),
    ("acceptance criteria owned", ["acceptance"]),
    ("stop conditions", ["stop"]),
]

# Things the specification places out of scope. A plan that turns one of these into a task has
# expanded the change, which no amount of good execution afterwards puts right.
OUT_OF_SCOPE_TERMS = [
    "void-auth", "void-capture", "void-pay", "void-refund",
    "settlement", "dcf", "injection", "lcs",
    "pre-risk", "excessive_refunds",
]


class Check:
    def __init__(self, name: str, passed: bool, detail: str):
        self.name, self.passed, self.detail = name, passed, detail


def read(root: pathlib.Path, rel: str) -> str | None:
    p = root / rel
    return p.read_text(encoding="utf-8") if p.is_file() else None


def validate(root: pathlib.Path) -> list[Check]:
    checks: list[Check] = []
    plan = read(root, PLAN_PATH)

    if plan is None:
        return [Check("orchestration plan exists", False, f"{PLAN_PATH} not found")]
    checks.append(Check("orchestration plan exists", True, PLAN_PATH))
    low = plan.lower()

    named = [r for r in BRIEFS if r in low]
    checks.append(Check("both repositories are named in the plan", len(named) == 2,
                        f"named: {', '.join(named) or 'none'}"))

    tagged = all(re.search(re.escape(repo), low) for repo in BRIEFS)
    checks.append(Check("work is attributed by repository", tagged,
                        "each repository has attributed work" if tagged
                        else "the plan does not attribute work to specific repositories"))

    ac_refs = set(re.findall(r"\bAC-\d+\b", plan))
    checks.append(Check("acceptance criteria are mapped to work", len(ac_refs) >= 3,
                        f"{len(ac_refs)} acceptance criteria referenced (need at least 3)"))

    rollout_words = ["rollout", "roll out", "deploy", "order", "sequence"]
    has_rollout = any(w in low for w in rollout_words)
    checks.append(Check("rollout order is stated", has_rollout,
                        "an order is proposed" if has_rollout
                        else "the plan does not say which side lands first"))

    has_reason = has_rollout and ("because" in low or "so that" in low or "reason" in low)
    checks.append(Check("rollout order states its rationale", has_reason,
                        "reasoning present" if has_reason
                        else "a rollout order without a reason is an assertion, not a plan"))

    compat_named = "pair" in low or "compatib" in low
    checks.append(Check("a compatibility check is named", compat_named,
                        "named" if compat_named
                        else "the plan does not say how compatibility will be demonstrated"))

    # A term is smuggled only if it appears somewhere that does *not* also mark it as excluded.
    # Matching per line rather than with a directional regex, because "Void is out of scope" and
    # "out of scope: Void" are the same statement and an order-sensitive pattern accepts only one.
    exclusion_marker = re.compile(r"out of scope|excluded|not in scope|must not|no .* (is|are) "
                                  r"(built|implemented|produced)|remains? downstream")
    smuggled = set()
    for line in low.splitlines():
        if exclusion_marker.search(line):
            continue
        for term in OUT_OF_SCOPE_TERMS:
            if re.search(r"\b" + re.escape(term) + r"\b", line):
                smuggled.add(term)
    smuggled = sorted(smuggled)
    checks.append(Check("no out-of-scope component became work", not smuggled,
                        "none" if not smuggled
                        else "appears as work rather than as an exclusion: " + ", ".join(smuggled)))

    # Stage 2's open authority items are not authorised for implementation. Checked across the plan
    # *and* both briefs: a question left open in the plan but handed to an agent in a brief has
    # still become implementation work, and the brief is what the agent actually executes.
    open_qs = read(root, "specs/refund-seam-phase1.spec.md") or ""
    oq_ids = set(re.findall(r"\bOQ-\d+\b", open_qs))
    tasked = set()
    for label, doc in [("plan", plan)] + [(repo, read(root, rel) or "")
                                          for repo, rel in BRIEFS.items()]:
        for q in oq_ids:
            if q in doc and not re.search(
                    re.escape(q) + r"[^.\n]{0,80}(open|unresolved|escalat|not authoris|"
                                   r"not authoriz|out of scope|excluded)", doc, re.IGNORECASE):
                tasked.add(f"{q} ({label})")
    tasked = sorted(tasked)
    checks.append(Check("open authority items did not become tasks", not tasked,
                        "none" if not tasked
                        else "planned as work rather than left open: " + ", ".join(tasked)))

    # ---- Acceptance-criteria ownership -------------------------------------------------------
    # Stage 3's contracts are the canonical per-repository AC split. Stage 5 judges each repository
    # against its own criteria, so if the split is missing or incomplete there is nothing for one
    # of the two validators to judge, and the second validator quietly becomes a no-op.
    spec_text = read(root, "specs/refund-seam-phase1.spec.md") or ""
    spec_acs = set(re.findall(r"\bAC-\d+\b", spec_text))
    owned: dict[str, set[str]] = {}
    for repo, rel in BRIEFS.items():
        text = read(root, rel) or ""
        section = re.search(r"Acceptance criteria owned:?(.*?)(?:\n#{1,3} |\nNO_DIFF_EXPECTED|\Z)",
                            text, re.S | re.IGNORECASE)
        owned[repo] = set(re.findall(r"\bAC-\d+\b", section.group(1))) if section else set()

    assigned = set().union(*owned.values()) if owned else set()
    if spec_acs:
        uncovered = sorted(spec_acs - assigned)
        checks.append(Check("every acceptance criterion is owned by a contract", not uncovered,
                            "all covered" if not uncovered
                            else "no contract owns: " + ", ".join(uncovered)))

        unknown = sorted(assigned - spec_acs)
        checks.append(Check("no contract references an unknown criterion", not unknown,
                            "none" if not unknown
                            else "not in the validated specification: " + ", ".join(unknown)))

        empty = sorted(r for r, a in owned.items() if not a)
        checks.append(Check("each repository contract owns at least one criterion", not empty,
                            "both own criteria" if not empty
                            else "owns none: " + ", ".join(empty)
                                 + " -- a repository with no criteria leaves its Stage 5 validator "
                                   "nothing to judge. Expecting no code change is NO_DIFF_EXPECTED, "
                                   "which is a different statement"))

        # Presence is not enough: the field decides whether Stage 4 expects a diff at all, so a
        # value that is neither true nor false leaves that undecided while looking answered.
        bad_decl = []
        for r, rel in BRIEFS.items():
            text = read(root, rel) or ""
            if "NO_DIFF_EXPECTED" not in text:
                bad_decl.append(f"{r} (missing)")
            elif not re.search(r"NO_DIFF_EXPECTED\s*:\s*(true|false)\b", text, re.IGNORECASE):
                bad_decl.append(f"{r} (not true or false)")
        checks.append(Check("each contract declares a valid diff expectation", not bad_decl,
                            "both declare NO_DIFF_EXPECTED: true|false" if not bad_decl
                            else "NO_DIFF_EXPECTED " + ", ".join(bad_decl)))

    for repo, rel in BRIEFS.items():
        brief = read(root, rel)
        if brief is None:
            checks.append(Check(f"agent brief: {repo}", False, f"{rel} not found"))
            continue
        blow = brief.lower()
        missing = [label for label, words in BRIEF_SECTIONS
                   if not any(w in blow for w in words)]
        checks.append(Check(f"agent brief: {repo}", not missing,
                            "all required sections present" if not missing
                            else "missing: " + ", ".join(missing)))

        # The working boundary and the stop boundary. The tool grant is not checked here: it is
        # fixed in the repo-implementer definition, not chosen per task.
        has_allowed = "allowed" in blow
        has_excluded = "excluded" in blow
        has_stop = "stop" in blow
        bounded = has_allowed and has_excluded and has_stop
        checks.append(Check(f"boundaries stated: {repo}", bounded,
                            "allowed scope, excluded scope and stop conditions present" if bounded
                            else "an agent contract without both a working boundary and a stop "
                                 "boundary is unbounded"))

    return checks


def write_status(root: pathlib.Path, checks: list[Check]) -> dict:
    ready = all(c.passed for c in checks)
    status = {
        "valid": ready,
        "status": "READY" if ready else "DRAFT",
        "structural_checks": len(checks),
        "structural_checks_passed": sum(1 for c in checks if c.passed),
        "semantic_authority": "human-reviewed",
        "note": "Structural readiness only. Whether the chosen rollout order is correct, and "
                "whether ownership was assigned to the right service, remain human rulings.",
    }
    (root / STATUS_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / STATUS_PATH).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status


def self_test() -> int:
    """Every rule the gate claims to enforce gets a case that fails without it."""
    import tempfile

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "docs/plans").mkdir(parents=True)
        (root / "docs/plans/orchestration-plan.md").write_text("# Plan\n\nWe will fix the bugs.\n")
        checks = validate(root)
        results.append(("an empty plan is refused", not all(c.passed for c in checks),
                        f"{sum(1 for c in checks if not c.passed)} failing check(s)"))

    # ---- one scaffold, mutated per case -------------------------------------------------------
    SPEC = "| OQ-1 | derivation | Open |\nAC-1 AC-2 AC-3 AC-4 AC-5\n"
    PLAN = """# Orchestration plan

Work is split across pgs-tta and pgs-payment-processor.

pgs-tta owns AC-1, AC-3 and AC-4. pgs-payment-processor owns AC-5 and confirms AC-2.

Rollout order: the producer change lands first, because the additive contract keeps the previous
consumer working, so the two can coexist while the change is in flight.

Compatibility is demonstrated by the pair verification harness.

Void flows and settlement generation are out of scope and are not work in this plan.
OQ-1 remains open and is not authorised for implementation.
"""
    BRIEF = """# Brief

## Outcome
## Authoritative inputs
## Repository scope
## Allowed areas
## Excluded areas
## Acceptance criteria owned
{acs}
NO_DIFF_EXPECTED: {nodiff}
## Verification required
run the repository's full Maven verification before returning
## Dependencies on the other repository
## Stop conditions
{stop}
"""

    def build(plan=PLAN, spec=SPEC, tta=None, proc=None):
        tmp = tempfile.mkdtemp()
        root = pathlib.Path(tmp)
        (root / "docs/plans").mkdir(parents=True)
        (root / "docs/agent-briefs").mkdir(parents=True)
        (root / "specs").mkdir(parents=True)
        (root / "specs/refund-seam-phase1.spec.md").write_text(spec)
        (root / "docs/plans/orchestration-plan.md").write_text(plan)
        default = dict(acs="AC-1 AC-2 AC-3 AC-4 AC-5", nodiff="false",
                       stop="Stop and report if the specification is silent.")
        (root / BRIEFS["pgs-tta"]).write_text(BRIEF.format(**{**default, **(tta or {})}))
        (root / BRIEFS["pgs-payment-processor"]).write_text(
            BRIEF.format(**{**default, **(proc or {})}))
        return root

    def failing(root):
        return [c.name for c in validate(root) if not c.passed]

    def case(label, root, expect_check=None):
        names = failing(root)
        if expect_check is None:
            results.append((label, not names, "all checks pass" if not names
                            else "failing: " + "; ".join(names)))
        else:
            results.append((label, expect_check in names,
                            "refused" if expect_check in names else f"NOT refused ({names})"))

    # a valid plan, with the same AC owned by both repositories -- legitimate when each side must
    # provide its own local evidence for the criterion
    case("a valid plan reaches READY, cross-repository AC assignment accepted", build())

    case("an unassigned acceptance criterion is refused",
         build(tta={"acs": "AC-1"}, proc={"acs": "AC-2"}),
         "every acceptance criterion is owned by a contract")

    case("an invented acceptance criterion is refused",
         build(tta={"acs": "AC-1 AC-2 AC-3 AC-4 AC-5 AC-9"}),
         "no contract references an unknown criterion")

    case("an open authority item assigned for implementation is refused",
         build(tta={"acs": "AC-1 AC-2 AC-3 AC-4 AC-5\nImplement OQ-1 in this repository."}),
         "open authority items did not become tasks")

    no_stop = build()
    brief = no_stop / BRIEFS["pgs-tta"]
    text = brief.read_text(encoding="utf-8")
    brief.write_text(text.split("## Stop conditions")[0], encoding="utf-8")
    case("missing stop conditions is refused", no_stop, "agent brief: pgs-tta")

    case("a rollout order with no rationale is refused",
         build(plan=PLAN.replace(
             "Rollout order: the producer change lands first, because the additive contract keeps "
             "the previous\nconsumer working, so the two can coexist while the change is in "
             "flight.", "Rollout order: the producer change lands first.")),
         "rollout order states its rationale")

    case("a non-boolean NO_DIFF_EXPECTED is refused",
         build(tta={"nodiff": "maybe"}), "each contract declares a valid diff expectation")

    ok = True
    for label, passed, detail in results:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}  --  {detail}")
        ok = ok and passed
    print()
    print(f"validate_plan self-test: {sum(1 for _, p, _ in results if p)} passed, "
          f"{sum(1 for _, p, _ in results if not p)} failed")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = pathlib.Path(__file__).resolve().parents[2]
    if not (root / PLAN_PATH).is_file():
        print(f"orchestration plan not found at {PLAN_PATH}")
        print("Stage 3 produces it, together with one implementation brief per repository.")
        return 2

    checks = validate(root)
    print(f"plan: {PLAN_PATH}\n")
    width = max(len(c.name) for c in checks)
    for c in checks:
        print(f"  [{'PASS' if c.passed else 'FAIL'}] {c.name:<{width}}  {c.detail}")
    status = write_status(root, checks)
    print(f"\n  {status['structural_checks_passed']}/{status['structural_checks']} structural "
          f"checks  ->  {status['status']}")
    print(f"  wrote {STATUS_PATH}")
    return 0 if status["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
