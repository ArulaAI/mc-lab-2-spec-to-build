#!/usr/bin/env python3
"""run_pair_verification.py -- prove the seam, not the two repositories.

Two green repositories are not evidence that the change is correct. Correctness across a service
boundary lives in the relationship between the two implementations, and only a test that exercises
both at once can see it.

    python3 scripts/run_pair_verification.py            # install both services, run the harness
    python3 scripts/run_pair_verification.py --quick    # skip the install step
    python3 scripts/run_pair_verification.py --explain  # describe the compatibility matrix

Why this is a script rather than a Maven command: the harness resolves both services as
dependencies, so each has to be installed to the local repository first, and in that order.
Getting the order wrong produces a confusing resolution error rather than a useful failure.
Written in Python rather than shell so it behaves the same on a managed Windows laptop.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVICES = ("pgs-payment-processor", "pgs-tta")
HARNESS = ROOT / "lab-harness" / "pair-verification"

MATRIX = """
compatibility matrix -- what the harness is actually asking

    previous consumer -> previous producer     baseline; the world before this change
    previous consumer -> current producer      must succeed. This is what makes it safe to
                                               deploy the producer first.
    current consumer  -> previous producer     must be shown to fail. This is why the reverse
                                               order is unsafe. The test PASSES by detecting it.
    current consumer  -> current producer      the intended final state

The rule this supports is not "always deploy the producer first". It is: derive a sequence in
which old and new can coexist safely. For this particular additive change that sequence happens
to be producer first -- and the evidence is in the matrix rather than in an assertion.
"""


def mvn() -> str:
    return shutil.which("mvn") or "mvn"


def run(cmd: list[str], cwd: pathlib.Path) -> int:
    print(f"\n$ {' '.join(cmd)}   ({cwd.relative_to(ROOT)})")
    return subprocess.run(cmd, cwd=cwd).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="skip installing the services first")
    parser.add_argument("--explain", action="store_true", help="describe the matrix and exit")
    args = parser.parse_args()

    if args.explain:
        print(MATRIX)
        return 0

    missing = [s for s in SERVICES if not (ROOT / s / "pom.xml").is_file()]
    if missing:
        print(f"service repositories not found: {', '.join(missing)}")
        print("Run: python3 scripts/verify_setup.py")
        return 2

    if not args.quick:
        for service in SERVICES:
            # Tests are skipped here on purpose: this step exists to publish the artifacts the
            # harness resolves. Each repository's own suite is a separate question, and running it
            # twice would only make this slower.
            code = run([mvn(), "-B", "-q", "install", "-DskipTests"], cwd=ROOT / service)
            if code != 0:
                print(f"\ncould not install {service}. Fix its build first: "
                      f"cd {service} && mvn verify")
                return code

    code = run([mvn(), "-B", "clean", "verify"], cwd=HARNESS)

    # Record the outcome so the result is reviewable afterwards without re-running the harness.
    result_file = ROOT / "docs" / "pair-result.txt"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(
        f"pair verification: {'GREEN' if code == 0 else 'RED'}\n"
        f"exit status: {code}\n")

    print()
    if code == 0:
        print("PAIR VERIFICATION GREEN -- the represented seam holds.")
        print()
        print("What this does and does not establish: it proves the seam represented in this lab")
        print("is internally consistent, contract-compatible and tested locally. It is not a claim")
        print("that the wider PGS refund capability is production-ready, and it does not replace")
        print("integration or release governance.")
    else:
        print("PAIR VERIFICATION RED -- the two services do not agree at the seam.")
        print()
        print("Each failure names the disagreement in its assertion message. Read those before")
        print("changing anything: the failing test tells you which side is asserting what, and")
        print("which side owns the decision is a ruling for you to make, not for the test.")
    return code


if __name__ == "__main__":
    sys.exit(main())
