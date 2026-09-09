# Lab 2 — Stage 3–5 Support Guide

> **Use this only if you are blocked.**
>
> The Lab Action Guide is still the main path.  
> This guide gives you only enough support to get moving again.

---

## How to read this guide

### 💡 Layer 1 — Hint
Use this first. It gives you a nudge without giving you the path.

### ▶ Layer 2 — Guided Start
This is a **copy-pastable prompt**. Paste the whole block into Claude exactly as written.

### ⌨️ Run This Command
Run the slash command exactly as shown.

### 🔎 Check Your Result
Use this to decide whether you are ready to continue.

---

# Stage 3 — Plan Across Repositories

## Goal

Leave Stage 3 with:

```text
docs/plans/orchestration-plan.md
docs/agent-briefs/tta-implementation-brief.md
docs/agent-briefs/processor-implementation-brief.md
```

> Stage 2 established **what is authorized**.  
> Stage 3 decides **how that authorized work is divided and bounded**.

---

## 💡 Layer 1 — Hint

Ask yourself:

> If the TTA brief went to one engineer and the Payment Processor brief went to another, could they work independently without rediscovering scope or making a missing business decision?

Your plan should make clear:

- which acceptance criteria are in scope;
- which repository is responsible for each;
- what dependencies exist across the seam;
- what sequencing or compatibility constraints are actually supported;
- which open authority items remain outside implementation.

Each implementation brief should define:

```text
Repository
Objective
Acceptance criteria owned
Authoritative context
Allowed repository scope
Excluded areas
NO_DIFF_EXPECTED: true | false
Verification required
Stop conditions
```

If this is enough to get you moving, return to the Action Guide.

---

## ▶ Layer 2 — Guided Start

If you are still blocked, use the tested prompt below to move forward:

```text
Using the validated specification and the Stage 3 planning requirements,
propose the cross-repository decomposition.
Then create:
 - docs/plans/orchestration-plan.md
 - docs/agent-briefs/tta-implementation-brief.md
 - docs/agent-briefs/processor-implementation-brief.md
Use only authorized Stage 2 scope.
Keep open authority items excluded.
Do not implement code.
```

---

## ⌨️ Run This Command

When the three artifacts exist, run:

```text
/check-plan
```

If it fails, use the failed checks as your editing queue.

> Fix the relevant planning artifact.  
> Do **not** invent a requirement or resolve an authority gap simply to make the gate green.

---

## 🔎 Check Your Result

Move on when:

```text
[ ] orchestration-plan.md exists
[ ] both implementation briefs exist
[ ] every authorized AC is assigned
[ ] unresolved authority remains outside implementation
[ ] /check-plan reports READY
```

---

# Stage 4 — Build & Validate

## Goal

Execute the Stage 3 implementation briefs without expanding scope.

> **The brief defines the boundary. The agent discovers the implementation.**

You do **not** need to write another detailed implementation prompt.

---

## 💡 Layer 1 — Hint

Before you dispatch an implementation agent, check the brief.

It should already tell the agent:

- what outcome this repository owns;
- what it may change;
- what it must avoid;
- how it must verify the work;
- when it must stop.

After the agent returns, inspect the evidence rather than how confident the explanation sounds.

Look for:

```text
REPOSITORY
ACCEPTANCE_CRITERIA_ADDRESSED
FILES_CHANGED
VERIFICATION_COMMAND
VERIFICATION_RESULT
UNRESOLVED
STOP_REQUIRED
```

Remember:

> `FILES_CHANGED: none` can be a valid result if the repository already satisfies the acceptance criteria it owns and the agent can show the evidence.

If this is enough to get you moving, return to the Action Guide.

---

## ▶ Layer 2 — Guided Start

Follow the execution order from **your Stage 3 plan**.

### If Payment Processor is next

Use this tested prompt:

```text
Use the @repo-implementer agent for @pgs-payment-processor/ with @docs/agent-briefs/processor-implementation-brief.md. Follow the contract exactly. Run its required verification. Return the standard result.
```

### If TTA is next

Use this tested prompt:

```text
Use the @repo-implementer agent for @pgs-tta/ with @docs/agent-briefs/tta-implementation-brief.md. Follow the contract exactly. Run its required verification. Return the standard result.
```

> **Do not automatically run both write agents in parallel.**  
> Follow the execution order established in your Stage 3 plan.

---

## 🔎 Check Your Result THE RETURN

Before dispatching the next repository, ask:

