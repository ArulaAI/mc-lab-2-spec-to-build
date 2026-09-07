#!/usr/bin/env python3
"""build_validator_brief.py -- assemble the Stage 5 brief for a fresh judging context.

The separation this protects
----------------------------
A validator that inherits the builder's reasoning inherits the builder's confidence, and confidence
is the thing that most needs checking. So the brief is assembled **mechanically from an allowlist**:
the validated specification, both repository diffs, the context ledger, the pair-verification
result, the orchestration plan, and the two scope documents.

No chat history. No builder rationale. No agent return summaries. Not because this script is
careful about leaving them out, but because it has no way to reach them: the allowlist is the whole
of its input. That is a stronger guarantee than an instruction to be discreet, and it is the reason
this is a script rather than a prompt.

    python3 .claude/scripts/build_validator_brief.py
    python3 .claude/scripts/build_validator_brief.py --check   # verify sources, write nothing
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

OUTPUT = "docs/validator-brief.md"

# The complete input surface. Anything not named here cannot reach the validator.
ALLOWLIST = [
    ("Specification under review", "specs/refund-seam-phase1.spec.md"),
    ("Specification readiness status", "specs/spec.status.json"),
    ("Out of scope (authoritative)", "specs/OUT_OF_SCOPE.md"),
    ("Non-negotiables (authoritative)", "specs/NON_NEGOTIABLES.md"),
    ("Context ledger", "docs/context-ledger.md"),
    ("Orchestration plan", "docs/plans/orchestration-plan.md"),
]
REPOS = ("pgs-tta", "pgs-payment-processor")

INSTRUCTIONS = """\
## What you are being asked to do

Judge whether the change below satisfies the specification, without having seen it being made.

You have the specification, both diffs, the reconciled context ledger, the plan, the deterministic
pair-verification result, and the two authoritative scope documents. You do not have the builder's
reasoning, and that is deliberate: your value here is that you cannot inherit their confidence.

Report against these headings:

```
## Verdict
## Acceptance criteria, one by one
## Contract findings
## Scope findings
## Compatibility findings
## Evidence paths
## Unverified assumptions
```

Rules for your report:

1. **Cite evidence.** Every finding names a file and, where it applies, a line. A finding you
   cannot point at belongs under Unverified assumptions.
2. **Judge against the specification, not against your preferences.** Code you would have written
   differently is not a finding. Code that does not satisfy an acceptance criterion is.
3. **Check what is absent.** An acceptance criterion with no corresponding change or test is a
   finding, and it is the kind a diff review most easily misses.
4. **Check scope in both directions.** Something built that the out-of-scope document excludes is a
   finding. So is something excluded that quietly reappeared.
5. **Do not propose fixes.** You have no write tools by design. Whether a finding is material, and
   what to do about it, is the coordinating engineer's ruling — a finding does not authorise a
   change.
"""


def run(cmd: list[str], cwd: pathlib.Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def fence(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text.rstrip()}\n```\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify sources; write nothing")
    args = parser.parse_args()

    root = pathlib.Path(__file__).resolve().parents[2]
    missing: list[str] = []
    parts: list[str] = [
        "# Validator brief — refund seam, phase 1",
        "",
        "Assembled mechanically. Every section below comes from a file on a fixed allowlist; "
        "no conversation, rationale or agent summary is included, and none is reachable by the "
        "script that produced this.",
        "",
        INSTRUCTIONS,
        "---",
        "",
    ]

    for title, rel in ALLOWLIST:
        path = root / rel
        parts.append(f"## {title}\n\n*Source: `{rel}`*\n")
        if path.is_file():
            content = path.read_text(encoding="utf-8").strip()
            parts.append(fence(content, "json" if rel.endswith(".json") else "markdown"))
        else:
            missing.append(rel)
            parts.append(f"*Not present in the workspace.*\n")
        parts.append("")

    for repo in REPOS:
        repo_path = root / repo
        parts.append(f"## Change under review — `{repo}`\n")
        if not (repo_path / ".git").is_dir():
            missing.append(f"{repo}/.git")
            parts.append("*Repository not initialised; no diff available.*\n\n")
            continue
        diff = run(["git", "diff", "HEAD"], repo_path)
        stat = run(["git", "diff", "--stat", "HEAD"], repo_path)
        parts.append("*Source: `git diff HEAD`*\n")
        if not diff.strip():
            parts.append("*No changes against the starter commit.*\n\n")
        else:
            parts.append(fence(stat, "text"))
            parts.append(fence(diff, "diff"))
        parts.append("")

    parts.append("## Deterministic pair-verification result\n")
    parts.append("*Source: `scripts/run_pair_verification.py`*\n")
    harness = root / "lab-harness" / "pair-verification"
    mvn = shutil.which("mvn") or "mvn"
    result = subprocess.run([mvn, "-B", "clean", "verify"], cwd=harness,
                            capture_output=True, text=True)
    summary = [ln for ln in result.stdout.splitlines()
               if "Tests run:" in ln or "BUILD SUCCESS" in ln or "BUILD FAILURE" in ln]
    parts.append(fence("\n".join(summary) or "harness did not produce a summary", "text"))
    parts.append(f"\nHarness exit status: **{'GREEN' if result.returncode == 0 else 'RED'}**\n")

    brief = "\n".join(parts)

    if args.check:
        print(f"allowlisted sources: {len(ALLOWLIST) + len(REPOS)}")
        if missing:
            print("missing:")
            for m in missing:
                print(f"  - {m}")
            return 1
        print("all sources present")
        return 0

    (root / OUTPUT).write_text(brief, encoding="utf-8")
    print(f"wrote {OUTPUT}  ({len(brief.splitlines())} lines)")
    if missing:
        print("\nassembled with missing sources:")
        for m in missing:
            print(f"  - {m}")
    print("\nNext: dispatch the fresh code-to-spec-validator against this brief.")
    print("It must run in a separate context, with read and test tools only and no write tools.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
