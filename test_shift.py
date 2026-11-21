# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
"""Checks of THEORY.md Sec. 5 (pure Python, exact arithmetic):
  Lemma S   the shift lemma for composite d (counting step, and end to end),
  Lemma L   linear lifts of (1..15) are proper at every level divisible by 16.
"""
import random
import unittest
from fractions import Fraction
from math import gcd

import lrc_ref as R


class Loneliness(unittest.TestCase):
    def test_one_to_k_is_tight(self):
        for k in range(1, 8):
            val, _ = R.loneliness(list(range(1, k + 1)))
            self.assertEqual(val, Fraction(1, k + 1), k)

    def test_small_known_values(self):
        self.assertEqual(R.loneliness([1, 3])[0], Fraction(1, 2))
        self.assertEqual(R.loneliness([1, 2])[0], Fraction(1, 3))
        self.assertEqual(R.loneliness([5])[0], Fraction(1, 2))

    def test_lrc_small_cases(self):
        # LRC is a theorem for these sizes; this checks the loneliness routine
        rng = random.Random(7)
        for _ in range(60):
            m = rng.randint(1, 5)
            u = rng.sample(range(1, 40), m)
            self.assertGreaterEqual(R.loneliness(u)[0], Fraction(1, m + 1), u)


class LemmaSCounting(unittest.TestCase):
    """For d not dividing x: at most g * ceil(2 (d/g) / (k+1)) of the d shifts
    t0 + q/d put x in the open bad arc ||.|| < 1/(k+1), with g = gcd(x, d)."""

    def test_counting_bound_exhaustive_small(self):
        rng = random.Random(11)
        t0s = [Fraction(0), Fraction(1, 2), Fraction(1, 3)] + \
              [Fraction(rng.randint(0, 999), 1000) for _ in range(6)] + \
              [Fraction(rng.randint(0, 9999), 9973) for _ in range(6)]
        for k in (3, 7, 14, 15):
            for d in range(2, 41):
                for x in range(1, d + 1):
                    if x % d == 0:
                        self.assertEqual(R.shift_cost(x, d, k), 0)
                        continue
                    bound = R.shift_cost(x, d, k)
                    for t0 in t0s:
                        bad = R.bad_shifts(t0, x, d, k)
                        self.assertLessEqual(len(bad), bound, (k, d, x, t0))

    def test_bound_is_attained_sometimes(self):
        # the bound is not slack in general: odd x, d = 16, k = 15 can lose 2 shifts
        k, d, x = 15, 16, 1
        worst = max(len(R.bad_shifts(Fraction(j, 997), x, d, k)) for j in range(997))
        self.assertEqual(worst, R.shift_cost(x, d, k))
        self.assertEqual(R.shift_cost(1, 16, 15), 2)
        self.assertEqual(R.shift_cost(8, 16, 15), 8)
        self.assertEqual(R.shift_cost(1, 2, 15), 1)

    def test_table_k15(self):
        # THEORY.md Sec. 5 table: forbidden shifts per exceptional coordinate, k = 15
        exp = {4: {1: 1, 2: 2}, 8: {1: 1, 2: 2, 4: 4},
               16: {1: 2, 2: 2, 4: 4, 8: 8}, 32: {1: 4, 2: 4, 4: 4, 8: 8, 16: 16},
               3: {1: 1}, 5: {1: 1}, 7: {1: 1}, 11: {1: 2}, 13: {1: 2}}
        for d, row in exp.items():
            for g, f in row.items():
                self.assertEqual(R.shift_cost(g, d, 15), f, (d, g))


class LemmaSEndToEnd(unittest.TestCase):
    """shift_ok(u) != 0  ==>  the construction of the proof finds a witness."""

    def _check(self, u, k, l):
        d = R.shift_ok(u, k, l)
        if not d:
            return False
        D = sorted({x for x in u if x % d == 0})
        if D:
            val, _ = R.loneliness(D)
            self.assertGreaterEqual(val, Fraction(1, len(D) + 1), (u, d))
        res = R.shift_witness(u, k, d)
        self.assertIsNotNone(res, (u, k, d))
        t, _ = res
        self.assertTrue(all(R.dist(t * x) >= Fraction(1, k + 1) for x in u), (u, t))
        return True

    def test_k7_random(self):
        rng = random.Random(3)
        hits = 0
        for _ in range(120):
            l = rng.choice([4, 8, 6, 12])
            d = rng.choice([x for x in range(2, l + 1) if l % x == 0])
            e = rng.randint(1, 3)
            u = [d * rng.randint(1, 6) for _ in range(7 - e)] + \
                [rng.randint(1, 30) for _ in range(e)]
            hits += self._check(u, 7, l)
        self.assertGreater(hits, 10)

    def test_k15_level16(self):
        rng = random.Random(5)
        hits = 0
        for _ in range(12):
            e = rng.randint(2, 7)
            u = [16 * rng.randint(1, 6) for _ in range(15 - e)] + \
                [2 * rng.randint(0, 20) + 1 for _ in range(e)]
            hits += self._check(u, 15, 16)
        self.assertGreater(hits, 5)

    def test_shift_ok_rejects(self):
        # d = 2 never certifies anything beyond the gcd clause when k = 15
        u = [2] * 13 + [1, 3]
        self.assertEqual(R.shift_ok(u, 15, 2), 0)
        # all coordinates divisible by d: e = 0 is excluded (that is the gcd clause)
        self.assertEqual(R.shift_ok([16] * 15, 15, 16), 0)
        # seven odd exceptions, eight multiples of 16: d = 8 already works (7 < 8)
        self.assertEqual(R.shift_ok([16] * 8 + [1] * 7, 15, 16), 8)
        # eight odd exceptions: 8 is not < 8 and 16 is not < 16
        self.assertEqual(R.shift_ok([16] * 7 + [1] * 8, 15, 16), 0)
        # two odd and one 2 mod 4 exception: d = 4 costs 1 + 1 + 2 = 4, d = 8 costs 4 < 8
        self.assertEqual(R.shift_ok([16] * 12 + [1, 3, 2], 15, 16), 8)


class LemmaL(unittest.TestCase):
    """Linear lifts lambda*(1..15) mod 16p are proper at level 16 (and 32)."""

    def test_linear_lifts_proper(self):
        k = 15
        base = list(range(1, 16))
        for p in (17, 19, 23):
            for l in (16, 32):
                L = l * p
                for lam in range(1, L):
                    if lam % p == 0:
                        continue
                    if lam % 7 not in (1, 3):  # a sample keeps the test fast
                        continue
                    w = [(lam * x) % L for x in base]
                    if any(x % p == 0 for x in w):
                        continue
                    self.assertTrue(R.proper(w, k, p, l), (p, l, lam))

    def test_linear_lift_witness_is_one_sixteenth(self):
        # for a unit lambda the witness is b = lambda^{-1} * (lp/16) mod lp
        k, p, l = 15, 19, 16
        L = l * p
        for lam in (1, 3, 5, 7, 21, 37):
            if gcd(lam, L) != 1:
                continue
            w = [(lam * x) % L for x in range(1, 16)]
            b = (pow(lam, -1, L) * (L // 16)) % L
            self.assertTrue(all((k + 1) * min((b * x) % L, L - (b * x) % L) >= L for x in w))

    def test_one_to_15_not_proper_at_level_1(self):
        # the contrast: at level 1 the tight vector itself has no grid witness
        k, p = 15, 17
        self.assertFalse(R.proper(list(range(1, 16)), k, p, 1))


if __name__ == "__main__":
    unittest.main()
