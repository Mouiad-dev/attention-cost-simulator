
"""Core cost model. Pure math: context length -> theoretical work.

This module knows NOTHING about charts, CLIs, or files.
It only answers one question: "how much work does a context of length N cost?"

Two components of the work:
- linear part   : every token passes through the network once      -> grows like N
- quadratic part: attention, every token attends to every token    -> grows like N^2

We report both so the caller can SEE where the quadratic part takes over.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CostPoint:
    """The cost of ONE context length. A fact, so it is frozen (immutable)."""

    length: int          # context length in tokens
    linear_cost: float   # work that grows linearly with length (~ N)
    attention_cost: float  # work that grows quadratically with length (~ N^2)

    @property
    def total_cost(self) -> float:
        """Total theoretical work = linear + quadratic."""
        return self.linear_cost + self.attention_cost


def cost_for_length(length: int) -> CostPoint:
    """Compute the theoretical cost for a single context length.

    We use RELATIVE units, not real GPU seconds. The point is the SHAPE
    of the growth (linear vs quadratic), not a hardware benchmark.

    linear_cost    = N        (one pass per token)
    attention_cost = N * N    (each token attends to every other token)
    """
    if length < 0:
        raise ValueError(f"length must be >= 0, got {length}")

    linear_cost = float(length)
    attention_cost = float(length) * float(length)
    return CostPoint(
        length=length,
        linear_cost=linear_cost,
        attention_cost=attention_cost,
    )


def simulate(lengths: list[int]) -> list[CostPoint]:
    """Compute cost points for a list of context lengths.

    Returns them sorted by length so any chart drawn from them is left-to-right.
    """
    if not lengths:
        raise ValueError("lengths must not be empty")

    unique_sorted = sorted(set(lengths))
    return [cost_for_length(n) for n in unique_sorted]


def growth_ratio(points: list[CostPoint]) -> float:
    """The headline number: how many times more expensive is the longest
    context vs the shortest, for ATTENTION alone (the N^2 part).

    This is the sentence you say in the interview:
    "from 1k to 100k, attention cost multiplies by X".
    """
    if len(points) < 2:
        raise ValueError("need at least 2 points to compute a ratio")

    smallest = points[0].attention_cost
    largest = points[-1].attention_cost
    if smallest == 0:
        raise ValueError("shortest context has zero cost; cannot divide")

    return largest / smallest