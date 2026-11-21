# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Slow, obviously-correct reference implementation used to test lrc.c.

Definitions follow Allikvere, arXiv:2609.02604, Sections 2 and 4 (k speeds,
k+1 runners).  Everything here is brute force and only meant for tiny p.
"""
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


def cascade(v, k, p, mults):
    """number of improper lifts at each level, and the final survivors"""
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
