# attention-cost-simulator

A small offline CLI that **charts why long context is expensive**: it shows how
attention cost grows as **N²** (quadratically) with context length, not linearly.

Step 0 · L2 of the Backend → AI Engineer roadmap. the intuition that later justifies context compression.

---

## The idea in one line

Every token in the context must "attend to" every other token. Double the
length → **4x** the attention work. This tool makes that visible.

| Context length | Linear (~N) | Attention (~N²) |
|---|---|---|
| 1,000 | 1,000 | 1,000,000 |
| 10,000 | 10,000 | 100,000,000 |
| 100,000 | 100,000 | 10,000,000,000 |

Going 100x longer → **10,000x** more attention cost.

---

## Architecture

Dependencies point **one way**: `cli → simulator, plotter`. Logic never depends
on the interface, so this could become a FastAPI service by adding one file and
reusing `simulator`/`plotter` untouched.

```
src/attention_sim/
├── simulator.py   # CORE math: length → cost. Knows nothing about charts/CLI.
├── plotter.py     # DRAWING: numbers → chart image. Knows nothing about CLI.
└── cli.py         # INTERFACE: parse args, orchestrate, print. No logic.
```

### Key decisions

1. **Offline by design** — a tool that *measures* cost must not itself cost
   money. No LLM call; pure math. (cost/latency trade-off)
2. **Two lines: intuition vs reality** — linear (~N) vs attention (~N²), so the
   gap is the lesson.
3. **Log scale on Y** — without it the N² line flattens the N line into the
   floor; log scale makes both readable.
4. **`Agg` matplotlib backend** — draws to a file with no display, so it runs
   inside Docker.
5. **Immutable `CostPoint`** — a cost is a fact, so the dataclass is `frozen`.
6. **Derived data not stored** — `total_cost` is computed, never saved, so it
   can never drift out of sync.

---

## Run it

```bash
pip install -e .
attention-sim 1000 10000 100000                 # table + chart + headline number
attention-sim 1000 50000 200000 -o big.png      # custom lengths and output
pytest                                          # run the 8 tests

# Docker (fully offline, one command):
docker compose run --rm attention-sim 1000 10000 100000 -o output/chart.png
```
<img width="1080" height="720" alt="image" src="https://github.com/user-attachments/assets/78cf387a-8f28-49f6-a84b-8676c366c7f0" />

---

## The number

From 1k to 100k tokens, attention cost multiplies by **10,000x**.

## Interview sentence

> "I built an offline simulator that charts attention cost. I plotted the linear
> intuition against the real N² curve on a log scale, so the gap is obvious. The
> number: going 100x longer in context is 10,000x more attention work — which is
> exactly why context compression is an engineering decision, not a nice-to-have."
