"""Drawing layer. Turns numbers into a chart image.

This module knows NOTHING about CLIs or argument parsing.
It takes CostPoints (from the simulator) and produces a PNG file.

Why matplotlib with the "Agg" backend?
- Agg is a NON-interactive backend: it draws straight to a file, never to a
  screen. That is exactly what we want inside Docker, where there is no display.
"""

import matplotlib

matplotlib.use("Agg")  # must be set BEFORE importing pyplot; picks the file-only backend

import matplotlib.pyplot as plt  # noqa: E402  (import after backend is set, on purpose)

from .simulator import CostPoint


def plot_costs(points: list[CostPoint], output_path: str) -> str:
    """Draw two lines and save the chart to output_path.

    Line 1 (linear)    = the INTUITION people wrongly assume: cost grows with N.
    Line 2 (attention) = the REALITY: cost grows with N^2.

    Returns the path it saved to, so the caller can report it.
    """
    if not points:
        raise ValueError("no points to plot")

    lengths = [p.length for p in points]
    linear = [p.linear_cost for p in points]
    attention = [p.attention_cost for p in points]

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(lengths, linear, marker="o", label="Linear cost ~ N (the intuition)")
    ax.plot(lengths, attention, marker="o", label="Attention cost ~ N² (the reality)")

    # Log scale on Y: without it, the N^2 line is so tall it flattens the N line
    # into the floor and you can't compare them. Log scale lets both be readable.
    ax.set_yscale("log")

    ax.set_xlabel("Context length (tokens)")
    ax.set_ylabel("Relative work (log scale)")
    ax.set_title("Why long context is expensive: attention grows as N²")
    ax.legend()
    ax.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)  # free memory; important if this ever runs many times in a loop

    return output_path