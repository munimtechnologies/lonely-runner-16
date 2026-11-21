# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Grid-point witnesses (THEORY.md Sec. 9, Lemma G).

A second, independent and much simpler implementation of the kill test of
uniform.py (THEORY.md Sec. 8), plus the fast sufficient test used in Lemma G2.

Setting as in uniform.py: k speeds, a level-one vector s, a level L, and a lift
z (values mod L).  For beta in Z_L the positions are  beta z_i / L + t s_i  (mod 1).
Take a grid point x = c/D, put N = lcm(L, D, k+1), B = N/(k+1) and

    a_i = beta z_i (N/L) + c s_i (N/D)   (mod N),

so that the position of coordinate i at time x is a_i/N.  As t moves right from x,
coordinate i stays at distance > 1/(k+1) for small t - x > 0 iff a_i is not in
[0, B) u [N-B, N), i.e. B <= a_i < N - B; moving left, iff B < a_i <= N - B.
If every coordinate is good on one side, the strict witnesses on that side reach

    dR = min_i (N - B - a_i) / (N s_i)     (to the right),
    dL = min_i (a_i - B) / (N s_i)         (to the left),

and the component of G_beta (the open set of strict witnesses) that contains or
starts at x has length dR + dL if x itself is strict (good on both sides), dR if
x is its left end, dL if x is its right end.  Every number is an exact Fraction.

With D = 2Q (Q = lcm(L, k+1) lcm(s), uniform.qunit) every component of every
G_beta contains a strict grid point (its endpoints lie in (1/Q)Z), so grid_killed
with D = 2Q decides exactly the same thing as uniform.uniform_killed, for every
threshold P.  test_grid.py checks this.  With a small D (e.g. D = k + 1) it is only
a sufficient test, but a fast one.
"""
from fractions import Fraction
from math import gcd


def lcm(a, b):
    return a * b // gcd(a, b)


def prime_factors(n):
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def gcd_clause(z, L):
    """some prime q | L divides all coordinates but at most one (any L >= 1)"""
    for q in prime_factors(L):
        if sum(1 for x in z if x % q) <= 1:
            return True
    return False


def t0_witness(z, L, k):
    """some beta makes t = 0 a (non-strict) witness: (k+1) ||beta z_i / L|| >= 1"""
    for beta in range(L):
        ok = True
        for x in z:
            r = (beta * x) % L
            if (k + 1) * min(r, L - r) < L:
                ok = False
                break
        if ok:
            return True
    return False


def positions(s, k, z, L, beta, c, D):
    N = lcm(lcm(L, D), k + 1)
    a = [(beta * z[i] * (N // L) + c * s[i] * (N // D)) % N for i in range(k)]
    return N, N // (k + 1), a


def side_good(a, N, B):
    """(good moving right, good moving left) for the position numerators a"""
    right = all(B <= x < N - B for x in a)
    left = all(B < x <= N - B for x in a)
    return right, left


def component_at(s, k, z, L, beta, c, D):
    """length (Fraction) of the component of G_beta at the grid point c/D, or None
    if c/D is neither in G_beta nor an endpoint of one of its components"""
    N, B, a = positions(s, k, z, L, beta, c, D)
    right, left = side_good(a, N, B)
    if not right and not left:
        return None
    length = Fraction(0)
    if right:
        length += min(Fraction(N - B - a[i], N * s[i]) for i in range(k))
    if left:
        length += min(Fraction(a[i] - B, N * s[i]) for i in range(k))
    return length


def grid_killed(s, k, z, L, D, P):
    """gcd clause, or an exact witness at t = 0, or a component of some G_beta that
    meets the grid (1/D)Z and is longer than 1/P (P None: any component)"""
    if gcd_clause(z, L):
        return True
    if t0_witness(z, L, k):
        return True
    for beta in range(L):
        for c in range(D):
            ln = component_at(s, k, z, L, beta, c, D)
            if ln is not None and (P is None or ln * P > 1):
                return True
    return False


def exact_D(s, k, L):
    """D = 2Q with Q = lcm(L, k+1) * lcm(s) (the product, as in uniform.qunit):
    grid_killed(..., exact_D(...), P) is an exact test (Lemma G(ii))"""
    ls = 1
    for x in s:
        ls = lcm(ls, x)
    return 2 * lcm(L, k + 1) * ls


def blocked_masks(s, k, L, D, zvals, betas=None):
    """For the near-grid test with every coordinate restricted to the values in
    zvals: one entry per (beta, c, side) with, for each value v, the bitmask of
    coordinates i that are bad on that side when z_i = v.  A lift z is blocked by
    an entry iff some coordinate i is bad for its own value z_i."""
    out = []
    betas = range(L) if betas is None else betas
    for beta in betas:
        for c in range(D):
            for side in ("R", "L"):
                masks = []
                for v in zvals:
                    z = [v] * k
                    N, B, a = positions(s, k, z, L, beta, c, D)
                    m = 0
                    for i in range(k):
                        good = (B <= a[i] < N - B) if side == "R" else (B < a[i] <= N - B)
                        if not good:
                            m |= 1 << i
                    masks.append(m)
                out.append((beta, c, side, masks))
    return out
