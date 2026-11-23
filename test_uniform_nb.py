# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for uniform_nb.py (THEORY_16.md): non-binary levels against brute force.

brute_proper is Definition 2.1 of arXiv:2609.02604 written out directly (the
gcd clause over the primes dividing L, then every time b in Z_{Lp}); it shares
no code with uniform_nb."""
import random
import unittest
from itertools import product

import thresh as T
import uniform as U
import uniform_nb as N


def crt_lift(s, z, L, p):
    w = []
    for si, zi in zip(s, z):
        for m in range(L):
            x = si % p + p * m
            if x % L == zi % L:
                w.append(x)
                break
    return w


def brute_proper(s, k, z, L, p, use_gcd=True):
    w = crt_lift(s, z, L, p)
    if use_gcd:
        for d in range(2, L + 1):
            if L % d == 0 and all(d % e for e in range(2, d)):
                if sum(1 for x in w if x % d) <= 1:
                    return True
    M = L * p
    for b in range(1, M):
        if all((k + 1) * min((b * x) % M, M - (b * x) % M) >= M for x in w):
            return True
    return False


def brute_chain(s, k, p, chain, use_gcd=True):
    """canonical improper classes at each level of the chain, by brute force"""
    zero = tuple(0 for _ in s)
    cur = [] if brute_proper(s, k, zero, 1, p) else [zero]
    out = []
    L = 1
    for c in chain:
        L2 = c * L
        nxt = set()
        for z in cur:
            for a in product(range(c), repeat=k):
                z2 = tuple((z[i] + L * a[i]) % L2 for i in range(k))
                if not brute_proper(s, k, z2, L2, p, use_gcd):
                    nxt.add(N.canon(z2, L2))
        out.append((L2, nxt))
        cur = sorted(nxt)
        L = L2
    return out


def chain_sets(s, k, chain, P, use_gcd=True, bruteforce=False):
    r = N.cascade_chain(s, k, chain, P, use_gcd=use_gcd, bruteforce=bruteforce)
    out = []
    L = 1
    for c in chain:
        L *= c
        got = N.last_set(r, L)
        assert got is not None
        out.append((L, got))
    return out


class Basics(unittest.TestCase):
    def test_units_canon(self):
        self.assertEqual(N.units(15), [1, 2, 4, 7, 8, 11, 13, 14])
        self.assertEqual(N.units(14), [1, 3, 5, 9, 11, 13])
        self.assertEqual(N.canon((3, 5, 0), 15), N.canon((6, 10, 0), 15))
        for L in (2, 4, 8, 16):  # same canonical forms as uniform.py at binary levels
            for z in [(1, 3, 2), (5 % L, 2 % L, 7 % L)]:
                self.assertEqual(N.canon(z, L), U.canon(z, L))

    def test_gcd_clause(self):
        self.assertTrue(N.gcd_clause((3, 6, 9, 1), 15))      # d = 3, one exception
        self.assertTrue(N.gcd_clause((5, 10, 0, 7), 15))     # d = 5
        self.assertFalse(N.gcd_clause((3, 6, 1, 2), 15))
        self.assertTrue(N.gcd_clause((7, 0, 7, 3), 14))      # d = 7
        self.assertTrue(N.gcd_clause((2, 4, 1, 6), 14))      # d = 2
        self.assertFalse(N.gcd_clause((3, 6, 9, 1), 15, use_gcd=False))
        for z in [(1, 2, 4), (1, 3, 5), (2, 4, 6), (0, 0, 1)]:
            self.assertEqual(N.gcd_clause(z, 8), U.gcd_clause(z, 8))

    def test_crt2(self):
        for a in range(3):
            for b in range(5):
                x = N.crt2(a, 3, b, 5)
                self.assertEqual((x % 3, x % 5), (a, b))


class BinaryAgrees(unittest.TestCase):
    """at binary levels the general code must reproduce uniform.py exactly"""

    def test_k3(self):
        for P in (None, 13):
            r1 = U.cascade((1, 2, 3), 3, 3, P)
            got = chain_sets((1, 2, 3), 3, [2, 2, 2], P)
            want = [set(map(tuple, lv["survivors"])) for lv in r1["levels"]]
            while len(want) < 3:
                want.append(set())
            self.assertEqual([g for _, g in got], want)

    def test_k7(self):
        s = tuple(range(1, 8))
        for P in (None, 29):
            r1 = U.cascade(s, 7, 2, P)
            got = chain_sets(s, 7, [2, 2], P)
            want = [set(map(tuple, lv["survivors"])) for lv in r1["levels"]]
            while len(want) < 2:
                want.append(set())
            self.assertEqual([g for _, g in got], want)


class Sandwich(unittest.TestCase):
    """U_inf(L) <= J_p(L) <= U_p(L) at non-binary levels (Lemma U)"""

    def check(self, s, k, p, chain, use_gcd=True):
        bf = brute_chain(s, k, p, chain, use_gcd)
        ui = chain_sets(s, k, chain, None, use_gcd)
        up = chain_sets(s, k, chain, p, use_gcd)
        for (L, b), (_, lo), (_, hi) in zip(bf, ui, up):
            self.assertTrue(lo <= b, (s, p, L, sorted(lo - b)[:3]))
            self.assertTrue(b <= hi, (s, p, L, sorted(b - hi)[:3]))
        return bf, ui, up

    def test_k3(self):
        for p in (11, 13, 17):
            self.check((1, 2, 3), 3, p, [3, 5])
            self.check((1, 2, 3), 3, p, [5, 3])
        self.check((1, 2, 3), 3, 11, [2, 3])
        self.check((1, 2, 3), 3, 11, [2, 7])
        self.check((1, 2, 3), 3, 13, [3, 5], use_gcd=False)

    def test_k4(self):
        self.check((1, 2, 3, 4), 4, 11, [3, 5])
        self.check((1, 2, 3, 4), 4, 13, [5])
        self.check((1, 2, 3, 4), 4, 7, [2, 5])

    def test_k5_level6(self):
        # (1..5): k + 1 = 6 is not a power of 2, but level 6 = 2 * 3 reaches 1/6
        self.check((1, 2, 3, 4, 5), 5, 11, [2, 3])
        self.check((1, 2, 3, 4, 5), 5, 13, [3, 2])

    def test_other_vectors(self):
        self.check((1, 2, 4), 3, 11, [3, 5])
        self.check((1, 3, 4, 7), 4, 11, [3])


class DfsMatchesDirect(unittest.TestCase):
    def test_k3_k4(self):
        for s, k, chains in [((1, 2, 3), 3, ([3, 5], [5, 3], [2, 7])),
                             ((1, 2, 3, 4), 4, ([5], [7]))]:
            for chain in chains:
                for P in (None, 11):
                    for g in (True, False):
                        self.assertEqual(chain_sets(s, k, chain, P, g),
                                         chain_sets(s, k, chain, P, g, bruteforce=True),
                                         (s, chain, P, g))


class CombineMatchesChain(unittest.TestCase):
    def test_combine(self):
        for s, k in [((1, 2, 3), 3), ((1, 2, 3, 4), 4), ((1, 2, 4), 3)]:
            for P in (None, 11):
                for g in (True, False):
                    a = chain_sets(s, k, [3], P, g)[0][1]
                    b = chain_sets(s, k, [5], P, g)[0][1]
                    comb, tested, cut = N.combine(s, k, 3, a, 5, b, P, g)
                    self.assertFalse(cut)
                    self.assertEqual(tested, len(a) * len(b) * 4)
                    c35 = chain_sets(s, k, [3, 5], P, g)[1][1]
                    c53 = chain_sets(s, k, [5, 3], P, g)[1][1]
                    self.assertEqual(comb, c35, (s, P, g))
                    self.assertEqual(comb, c53, (s, P, g))
        # level 14 = 2 * 7 for k = 3
        a = chain_sets((1, 2, 3), 3, [2], None)[0][1]
        b = chain_sets((1, 2, 3), 3, [7], None)[0][1]
        comb, _, _ = N.combine((1, 2, 3), 3, 2, a, 7, b, None)
        self.assertEqual(comb, chain_sets((1, 2, 3), 3, [2, 7], None)[1][1])


class ExactPerPrime(unittest.TestCase):
    """thresh.proper_at on uniform_nb.lift_info is Definition 2.1 exactly"""

    def check_all(self, s, k, L, primes, sample=None, seed=1, use_gcd=True):
        rng = random.Random(seed)
        zs = list(product(range(L), repeat=k))
        if sample is not None and len(zs) > sample:
            zs = rng.sample(zs, sample)
        n = 0
        for z in zs:
            info = N.lift_info(s, k, z, L, use_gcd)
            for p in primes:
                self.assertEqual(T.proper_at(info, p), brute_proper(s, k, z, L, p, use_gcd),
                                 (s, z, L, p, info.status))
                n += 1
                thr = T.threshold(info)
                if thr is not None and p > thr:
                    self.assertTrue(T.proper_at(info, p))
        return n

    def test_k3(self):
        n = 0
        for L in (3, 5, 6):
            n += self.check_all((1, 2, 3), 3, L, (7, 11, 13))
        self.assertGreater(n, 1000)
        self.check_all((1, 2, 3), 3, 15, (7, 11), sample=300)
        self.check_all((1, 2, 3), 3, 15, (11,), sample=200, seed=3, use_gcd=False)

    def test_k4(self):
        self.check_all((1, 2, 3, 4), 4, 5, (7, 11))
        self.check_all((1, 2, 3, 4), 4, 15, (7,), sample=150, seed=2)
        self.check_all((1, 3, 4, 7), 4, 3, (11, 13))


class LinearLifts(unittest.TestCase):
    """THEORY.md 8.5 at non-binary levels: the linear lift of a tight vector is
    killed exactly when k + 1 divides the level (t = 0, Lemma L)"""

    def test_small(self):
        s = (1, 2, 3, 4)
        self.assertEqual(N.lift_info(s, 4, s, 5).status, "t0")
        self.assertFalse(N.killed(s, 4, tuple(x % 3 for x in s), 3, None))
        s = (1, 2, 3, 4, 5)
        self.assertEqual(N.lift_info(s, 5, s, 6).status, "t0")
        self.assertFalse(N.killed(s, 5, tuple(x % 2 for x in s), 2, None))
        self.assertFalse(N.killed(s, 5, tuple(x % 3 for x in s), 3, None))

    def test_paper_vectors(self):
        a14 = tuple(range(1, 15))
        self.assertEqual(N.lift_info(a14, 14, tuple(x % 15 for x in a14), 15).status, "t0")
        self.assertFalse(N.killed(a14, 14, tuple(x % 3 for x in a14), 3, None))
        a13 = tuple(range(1, 14))
        b13 = tuple(list(range(1, 12)) + [13, 24])
        for s in (a13, b13):
            self.assertEqual(N.lift_info(s, 13, tuple(x % 14 for x in s), 14).status, "t0")
            self.assertFalse(N.killed(s, 13, tuple(x % 2 for x in s), 2, None))


if __name__ == "__main__":
    unittest.main()
