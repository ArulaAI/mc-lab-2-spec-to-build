#!/usr/bin/env python3
"""verify_setup.py -- prepare and check the Lab 2 workspace. Run this BEFORE session day.

What it does
------------
1. Checks the toolchain: a JDK, Maven, Git and Python.
2. Creates the two service repositories from ``starter/``, each as a real Git repository with a
   single committed starter commit. Stage 5 compares work against that commit, so a repository
   without a committed HEAD cannot be reviewed.
3. Warms the Maven cache by building both repositories.
4. Confirms the expected starting state: each repository green on its own, the pair harness red.

    python3 scripts/verify_setup.py            # set up and check
    python3 scripts/verify_setup.py --check    # check only, change nothing
    python3 scripts/verify_setup.py --reset    # DESTRUCTIVE: discard the working copies and restore

Setup runs outside live session time. The first Maven build on a cold cache downloads
dependencies, and a room of thirty people discovering that at minute three loses the lab.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVICES = ("pgs-tta", "pgs-payment-processor")
MIN_JAVA = 17
MIN_MAVEN = (3, 9)


class Result:
    def __init__(self) -> None:
        self.problems: list[str] = []

    def check(self, label: str, ok: bool, detail: str, fatal: bool = True) -> bool:
        print(f"  [{'ok' if ok else 'FAIL'}] {label:<34} {detail}")
        if not ok and fatal:
            self.problems.append(f"{label}: {detail}")
        return ok


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)


def tool(name: str) -> str | None:
    return shutil.which(name)


def check_toolchain(r: Result) -> None:
    print("\ntoolchain")

    java = tool("java")
    version = "not found"
    ok = False
    if java:
        out = run([java, "-version"]).stderr
        m = re.search(r'version "?(\d+)', out)
        if m:
            major = int(m.group(1))
            ok = major >= MIN_JAVA
            version = f"Java {major}" + ("" if ok else f" (need {MIN_JAVA} or newer)")
    r.check("JDK", ok, version)

    mvn = tool("mvn")
    version, ok = "not found", False
    if mvn:
        out = run([mvn, "-v"]).stdout
        m = re.search(r"Apache Maven (\d+)\.(\d+)", out)
        if m:
            found = (int(m.group(1)), int(m.group(2)))
            ok = found >= MIN_MAVEN
            version = f"Maven {found[0]}.{found[1]}" + ("" if ok else " (need 3.9 or newer)")
    r.check("Maven", ok, version)

    git = tool("git")
    r.check("Git", bool(git), run([git, "--version"]).stdout.strip() if git else "not found")

    r.check("Python", sys.version_info >= (3, 9),
            f"Python {sys.version_info.major}.{sys.version_info.minor}")


def check_workspace(r: Result) -> None:
    print("\nworkspace")
    for rel in ["starter", "lab-harness/pair-verification", "specs/refund-seam-phase1.spec.md",
                ".claude/hooks/gate_guard.py", ".claude/scripts/validate_spec.py"]:
        r.check(rel, (ROOT / rel).exists(), "present" if (ROOT / rel).exists() else "MISSING")

    gate = run([sys.executable, str(ROOT / ".claude/hooks/gate_guard.py"), "--self-test"])
    passed = "0 failed" in gate.stdout
    r.check("write gate self-test", passed,
            gate.stdout.strip().splitlines()[-1] if gate.stdout else "did not run")


def existing_work(service: pathlib.Path) -> bool:
    """True if the working copy holds commits or uncommitted changes beyond the starter commit."""
    if not (service / ".git").is_dir():
        return False
    log = run(["git", "log", "--oneline"], cwd=service).stdout.strip().splitlines()
    dirty = run(["git", "status", "--porcelain"], cwd=service).stdout.strip()
    return len(log) > 1 or bool(dirty)


def create_repos(r: Result, reset: bool) -> None:
    print("\nservice repositories")
    for name in SERVICES:
        target = ROOT / name
        source = ROOT / "starter" / name

        if target.exists() and not reset:
            has_work = existing_work(target)
            r.check(name, True,
                    "already present -- left untouched"
                    + (" (contains your work)" if has_work else ""), fatal=False)
            continue

        if target.exists() and reset:
            shutil.rmtree(target)

        shutil.copytree(source, target, ignore=shutil.ignore_patterns("target", "journey"))
        run(["git", "init", "-q"], cwd=target)
        run(["git", "add", "-A"], cwd=target)
        run(["git", "-c", "user.name=Lab Setup", "-c", "user.email=lab@example.invalid",
             "commit", "-q", "-m", "Starter state for Lab 2"], cwd=target)

        head = run(["git", "rev-parse", "--short", "HEAD"], cwd=target).stdout.strip()
        commits = len(run(["git", "log", "--oneline"], cwd=target).stdout.strip().splitlines())
        r.check(name, bool(head) and commits == 1,
                f"created, one starter commit at {head}")


def confirm_state(r: Result) -> None:
    print("\nexpected starting state (this also warms the Maven cache)")
    for name in SERVICES:
        result = run(["mvn", "-B", "clean", "verify"], cwd=ROOT / name)
        r.check(name, result.returncode == 0,
                "GREEN" if result.returncode == 0 else "RED -- each repository must build on its own")

    for name in SERVICES:
        run(["mvn", "-B", "-q", "install", "-DskipTests"], cwd=ROOT / name)

    harness = ROOT / "lab-harness" / "pair-verification"
    result = run(["mvn", "-B", "clean", "verify"], cwd=harness)
    red = result.returncode != 0
    r.check("pair verification", red,
            "RED, as expected at the start" if red
            else "GREEN -- it should be red before you begin; the seam is not correct yet")


def confirm_reset(targets: list[pathlib.Path]) -> bool:
    print("\n--reset is destructive.\n")
    print("  These directories will be DELETED and rebuilt from starter/.")
    print("  Any code you have written in them, and their entire Git history, will be lost:\n")
    for t in targets:
        marker = "  <-- contains work beyond the starter commit" if existing_work(t) else ""
        print(f"    {t.relative_to(ROOT)}{marker}")
    print()
    try:
        answer = input("  Type 'reset' to confirm, anything else to cancel: ").strip()
    except EOFError:
        print("  no confirmation possible on a non-interactive terminal -- cancelled")
        return False
    return answer == "reset"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="check only; do not create or modify anything")
    parser.add_argument("--reset", action="store_true",
                        help="DESTRUCTIVE: discard the service working copies and restore them")
    args = parser.parse_args()

    print("Lab 2 -- One Refund Across a Service Boundary")
    print("workspace setup and verification")

    if args.reset:
        targets = [ROOT / n for n in SERVICES if (ROOT / n).exists()]
        if targets and not confirm_reset(targets):
            print("\ncancelled. Nothing was changed.")
            return 1

    r = Result()
    check_toolchain(r)
    check_workspace(r)

    if not args.check:
        create_repos(r, reset=args.reset)
        confirm_state(r)

    print()
    if r.problems:
        print("SETUP INCOMPLETE:")
        for p in r.problems:
            print(f"  - {p}")
        print("\nResolve these before session day.")
        return 1

    print("Setup complete. Both service repositories are ready and the starting state is correct.")
    if not args.check:
        print("\nOpen this directory in Claude Code and run /lab to begin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
