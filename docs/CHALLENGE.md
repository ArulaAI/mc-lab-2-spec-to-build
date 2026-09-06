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
- The facilitator has the full list. Compare notes at the end.

Good hunting.
