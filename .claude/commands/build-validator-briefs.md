---
name: build-validator-briefs
description: "Stage 5. Assembles one fresh-context validator brief per repository from a fixed allowlist."
---

Assemble the repo-scoped validator briefs.

1. Execute: `python3 .claude/scripts/build_validator_brief.py`
2. Report which briefs were written and how many lines each carries.
3. State what each brief contains and, more importantly, what it does not:

   - **contains** — the validated specification, `specs/OUT_OF_SCOPE.md`,
     `specs/NON_NEGOTIABLES.md`, that repository's agent contract, that repository's diff, and that
     repository's verification evidence;
   - **does not contain** — any chat history, any builder rationale, any implementation-agent
     reasoning, or the other repository's implementation.

   That exclusion is structural rather than a matter of discretion: the script assembles from a
   fixed allowlist and has no path to a conversation. Say so — the guarantee is the lesson.

Do not ask the participant any question. This command assembles evidence; the human decisions on
the core path are the decision gates in `.claude/decision-gates.yaml`.

Do not dispatch the validators yourself, and do not summarise or edit a brief. The participant
dispatches two fresh validators in parallel, one brief each, with read and test tools and no write
tools.
