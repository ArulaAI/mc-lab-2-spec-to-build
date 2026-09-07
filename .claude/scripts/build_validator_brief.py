#!/usr/bin/env python3
"""build_validator_brief.py -- assemble one fresh-context brief per repository.

The separation this protects
----------------------------
A validator that inherits the builder's reasoning inherits the builder's confidence, and confidence
is the thing that most needs checking. Each brief is assembled **mechanically from an allowlist**:
the validated specification, the two authoritative scope documents, that repository's agent
contract, that repository's diff, and that repository's verification evidence.

No chat history. No builder rationale. No agent return summaries. Not because this script is
careful about leaving them out, but because it has no way to reach them: the allowlist is the whole
of its input. That is a stronger guarantee than an instruction to be discreet, and it is the reason
this is a script rather than a prompt.

Why two briefs rather than one
------------------------------
A single combined brief hands both validators the same package, including the other repository's
implementation. That has two costs. The obvious one is context the validator does not need. The
subtle and worse one is that a reviewer holding both diffs stops judging *this* repository against
*its* criteria and starts reviewing the change as a whole -- which is the pair harness's job, and
the harness does it deterministically. Splitting the evidence is what keeps the two judgements
independent.

Each brief carries the shared authority both validators need -- the specification and the two scope
documents -- and nothing of the other repository's internals. The scope documents are not optional:
without them a validator can only ask "does the diff do what it claims", never "was something
required omitted" or "was something excluded built anyway". The second pair of questions is where
the resist-and-record judgement lives.

    python3 .claude/scripts/build_validator_brief.py
    python3 .claude/scripts/build_validator_brief.py --check      # verify sources, write nothing
    python3 .claude/scripts/build_validator_brief.py --self-test
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

# Authority both validators need. Shared, not repository-specific.
SHARED = [
    ("Specification under review", "specs/refund-seam-phase1.spec.md"),
    ("Specification readiness status", "specs/spec.status.json"),
    ("Out of scope (authoritative)", "specs/OUT_OF_SCOPE.md"),
    ("Non-negotiables (authoritative)", "specs/NON_NEGOTIABLES.md"),
]

# repo -> (output brief, that repository's agent contract)
REPOS = {
    "pgs-tta": ("docs/validator-brief-tta.md",
                "docs/agent-briefs/tta-implementation-brief.md"),
    "pgs-payment-processor": ("docs/validator-brief-payment-processor.md",
                              "docs/agent-briefs/processor-implementation-brief.md"),
}

INSTRUCTIONS = """\
## What you are being asked to do

Judge whether **{repo}** satisfies the acceptance criteria its agent contract owns, without having
seen the work being done.

You have the specification, the two authoritative scope documents, this repository's contract, its
diff and its verification evidence. You do not have the builder's reasoning, and you do not have
the other repository's implementation. Both omissions are deliberate: your value here is that you
cannot inherit anyone's confidence, and cross-repository behaviour is proven deterministically by
the pair harness rather than judged by you.

Report every finding in this shape:

```
REPOSITORY: {repo}
AC:
VERDICT: PASS | FAIL | UNVERIFIED
FINDING:
EVIDENCE:
```

Rules for your report:

1. **Judge the repository, not the diff.** Current code, tests, verification evidence and the diff
   where one exists. **No diff is not automatically a failure** -- a contract may declare
   `NO_DIFF_EXPECTED: true`, in which case the question is whether the owned criteria are already
   satisfied by code that was already there.
2. **Cite evidence.** File and line, or the verification output. A finding you cannot point at is
   `UNVERIFIED`, which is a real verdict and not a softer way of saying FAIL.
3. **Check scope in both directions.** Something the specification requires and this repository
   does not do is a finding. So is something `OUT_OF_SCOPE.md` excludes that was built anyway.
4. **Stay inside this repository.** If judging a criterion would need the other side, say so and
   mark it `UNVERIFIED`. Do not infer what the other repository does.
5. **Do not propose fixes.** You have no write tools by design. Whether a finding is material, and
   what to do about it, is the coordinating engineer's ruling -- a finding does not authorise a
   change.
