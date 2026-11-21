# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Slow, obviously-correct reference implementation used to test lrc.c.

Definitions follow Allikvere, arXiv:2609.02604, Sections 2 and 4 (k speeds,
k+1 runners).  Everything here is brute force and only meant for tiny p.
The shift lemma ("Lemma S") and the exact loneliness of an integer vector are
described in THEORY.md, Sec. 5.
"""
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import gcd


def folded(p):
    return range(1, (p - 1) // 2 + 1)


def fold(x, p):
    x %= p
    return p - x if x > (p - 1) // 2 else x


def covers(v, a, k, p):
    """speed class v covers folded time a"""
    x = (a * v) % p
    return (k + 1) * min(x, p - x) < p


def cover_set(v, k, p):
    return frozenset(a for a in folded(p) if covers(v, a, k, p))


def level1_improper(vec, k, p):
    times = set(folded(p))
    got = set()
    for v in vec:
        got |= cover_set(v, k, p)
    return got == times


def irredundant_covers(k, p, maxsize=None):
    """all irredundant covers (as sorted tuples) containing class 1, size <= maxsize"""
    maxsize = k if maxsize is None else maxsize
    n = (p - 1) // 2
    times = frozenset(folded(p))
    cs = {v: cover_set(v, k, p) for v in folded(p)}
    out = []
    others = [v for v in folded(p) if v != 1]
    for s in range(1, maxsize + 1):
        for rest in combinations(others, s - 1):
            fam = (1,) + rest
            u = set()
            for v in fam:
                u |= cs[v]
            if u != times:
                continue
            ok = True
            for v in fam:
                u2 = set()
                for x in fam:
                    if x != v:
                        u2 |= cs[x]
                if u2 == times:
                    ok = False
                    break
            if ok:
                out.append(tuple(sorted(fam)))
    return out


def canonical(c, p):
    best = tuple(sorted(c))
    for x in c:
        inv = pow(x, p - 2, p)
        t = tuple(sorted(fold(inv * y, p) for y in c))
        if t < best:
            best = t
    return best


def canonical_covers(k, p, maxsize=None):
    return sorted({c for c in irredundant_covers(k, p, maxsize) if canonical(c, p) == c})


def all_level1_improper_multisets(k, p):
    return {m for m in combinations_with_replacement(list(folded(p)), k)
            if level1_improper(m, k, p)}


def expand_orbits(covs, k, p):
    """every k-multiset obtained from canonical covers by adding extra classes and
    multiplying by a unit"""
    out = set()
    fl = list(folded(p))
    for c in covs:
        extra = k - len(c)
        for ext in combinations_with_replacement(fl, extra):
            base = list(c) + list(ext)
            for u in fl:
                out.add(tuple(sorted(fold(u * y, p) for y in base)))
    return out


def prime_factors(l):
    f, d = [], 2
    while d * d <= l:
        if l % d == 0:
            f.append(d)
            while l % d == 0:
                l //= d
        d += 1
    if l > 1:
        f.append(l)
    return f


def proper(w, k, p, l):
    for d in prime_factors(l):
        if sum(1 for x in w if x % d) <= 1:
            return True
    L = l * p
    for b in range(1, L):
        if all((k + 1) * min((b * x) % L, L - (b * x) % L) >= L for x in w):
            return True
    return False


# ---------------- Lemma S (THEORY.md Sec. 5) ----------------

def shift_cost(x, d, k):
    """number of shifts q in 0..d-1 that coordinate x can forbid (0 if d | x)"""
    g = gcd(x, d)
    if g == d:
        return 0
    n = d // g
    return g * (-(-2 * n // (k + 1)))  # g * ceil(2n/(k+1))


def shift_ok(w, k, l):
    """smallest d | l (d >= 2) certified by Lemma S, or 0"""
    for d in range(2, l + 1):
        if l % d:
            continue
        e = sum(1 for x in w if x % d)
        tot = sum(shift_cost(x, d, k) for x in w)
        if e >= 1 and tot < d:
            return d
    return 0


def cascade(v, k, p, mults, shift=False):
    """number of improper lifts kept at each level, and the final survivors.
    With shift=True, improper lifts certified by Lemma S are dropped."""
    if proper(v, k, p, 1):
        return [], []
    cur = [tuple(v)]
    l = 1
    counts = []
    for c in mults:
        L = l * p
        nl = l * c
        nxt = []
        for w in cur:
            for a in product(range(c), repeat=k):
                w2 = tuple(w[i] + a[i] * L for i in range(k))
                if not proper(w2, k, p, nl):
                    if shift and shift_ok(w2, k, nl):
                        continue
                    nxt.append(w2)
        counts.append(len(nxt))
        cur = nxt
        l = nl
        if not cur:
            break
    return counts, cur


def improper_at_level_bruteforce(k, p, l):
    """all improper vectors in Z_{p,l}^k as sorted tuples (no symmetry reduction);
    for very small k, p, l only"""
    L = l * p
    res = [x for x in range(L) if x % p]
    out = set()
    for w in combinations_with_replacement(res, k):
        if not proper(w, k, p, l):
            out.add(w)
    return out


# ---------------- exact loneliness of an integer vector ----------------

def dist(x):
    """distance of a Fraction to the nearest integer"""
    f = x - (x.numerator // x.denominator)
    return min(f, 1 - f)


def loneliness(u):
    """max over real t of min_i ||t u_i|| for positive integers u (exact).
    At a maximum two active constraints have opposite slopes, so
    t = a/(u_i + u_j) for some i <= j and integer a."""
    u = [x for x in u if x]
    best, arg = Fraction(0), Fraction(0)
    for i in range(len(u)):
        for j in range(i, len(u)):
            s = u[i] + u[j]
            for a in range(1, s):
                t = Fraction(a, s)
                m = min(dist(t * x) for x in u)
                if m > best:
                    best, arg = m, t
    return best, arg


def bad_shifts(t0, x, d, k):
    """the shifts q in 0..d-1 with ||(t0 + q/d) x|| < 1/(k+1)"""
    lim = Fraction(1, k + 1)
    return [q for q in range(d) if dist((t0 + Fraction(q, d)) * x) < lim]


def shift_witness(u, k, d):
    """Constructive form of Lemma S: an LR time for the coordinates divisible by d
    (exact loneliness, which LRC(m) bounds below by 1/(m+1)), then the first
    shift q/d that is a witness for every coordinate; returns (t, q) or None."""
    D = sorted({x for x in u if x % d == 0})
    t0 = loneliness(D)[1] if D else Fraction(0)
    lim = Fraction(1, k + 1)
    for q in range(d):
        t = t0 + Fraction(q, d)
        if all(dist(t * x) >= lim for x in u):
            return t, q
    return None
