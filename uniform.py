# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Binary lifting of one level-one orbit, uniformly in the prime p (THEORY.md Sec. 8).

Setting.  k speeds, a level-one vector s (positive integers, s_i < p), and binary
levels L = 1, 2, 4, ...  A lift of s to level L is a vector w in Z_{Lp}^k with
w_i = s_i (mod p); write z_i = w_i mod L.  Because gcd(L, p) = 1, a time
b in Z_{Lp} corresponds to a pair (beta, sigma) in Z_L x Z_p, and

    b w_i / (Lp) = beta z_i / L + t s_i   (mod 1),   t = sigma / p,

(write 1 = A L + B p; beta = bB mod L, sigma = bA mod p).  So w is proper iff the
gcd clause holds (L a power of 2: at most one z_i is odd) or some beta in Z_L and
some t in (1/p)Z have ||beta z_i / L + t s_i|| >= 1/(k+1) for all i.

The only grid point that can be a rational with denominator coprime to p is t = 0.
So, for a prime p not dividing Q (below) and not dividing any s_i:
  * an exact witness at t = 0 is a witness for every p;
  * any other witness lies in the interior of the open set G_beta of strict
    witnesses, a finite union of open intervals with rational endpoints;
  * an open interval longer than 1/p always contains a point of (1/p)Z.
Hence, writing U_P(L) for the lifts not killed by (gcd clause, exact t = 0,
or a component of some G_beta longer than 1/P), and U_inf(L) for those not
killed by (gcd clause, t = 0, or G_beta non-empty):

    U_inf(L)  subset of  (true improper lifts at p)  subset of  U_P(L)   for p >= P.

The engine (lrc.c, lrc_ref.py) computes the middle set at one prime.  This module
computes the outer two for all primes at once.  Lifts are identified with z, and
z ~ lambda z for odd lambda (the unit Lambda = lambda mod L, 1 mod p).

