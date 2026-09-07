#!/usr/bin/env python3
"""grade_repo.py -- deterministic grader for Lab 2.

Determinism is the contract. The same workspace state always produces the same score: nothing here
samples, calls a model, or depends on wall-clock time. Two participants who reached the same
outcome by different routes score identically, which is the whole point — the rubric grades
engineering outcomes and evidence, never how anything was worded.

    python3 .claude/scripts/grade_repo.py
    python3 .claude/scripts/grade_repo.py --json
    python3 .claude/scripts/grade_repo.py --self-test

Check vocabulary
----------------
    event_count_gte:<n>                       at least n journey events recorded
    file_contains:<path>:<keyword>            keyword appears in authored content
    file_table_rows_gte:<path>:<n>            at least n populated, non-template table rows
    file_table_row_contains_all:<path>:<k,k>  keywords co-occur on ONE well-formed row
    file_sections_nonempty:<path>:<n>         at least n `##` sections carry authored content
    json_true:<path>:<key>                    a JSON file has that key set to true
    unmodified:<path>                         a protected file is byte-for-byte as shipped
    seed_intact:<fixture-id>                  a seeded file is unmodified and uncorrupted
    repo_changed:<repo>                       that service repository has work beyond its starter
    all_of:<check>;<check>                    every sub-check passes
    any_of:<check>;<check>                    at least one sub-check passes

What this cannot prove, said plainly
------------------------------------
A journey event records that a tool ran, not what it returned, so no check here can prove a build
went green from the journey alone. Build outcomes are graded from recorded results and repository
state instead. And a well-shaped ledger looks the same whether it was reasoned out or copied from
somewhere — the facilitator's live spot-check is the control for that, not this script.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:
    print("grade_repo.py needs PyYAML:\n    python3 -m pip install pyyaml", file=sys.stderr)
    sys.exit(3)

DEFAULT_RUBRIC = ".claude/rubrics/lab-2.yaml"
DEFAULT_JOURNEY_DIR = ".claude/journey"
FIXTURE_DIR = ".claude/fixtures"

_SEPARATOR_ROW = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

# A real ledger or disposition row fills most of its columns. Both tables have six, so four
# populated cells is a floor no honest row trips over and no crammed one-liner clears.
MIN_ROW_CELLS = 4
MIN_SECTION_CHARS = 40


def strip_comments(text: str) -> str:
    """Remove HTML comment blocks.

    Load-bearing rather than cosmetic: every template here carries its instructions in HTML
    comments, and those instructions name the very artifacts the rubric looks for. Without
    stripping, an untouched template scores for content nobody wrote.
    """
    return _HTML_COMMENT.sub(" ", text)


class Workspace:
    def __init__(self, root: str):
        self.root = os.path.realpath(root)
        self._cache: dict[str, str | None] = {}
        self.journey_files = self._find_journey()
        self.journey_events = self._load_journey()

    def read(self, rel: str) -> str | None:
        if rel not in self._cache:
            try:
                with open(os.path.join(self.root, rel), encoding="utf-8", errors="replace") as fh:
                    self._cache[rel] = fh.read()
            except OSError:
                self._cache[rel] = None
        return self._cache[rel]

    def _find_journey(self) -> list[str]:
        configured = os.environ.get("WORKBENCH_JOURNEY_DIR", DEFAULT_JOURNEY_DIR)
        if not os.path.isabs(configured):
            configured = os.path.join(self.root, configured)
        # Glob rather than assume one filename: a session that reconnects produces several.
        return sorted(glob.glob(os.path.join(configured, "*.jsonl")))

    def _load_journey(self) -> list[dict]:
        events = []
        for path in self.journey_files:
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except ValueError:
                            continue  # a torn final line is normal for an append-only log
                        if isinstance(obj, dict):
                            events.append(obj)
            except OSError:
                continue
        return events


def table_rows(text: str) -> list[str]:
    rows = []
    for line in strip_comments(text).splitlines():
        s = line.strip()
        if not s.startswith("|") or _SEPARATOR_ROW.match(s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 2 and any(cells):
            rows.append(s)
    return rows


def sections_with_content(text: str) -> list[str]:
    filled, heading, buf = [], None, []
    for line in strip_comments(text).splitlines():
        if line.lstrip().startswith("##"):
            if heading and len("\n".join(buf).strip()) >= MIN_SECTION_CHARS:
                filled.append(heading)
            heading, buf = line.lstrip("# ").strip(), []
        elif heading is not None:
            buf.append(line)
    if heading and len("\n".join(buf).strip()) >= MIN_SECTION_CHARS:
        filled.append(heading)
    return filled


class CheckError(Exception):
    pass


def run_check(spec: str, ws: Workspace) -> tuple[bool, str]:
    spec = (spec or "").strip()
    if not spec:
        raise CheckError("empty check")

    if spec.startswith("all_of:"):
        subs = [s for s in spec[len("all_of:"):].split(";") if s.strip()]
        if not subs:
            raise CheckError("all_of with no sub-checks")
        details, ok = [], True
        for sub in subs:
            sub_ok, sub_detail = run_check(sub.strip(), ws)
            details.append(("PASS " if sub_ok else "FAIL ") + sub.strip())
            ok = ok and sub_ok
        return ok, " | ".join(details)

    if spec.startswith("any_of:"):
        # Needed because one repository may legitimately require no change. Naming which one in
        # the check would encode where the defects are, in a file participants can read.
        subs = [x for x in spec[len("any_of:"):].split(";") if x.strip()]
        if not subs:
            raise CheckError("any_of with no sub-checks")
        details, ok = [], False
        for sub in subs:
            sub_ok, _ = run_check(sub.strip(), ws)
            details.append(("PASS " if sub_ok else "FAIL ") + sub.strip())
            ok = ok or sub_ok
        return ok, " | ".join(details)

    if spec.startswith("event_count_gte:"):
        n = int(spec.split(":", 1)[1])
        got = len(ws.journey_events)
        return got >= n, f"{got} event(s), needed {n}"

    if spec.startswith("json_true:"):
        _, path, key = spec.split(":", 2)
        text = ws.read(path)
        if text is None:
            return False, f"{path} not found"
        try:
            value = json.loads(text).get(key)
        except ValueError:
            return False, f"{path} is not valid JSON"
        return value is True, f"{key}={value!r}"

    if spec.startswith("unmodified:"):
        path = spec.split(":", 1)[1]
        return check_unmodified(path, ws)

    if spec.startswith("seed_intact:"):
        return check_seed_intact(spec.split(":", 1)[1], ws)

    if spec.startswith("repo_changed:"):
        repo = spec.split(":", 1)[1]
        return check_repo_changed(repo, ws)

    if spec.startswith("file_table_rows_gte:"):
        _, path, raw = spec.split(":", 2)
        text = ws.read(path)
        if text is None:
            return False, f"{path} not found"
        rows = table_rows(text)
        return len(rows) >= int(raw), f"{len(rows)} content row(s), needed {raw}"

    if spec.startswith("file_table_row_contains_all:"):
        _, path, raw = spec.split(":", 2)
        text = ws.read(path)
        if text is None:
            return False, f"{path} not found"
        keywords = [k.strip().lower() for k in raw.split(",") if k.strip()]
        crammed = False
        for row in table_rows(text):
            if not all(k in row.lower() for k in keywords):
                continue
            populated = len([c for c in row.strip("|").split("|") if c.strip()])
            if populated < MIN_ROW_CELLS:
                crammed = True
                continue
            return True, "found on a well-formed row"
        if crammed:
            return False, (f"keywords found only on a row with fewer than {MIN_ROW_CELLS} populated "
                           f"cells; a real row records claim, evidence, ruling and status")
        return False, f"no row contains: {', '.join(keywords)}"

    if spec.startswith("file_sections_nonempty:"):
        _, path, raw = spec.split(":", 2)
        text = ws.read(path)
        if text is None:
            return False, f"{path} not found"
        filled = sections_with_content(text)
        return len(filled) >= int(raw), f"{len(filled)} section(s) with authored content, needed {raw}"

    if spec.startswith("file_contains:"):
        _, path, keyword = spec.split(":", 2)
        text = ws.read(path)
        if text is None:
            return False, f"{path} not found"
        hit = keyword.strip().lower() in strip_comments(text).lower()
        return hit, "found" if hit else f"'{keyword.strip()}' not present in authored content"

    raise CheckError(f"unknown check type: '{spec}'")


def check_unmodified(path: str, ws: Workspace) -> tuple[bool, str]:
    baseline = ws.read(os.path.join(FIXTURE_DIR, "protected-files.json"))
    if baseline is None:
        return False, "protected-files.json baseline not found"
    expected = json.loads(baseline).get("files", {}).get(path)
    if not expected:
        return False, f"no baseline recorded for {path}"
    text = ws.read(path)
    if text is None:
        return False, f"{path} not found"
    actual = hashlib.sha256(text.encode()).hexdigest()
    return actual == expected, "byte-for-byte as shipped" if actual == expected else "MODIFIED"


def check_seed_intact(fixture_id: str, ws: Workspace) -> tuple[bool, str]:
    """A seeded file must come back untouched.

    Recording the finding proves it was noticed. It proves nothing about whether it was also
    quietly 'fixed' — and for out-of-scope code, implementing it is the failure the lab exists to
    catch. Both halves are needed, so this checks the code and the rubric checks the disposition.
    """
    raw = ws.read(os.path.join(FIXTURE_DIR, f"{fixture_id}.json"))
    if raw is None:
        return False, f"fixture {fixture_id} not found"
    fixture = json.loads(raw)

    text = ws.read(fixture["target"])
    if text is None:
        return False, f"seed target {fixture['target']} not found"

    for expected in fixture.get("expect_exact", []):
        if expected not in text:
            return False, f"seeded block modified in {fixture['target']}"

    for pattern in fixture.get("forbid_regex", []):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return False, (f"out-of-scope work appears to have been implemented: "
                           f"{m.group(0)[:60]!r} in {fixture['target']}")

    actual = hashlib.sha256(text.encode()).hexdigest()
    if fixture.get("sha256") and actual != fixture["sha256"]:
        return False, f"{fixture['target']} differs from the shipped bytes"
    return True, "untouched, and no out-of-scope implementation added"


def check_repo_changed(repo: str, ws: Workspace) -> tuple[bool, str]:
    path = os.path.join(ws.root, repo)
    if not os.path.isdir(os.path.join(path, ".git")):
        return False, f"{repo} is not an initialised repository"
    diff = subprocess.run(["git", "diff", "HEAD", "--stat"], cwd=path,
                          capture_output=True, text=True).stdout.strip()
    log = subprocess.run(["git", "log", "--oneline"], cwd=path,
                         capture_output=True, text=True).stdout.strip().splitlines()
    changed = bool(diff) or len(log) > 1
    return changed, "work present" if changed else "unchanged from the starter commit"


def grade(root: str, rubric_path: str) -> dict:
    ws = Workspace(root)
    rubric_text = ws.read(rubric_path)
    if rubric_text is None:
        raise SystemExit(f"rubric not found: {rubric_path}")
    rubric = yaml.safe_load(rubric_text) or {}

    results, score, total = [], 0.0, 0.0
    for crit in rubric.get("criteria", []):
        max_score = float(crit.get("max_score", 0) or 0)
        total += max_score
        try:
            ok, detail = run_check(crit.get("check", ""), ws)
        except CheckError as ex:
            ok, detail = False, f"GRADER ERROR: {ex}"
        score += max_score if ok else 0.0
        results.append({"id": crit.get("id"), "description": crit.get("description", ""),
                        "max_score": max_score, "score": max_score if ok else 0.0,
                        "passed": ok, "detail": detail})

    threshold = rubric.get("pass_threshold", 0)
    return {"lab": rubric.get("lab"), "title": rubric.get("title", ""), "rubric": rubric_path,
            "journey_events": len(ws.journey_events), "score": score, "total": total,
            "pass_threshold": threshold, "passed": score >= threshold, "criteria": results}


def render(card: dict) -> str:
    lines = [f"Lab {card['lab']} -- {card['title']}", f"rubric: {card['rubric']}",
             f"journey: {card['journey_events']} event(s)", ""]
    width = max((len(c["id"] or "") for c in card["criteria"]), default=10)
    for c in card["criteria"]:
        lines.append(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['id']:<{width}} "
                     f"{c['score']:>3.0f}/{c['max_score']:<3.0f}  {c['detail']}")
    pct = (100.0 * card["score"] / card["total"]) if card["total"] else 0.0
    lines += ["", f"  SCORE {card['score']:.0f}/{card['total']:.0f} ({pct:.0f}%)   "
                  f"threshold {card['pass_threshold']}  ->  "
                  f"{'PASS' if card['passed'] else 'FAIL'}"]
    return "\n".join(lines)


def self_test(real_root: str, rubric_path: str) -> int:
    """The grader must discriminate. A rubric that passes an empty workspace grades nothing."""
    rubric_text = open(os.path.join(real_root, rubric_path), encoding="utf-8").read()
    threshold = yaml.safe_load(rubric_text)["pass_threshold"]
    cases = []

    def scaffold(tmp: str) -> None:
        for rel in [rubric_path, os.path.join(FIXTURE_DIR, "seed-07-void-adjacency.json"),
                    os.path.join(FIXTURE_DIR, "protected-files.json"),
                    "specs/OUT_OF_SCOPE.md"]:
            src = os.path.join(real_root, rel)
            if os.path.isfile(src):
                dst = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(src, encoding="utf-8") as a, open(dst, "w", encoding="utf-8") as b:
                    b.write(a.read())

    with tempfile.TemporaryDirectory() as tmp:
        scaffold(tmp)
        card = grade(tmp, rubric_path)
        cases.append(("an empty workspace scores below threshold",
                      not card["passed"], f"{card['score']:.0f}/{card['total']:.0f}"))

    with tempfile.TemporaryDirectory() as tmp:
        scaffold(tmp)
        crammed = ("| a | b |\n|---|---|\n"
                   "| contract refund UNKNOWN everything | one row |\n")
        os.makedirs(os.path.join(tmp, "docs"), exist_ok=True)
        with open(os.path.join(tmp, "docs/context-ledger.md"), "w") as fh:
            fh.write(crammed)
        card = grade(tmp, rubric_path)
        ledger = [c for c in card["criteria"] if c["id"].startswith("ledger-")]
        cases.append(("a crammed single-row ledger earns no ledger credit",
                      not any(c["passed"] for c in ledger),
                      "; ".join(f"{c['id']}={c['passed']}" for c in ledger)))

    with tempfile.TemporaryDirectory() as tmp:
        scaffold(tmp)
        ws = Workspace(tmp)
        yes, _ = run_check("any_of:file_contains:%s:pass_threshold;file_contains:nope.md:x" % rubric_path, ws)
        no, _ = run_check("any_of:file_contains:nope.md:x;file_contains:also-nope.md:y", ws)
        cases.append(("any_of passes on one hit and fails on none", yes and not no, f"{yes}/{no}"))

    ok = True
    for label, passed, detail in cases:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}  --  {detail}")
        ok = ok and passed
    print()
    print(f"grade_repo self-test: {sum(1 for _, p, _ in cases if p)} passed, "
          f"{sum(1 for _, p, _ in cases if not p)} failed")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=None)
    ap.add_argument("--rubric", default=DEFAULT_RUBRIC)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    root = os.path.realpath(args.repo) if args.repo else str(pathlib.Path(__file__).resolve().parents[2])
    if args.self_test:
        return self_test(root, args.rubric)

    card = grade(root, args.rubric)
    print(json.dumps(card, indent=2) if args.json else render(card))
    return 0 if card["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
