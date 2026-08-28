"""Tests for the core math. We test the SIMULATOR, not the drawing.

Why not test the plotter? Because a chart image is hard to assert on and its
value is visual. The math is what must be correct, so that is what we lock down.
"""

import pytest

from attention_sim.simulator import (
    CostPoint,
    cost_for_length,
    growth_ratio,
    simulate,
)


def test_attention_is_length_squared():
    """The whole point: attention cost = N * N."""
    point = cost_for_length(1000)
    assert point.linear_cost == 1000
    assert point.attention_cost == 1_000_000  # 1000^2


def test_doubling_length_quadruples_attention():
    """2x length must give 4x attention cost, not 2x. This is the lesson."""
    small = cost_for_length(1000)
    big = cost_for_length(2000)
    assert big.attention_cost == small.attention_cost * 4


def test_growth_ratio_squares_the_length_ratio():
    """100x longer context -> 10,000x more attention cost (100^2)."""
    points = simulate([1000, 100000])
    assert growth_ratio(points) == 10_000


def test_simulate_sorts_and_dedupes():
    """Input order/duplicates must not matter; output is sorted and unique."""
    points = simulate([5000, 1000, 5000])
    lengths = [p.length for p in points]
    assert lengths == [1000, 5000]


def test_negative_length_is_rejected():
    with pytest.raises(ValueError):
        cost_for_length(-1)


def test_empty_list_is_rejected():
    with pytest.raises(ValueError):
        simulate([])


def test_ratio_needs_two_points():
    with pytest.raises(ValueError):
        growth_ratio([cost_for_length(1000)])


def test_costpoint_is_immutable():
    """CostPoint is a fact; it must not be mutable."""
    point = cost_for_length(1000)
    with pytest.raises(Exception):
        point.length = 2000  # frozen dataclass -> raises