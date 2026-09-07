#!/usr/bin/env python3
"""check_matcher_drift.py -- is the write gate still covering the tools that exist?

The problem
-----------
`.claude/settings.json` registers the write gate against a matcher that names tools explicitly:

    Write|Edit|MultiEdit|NotebookEdit

That is an allowlist of tools to *intercept*. Anything not named runs unguarded, and nothing
announces it. So the gate's coverage is frozen at the moment it was authored, while the harness's
tool set moves: `MultiEdit` was in that matcher and is no longer offered, and a future version that
adds a write-capable tool under any other name would walk straight past the gate.

That is the same failure shape as a stale interpreter cache -- a control that stops applying
without saying so -- which is why it gets a check rather than a comment.

How it detects drift without knowing the future
-----------------------------------------------
It does not try to enumerate the harness's tools, which a script cannot do. It reads the journey
trail, which records the name of every tool actually used in a session, and compares that against
the matcher. Anything observed, not covered, and not on the known-harmless list is reported.

    python3 .claude/scripts/check_matcher_drift.py
    python3 .claude/scripts/check_matcher_drift.py --json
    python3 .claude/scripts/check_matcher_drift.py --self-test

Exit codes: 0 = no drift, 1 = review needed, 2 = could not read the configuration.

Run it in the facilitator pre-flight and in the post-change regression gate. A finding here is not
automatically a hole -- a new read-only tool is harmless -- but every finding needs a human ruling,
because the cost of guessing wrong is a control that looks present and is not.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETTINGS = ".claude/settings.json"
DEFAULT_JOURNEY_DIR = ".claude/journey"

# Tools that are known not to write files, or whose write capability is a documented,
# deliberately-accepted ceiling rather than drift.
#
# Bash is the notable entry: it can obviously write, and the gate does not intercept it. That is
# recorded in docs/CHALLENGE.md and in the facilitator key as the reason detection (hash
# comparison) rather than prevention is the actual control. Listing it here keeps the signal clean
# instead of reporting the same accepted limit on every run.
KNOWN_HARMLESS = {
    "Bash",           # documented ceiling -- shell redirection is not intercepted
    "Read", "Glob", "Grep", "LS",
    "Agent", "Task", "Skill", "SlashCommand",
    "TodoWrite",      # writes session todos, not repository files
    "WebFetch", "WebSearch", "ToolSearch", "ListPlugins", "ListSkills",
    "AskUserQuestion", "ExitPlanMode", "EnterPlanMode",
    "BashOutput", "KillShell", "Monitor",
}

# Names that suggest a file-mutating tool. Used only to rank an unknown tool's urgency, never to
# clear one: an unknown tool that does not match still gets reported, because a name is not a
# capability.
WRITE_SUSPICION = re.compile(
    r"write|edit|patch|create|replace|insert|append|modify|save|notebook|apply|move|delete|rename",
    re.IGNORECASE,
)


def read_matcher(root: pathlib.Path) -> str | None:
    path = root / SETTINGS
    if not path.is_file():
        return None
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None
    for entry in cfg.get("hooks", {}).get("PreToolUse", []):
        for hook in entry.get("hooks", []):
            if "gate_guard" in hook.get("command", ""):
                return entry.get("matcher", "")
    return None


def covered_tools(matcher: str) -> set[str]:
    return {t.strip() for t in matcher.split("|") if t.strip()}


def observed_tools(root: pathlib.Path) -> dict[str, int]:
    """Every distinct tool name in the journey trail, with a use count."""
    configured = os.environ.get("WORKBENCH_JOURNEY_DIR", DEFAULT_JOURNEY_DIR)
    if not os.path.isabs(configured):
        configured = str(root / configured)

    seen: dict[str, int] = {}
    # Journey files may also sit at the repository root under journey/ depending on how the
    # session was configured, so both locations are read.
    for pattern in (os.path.join(configured, "*.jsonl"), str(root / "journey" / "*.jsonl")):
        for path in glob.glob(pattern):
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except ValueError:
                            continue  # a torn final line is normal for an append-only log
                        name = event.get("tool") or event.get("tool_name")
                        if name:
                            seen[name] = seen.get(name, 0) + 1
            except OSError:
                continue
    return seen


def analyse(root: pathlib.Path) -> dict:
    matcher = read_matcher(root)
    if matcher is None:
        return {"status": "NO_CONFIG",
                "detail": f"no gate_guard PreToolUse hook found in {SETTINGS}"}

    covered = covered_tools(matcher)
    seen = observed_tools(root)

    unguarded = sorted(
        (name, count) for name, count in seen.items()
        if name not in covered and name not in KNOWN_HARMLESS
    )
    stale = sorted(t for t in covered if t not in seen)

    return {
        "status": "DRIFT" if unguarded else "CLEAN",
        "matcher": matcher,
        "covered": sorted(covered),
        "observed": dict(sorted(seen.items(), key=lambda kv: -kv[1])),
        "unguarded": [
            {"tool": n, "uses": c, "write_suspicion": bool(WRITE_SUSPICION.search(n))}
            for n, c in unguarded
        ],
        "matcher_entries_never_observed": stale,
    }


def render(r: dict) -> str:
    if r["status"] == "NO_CONFIG":
        return f"matcher drift check\n\n  NO_CONFIG -- {r['detail']}"

    out = ["matcher drift check", "", f"  matcher: {r['matcher']}",
           f"  tools observed in the journey trail: {len(r['observed'])}", ""]

    if r["matcher_entries_never_observed"]:
        out.append("  matcher entries never observed in any session:")
        for t in r["matcher_entries_never_observed"]:
            out.append(f"    - {t}  (harmless if the tool no longer exists; "
                       f"remove it only once you are sure)")
        out.append("")

    if not r["unguarded"]:
        out += [
            "  CLEAN -- every tool observed is either covered by the matcher or known harmless.",
            "",
            "  This does not prove the gate covers tools nobody has used yet. It proves the gate",
            "  covers everything this workspace has actually seen. Re-run it after a Claude Code",
            "  upgrade, when the tool set is exactly what may have changed.",
        ]
        return "\n".join(out)

    out.append("  DRIFT -- tools were used that the write gate does not intercept:")
    out.append("")
    for item in r["unguarded"]:
        flag = "  <-- name suggests it can modify files" if item["write_suspicion"] else ""
        out.append(f"    {item['tool']}  ({item['uses']} use(s)){flag}")
    out += [
        "",
        "  Each needs a ruling. If a tool can write to a path, add it to the matcher in",
        f"  {SETTINGS} and re-run the gate's own self-test. If it cannot, add it to",
        "  KNOWN_HARMLESS in this script with a one-line reason.",
        "",
        "  Until then the protected paths are unguarded against that tool, and",
        "  anti_gaming.py's hash comparison is the only thing that would notice.",
    ]
    return "\n".join(out)


def self_test() -> int:
    import tempfile

    cases = []

    def workspace(matcher: str, tools: list[str]) -> pathlib.Path:
        tmp = pathlib.Path(tempfile.mkdtemp())
        (tmp / ".claude" / "journey").mkdir(parents=True)
        (tmp / ".claude" / "settings.json").write_text(json.dumps({
            "hooks": {"PreToolUse": [{"matcher": matcher, "hooks": [
                {"type": "command", "command": "bash .../gate-python .../gate_guard.py"}]}]}
        }), encoding="utf-8")
        with open(tmp / ".claude" / "journey" / "s.jsonl", "w", encoding="utf-8") as fh:
            for t in tools:
                fh.write(json.dumps({"event": "pre-tool", "tool": t}) + "\n")
        return tmp

    r = analyse(workspace("Write|Edit", ["Write", "Read", "Bash", "Edit"]))
    cases.append(("all observed tools covered or harmless -> CLEAN", r["status"] == "CLEAN", r["status"]))

    r = analyse(workspace("Write|Edit", ["Write", "ApplyPatch"]))
    cases.append(("an unknown tool is reported as DRIFT", r["status"] == "DRIFT",
                  str([u["tool"] for u in r["unguarded"]])))
    cases.append(("a write-suggestive name is flagged",
                  any(u["write_suspicion"] for u in r["unguarded"]),
                  str(r["unguarded"])))

    r = analyse(workspace("Write|Edit", ["Write", "Telemetry"]))
    cases.append(("an unknown tool is reported even without a write-ish name",
                  r["status"] == "DRIFT" and not r["unguarded"][0]["write_suspicion"],
                  str(r["unguarded"])))

    r = analyse(workspace("Write|Edit|MultiEdit", ["Write", "Edit"]))
    cases.append(("a matcher entry never observed is surfaced",
                  r["matcher_entries_never_observed"] == ["MultiEdit"],
                  str(r["matcher_entries_never_observed"])))
    cases.append(("a never-observed matcher entry is not itself drift",
                  r["status"] == "CLEAN", r["status"]))

    tmp = pathlib.Path(tempfile.mkdtemp())
    cases.append(("a workspace with no hook config reports NO_CONFIG",
                  analyse(tmp)["status"] == "NO_CONFIG", analyse(tmp)["status"]))

    r = analyse(workspace("Write", ["Bash"]))
    cases.append(("Bash is treated as a documented ceiling, not drift",
                  r["status"] == "CLEAN", r["status"]))

    ok = True
    for label, passed, detail in cases:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}  --  {detail}")
        ok = ok and passed
    print()
    print(f"check_matcher_drift self-test: {sum(1 for _, p, _ in cases if p)} passed, "
          f"{sum(1 for _, p, _ in cases if not p)} failed")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    result = analyse(ROOT)
    print(json.dumps(result, indent=2) if args.json else render(result))
    if result["status"] == "NO_CONFIG":
        return 2
    return 1 if result["status"] == "DRIFT" else 0


if __name__ == "__main__":
    sys.exit(main())
