# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for thresh.py (THEORY_15.md) against a brute force written here from the
definition: w in Z_{Lp}^k is proper iff (L even and at most one w_i is odd) or some
b in Z_{Lp} has ||b w_i / (Lp)|| >= 1/(k+1) for every i."""
import random
import unittest
from fractions import Fraction
from itertools import product

import thresh as T
import uniform as U


def crt_lift(s, z, L, p):
    w = []
    for si, zi in zip(s, z):
        for m in range(L):
            x = si % p + p * m
            if x % L == zi % L:
                w.append(x)
                break
    return w


def brute_proper(s, k, z, L, p):
    w = crt_lift(s, z, L, p)
    if L >= 2 and sum(1 for x in w if x % 2) <= 1:
        return True
    N = L * p
    for b in range(1, N):
        if all((k + 1) * min((b * x) % N, N - (b * x) % N) >= N for x in w):
            return True
    return False


def brute_cascade(s, k, p, nlevels):
    """canonical improper classes at L = 1, 2, 4, ... by brute force"""
    out = []
    zero = tuple(0 for _ in s)
    cur = [zero] if not brute_proper(s, k, zero, 1, p) else []
    out.append((1, set(cur)))
    L = 1
    for _ in range(nlevels):
        if not cur:
            break
        L2 = 2 * L
        nxt = set()
        for z in cur:
            for d in product((0, 1), repeat=k):
                z2 = tuple((z[i] + L * d[i]) % L2 for i in range(k))
                if not brute_proper(s, k, z2, L2, p):
                    nxt.add(U.canon(z2, L2))
        out.append((L2, nxt))
        cur = sorted(nxt)
        L = L2
    return out


class ExactPerPrime(unittest.TestCase):
    def check_all(self, s, k, levels, primes, sample=None, seed=1):
        rng = random.Random(seed)
        n = 0
        for L in levels:
            zs = list(product(range(L), repeat=k))
            if sample is not None and len(zs) > sample:
                zs = rng.sample(zs, sample)
            for z in zs:
                info = T.lift_info(s, k, z, L)
                for p in primes:
                    self.assertEqual(T.proper_at(info, p), brute_proper(s, k, z, L, p),
                                     (s, z, L, p, info.status))
                    n += 1
        return n

    def test_k3(self):
        n = self.check_all((1, 2, 3), 3, (1, 2, 4, 8), (5, 7, 11, 13))
        self.assertGreater(n, 2000)

    def test_k4_tight(self):
        self.check_all((1, 2, 3, 4), 4, (1, 2, 4), (7, 11, 13))
        self.check_all((1, 2, 3, 4), 4, (8,), (7, 11), sample=150)

    def test_k4_other(self):
        self.check_all((1, 3, 4, 7), 4, (2, 4), (11, 13), sample=120, seed=2)


class Threshold(unittest.TestCase):
    def test_proper_above_threshold(self):
        s, k = (1, 2, 3), 3
        primes = T.primes_between(5, 160)
        seen = 0
        for L in (2, 4):
            for z in product(range(L), repeat=k):
                info = T.lift_info(s, k, z, L)
                thr = T.threshold(info)
                if thr is None or thr == 0:
                    continue
                for p in primes:
                    if p > thr:
                        seen += 1
                        self.assertTrue(brute_proper(s, k, z, L, p), (z, L, p, thr))
        self.assertGreater(seen, 50)

    def test_none_means_improper_everywhere(self):
        # (1,2,3,4) is tight (only witness 1/5): its base has no strict witness,
        # so it is improper at level 1 at every prime not dividing Q
        info = T.lift_info((1, 2, 3, 4), 4, (0, 0, 0, 0), 1)
        self.assertEqual(info.status, "open")
        self.assertIsNone(T.threshold(info))
        for p in (7, 11, 13, 17, 19, 23):
            self.assertFalse(brute_proper((1, 2, 3, 4), 4, (0, 0, 0, 0), 1, p))

    def test_matches_uniform(self):
        rng = random.Random(5)
        for s, k in (((1, 2, 3, 4), 4), ((1, 3, 4, 7), 4), ((1, 2, 3), 3)):
            for L in (1, 2, 4, 8):
                zs = list(product(range(L), repeat=k))
                if len(zs) > 80:
                    zs = rng.sample(zs, 80)
                for z in zs:
                    info = T.lift_info(s, k, z, L)
                    for P in (None, 7, 11, 23, 101, 1009):
                        self.assertEqual(T.killed_uniform(info, P),
                                         U.uniform_killed(s, k, tuple(x % L for x in z), L, P),
                                         (s, z, L, P))


class PrimeLevels(unittest.TestCase):
    def test_matches_brute_cascade(self):
        s, k = (1, 2, 3, 4), 4
        levels, cut = T.level_infos(s, k, 3, 7)
        self.assertIsNone(cut)
        for p in (7, 11, 13):
            brute = dict(brute_cascade(s, k, p, 3))
            listed = dict(levels)
            for L, st in brute.items():
                if L not in listed:  # Lemma U: nothing improper outside U_P
                    self.assertEqual(st, set(), (p, L))
            for L, infos in levels:
                mine = {inf.z for inf in infos if not T.proper_at(inf, p)}
                self.assertEqual(mine, brute.get(L, set()), (p, L))
            sizes, _ = T.prime_levels(levels, p)
            for L, n in sizes:
                self.assertEqual(n, len(brute.get(L, set())), (p, L))

    def test_primes(self):
        self.assertEqual(T.primes_between(250, 300), [251, 257, 263, 269, 271, 277, 281, 283, 293])
        self.assertEqual(len(T.primes_between(1, 1000)), 168)

    def test_threshold_value_example(self):
        # one hand-checkable case: s = (1,), k = 1, L = 1: bad arc ||t|| <= 1/2 is the
        # whole circle, so no strict witness; uniform.Cells needs two end points,
        # so use k = 2, s = (1, 2): bad arcs ||t|| <= 1/3 and ||2t|| <= 1/3
        info = T.lift_info((1, 2), 2, (0, 0), 1)
        # t = 1/3 .. 2/3 is outside ||t|| <= 1/3 only at the open middle (1/3, 2/3);
        # ||2t|| <= 1/3 covers t in [1/3, 2/3] around 1/2 only for |t - 1/2| <= 1/6,
        # i.e. exactly [1/3, 2/3]: the base (1, 2) has no strict witness at all.
        self.assertIsNone(T.threshold(info))
        self.assertEqual(Fraction(0), T.threshold(T.lift_info((1, 2), 2, (1, 0), 2)))


if __name__ == "__main__":
    unittest.main()
