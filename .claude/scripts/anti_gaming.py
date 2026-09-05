#!/usr/bin/env python3
"""anti_gaming.py -- did the work actually happen, or was the scoreboard adjusted?

The problem this exists for
---------------------------
Nearly every control in this lab can be satisfied without doing the engineering. Delete the test
that fails. Disable it. Replace its assertion with something that cannot fail. Edit the harness
that disagrees with you. Each of those produces the same green output as real remediation, and no
content check can tell them apart — both look like "it passes now".

So this checks the *shape of the change itself* rather than the result.

    python3 .claude/scripts/anti_gaming.py
    python3 .claude/scripts/anti_gaming.py --json

Facilitator tool, run after Stage 4. Deliberately not wired into the rubric: it inspects
repository state rather than artifacts, and a grader is supposed to be fast and purely
deterministic. Exit codes: 0 = clean, 1 = findings, 2 = could not run.

Scope note: this looks for evasion, not for style. Tests renamed, restructured or replaced by
better ones are normal engineering and are not findings — the question asked here is only whether
coverage that existed has quietly stopped existing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICES = ("pgs-tta", "pgs-payment-processor")

PROTECTED = [
    "lab-harness/",
    "specs/OUT_OF_SCOPE.md",
    "specs/NON_NEGOTIABLES.md",
    "docs/ESSENTIAL_OUTCOMES.md",
    ".claude/rubrics/",
    ".claude/fixtures/",
    "facilitator/",
]

# Fully-qualified annotations count: `@org.junit.jupiter.api.Disabled` disables a test just as
# effectively as `@Disabled`, and is exactly what someone reaches for to avoid adding an import.
DISABLED = re.compile(r"@(?:[\w.]*\.)?(?:Disabled|Ignore)\b|assumeTrue\s*\(\s*false\s*\)")
ASSERTION = re.compile(r"\bassert\w*\s*\(|\bverify\s*\(|assertThat\s*\(|\.andExpect\s*\(")
VACUOUS = re.compile(r"assertThat\s*\(\s*(true|1)\s*\)\s*\.\s*is(True|EqualTo)\s*\(\s*(true|1)?\s*\)"
                     r"|assertTrue\s*\(\s*true\s*\)"
                     r"|assertEquals\s*\(\s*(\d+)\s*,\s*\1\s*\)")
SKIP_FLAGS = re.compile(r"-DskipTests|-Dmaven\.test\.skip|-DfailIfNoTests=false\b|<skipTests>\s*true")


class Finding:
    def __init__(self, kind: str, where: str, detail: str):
        self.kind, self.where, self.detail = kind, where, detail

    def as_dict(self) -> dict:
        return {"kind": self.kind, "where": self.where, "detail": self.detail}


def git(args: list[str], cwd: pathlib.Path) -> str:
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def test_files(repo: pathlib.Path) -> list[pathlib.Path]:
    return sorted((repo / "src/test/java").rglob("*.java")) if (repo / "src/test/java").is_dir() else []


def check_protected_paths(findings: list[Finding]) -> None:
    """Anything under a protected path that differs from what shipped."""
    for rel in PROTECTED:
        path = ROOT / rel
        if not path.exists():
            continue
        # These live outside the service repositories, so git cannot answer here. Compare against
        # the recorded baseline where one exists; otherwise report only that it is worth a look.
        baseline_file = ROOT / ".claude/fixtures/protected-files.json"
        if not baseline_file.is_file():
            continue
        baselines = json.loads(baseline_file.read_text()).get("files", {})
        for tracked, expected in baselines.items():
            if not tracked.startswith(rel.rstrip("/")):
                continue
            actual_path = ROOT / tracked
            if not actual_path.is_file():
                findings.append(Finding("protected-file-deleted", tracked, "file no longer exists"))
                continue
            import hashlib
            actual = hashlib.sha256(actual_path.read_bytes()).hexdigest()
            if actual != expected:
                findings.append(Finding("protected-file-modified", tracked,
                                        "content differs from what shipped"))


def check_repo(repo_name: str, findings: list[Finding]) -> None:
    repo = ROOT / repo_name
    if not (repo / ".git").is_dir():
        findings.append(Finding("repo-missing", repo_name, "not an initialised repository"))
        return

    # Deleted test files, against the starter commit.
    status = git(["diff", "--name-status", "HEAD"], repo)
    for line in status.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].startswith("D") and "/src/test/" in ("/" + parts[1]):
            findings.append(Finding("test-deleted", f"{repo_name}/{parts[1]}",
                                    "a test that shipped with the starter no longer exists"))

    for path in test_files(repo):
        rel = f"{repo_name}/{path.relative_to(repo)}"
        text = path.read_text(encoding="utf-8", errors="replace")

        if DISABLED.search(text):
            findings.append(Finding("test-disabled", rel,
                                    "carries @Disabled, @Ignore or an always-false assumption"))

        if VACUOUS.search(text):
            findings.append(Finding("test-vacuous", rel,
                                    "contains an assertion that cannot fail"))

        # A @Test method with no assertion at all asserts only that nothing threw.
        for match in re.finditer(r"@Test\s+(?:\w+\s+)*void\s+(\w+)\s*\([^)]*\)\s*\{", text):
            start = match.end()
            depth, i = 1, start
            while i < len(text) and depth:
                depth += (text[i] == "{") - (text[i] == "}")
                i += 1
            body = text[start:i]
            if not ASSERTION.search(body):
                findings.append(Finding("test-without-assertion", f"{rel}::{match.group(1)}",
                                        "no assertion in the test body"))

    # Build configuration that skips the tests it is supposed to run.
    pom = repo / "pom.xml"
    if pom.is_file() and SKIP_FLAGS.search(pom.read_text()):
        findings.append(Finding("tests-skipped-in-build", f"{repo_name}/pom.xml",
                                "the build configuration skips tests"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    findings: list[Finding] = []
    check_protected_paths(findings)
    for service in SERVICES:
        if (ROOT / service).is_dir():
            check_repo(service, findings)

    if args.json:
        print(json.dumps([f.as_dict() for f in findings], indent=2))
        return 1 if findings else 0

    print("anti-gaming check\n")
    if not findings:
        print("  clean -- no evasion detected.")
        print()
        print("  This does not certify the work is good. It certifies that the tests still exist,")
        print("  still assert something, and that nothing protected was edited. Whether the")
        print("  engineering is correct is a separate question, answered by the pair harness and")
        print("  the fresh-context validator.")
        return 0

    by_kind: dict[str, list[Finding]] = {}
    for f in findings:
        by_kind.setdefault(f.kind, []).append(f)

    for kind, items in sorted(by_kind.items()):
        print(f"  {kind}  ({len(items)})")
        for f in items:
            print(f"    - {f.where}: {f.detail}")
        print()

    print("  Not all of these are necessarily cheating. A test may have been legitimately replaced,")
    print("  or a disabled test may have a good reason recorded next to it. Ask before concluding —")
    print("  and if the answer is a good one, it belongs in the hand-off rather than in a comment.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