Exact integer arithmetic throughout: times are measured in units of 1/Q with
Q = lcm(L, k+1) * lcm(s), so every arc endpoint is an integer.
"""
from functools import reduce
from itertools import product
from math import gcd


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_list(xs):
    return reduce(lcm, xs, 1)


def is_pow2(L):
    return L >= 1 and L & (L - 1) == 0


def canon(z, L):
    """smallest image of z under z -> lambda z mod L, lambda odd (L a power of 2)"""
    assert is_pow2(L)
    if L == 1:
        return tuple(0 for _ in z)
    best = None
    for lam in range(1, L, 2):
        t = tuple((lam * x) % L for x in z)
        if best is None or t < best:
            best = t
    return best


def qunit(L, k, s):
    return lcm(L, k + 1) * lcm_list(s)


def arcs_for(si, c, L, k, Q):
    """closed bad arcs {t in [0,1): ||si t + c/L|| <= 1/(k+1)} in units of 1/Q,
    as (start in [0, Q), length)"""
    qL = Q // L
    qr = Q // (k + 1)
    assert qL * L == Q and qr * (k + 1) == Q
    ln, r = divmod(2 * qr, si)
    assert r == 0
    out = []
    for j in range(si):
        num = j * Q - c * qL - qr
        a, r = divmod(num, si)
        assert r == 0
        out.append((a % Q, ln))
    return out


def exact_bad(x, L, k):
    """True if beta z_i / L = x / L (mod 1) is at distance < 1/(k+1) from 0"""
    x %= L
    return (k + 1) * min(x, L - x) < L


class Cells:
    """the circle [0, Q) cut at every endpoint of the given arcs"""

    def __init__(self, arc_lists, Q):
        pts = set()
        for arcs in arc_lists:
            for a, ln in arcs:
                pts.add(a)
                pts.add((a + ln) % Q)
        E = sorted(pts)
        self.Q = Q
        self.M = M = len(E)
        assert M >= 2
        self.E2 = E + [e + Q for e in E] + [E[0] + 2 * Q]
        self.pos = {e: i for i, e in enumerate(E)}
        self.lengths = [self.E2[m + 1] - self.E2[m] for m in range(M)]
        self.full = (1 << M) - 1

    def mask(self, arcs):
        """bit m is set iff cell m lies inside one of the closed arcs"""
        E2, M = self.E2, self.M
        bits = 0
        for a, ln in arcs:
            m = self.pos[a]
            end = a + ln
            while E2[m + 1] <= end:
                bits |= 1 << (m % M)
                m += 1
        return bits

    def big(self, P):
        """cells longer than 1/P (all cells if P is None) plus the exact bit M"""
        b = 1 << self.M
        for m, ln in enumerate(self.lengths):
            if P is None or ln * P > self.Q:
                b |= 1 << m
        return b

    def killed(self, orv, P):
        """orv: OR of the chosen coordinates' masks, exact bit at position M.
        True iff this beta gives a witness: t = 0 is good, or an uncovered run of
        cells (an open interval of strict witnesses) is longer than 1/P
        (P None: any uncovered cell)."""
        M = self.M
        if not (orv >> M) & 1:
            return True
        unc = self.full & ~orv
        if unc == 0:
            return False
        if P is None:
            return True
        if unc == self.full:
            return True
        # rotate so that bit 0 is a covered cell; then no run wraps around
        cov = self.full & ~unc
        c = (cov & -cov).bit_length() - 1
        x = ((unc >> c) | (unc << (M - c))) & self.full
        lengths, Q = self.lengths, self.Q
        run, prev = 0, -2
        while x:
            low = x & -x
            m = low.bit_length() - 1
            x ^= low
            if m != prev + 1:
                run = 0
            run += lengths[(m + c) % M]
            if run * P > Q:
                return True
            prev = m
        return False


def gcd_clause(z, L):
    """for L a power of 2 (L >= 2): at most one coordinate is odd"""
    return L >= 2 and sum(1 for x in z if x % 2) <= 1


def uniform_killed(s, k, z, L, P):
    """direct check of one lift z (values mod L) over every beta in Z_L"""
    assert is_pow2(L) and len(s) == len(z) == k
    if gcd_clause(z, L):
        return True
    Q = qunit(L, k, s)
    for beta in range(L):
        arc_lists = [arcs_for(s[i], (beta * z[i]) % L, L, k, Q) for i in range(k)]
        cells = Cells(arc_lists, Q)
        orv = 0
        for i in range(k):
            orv |= cells.mask(arc_lists[i])
            if exact_bad(beta * z[i], L, k):
                orv |= 1 << cells.M
        if cells.killed(orv, P):
            return True
    return False


def lift_parent(s, k, z, L, P, order=None):
    """canonical forms of the lifts of z (level L, improper) to level 2L that are
    not killed.  Only odd beta are tested: for beta = 2b the positions equal those
    of b at level L, where the parent was not killed."""
    L2 = 2 * L
    Q = qunit(L2, k, s)
    idx = list(range(k)) if order is None else list(order)
    vals = [((z[i]) % L2, (z[i] + L) % L2) for i in range(k)]
    per = []
    for beta in range(1, L2, 2):
        arcs = [[arcs_for(s[i], (beta * v) % L2, L2, k, Q) for v in vals[i]] for i in range(k)]
        cells = Cells([a for pair in arcs for a in pair], Q)
        ex = 1 << cells.M
        masks = []
        for i in idx:
            masks.append(tuple(cells.mask(arcs[i][d]) | (ex if exact_bad(beta * vals[i][d], L2, k) else 0)
                               for d in (0, 1)))
        big = cells.big(P)
        suf = [0] * (k + 1)
        for d in range(k - 1, -1, -1):
            suf[d] = suf[d + 1] | masks[d][0] | masks[d][1]
        per.append((cells, masks, big, suf))
    nb = len(per)
    out = set()
    choice = [0] * k

    def leaf(cur):
        zz = [0] * k
        for pos, i in enumerate(idx):
            zz[i] = vals[i][choice[pos]]
        if gcd_clause(zz, L2):
            return
        for j in range(nb):
            if per[j][0].killed(cur[j], P):
                return
        out.add(canon(zz, L2))

    def dfs(d, cur):
        for j in range(nb):
            big = per[j][2]
            if (cur[j] | per[j][3][d]) & big != big:
                return
        if d == k:
            leaf(cur)
            return
        for c in (0, 1):
            choice[d] = c
            dfs(d + 1, [cur[j] | per[j][1][d][c] for j in range(nb)])

    dfs(0, [0] * nb)
    return out


def base_killed(s, k, P):
    return uniform_killed(s, k, tuple(0 for _ in s), 1, P)


def cascade(s, k, nlevels, P, max_parents=None, bruteforce=False, deadline=None, clock=None):
    """levels 2, 4, ..., 2^nlevels.  Returns dict with per-level canonical survivor
    lists; 'base_killed' if s itself is killed at level 1; 'cut' if a level had more
    than max_parents survivors or the deadline passed (no claim beyond that level)."""
    res = {"base_killed": base_killed(s, k, P), "levels": [], "cut": None}
    if res["base_killed"]:
        return res
    parents = [tuple(0 for _ in s)]
    L = 1
    for _ in range(nlevels):
        L2 = 2 * L
        nxt = set()
        for z in parents:
            if deadline is not None and clock() > deadline:
                res["cut"] = {"level": L2, "reason": "deadline"}
                return res
            if bruteforce:
                for d in product((0, 1), repeat=k):
                    z2 = tuple((z[i] + L * d[i]) % L2 for i in range(k))
                    if not uniform_killed(s, k, z2, L2, P):
                        nxt.add(canon(z2, L2))
            else:
                nxt |= lift_parent(s, k, z, L, P)
        res["levels"].append({"level": L2, "survivors": sorted(nxt)})
        if not nxt:
            break
        if max_parents is not None and len(nxt) > max_parents:
            res["cut"] = {"level": L2, "reason": "more than %d survivors" % max_parents}
            return res
        parents = sorted(nxt)
        L = L2
    return res


def is_linear(z, s, L):
    """z = lambda s (mod L) for some integer lambda"""
    return any(all((lam * s[i] - z[i]) % L == 0 for i in range(len(s))) for lam in range(L))