"""


def run(cmd: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def fence(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text.rstrip()}\n```\n"


def build(root: pathlib.Path, repo: str, contract_rel: str,
          run_verification: bool = True) -> tuple[str, list[str]]:
    missing: list[str] = []
    parts = [
        f"# Validator brief — {repo}",
        "",
        f"Assembled mechanically for **{repo}** alone. Every section comes from a file on a fixed "
        "allowlist. No conversation, rationale or agent summary is included, and none is reachable "
        "by the script that produced this. The other repository's implementation is deliberately "
        "absent.",
        "",
        INSTRUCTIONS.format(repo=repo),
        "---",
        "",
    ]

    for title, rel in SHARED + [(f"Agent contract — {repo}", contract_rel)]:
        path = root / rel
        parts.append(f"## {title}\n\n*Source: `{rel}`*\n")
        if path.is_file():
            parts.append(fence(path.read_text(encoding="utf-8").strip(),
                               "json" if rel.endswith(".json") else "markdown"))
        else:
            missing.append(rel)
            parts.append("*Not present in the workspace.*\n")
        parts.append("")

    repo_path = root / repo
    parts.append(f"## Change under review — `{repo}`\n")
    if not (repo_path / ".git").is_dir():
        missing.append(f"{repo}/.git")
        parts.append("*Repository not initialised; no diff available.*\n\n")
    else:
        diff = run(["git", "diff", "HEAD"], repo_path)
        stat = run(["git", "diff", "--stat", "HEAD"], repo_path)
        parts.append("*Source: `git diff HEAD`*\n")
        if not diff.stdout.strip():
            parts.append("*No changes against the starter commit. If this repository's contract "
                         "declares `NO_DIFF_EXPECTED: true`, judge whether the owned criteria are "
                         "already satisfied.*\n\n")
        else:
            parts.append(fence(stat.stdout, "text"))
            parts.append(fence(diff.stdout, "diff"))
    parts.append("")

    parts.append(f"## Verification evidence — `{repo}`\n")
    if run_verification and (repo_path / "pom.xml").is_file():
        mvn = shutil.which("mvn") or "mvn"
        result = run([mvn, "-B", "-f", str(repo_path / "pom.xml"), "verify"], root)
        summary = [ln for ln in result.stdout.splitlines()
                   if "Tests run:" in ln or "BUILD SUCCESS" in ln or "BUILD FAILURE" in ln]
        parts.append(f"*Source: `mvn -B -f {repo}/pom.xml verify`*\n")
        parts.append(fence("\n".join(summary) or "the build produced no summary", "text"))
        parts.append(f"\nResult: **{'GREEN' if result.returncode == 0 else 'RED'}**\n")
    else:
        parts.append("*Verification not run.*\n")

    return "\n".join(parts), missing


def other_repo(repo: str) -> str:
    return next(r for r in REPOS if r != repo)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify sources; write nothing")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(__file__).resolve().parents[2]

    if args.self_test:
        return self_test(root)

    if args.check:
        allmissing = []
        for repo, (_, contract) in REPOS.items():
            _, missing = build(root, repo, contract, run_verification=False)
            allmissing += [f"{repo}: {m}" for m in missing]
        print(f"briefs to assemble: {len(REPOS)}   allowlisted sources each: {len(SHARED) + 3}")
        if allmissing:
            print("missing:")
            for m in allmissing:
                print(f"  - {m}")
            return 1
        print("all sources present")
        return 0

    for repo, (out_rel, contract) in REPOS.items():
        brief, missing = build(root, repo, contract)
        (root / out_rel).write_text(brief, encoding="utf-8")
        print(f"wrote {out_rel}  ({len(brief.splitlines())} lines)")
        for m in missing:
            print(f"    missing source: {m}")

    print("\nEach validator gets its own brief. Dispatch two fresh validators in parallel, one")
    print("brief each, with read and test tools and no write tools. Do not hand both the same")
    print("package: a reviewer holding both diffs starts reviewing the change as a whole, which")
    print("is the pair harness's job and is already answered deterministically.")
    return 0


def self_test(root: pathlib.Path) -> int:
    """The property that matters is that neither brief carries the other repository's diff."""
    cases = []
    briefs = {}
    for repo, (_, contract) in REPOS.items():
        briefs[repo], _ = build(root, repo, contract, run_verification=False)

    for repo, text in briefs.items():
        other = other_repo(repo)
        cases.append((f"{repo} brief names its own repository",
                      f"# Validator brief — {repo}" in text, ""))
        cases.append((f"{repo} brief carries no diff header from {other}",
                      f"## Change under review — `{other}`" not in text, ""))
        cases.append((f"{repo} brief carries the scope documents",
                      "OUT_OF_SCOPE.md" in text and "NON_NEGOTIABLES.md" in text, ""))
        cases.append((f"{repo} brief states no-diff is not automatic failure",
                      "not automatically a failure" in text, ""))
        cases.append((f"{repo} brief allows UNVERIFIED",
                      "UNVERIFIED" in text, ""))

    ok = True
    for label, passed, detail in cases:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}  {detail}")
        ok = ok and passed
    print()
    print(f"build_validator_brief self-test: {sum(1 for _, p, _ in cases if p)} passed, "
          f"{sum(1 for _, p, _ in cases if not p)} failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
