# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""The flag bound with the dual cap t_d <= U (THEORY_10.md, Proposition 10.2).

Minimise prod t_i over t in (0, inf)^d subject to
  (P_r) t_1 + ... + t_r >= B_r            r = 1..d
  (R_i) t_{i+1} >= (3/4) t_i              i = 1..d-1
  (C)   t_d <= U
in exact rational arithmetic.  Two independent methods:
  capped_min_blocks      vertices by block pattern (uses the structural lemma)
  capped_min_bruteforce  every d-subset of the 2d constraints (small d only)
"""
import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

RHO = Fraction(3, 4)


def B(n, r):
    return Fraction(2 * r, (n + 1) * (n + 1 - r)) ** 2


def B_list(n):
    """[B_0 = 0, B_1, ..., B_d] with d = n - 1."""
    return [Fraction(0)] + [B(n, r) for r in range(1, n)]


def c_from_B(Bs):
    return [Bs[r] - Bs[r - 1] for r in range(1, len(Bs))]


def c_list(n):
    return c_from_B(B_list(n))


def prod(xs):
    out = Fraction(1)
    for x in xs:
        out *= x
    return out


def K(n):
    return prod(c_list(n))


def structural_condition(Bs):
    """c_r > 0 and c_{r+1} > (3/4) c_r for all r (THEORY_10.md, structural lemma)."""
    cs = c_from_B(Bs)
    return all(x > 0 for x in cs) and all(cs[i + 1] > RHO * cs[i] for i in range(len(cs) - 1))


def feasible(t, Bs, U):
    d = len(t)
    if any(x <= 0 for x in t):
        return False
    T = Fraction(0)
    for r in range(1, d + 1):
        T += t[r - 1]
        if T < Bs[r]:
            return False
    for i in range(d - 1):
        if t[i + 1] < RHO * t[i]:
            return False
    return U is None or t[-1] <= U


def _blocks(mask, d):
    """bit i-1 of mask set <=> a block ends at index i (1 <= i < d)."""
    out, s = [], 1
    for i in range(1, d):
        if (mask >> (i - 1)) & 1:
            out.append((s, i))
            s = i + 1
    out.append((s, d))
    return out


def capped_min_blocks(Bs, U):
    """(min product, argmin t, candidates checked); (None, None, n) if infeasible."""
    d = len(Bs) - 1
    w = [None] + [RHO ** (i - 1) for i in range(1, d + 1)]
    Wc = [Fraction(0)]
    for i in range(1, d + 1):
        Wc.append(Wc[-1] + w[i])
    best, arg, checked = None, None, 0
    for mask in range(1 << (d - 1)):
        bl = _blocks(mask, d)
        k = len(bl)
        Wb = [Wc[e] - Wc[s - 1] for s, e in bl]
        # (A): every block-end prefix active
        base = [(Bs[e] - Bs[s - 1]) / Wb[j] for j, (s, e) in enumerate(bl)]
        cands = [base]
        if U is not None:
            yk = Fraction(U) / w[d]
            cands.append(base[:-1] + [yk])                       # (B1): C, not P_d
            if k >= 2:                                           # (B2): C, not P_{e_{k-1}}
                s1 = bl[k - 2][0]
                y1 = (Bs[d] - Bs[s1 - 1] - Wb[k - 1] * yk) / Wb[k - 2]
                cands.append(base[:-2] + [y1, yk])
        for y in cands:
            checked += 1
            t = []
            for j, (s, e) in enumerate(bl):
                for i in range(s, e + 1):
                    t.append(y[j] * w[i])
            if not feasible(t, Bs, U):
                continue
            p = prod(t)
            if best is None or p < best:
                best, arg = p, t
    return best, arg, checked


def _solve(A, b):
    """exact Gaussian elimination; None if singular."""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col] / pv
                M[r] = [x - f * y for x, y in zip(M[r], M[col])]
    return [M[i][n] / M[i][i] for i in range(n)]


def capped_min_bruteforce(Bs, U):
    """vertex enumeration over all d-subsets of the 2d constraints (small d)."""
    d = len(Bs) - 1
    zero = Fraction(0)
    rows = []
    for r in range(1, d + 1):
        rows.append(([Fraction(1)] * r + [zero] * (d - r), Bs[r]))
    for i in range(d - 1):
        a = [zero] * d
        a[i] = -RHO
        a[i + 1] = Fraction(1)
        rows.append((a, zero))
    a = [zero] * d
    a[d - 1] = Fraction(-1)
    rows.append((a, -Fraction(U)))
    best, arg = None, None
    for S in combinations(range(len(rows)), d):
        t = _solve([rows[i][0] for i in S], [rows[i][1] for i in S])
        if t is None or not feasible(t, Bs, U):
            continue
        p = prod(t)
        if best is None or p < best:
            best, arg = p, t
    return best, arg


@lru_cache(maxsize=None)
def _capped_min_cached(n, U):
    best, arg, checked = capped_min_blocks(B_list(n), U)
    return best, tuple(arg) if arg is not None else None, checked


def capped_min(n, U=Fraction(1, 3)):
    best, arg, checked = _capped_min_cached(n, Fraction(U))
    return best, list(arg) if arg is not None else None, checked


def gain_nats(n, U=Fraction(1, 3)):
    """drop of the bound on log(v_1...v_n): (n/2) ln(min / K_n)."""
    best = capped_min(n, U)[0]
    return n / 2 * math.log(best / K(n))


# ---------------- Lemma 10.1: the identity t_d * sum q_k h_k^2 = 1 ----------------

def e_gram_last(v, order=None):
    """For v with v[0] == 1: basis b_i = P e_{order[i]} of Lambda = P Z^n (order is a
    permutation of 1..n-1), E-inner product <x,y> = x^T S y with
    S = Q^-1 - Q^-1 v v^T Q^-1 / (v^T Q^-1 v) on H.  Returns (t_d, h, sum q h^2)."""
    n = len(v)
    assert v[0] == 1
    order = list(order) if order is not None else list(range(1, n))
    vmax = max(v)
    u = [Fraction(x, vmax) for x in v]
    q = [1 + 2 * x - x * x for x in u]
    vv = sum(Fraction(x * x) for x in v)

    def P(x):
        a = sum(Fraction(xi) * vi for xi, vi in zip(x, v)) / vv
        return [Fraction(xi) - a * vi for xi, vi in zip(x, v)]

    qiv = [Fraction(vi) / qi for vi, qi in zip(v, q)]          # Q^-1 v
    den = sum(Fraction(vi) * x for vi, x in zip(v, qiv))      # v^T Q^-1 v

    def ip(x, y):
        a = sum(xi * yi / qi for xi, yi, qi in zip(x, y, q))
        bx = sum(xi * c for xi, c in zip(x, qiv))
        by = sum(yi * c for yi, c in zip(y, qiv))
        return a - bx * by / den

    basis = []
    for k in order:
        e = [0] * n
        e[k] = 1
        basis.append(P(e))
    gs, norms = [], []
    for b in basis:
        x = list(b)
        for g, nn in zip(gs, norms):
            mu = ip(b, g) / nn
            x = [xi - mu * gi for xi, gi in zip(x, g)]
        gs.append(x)
        norms.append(ip(x, x))
    t_d = norms[-1]
    # h: integer relation with h . b_i = h_{order[i]} = 0 for i < d, h_{order[-1]} = 1,
    # and h . v = 0  =>  h_0 = -v[order[-1]]
    h = [0] * n
    h[order[-1]] = 1
    h[0] = -v[order[-1]]
    assert sum(hi * vi for hi, vi in zip(h, v)) == 0
    sq = sum(qi * hi * hi for qi, hi in zip(q, h))
    return t_d, h, sq


# ---------------- Lemma 10.4: hyperplane loneliness ----------------

def hyperplane_delta(h):
    L = sum(abs(x) for x in h)
    return Fraction(1, 2) if L % 2 == 0 else Fraction(1, 2) - Fraction(1, 2 * L)


def hyperplane_grid_max(h1, h2, N=30):
    """max over s = (a1/N, a2/N, s3) with h1 s1 + h2 s2 + s3 = 0 of min_k ||s_k||."""
    best = 0
    for a1 in range(N):
        for a2 in range(N):
            a3 = -(h1 * a1 + h2 * a2)
            m = N
            for a in (a1, a2, a3):
                r = a % N
                m = min(m, r, N - r)
            best = max(best, m)
    return Fraction(best, N)


if __name__ == "__main__":
    out = {}
    for n in (14, 15):
        best, arg, checked = capped_min(n)
        out[n] = {"K_n": str(K(n)), "capped_min": str(best), "kappa": str(best / K(n)),
                  "kappa_float": float(best / K(n)), "argmin_tail": [str(x) for x in arg[-3:]],
                  "candidates_checked": checked, "gain_nats": gain_nats(n)}
    json.dump(out, sys.stdout, indent=1)
