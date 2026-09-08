#!/usr/bin/env python3
"""check_leakage.py -- does any participant-readable file hand over an answer?

Why this is a script and not a grep in a checklist
--------------------------------------------------
The sweep that ran before this existed was a shell loop over a list of patterns. It reported clean,
and it was clean *for the patterns it held*: seed identifiers, seeded class names, rollout answers,
machine paths. It had no pattern for an English sentence describing a finding, so it never looked at
`.claude/rubrics/lab-2.yaml`, whose criteria descriptions named two of the planted disagreements and
gave the disposition of a third. `/lab` renders from that file. The leak was reachable in the first
thirty seconds of the lab and the sweep called it clean.

A pattern list only finds the shapes someone already thought of. The fix is not a longer list; it is
putting the list somewhere it can be regression-tested, and giving it negative fixtures that fail
loudly when a class stops being covered. Hence `--self-test`.

    python3 .claude/scripts/check_leakage.py
    python3 .claude/scripts/check_leakage.py --self-test
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

# Files participants can read. The rubric and lab.json are in scope: the write gate makes them
# unwritable, which says nothing about who can read them, and /lab renders from the rubric.
def in_scope(root: pathlib.Path) -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    keep = []
    for rel in out.stdout.splitlines():
        if rel.startswith("facilitator/"):
            continue                                  # facilitator package, not participant-facing
        if rel.endswith((".md", ".yaml", ".yml", ".json")):
            keep.append(pathlib.Path(rel))
    return keep

# (class, pattern, why it leaks). Anything matching is a leak unless a line-level allowance below
# applies. Patterns are deliberately narrow: a class that over-matches gets muted by allowances and
# then protects nothing.
RULES = [
    ("seed-id", r"SEED-[0-9]",
     "names a seeded defect by its manifest identifier"),
    # Not bare "planted": the guide and PRE_READ are required to disclose that the defects are
    # planted teaching fixtures implying nothing about real Mastercard systems. Suppressing that
    # sentence to satisfy a scanner would trade an honesty obligation for a clean report.
    ("seed-vocab", r"\b(seed manifest|SEED_MANIFEST|FACILITATOR_KEY|final-reference|"
     r"planted defect is|which defect|answer key)\b",
     "exposes the construction vocabulary of the fixtures"),
    ("seeded-symbol", r"\b(LocalRefundLimitRule|VoidTransactionSupport|selectEndpoint|idempotencyKeyFor)\b",
     "names a symbol that only exists because of a seed"),
    ("rollout-answer", r"\b(producer.first|consumer.first)\b",
     "gives away the rollout-order ruling"),
    ("defect-count", r"\b(four of five|five (fix|defect|seed)s?|both repositories need)\b",
     "tells the participant how many findings to expect, or where"),
    # The class the shell sweep did not have. A finding stated in prose is the answer key whether or
    # not it uses lab vocabulary, and "the correct action is no diff" is worse: it is the ruling.
    ("finding-prose",
     r"(?i)\b(the )?(contract.version drift|divergent business rule|version drift is|"
     r"remaining.refundable rule|the correct action was no diff|correct action is no diff)\b",
     "states a finding, or its disposition, that the participant is meant to discover"),
    ("machine-path", r"(/Users/|C:\\\\|Versions/3\.[0-9]+/bin)",
     "embeds a path from the author's machine"),
]

# Line-level allowances, each with the reason it is not a leak. A file-level allowance would be too
# blunt: SCENARIO_GROUNDING has to use the construction vocabulary to explain the three layers, and
# that is exactly the file where a real leak would hide best. `substr` narrows an allowance to the
# specific sentence that earned it, so a genuine leak arriving later in the same file still fires.
ALLOW = [
    ("docs/SCENARIO_GROUNDING.md", "seed-vocab", None,
     "the document's purpose is to explain the three grounding layers, which requires the words"),
    ("docs/PGS_DECISIONS.md", "seed-vocab", None,
     "the decision register cites its own construction; it is sourced authority, not a hint"),
    ("LAB_ACTION_GUIDE.md", "finding-prose", "Adjacency is not authorisation",
     "states the general principle the stage teaches, attached to no file and no finding; this is "
     "the lesson, and removing it to satisfy a scanner would delete the pedagogy"),
]

# A third verdict, between clean and leaking.
#
# Some participant-facing text states findings because the approved scenario design says it should.
# The Essential Outcomes Card is the clearest case: it exists to tell participants what their
# workspace should show by the end, which is a normal thing for a 120-minute lab to do and is also,
# unavoidably, a description of what they are meant to find.
#
# Whether that is sanctioned pedagogy or an unintended leak is a scenario decision, and scenario
# decisions belong to the coordinating engineer. Suppressing the hit would hide a real question;
# rewriting the card would change approved design without a ruling. So it is reported as PENDING on
# every run, in its own section, until a ruling is recorded here.
PENDING = [
    ("docs/ESSENTIAL_OUTCOMES.md", "finding-prose",
     "The eight outcomes name the findings the participant is meant to reach. That may be "
     "deliberate -- the card's stated job is to say what 'done' looks like -- or it may be the "
     "same leak the rubric had. DESIGN DECISION REQUIRED: is the outcomes card a sanctioned "
     "channel for stating target findings, or must it become evidence-shaped like the rubric?"),
]


def scan(root: pathlib.Path) -> tuple[list, list]:
    hits: list = []
    pend: list = []
    for rel in in_scope(root):
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for cls, pat, why in RULES:
                if re.search(pat, line):
                    if any(str(rel) == f and cls == c and (sub is None or sub in line)
                           for f, c, sub, _ in ALLOW):
                        continue
                    if any(str(rel) == f and cls == c for f, c, _ in PENDING):
                        pend.append((str(rel), n, cls, line.strip()[:110]))
                        continue
                    hits.append((str(rel), n, cls, why, line.strip()[:110]))
    return hits, pend


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(__file__).resolve().parents[2]

    if args.self_test:
        return self_test()

    files = in_scope(root)
    hits, pend = scan(root)
    print(f"participant-readable files scanned: {len(files)}")
    print(f"leak classes:                       {len(RULES)}")
    print(f"line allowances (each reasoned):    {len(ALLOW)}")

    for rel, n, cls, why, line in hits:
        print(f"\nLEAK  {rel}:{n}  [{cls}]")
        print(f"        {why}")
        print(f"        {line}")

    if pend:
        print("\n--- RULING PENDING (not a defect; not releasable without a ruling) ---")
        seen = set()
        for rel, n, cls, line in pend:
            print(f"  {rel}:{n}  [{cls}]  {line}")
            for f, c, why in PENDING:
                if f == rel and c == cls and (f, c) not in seen:
                    seen.add((f, c))
                    print(f"      {why}")

    if hits:
        print(f"\n{len(hits)} leak(s). Not releasable.")
        return 1
    print(f"\nCLEAN -- no unruled participant-readable file hands over an answer."
          f"{f' {len(pend)} line(s) awaiting a ruling.' if pend else ''}")
    return 0


def self_test() -> int:
    """Every class needs a string that trips it. A class with no fixture is a class that can quietly
    stop working -- which is the exact failure this script exists because of."""
    pos = {
        "seed-id":        "see SEED-03 for the idempotency case",
        "seed-vocab":     "consult the SEED_MANIFEST for the answer key",
        "seeded-symbol":  "LocalRefundLimitRule caps the amount",
        "rollout-answer": "deploy producer-first",
        "defect-count":   "you will fix four of five",
        "finding-prose":  "The contract-version drift is identified, with evidence",
        "machine-path":   "/Users/someone/lab",
    }
    neg = [
        "The specification passes the structural readiness gate",
        "A cross-repository disagreement is reconciled with evidence and a human ruling",
        "Code excluded by OUT_OF_SCOPE.md is left untouched",
        "Prove the pair works together and disposition every material finding",
        "python3 scripts/run_pair_verification.py",
    ]
    cases = []
    for cls, pat, _ in RULES:
        cases.append((f"class {cls:<15} trips on its fixture",
                      bool(re.search(pat, pos[cls]))))
    for s in neg:
        fired = [c for c, p, _ in RULES if re.search(p, s)]
        cases.append((f"benign line stays clean: {s[:44]!r}", not fired))
    cases.append(("every rule has a positive fixture",
                  set(pos) == {c for c, _, _ in RULES}))
    cases.append(("every allowance names a class that exists",
                  all(c in {r for r, _, _ in RULES} for _, c, _, _ in ALLOW)))
    cases.append(("every allowance carries a reason",
                  all(w and len(w) > 20 for *_, w in ALLOW)))
    cases.append(("every pending item states the decision required",
                  all("DESIGN DECISION REQUIRED" in w for *_, w in PENDING)))
    cases.append(("the rewritten rubric descriptions are all benign",
                  not any(re.search(p, n) for _, p, _ in RULES
                          for n in neg[1:4])))

    ok = True
    for label, passed in cases:
        print(f"{'ok  ' if passed else 'FAIL'}  {label}")
        ok &= passed
    n = sum(1 for _, p in cases if p)
    print(f"\ncheck_leakage self-test: {n} passed, {len(cases) - n} failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
