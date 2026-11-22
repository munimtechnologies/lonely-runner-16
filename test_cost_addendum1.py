# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Checks for COST_addendum1.md (exact integer / rational arithmetic, < 5 s)."""
import itertools
import math
import unittest
from fractions import Fraction

import bounds


class Minkowski(unittest.TestCase):
    def test_threshold_r13(self):
        f15 = math.factorial(15)
        self.assertEqual(f15, 1307674368000)
        self.assertEqual(13 ** 15, 51185893014090757)
        self.assertEqual(13 ** 15 // f15, 39142)
        # every planned gate level: l <= 32, p <= 1000
        self.assertGreaterEqual(13 ** 15, f15 * 32 * 1000)

    def test_33_only_bites_beyond_4e10(self):
        self.assertGreater(33 ** 15 // math.factorial(15), 4 * 10 ** 10)

    def test_small_case_brute_force(self):
        # d = 3, M = 20: r^3 >= 3! * 20 holds for r = 5, so every w in (Z/20)^3
        # must satisfy m . w = 0 mod 20 for some nonzero m with ||m||_1 <= 5.
        d, M, r = 3, 20, 5
        self.assertGreaterEqual(r ** d, math.factorial(d) * M)
        ms = [m for m in itertools.product(range(-r, r + 1), repeat=d)
              if any(m) and sum(abs(x) for x in m) <= r]
        for w in itertools.product(range(M), repeat=d):
            self.assertTrue(any(sum(a * b for a, b in zip(m, w)) % M == 0 for m in ms), w)


class FlagSensitivity(unittest.TestCase):
    def test_uniform_scaling_of_B(self):
        f = Fraction(11, 10)
        cs = bounds.c_list(15)
        scaled = [f * c for c in cs]
        Kf = Fraction(1)
        for c in scaled:
            Kf *= c
        self.assertEqual(Kf, bounds.K(15) * f ** 14)
        # product bound change = 15 * (-1/2) * 14 ln f = -105 ln f, about -10 nats
        self.assertAlmostEqual(-105 * math.log(1.1), -10.0077, places=3)

    def test_single_r_derivatives(self):
        B = lambda r: bounds.B(15, r)
        c = lambda r: B(r) - B(r - 1)
        d14 = 7.5 * float(B(14) / c(14))
        d13 = 7.5 * float(B(13) / c(13) - B(13) / c(14))
        self.assertTrue(12.1 < d14 < 12.2, d14)
        self.assertTrue(9.7 < d13 < 9.8, d13)
        total = sum(B(r) / c(r) for r in range(1, 15)) - sum(B(r) / c(r + 1) for r in range(1, 14))
        self.assertEqual(total, 14)

    def test_c_increasing(self):
        cs = bounds.c_list(15)
        self.assertTrue(all(cs[i + 1] > cs[i] for i in range(len(cs) - 1)))


if __name__ == "__main__":
    unittest.main()
