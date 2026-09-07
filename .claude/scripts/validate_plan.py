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

BRIEF_SECTIONS = [
    "outcome",
    "authoritative inputs",
    "repository scope",
    "allowed areas",
    "excluded areas",
    "tools allowed",
    "acceptance criteria owned",
    "expected return shape",
    "stop conditions",
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
    has_reason = has_rollout and ("because" in low or "so that" in low or "reason" in low)
    checks.append(Check("rollout order is stated with a rationale", has_reason,
                        "order and reasoning present" if has_reason
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

    open_qs = read(root, "specs/refund-seam-phase1.spec.md") or ""
    oq_ids = set(re.findall(r"\bOQ-\d+\b", open_qs))
    tasked = sorted(q for q in oq_ids if q in plan and
                    not re.search(re.escape(q) + r"[^.\n]{0,80}(open|unresolved|escalat)", plan,
                                  re.IGNORECASE))
    checks.append(Check("unresolved questions did not become tasks", not tasked,
                        "none" if not tasked
                        else "planned as work rather than left open: " + ", ".join(tasked)))

    for repo, rel in BRIEFS.items():
        brief = read(root, rel)
        if brief is None:
            checks.append(Check(f"agent brief: {repo}", False, f"{rel} not found"))
            continue
        blow = brief.lower()
        missing = [s for s in BRIEF_SECTIONS if s.split()[0] not in blow]
        checks.append(Check(f"agent brief: {repo}", not missing,
                            "all required sections present" if not missing
                            else "missing: " + ", ".join(missing)))

        has_tools = "tools" in blow
        has_stop = "stop" in blow
        checks.append(Check(f"boundaries stated: {repo}", has_tools and has_stop,
                            "tool permissions and stop conditions present" if has_tools and has_stop
                            else "an agent without tool limits or stop conditions is unbounded"))

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
    """An empty plan must fail and a complete one must pass, or the gate is decorative."""
    import tempfile

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "docs/plans").mkdir(parents=True)
        (root / "docs/plans/orchestration-plan.md").write_text("# Plan\n\nWe will fix the bugs.\n")
        checks = validate(root)
        results.append(("an empty plan is refused", not all(c.passed for c in checks),
                        f"{sum(1 for c in checks if not c.passed)} failing check(s)"))

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "docs/plans").mkdir(parents=True)
        (root / "docs/agent-briefs").mkdir(parents=True)
        (root / "specs").mkdir(parents=True)
        (root / "specs/refund-seam-phase1.spec.md").write_text("| OQ-1 | derivation | Open |")
        (root / "docs/plans/orchestration-plan.md").write_text("""# Orchestration plan

Work is split across pgs-tta and pgs-payment-processor.

pgs-tta owns AC-1, AC-3 and AC-4. pgs-payment-processor owns AC-5 and confirms AC-2.

Rollout order: the producer change lands first, because the additive contract keeps the previous
consumer working, so the two can coexist while the change is in flight.

Compatibility is demonstrated by the pair verification harness.

Void flows and settlement generation are out of scope and are not work in this plan.
OQ-1 remains open and is escalated, not answered.
""")
        for rel in BRIEFS.values():
            (root / rel).write_text("""# Brief

## Outcome
## Authoritative inputs
## Repository scope
## Allowed areas
## Excluded areas
## Tools allowed
## Acceptance criteria owned
AC-1
## Dependencies on the other repository
## Expected return shape
## Stop conditions
Stop and report if the specification is silent.
""")
        checks = validate(root)
        failing = [c.name for c in checks if not c.passed]
        results.append(("a complete plan is accepted", not failing,
                        "all checks pass" if not failing else "failing: " + "; ".join(failing)))

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
