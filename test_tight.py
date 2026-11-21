# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Exact checks for THEORY.md Section 7 (tight sets for 16 runners).

Pure integer arithmetic, no engine needed:
  * the Goddyn-Wong / Zhang criterion for tight one-entry modifications of
    [n-1] gives exactly the persistent orbits Allikvere found for 14 runners
    (n = 14: (1..11,13,24)) and 15 runners (n = 15: none besides (1..14)), and
    none at all for 16 runners (n = 16, because n + 1 = 17 is prime);
  * (1..13,15,28) is NOT tight: t = 993/2800 is a strict witness, and so is
    every t in the open interval (5/14 - 1/336, 5/14 - 1/448);
  * it still has the non-strict witness a/16 (a odd) that Lemma L uses.
"""
import unittest
from fractions import Fraction
from math import gcd

GW_SET = list(range(1, 14)) + [15, 28]


def gw_tight(n, r, m):
    """Zhang (arXiv:2608.13599) Thm 1.1 / Goddyn-Wong Thm 2.3, case (1):
    [n-1] with r replaced by m*r is tight iff gcd(r, b) > 1 for every b with
    s <= b <= m*s - 1, where s = n - r (for n >= 4, m >= 2)."""
    s = n - r
    return all(gcd(r, b) > 1 for b in range(s, m * s))


def gw_list(n, mmax=60):
    return [(r, m) for r in range(1, n) for m in range(2, mmax + 1) if gw_tight(n, r, m)]


def frac_dist(x):
    """||x|| for a Fraction x."""
    f = x - (x.numerator // x.denominator)
    return min(f, 1 - f)


class GoddynWong(unittest.TestCase):
    def test_k13_matches_published_survivor(self):
        # n = 14 runners: the only tight one-entry modification is r = 12, m = 2,
        # i.e. (1..11,13,24), Allikvere's second persistent orbit for k = 13.
        self.assertEqual(gw_list(14), [(12, 2)])
        v = sorted([x for x in range(1, 14) if x != 12] + [24])
        self.assertEqual(v, list(range(1, 12)) + [13, 24])

    def test_k14_none(self):
        # n = 15 runners: none, matching the single persistent orbit (1..14).
        self.assertEqual(gw_list(15), [])

    def test_k15_none(self):
        # n = 16 runners: none.
        self.assertEqual(gw_list(16), [])

    def test_n_plus_1_prime_rule(self):
        # Lemma N (THEORY 7.2): if n + 1 is prime, b = s + 1 = n + 1 - r is
        # coprime to r and lies in [s, m s - 1] whenever s >= 2, m >= 2; and
        # s = 1 fails at b = 1.  So no (r, m) qualifies.
        for n in range(4, 200):
            if all((n + 1) % d for d in range(2, n + 1)):
                self.assertEqual(gw_list(n, 12), [], n)
                for r in range(1, n):
                    s = n - r
                    b = 1 if s == 1 else s + 1
                    self.assertEqual(gcd(r, b), 1)


class NotTight(unittest.TestCase):
    def test_strict_witness_993_2800(self):
        t = Fraction(993, 2800)
        for v in GW_SET:
            self.assertGreater(frac_dist(t * v), Fraction(1, 16), v)
        # the binding speeds, as in THEORY 7.3
        self.assertEqual(frac_dist(3 * t), Fraction(179, 2800))
        self.assertEqual(frac_dist(28 * t), Fraction(196, 2800))

    def test_whole_interval(self):
        lo = Fraction(5, 14) - Fraction(1, 336)
        hi = Fraction(5, 14) - Fraction(1, 448)
        # interior sample points, all strict witnesses
        for j in range(1, 200):
            t = lo + (hi - lo) * Fraction(j, 200)
            for v in GW_SET:
                self.assertGreater(frac_dist(t * v), Fraction(1, 16), (t, v))
        # at the endpoints one speed is exactly at distance 1/16
        self.assertEqual(frac_dist(3 * lo), Fraction(1, 16))
        self.assertEqual(frac_dist(28 * hi), Fraction(1, 16))
        self.assertEqual(hi - lo, Fraction(1, 1344))

    def test_lemma_L_witness_on_level_16_grid(self):
        for a in range(1, 16, 2):
            t = Fraction(a, 16)
            for v in GW_SET:
                self.assertGreaterEqual(frac_dist(t * v), Fraction(1, 16))
            for v in range(1, 16):
                self.assertGreaterEqual(frac_dist(t * v), Fraction(1, 16))

    def test_one_to_15_has_no_strict_witness_on_fine_grids(self):
        # sanity: [15] is tight, so no t = j/D (D <= 400) is a strict witness
        for D in range(1, 401):
            for j in range(0, D // 2 + 1):
                t = Fraction(j, D)
                self.assertFalse(all(frac_dist(t * v) > Fraction(1, 16)
                                     for v in range(1, 16)), (j, D))


if __name__ == "__main__":
    unittest.main()
