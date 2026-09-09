# Lab 2 — One Refund Across a Service Boundary

A 120-minute hands-on lab about governing AI safely when a money-moving change crosses a service boundary — where no single test suite, and no single agent, can see the whole picture. To understand the scenario you are working on, start with [`docs/SCENARIO_GROUNDING.md`](docs/SCENARIO_GROUNDING.md).

---

## Follow the Lab Action Guide

Everything you need — all six stages and how to work through each one — is in the **[LAB_ACTION_GUIDE](LAB_ACTION_GUIDE.md)**. That is the document you will be working from, start to finish.

---

## Before the session

Do this *before* session day. It takes a few minutes and will save you a lot of pain at minute forty.

### What you'll need

- **JDK 17+** — JDK 21 targeting Java 17 is the documented pattern and what this lab is tested against
- **Maven 3.9+**
- **Python 3.9+** with PyYAML (`bash .claude/scripts/run -m pip install pyyaml`)
- **Git**
- The **Workbench plugin** — needed for `/lab`, `/journey`, `/hand-off`, and the validators
- A warm `~/.m2` — the lab makes no network calls at runtime, but a cold Maven cache will take a few minutes on first build
- A **bash-compatible shell** — all commands go through one wrapper (`bash .claude/scripts/run <script>`), so you don't need to think about platform differences

### Set it up

```
bash .claude/scripts/run scripts/verify_setup.py
```

This checks your toolchain, initialises both service repositories, warms the Maven cache, and confirms you are ready to go. It must end with **"Setup complete"**. If it doesn't, read the first `[FAIL]` line — it names exactly what is missing.

---

## Reference map

When you need to look something up mid-lab, here is where to find it.

| Document | What it answers |
|---|---|
| [`LAB_ACTION_GUIDE.md`](LAB_ACTION_GUIDE.md) | How to run the lab, stage by stage |
| [`docs/ESSENTIAL_OUTCOMES.md`](docs/ESSENTIAL_OUTCOMES.md) | What gets graded |
| [`docs/SCENARIO_GROUNDING.md`](docs/SCENARIO_GROUNDING.md) | Real PGS behaviour vs. lab simplification vs. planted defect |
| [`docs/PGS_DECISIONS.md`](docs/PGS_DECISIONS.md) | Every decision and its source layer |
| [`docs/TERM_CARD.md`](docs/TERM_CARD.md) | The ten key terms, defined |
| [`docs/SPEC_COMPLETENESS_BAR.md`](docs/SPEC_COMPLETENESS_BAR.md) | When a spec is build-ready |
| [`specs/NON_NEGOTIABLES.md`](specs/NON_NEGOTIABLES.md) | What holds regardless of anything else |
| [`specs/OUT_OF_SCOPE.md`](specs/OUT_OF_SCOPE.md) | What must not be built |
| [`docs/CHALLENGE.md`](docs/CHALLENGE.md) | Bonus: break the write gate |

---

Questions? Reach out to your facilitator.

Happy coding!
