# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
"""Reproduce the published constants of Allikvere, arXiv:2609.02604, Sec. 3,
and check the n = 15 (16-runner) constants derived in THEORY.md."""
import unittest
from decimal import Decimal
from fractions import Fraction

import bounds


class FlagBound(unittest.TestCase):
    def test_K14_exact(self):
        self.assertEqual(bounds.K(14),
                         Fraction(2289670297, 97243124257250844122250000000000000000))

    def test_A13_A14(self):
        self.assertAlmostEqual(float(bounds.lnA(13).exp()) / 6362078580113.54, 1.0, places=12)
        self.assertAlmostEqual(float(bounds.lnA(14).exp()) / 206083383792625.44, 1.0, places=12)

    def test_product_bounds(self):
        b13 = bounds.product_log_bound(13, Fraction(101, 200))
        b14 = bounds.product_log_bound(14, Fraction(1, 2))
        self.assertTrue(Decimal("341.03199") < b13 < Decimal("341.032"))
        self.assertTrue(Decimal("414.7793") < b14 < Decimal("414.7794"))

    def test_required_logsum_14(self):
        need = bounds.required_gate_logsum(14, Fraction(1, 2))
        self.assertTrue(Decimal("401.9845") < need < Decimal("401.9846"))
        self.assertEqual(bounds.lcm_upto(15), 360360)

    def test_ratios(self):
        self.assertEqual(bounds.min_ratio(13), Fraction(1175, 688))
        self.assertEqual(bounds.min_ratio(14), Fraction(847, 513))
        self.assertGreater(bounds.min_ratio(15), Fraction(4, 3))

    def test_lcm16(self):
        self.assertEqual(bounds.lcm_upto(16), 720720)


class SixteenRunners(unittest.TestCase):
    """n = 15 constants; the hand derivation is in THEORY.md"""

    def test_ratio_15_exact(self):
        self.assertEqual(bounds.min_ratio(15), Fraction(3751, 2349))

    def test_c_values_15(self):
        # 64 c_r = b_r^2 - b_{r-1}^2 with b_r = r/(16-r)
        cs = bounds.c_list(15)
        self.assertEqual(cs[0] * 64, Fraction(1, 225))
        self.assertEqual(cs[6] * 64, Fraction(496, 2025))
        self.assertEqual(cs[13] * 64, Fraction(272, 9))

    def test_lnA15(self):
        self.assertTrue(Decimal("36.5364") < bounds.lnA(15) < Decimal("36.5366"))

    def test_product_bound_15(self):
        b15 = bounds.product_log_bound(15, Fraction(49, 100))
        self.assertTrue(Decimal("496.70") < b15 < Decimal("496.75"), b15)
        need = bounds.required_gate_logsum(15, Fraction(49, 100))
        self.assertTrue(Decimal("483.21") < need < Decimal("483.27"), need)

    def test_shape_lemma_15_exact(self):
        checks = bounds.shape_n15_exact()
        self.assertTrue(all(checks.values()), checks)
        self.assertTrue(bounds.check_quartic_factor_n15())

    def test_shape_15_numeric(self):
        m15, t15 = bounds.family_min(15, 1)
        self.assertTrue(943 < m15 < 947, m15)
        self.assertTrue(0.0724 < t15 < 0.0725, t15)
        _, h15 = bounds.shape(15, pieces=200000)
        self.assertGreater(h15, (15 / 0.49) ** 2)


class ShapeBound(unittest.TestCase):
    def test_family_minima_match_paper(self):
        m14, _ = bounds.family_min(14, 1)
        m13, _ = bounds.family_min(13, 1)
        self.assertTrue(796.4 < m14 < 800, m14)
        self.assertTrue(663.48 < m13 < 670, m13)

    def test_rigorous_sweep_below_minimum(self):
        for n in (13, 14, 15):
            m, _ = bounds.family_min(n, 1)
            lb = bounds.family_lower_bound(n, 1, pieces=20000)
            self.assertLessEqual(lb, m)
            self.assertGreater(lb, 0.99 * m)

    def test_paper_shape_constants(self):
        _, h13 = bounds.shape(13, pieces=200000)
        _, h14 = bounds.shape(14, pieces=200000)
        self.assertGreater(h13, (2600 / 101) ** 2)  # R13 < 101/200
        self.assertGreater(h14, 784)                # R14 < 1/2


if __name__ == "__main__":
    unittest.main()
