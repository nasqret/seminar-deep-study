"""Shared helpers of the seminar notes, imported by the notebooks and listed in the appendix.

Put here everything two notebooks need: the paper's objects transcribed once from its LaTeX
source, high-precision numerics, exact linear algebra. Then every number in the book can be traced
to code that is printed in full (`code.md`).

* `is_zero(z)`: the single place where a high-precision number is declared zero (threshold `EPS`);
  it records the largest value declared zero and the smallest declared nonzero in `GAP`, and the
  notebooks print `gap_report()` so that the reader sees how clear-cut the decisions were.
* `rank_exact`, `det_exact`: exact rank and determinant over Q (fractions) for integer matrices.
"""
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 50
EPS = mp.mpf(10) ** -30
GAP = {"zero_max": mp.mpf(0), "nonzero_min": mp.inf}


def is_zero(z):
    """Decide whether a 50-digit number is zero (threshold 1e-30) and record the gap."""
    a = abs(z)
    if a < EPS:
        GAP["zero_max"] = max(GAP["zero_max"], a)
        return True
    GAP["nonzero_min"] = min(GAP["nonzero_min"], a)
    return False


def gap_report():
    return (f"largest value declared zero: {mp.nstr(GAP['zero_max'], 3)}, "
            f"smallest value declared nonzero: {mp.nstr(GAP['nonzero_min'], 3)}")


def _echelon(rows):
    """Row-reduce a copy of `rows` over Q; return (reduced rows, rank, determinant sign/product)."""
    m = [[Fraction(x) for x in r] for r in rows]
    n_rows, n_cols = len(m), len(m[0]) if m else 0
    rank, det = 0, Fraction(1)
    for col in range(n_cols):
        pivot = next((r for r in range(rank, n_rows) if m[r][col] != 0), None)
        if pivot is None:
            det = Fraction(0)
            continue
        if pivot != rank:
            m[rank], m[pivot] = m[pivot], m[rank]
            det = -det
        det *= m[rank][col]
        for r in range(rank + 1, n_rows):
            f = m[r][col] / m[rank][col]
            if f:
                m[r] = [a - f * b for a, b in zip(m[r], m[rank])]
        rank += 1
    return m, rank, det


def rank_exact(rows):
    return _echelon(rows)[1]


def det_exact(rows):
    """Determinant of a square matrix, exactly."""
    assert rows and all(len(r) == len(rows) for r in rows), "square matrix expected"
    _, rank, det = _echelon(rows)
    return det if rank == len(rows) else Fraction(0)
