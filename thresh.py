# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Exact per-prime decision and uniform kill thresholds for the lifts of one
level-one vector (THEORY_15.md).  Built on uniform.py (THEORY.md Sec. 8).

For a level-one vector s (k speeds), a binary level L and a lift class z
(values mod L), `lift_info` computes, once and for all primes:

  * status "gcd": the gcd clause holds (at most one odd coordinate): proper at
    every prime;
  * status "t0": some beta in Z_L makes t = 0 an exact witness: proper at every
    prime;
  * status "open": otherwise; `cells` lists every open interval of strict
    witnesses (beta fixed, t on the circle), in units of 1/Q.

Two adjacent cells of uniform.Cells are never both uncovered (their common end
point is an end point of a closed bad arc, which covers the cell on its side),
so each uncovered cell is a whole component of strict witnesses.

Then for a prime p that divides neither Q nor any s_i:
  * `proper_at(info, p)` decides exactly whether the lift is proper at p: some
    t = j/p lies in an uncovered cell (t = j/p is never an arc end point for
    j != 0 because p does not divide Q);
  * `threshold(info)` = P*(z) = Q / (longest cell): the lift is proper at every
    such prime p > P*(z), because an open interval longer than 1/p contains a
    point of (1/p)Z.  None means no strict witness at all (improper at every
    prime); 0 means status gcd or t0.
  * `killed_uniform(info, P)` reproduces uniform.uniform_killed(s, k, z, L, P).

By Lemma U, the true improper lifts at p are contained in U_P(L) for p >= P,
and a lift that is proper at level L stays proper at level 2L (its witness b
becomes 2b; the gcd clause is the same for all powers of 2).  Hence, for every
prime p >= P (not dividing Q),

    J_p(L) = { z in U_P(L) : not proper_at(z, p) },

which `prime_levels` evaluates level by level.
"""
from fractions import Fraction

import uniform as U


class LiftInfo:
    __slots__ = ("s", "k", "z", "L", "Q", "status", "cells")

    def as_dict(self):
        thr = threshold(self)
        return {"z": list(self.z), "L": self.L, "status": self.status,
                "n_cells": len(self.cells),
                "longest_cell": (None if not self.cells else
                                 str(Fraction(self.cells[0][1] - self.cells[0][0], self.Q))),
                "threshold": None if thr is None else str(thr),
                "threshold_float": None if thr is None else float(thr)}


def lift_info(s, k, z, L):
    s = tuple(s)
    z = tuple(x % L for x in z)
    assert U.is_pow2(L) and len(s) == len(z) == k
    info = LiftInfo()
    info.s, info.k, info.z, info.L = s, k, z, L
    info.Q = Q = U.qunit(L, k, s)
    info.cells = []
    if U.gcd_clause(z, L):
        info.status = "gcd"
        return info
    cells = []
    for beta in range(L):
        if not any(U.exact_bad(beta * z[i], L, k) for i in range(k)):
            info.status = "t0"
            info.cells = []
            return info
        arc_lists = [U.arcs_for(s[i], (beta * z[i]) % L, L, k, Q) for i in range(k)]
        C = U.Cells(arc_lists, Q)
        orv = 0
        for arcs in arc_lists:
            orv |= C.mask(arcs)
        for m in range(C.M):
            if not (orv >> m) & 1:
                cells.append((C.E2[m], C.E2[m + 1]))
    cells.sort(key=lambda c: (c[0] - c[1], c[0]))  # longest first
    info.status = "open"
    info.cells = cells
    return info


def proper_at(info, p):
    """exact: is the lift proper at the prime p?  (p must not divide Q or any s_i)"""
    assert info.Q % p != 0 and all(x % p for x in info.s)
    if info.status != "open":
        return True
    Q = info.Q
    for a, b in info.cells:
        j = a * p // Q + 1
        if j * Q < b * p:
            return True
    return False


def threshold(info):
    """P*(z) as a Fraction (0 if proper everywhere, None if improper everywhere)"""
    if info.status != "open":
        return Fraction(0)
    if not info.cells:
        return None
    a, b = info.cells[0]
    return Fraction(info.Q, b - a)


def killed_uniform(info, P):
    """the decision of uniform.uniform_killed(s, k, z, L, P); P None = infinity"""
    if info.status != "open":
        return True
    if not info.cells:
        return False
    if P is None:
        return True
    a, b = info.cells[0]
    return (b - a) * P > info.Q


def primes_between(lo, hi):
    if hi < 2:
        return []
    sieve = bytearray([1]) * (hi + 1)
    sieve[0] = sieve[1] = 0
    i = 2
    while i * i <= hi:
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
        i += 1
    return [q for q in range(max(lo, 2), hi + 1) if sieve[q]]


def level_infos(s, k, nlevels, P, max_parents=3000, deadline=None, clock=None):
    """U_P(L) for L = 1, 2, ..., 2^nlevels as lists of LiftInfo.  Returns
    (levels, cut): levels = [(L, [info, ...]), ...] starting at L = 1 (empty list
    if the base vector is killed in U_P); cut as in uniform.cascade."""
    res = U.cascade(s, k, nlevels, P, max_parents=max_parents, deadline=deadline, clock=clock)
    levels = []
    if res["base_killed"]:
        levels.append((1, []))
        return levels, res["cut"]
    levels.append((1, [lift_info(s, k, tuple(0 for _ in s), 1)]))
    for lv in res["levels"]:
        L = lv["level"]
        levels.append((L, [lift_info(s, k, z, L) for z in lv["survivors"]]))
    return levels, res["cut"]


def prime_levels(levels, p):
    """sizes of J_p(L) for each listed level, computed from the U_P lists (valid
    for primes p >= P not dividing Q).  Returns (sizes, survivors_at_last_level)"""
    sizes = []
    last = []
    for L, infos in levels:
        surv = [inf for inf in infos if not proper_at(inf, p)]
        sizes.append((L, len(surv)))
        last = surv
        if not surv:
            break
    return sizes, last
