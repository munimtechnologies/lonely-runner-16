# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for indep.py / indep_brute.c (REVIEW_18.md, PLAN_addendum15.md).

Every fact asserted here is proved by hand in REVIEW_18.md (Section R6); no
prediction of the job is asserted. The C tests skip when no C compiler is found,
unless INDEP_REQUIRE_C=1 (run_tests_indep.py sets it in the compete job).
"""
import os
import random
import unittest
from fractions import Fraction as F

import indep as I

E15 = list(range(1, 16))
GW15 = list(range(1, 14)) + [15, 28]


def norm(y):
    y = y - (y.numerator // y.denominator)
    return min(y, 1 - y)


def crt_unit(lam, L, p):
    for x in range(L * p):
        if x % L == lam % L and x % p == 1:
            return x
    raise AssertionError


class Definitions(unittest.TestCase):
    def test_witness_matches_fractions(self):
        rng = random.Random(18)
        for _ in range(400):
            n = rng.choice([22, 44, 52, 116, 4016])
            k = rng.randint(1, 6)
            w = [rng.randrange(n) for _ in range(k)]
            b = rng.randrange(1, n)
            want = all(norm(F(b * wi, n)) >= F(1, k + 1) for wi in w)
            self.assertEqual(I.is_witness(b, w, n, k + 1), want)

    def test_tight_e15_improper_at_level_one(self):
        # R6(a): ||i x|| >= 1/16 for i = 1..15 forces x = j/16 with j odd; b/251 is
        # never such a point.
        self.assertFalse(I.proper([i % 251 for i in E15], 251, 1, 16))

    def test_linear_lift_e15(self):
        # R6(b): w_i = i at level L <= 8 is improper (x = b/(Lp) = j/16 needs
        # b = jLp/16, not an integer for j odd and L <= 8; 8 odd entries, so no gcd
        # clause); at level 16, b = p is a witness (x = 1/16).
        p = 251
        for L in (2, 4, 8):
            self.assertFalse(I.proper(list(E15), L * p, L, 16), L)
        self.assertTrue(I.proper(list(E15), 16 * p, 16, 16))

    def test_small_cascade_123(self):
        # R6(c): s = (1,2,3), k + 1 = 4, p = 11. Level 1 improper (x = j/4 needed),
        # linear lift (1,0,1) improper at level 2, linear (1,2,3) proper at level 4
        # (b = 11, x = 1/4).
        levels, cut = I.cascade([1, 2, 3], 11, 16)
        self.assertIsNone(cut)
        self.assertEqual(levels[0][:2], (1, 1))
        self.assertEqual(levels[1][0], 2)
        self.assertIn([1, 0, 1], levels[1][2])
        if len(levels) > 2:
            self.assertEqual(levels[2][0], 4)
            self.assertNotIn([1, 2, 3], levels[2][2])
        for L, c, zs in levels:
            self.assertEqual(c, len(zs))
            if L > 1:
                self.assertTrue(I.closed_under_units(zs, L))

    def test_unit_invariance(self):
        # R6(d): Lambda = lambda (mod L), 1 (mod p) maps a lift to a lift and
        # permutes the times, so properness is constant on unit classes.
        rng = random.Random(7)
        for _ in range(60):
            p = rng.choice([11, 13, 17, 19])
            L = rng.choice([2, 4, 8])
            k = rng.randint(2, 4)
            s = rng.sample(range(1, p), k)
            w = [(si + p * rng.randrange(L)) % (L * p) for si in s]
            lam = rng.randrange(1, L, 2)
            Lam = crt_unit(lam, L, p)
            w2 = [(Lam * wi) % (L * p) for wi in w]
            self.assertEqual([x % p for x in w2], [x % p for x in w])
            self.assertEqual(I.proper(w, L * p, L, k + 1), I.proper(w2, L * p, L, k + 1))

    def test_unit_class(self):
        self.assertEqual(I.unit_class([1, 2, 3], 4), (1, 2, 3))
        self.assertEqual(I.unit_class([3, 2, 1], 4), (1, 2, 3))
        self.assertEqual(I.unit_class([1, 0, 1], 2), (1, 0, 1))
        self.assertEqual(I.unit_class([5, 0, 7], 8), (1, 0, 3))

    def test_grade_prime_synthetic(self):
        u = {2: ({(1, 0, 1)}, True), 4: ({(1, 2, 3)}, True)}
        levels = [(1, 1, [[0, 0, 0]]), (2, 1, [[1, 0, 1]]), (4, 2, [[1, 2, 3], [3, 2, 1]]),
                  (8, 0, [])]
        rec = I.grade_prime("x", 11, levels, None, u, uinf={2: ({(1, 0, 1)}, True)})
        self.assertEqual(rec["I2_outside_U251"], [])
        self.assertEqual(rec["I3_missing_Uinf"], [])
        self.assertTrue(rec["I5_closure_ok"])
        self.assertEqual(rec["death_level"], 8)
        levels[2] = (4, 2, [[1, 2, 1], [3, 2, 3]])
        rec = I.grade_prime("x", 11, levels, None, u)
        self.assertEqual(rec["I2_outside_U251"], [{"level": 4, "z": [1, 2, 1]}])
        rec = I.grade_prime("x", 11, [(1, 1, [[0, 0, 0]]), (2, 0, [])], None, u,
                            uinf={2: ({(1, 0, 1)}, True)})
        self.assertEqual(rec["I3_missing_Uinf"], [{"level": 2, "z": [1, 0, 1]}])

    def test_u_classes_on_committed_file(self):
        path = os.path.join(I.HERE, "summary_uniform.json")
        if not os.path.exists(path):
            path = os.path.join(I.HERE, "results", "lrc16-uniform-v1", "summary_uniform.json")
        if not os.path.exists(path):
            self.skipTest("summary_uniform.json not present in this checkout")
        data = I.load_json(path)
        u = I.u_classes(data, "e15", 251)
        self.assertEqual(len(u[16][0]), 9)
        self.assertTrue(u[16][1])
        uinf = I.u_classes(data, "e15", None)
        for L in (2, 4, 8):
            self.assertEqual(uinf[L][0], {I.unit_class([i % L for i in E15], L)})
        self.assertEqual(uinf[16][0], set())
        self.assertEqual(I.u_classes(data, "gw15", None), {})


@unittest.skipUnless(os.environ.get("INDEP_REQUIRE_C") == "1" or I.build_c() is not None,
                     "no C compiler")
class CMatchesPython(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = I.build_c(required=True)

    def same(self, s, p, lmax, cap):
        py = I.cascade(s, p, lmax, cap)
        c = I.run_c(self.exe, s, p, lmax, cap)
        self.assertEqual(c, py, (s, p, lmax))
        return c

    def test_k3(self):
        for p in (11, 13, 29, 101):
            self.same([1, 2, 3], p, 16, 10 ** 6)

    def test_k5(self):
        for p in (31, 37):
            self.same([1, 2, 3, 4, 5], p, 8, 5000)

    def test_k7_capped(self):
        self.same(list(range(1, 8)), 29, 8, 300)

    def test_k9(self):
        self.same(list(range(1, 10)), 53, 2, 2000)

    def test_e15_first_levels(self):
        levels, cut = I.run_c(self.exe, E15, 251, 2, 100000)
        self.assertEqual(levels[0][:2], (1, 1))
        self.assertIn([i % 2 for i in E15], levels[1][2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