```text
[ ] Did the agent stay inside its repository?
[ ] Does every changed file trace to authorized work?
[ ] Did it stay outside excluded areas?
[ ] Did it return verification evidence?
[ ] Did it stop rather than invent unsupported behavior?
```

If completing the work requires behavior that the validated specification did not authorize, the correct outcome may be:

```text
STOP_REQUIRED
```

---

## OPTIONAL — AUDIT THE AGENT'S VERIFICATION

Only do this if you intentionally want to audit the returned verification evidence.

```bash
mvn -B -f pgs-payment-processor/pom.xml verify
```

or:

```bash
mvn -B -f pgs-tta/pom.xml verify
```

This is an **audit**, not a required duplicate step.

---

## 🔎 Check Your Result

Move on when:

```text
[ ] both repository briefs have been executed
[ ] each agent stayed inside its repository boundary
[ ] changed files trace to authorized work
[ ] required verification has evidence
[ ] no unsupported scope was added
```

---

# Stage 5 — Validate the Pair

## Goal

Stage 5 has three separate moves:

```text
1. PROVE THE PAIR
        ↓
2. GET FRESH JUDGMENT
        ↓
3. DISPOSITION THE FINDINGS
```

> Two green repositories get you **into** Stage 5.  
> They do not finish it.

---

## 💡 Layer 1 — Hint

### 1 — Prove the pair

Ask:

> Do the two repositories actually agree when exercised together?

That is different from asking whether each repository builds independently.

### 2 — Get fresh judgment

The implementation agents already know their own reasoning.

The validators should judge from a fresh evidence set instead of inheriting the implementation conversation.

### 3 — Disposition findings

A validator finding is **not** automatically an instruction to change code.

For each finding, ask:

```text
Is it supported by evidence?
Is it inside the authorized scope?
Is it material?
Can the available evidence settle it?
Would acting on it require new authority?
```

If this is enough to get you moving, return to the Action Guide.

---

## ⌨️ Run This Command

### Step 1 — Prove the pair

Run:

```text
/verify-pair
```

Preserve and understand the result before changing anything.

> Do not immediately turn a pair failure into a repair task.

---

## ⌨️ Run This Command

### Step 2 — Build the fresh validator briefs

Run:

```text
/build-validator-briefs
```

---

## ▶ Layer 2 — Guided Start

### Step 3 — Launch the fresh validators

Use this tested prompt exactly as written:

```text
Use two @"workbench\:code-to-spec-validator (agent)" subagents in parallel: 
1. Validate: @docs/validator-brief-payment-processor.md 
2. Validate: @docs/validator-brief-tta.md 
Each validator should judge only the repository and acceptance criteria contained in its brief. 
Do not edit anything. Return both results separately.
```

The validators should not receive:

- builder conversation history;
- your earlier reasoning;
- the other repository's implementation details.

---

## 🔎 Check Your Result THE VALIDATOR RESULTS

For each finding, decide what the evidence supports.

Use:

```text
docs/finding-dispositions.md
```

Record:

```text
Finding
Evidence
In scope?
Material?
Disposition
Rationale
```

> **Validator finding ≠ authorization to change code.**

You still own the engineering decision.

---

## IF THE SIGNALS DISAGREE

### Pair fails, validators look good

Do not explain away the deterministic pair evidence.

Investigate what the pair verification actually demonstrated.

### Pair passes, validator raises a concern

Inspect the cited evidence.

Do not automatically code to satisfy the validator.

---

## 🔎 Check Your Result

Move on when:

```text
[ ] /verify-pair has been run
[ ] you understand what the pair result proves
[ ] both fresh validators completed
[ ] every material finding has a disposition
[ ] every disposition has a rationale
[ ] you can explain what repository verification proved
[ ] you can explain what pair verification added
```

---

# Quick Recovery Card

If you only need the shortest possible path:

```text
STAGE 3
▶ Use the guided planning prompt
⌨️ /check-plan

STAGE 4
▶ Use the guided repo-implementer prompt for the next repo
🔎 Inspect the return
▶ Repeat for the second repo

STAGE 5
⌨️ /verify-pair
⌨️ /build-validator-briefs
▶ Use the guided fresh-validator prompt
🔎 Disposition the findings
```

---

## One rule for all three stages

If you are unsure whether Claude should make a decision, ask:

> **Is the answer already authorized by the evidence and boundaries we established?**

If yes, continue.

If no:

> **Stop, preserve the uncertainty, and do not manufacture the missing decision.**
