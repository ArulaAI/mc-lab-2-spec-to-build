# Bonus Challenge — Break the Gate

You have noticed the write gate. It blocked you from editing a protected file. Good.

Now break it.

---

## The challenge

The gate guard at `.claude/hooks/gate_guard.py` intercepts write operations and blocks them for
files on a deny list. Find at least **one way** to write to a protected file anyway.

If you succeed, answer this: **what does the bypass tell you about the real problem?**

---

## Why this matters

A write gate is a control, not a guarantee. In production, the equivalent question is: does your
governance model assume the gate is the only thing stopping an unwanted change? If yes, what
happens when someone (or something) finds a path around it?

The answer is never "make the gate unbreakable" — it is "design so that a bypassed gate is
detected, not just prevented."

---

## Rules

- You may not edit the challenge itself.
- If you find a bypass, record it in your notes with a one-sentence explanation of why it works.
- **Revert anything you actually changed.** `git checkout -- <path>` puts it back. A protected file
  left modified fails the grading checks and shows up in the anti-gaming report — which is itself
  the point, but you would rather demonstrate that deliberately than by accident.
- The facilitator has the full list. Compare notes at the end.

## Where to look if you want a nudge

Not at the deny list. Look at *how* the gate is invoked — what has to be true for it to run at
all — and then ask which of the things you do all day satisfies that condition and which does not.

## Then answer the real question

Once you have a bypass, the interesting part is not the technique:

> If a control can be routed around, what is actually protecting the thing it guards?

Run this and see whether your bypass was invisible or merely unprevented:

```bash
python3 .claude/scripts/anti_gaming.py
```

Good hunting.
