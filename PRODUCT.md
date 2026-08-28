## Who uses this?
An engineer (you) deciding whether to send a long context to the model as-is,
or compress it first. They want to *see* the cost difference before deciding —
not guess, and not read a math paper.

## The one job
Take several context lengths (e.g. 1k, 10k, 100k tokens) and draw a chart
showing how attention cost and latency grow **quadratically (N²)** — not linearly.

## Good enough when
- It draws a clear chart comparing at least 3 context lengths.
- It shows two lines: the *linear* cost (the intuition) vs the *real* N² cost
  (the reality), so the gap is visible.
- It prints one clear number: "from 1k to 100k, attention cost multiplies by X".

## Too slow / too expensive (the boundaries)
- Not a real-time service. Compute + draw once, done. No always-on server.
- Calls no real LLM — all theoretical, offline math (same rule as the previous tool).
  A tool that *measures* cost must not itself cost money.

## The measured number (goal)
The ratio between the cost of the longest context and the shortest context.
Expected example: 100k vs 1k → ~10,000x for attention alone.
