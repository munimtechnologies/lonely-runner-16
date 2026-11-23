# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""The uniform (prime-free) lifting cascade at non-binary levels (THEORY_16.md).

uniform.py and thresh.py handle binary levels L = 2^a only.  The published
14- and 15-runner proofs (Allikvere, arXiv:2609.02604, Sections 4.3-4.4) need
levels 14 = 2*7 and 15 = 3*5 for the tight vectors (1..13), (1..11,13,24) and
(1..14).  This module does the same computation for any level L, uniformly in
the prime p:

  * a lift class z in (Z_L)^k up to units of Z_L (a unit lambda mod L lifts to
    a unit of Z_{Lp} that is 1 mod p, which permutes the times);
  * the gcd clause of Definition 2.1(a): some prime d | L divides all
    coordinates but at most one;
  * the times b in Z_{Lp} <-> (beta, t), beta in Z_L, t in (1/p)Z (CRT, as in
    uniform.py, valid because gcd(L, p) = 1);
  * P-killed: gcd clause, or an exact witness at t = 0, or an open interval of
    strict witnesses longer than 1/P (P None: any open interval).

For every prime p >= P not dividing Q = lcm(L, k+1) lcm(s) or any s_i,
U_inf(L) <= J_p(L) <= U_P(L) (Lemma U; the proof in THEORY.md Sec. 8 never uses
that L is a power of 2).  Lifting from L to cL only needs the betas that are not
multiples of c (beta = c beta' gives the parent's positions), and a level-L1*L2
class with gcd(L1, L2) = 1 survives only if both reductions survive, which gives
the CRT combination `combine` (the uniform analogue of the paper's Lemma 4.5).

Exact integer arithmetic throughout (cells in units of 1/Q, as in uniform.py).
"""
from itertools import product
from math import gcd

import thresh as T
import uniform as U


class Deadline(Exception):
    pass


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


def units(L):
    return [x for x in range(1, L) if gcd(x, L) == 1] if L > 1 else [1]


def canon(z, L):
    """smallest image of z under z -> lambda z mod L, lambda a unit mod L"""
    if L == 1:
        return tuple(0 for _ in z)
    best = None
    for lam in units(L):
        t = tuple((lam * x) % L for x in z)
        if best is None or t < best:
            best = t
    return best


def gcd_clause(z, L, use_gcd=True):
    """Definition 2.1(a): some prime d | L divides every coordinate but at most one"""
    if not use_gcd or L == 1:
        return False
    for d in prime_factors(L):
        if sum(1 for x in z if x % d) <= 1:
            return True
    return False


def killed(s, k, z, L, P, use_gcd=True, betas=None):
    """is the lift class z (values mod L) P-killed at level L?  (P None = infinity)
    betas: the betas to try (default all of Z_L)."""
    z = tuple(x % L for x in z)
    if gcd_clause(z, L, use_gcd):
        return True
    Q = U.qunit(L, k, s)
    for beta in (range(L) if betas is None else betas):
        arc_lists = [U.arcs_for(s[i], (beta * z[i]) % L, L, k, Q) for i in range(k)]
        cells = U.Cells(arc_lists, Q)
        orv = 0
        for i in range(k):
            orv |= cells.mask(arc_lists[i])
            if U.exact_bad(beta * z[i], L, k):
                orv |= 1 << cells.M
        if cells.killed(orv, P):
            return True
    return False


def base_killed(s, k, P):
    return killed(s, k, tuple(0 for _ in s), 1, P)


def lift_children(s, k, z, L, c, P, use_gcd=True, deadline=None, clock=None):
    """canonical forms of the lifts of z (level L, not killed) to level cL that
    are not killed.  Branch and bound as in uniform.lift_parent, with c digits per
    coordinate; only betas that are not multiples of c are tested."""
    L2 = c * L
    Q = U.qunit(L2, k, s)
    vals = [tuple((z[i] + L * a) % L2 for a in range(c)) for i in range(k)]
    per = []
    for beta in range(1, L2):
        if beta % c == 0:
            continue
        arcs = [[U.arcs_for(s[i], (beta * v) % L2, L2, k, Q) for v in vals[i]] for i in range(k)]
        cells = U.Cells([a for row in arcs for a in row], Q)
        ex = 1 << cells.M
        masks = [tuple(cells.mask(arcs[i][a]) | (ex if U.exact_bad(beta * vals[i][a], L2, k) else 0)
                       for a in range(c)) for i in range(k)]
        big = cells.big(P)
        suf = [0] * (k + 1)
        for d in range(k - 1, -1, -1):
            u = suf[d + 1]
            for m in masks[d]:
                u |= m
            suf[d] = u
        per.append((cells, masks, big, suf))
    nb = len(per)
    out = set()
    choice = [0] * k
    nodes = [0]

    def leaf(cur):
        zz = tuple(vals[i][choice[i]] for i in range(k))
        if gcd_clause(zz, L2, use_gcd):
            return
        for j in range(nb):
            if per[j][0].killed(cur[j], P):
                return
        out.add(canon(zz, L2))

    def dfs(d, cur):
        nodes[0] += 1
        if deadline is not None and nodes[0] & 4095 == 0 and clock() > deadline:
            raise Deadline()
        for j in range(nb):
            big = per[j][2]
            if (cur[j] | per[j][3][d]) & big != big:
                return
        if d == k:
            leaf(cur)
            return
        for a in range(c):
            choice[d] = a
            dfs(d + 1, [cur[j] | per[j][1][d][a] for j in range(nb)])

    dfs(0, [0] * nb)
    return out


def cascade_chain(s, k, chain, P, use_gcd=True, max_parents=None, deadline=None, clock=None,
                  bruteforce=False):
    """levels c1, c1*c2, ... for chain = [c1, c2, ...].  Returns a dict with the
    canonical survivor list per level; 'cut' if a level had more than max_parents
    survivors with levels still to go, or the deadline passed."""
    s = tuple(s)
    res = {"chain": list(chain), "base_killed": base_killed(s, k, P), "levels": [], "cut": None}
    if res["base_killed"]:
        return res
    parents = [tuple(0 for _ in s)]
    L = 1
    for idx, c in enumerate(chain):
        L2 = c * L
        nxt = set()
        try:
            for z in parents:
                if deadline is not None and clock() > deadline:
                    raise Deadline()
                if bruteforce:
                    for a in product(range(c), repeat=k):
                        z2 = tuple((z[i] + L * a[i]) % L2 for i in range(k))
                        if not killed(s, k, z2, L2, P, use_gcd):
                            nxt.add(canon(z2, L2))
                else:
                    nxt |= lift_children(s, k, z, L, c, P, use_gcd, deadline, clock)
        except Deadline:
            res["cut"] = {"level": L2, "reason": "deadline"}
            return res
        res["levels"].append({"level": L2, "survivors": sorted(nxt)})
        if not nxt:
            break
        if max_parents is not None and len(nxt) > max_parents and idx + 1 < len(chain):
            res["cut"] = {"level": L2, "reason": "more than %d survivors" % max_parents}
            return res
        parents = sorted(nxt)
        L = L2
    return res


def last_set(res, level):
    """the survivor set at `level` (empty if the cascade emptied earlier), or None
    if the cascade was cut before reaching it"""
    for lv in res["levels"]:
        if lv["level"] == level:
            return set(map(tuple, lv["survivors"]))
    if res["base_killed"] or (res["levels"] and not res["levels"][-1]["survivors"]):
        return set()
    return None


def crt2(a, L1, b, L2):
    """x = a mod L1, x = b mod L2 (coprime), 0 <= x < L1 L2"""
    return (a + L1 * (((b - a) * pow(L1, -1, L2)) % L2)) % (L1 * L2)


def combine(s, k, L1, set1, L2, set2, P, use_gcd=True, deadline=None, clock=None):
    """U(L1 L2) from U(L1) and U(L2), gcd(L1, L2) = 1: every class of level L1 L2
    whose reductions are not killed is, up to a unit, CRT(a, mu b) with a in set1,
    b in set2 and mu a unit mod L2.  Betas divisible by L1 or by L2 give the
    positions of a reduction and are skipped.  Returns (set, tested, cut)."""
    assert gcd(L1, L2) == 1 and L1 > 1 and L2 > 1
    L = L1 * L2
    betas = [b for b in range(L) if b % L1 and b % L2]
    out = set()
    tested = 0
    us = units(L2)
    for a in sorted(set1):
        for b in sorted(set2):
            if deadline is not None and clock() > deadline:
                return out, tested, True
            for mu in us:
                z = tuple(crt2(a[i], L1, (mu * b[i]) % L2, L2) for i in range(k))
                tested += 1
                if not killed(s, k, z, L, P, use_gcd, betas=betas):
                    out.add(canon(z, L))
    return out, tested, False


def lift_info(s, k, z, L, use_gcd=True):
    """thresh.lift_info for any level L (general gcd clause); the result works
    with thresh.proper_at, thresh.threshold and thresh.killed_uniform."""
    s = tuple(s)
    z = tuple(x % L for x in z)
    assert len(s) == len(z) == k
    info = T.LiftInfo()
    info.s, info.k, info.z, info.L = s, k, z, L
    info.Q = Q = U.qunit(L, k, s)
    info.cells = []
    if gcd_clause(z, L, use_gcd):
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
