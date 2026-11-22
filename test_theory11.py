# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for THEORY_11.md and dual_cap_results.json (exact arithmetic where possible)."""
import itertools
import json
import math
import os
import unittest
from fractions import Fraction as F
from math import gcd

import capped as C

HERE = os.path.dirname(os.path.abspath(__file__))


def load_results():
    with open(os.path.join(HERE, "dual_cap_results.json")) as f:
        return json.load(f)


def relations(v, box):
    """nonzero integer h with entries in [-box, box] and h . v = 0"""
    out = []
    for h in itertools.product(range(-box, box + 1), repeat=len(v)):
        if any(h) and sum(a * b for a, b in zip(h, v)) == 0:
            out.append(h)
    return out


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rank(rows):
    M = [[F(x) for x in r] for r in rows]
    rk, cols = 0, len(M[0])
    for c in range(cols):
        piv = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c] / M[rk][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk


class ResultsFile(unittest.TestCase):
    """every number in dual_cap_results.json is recomputed from capped.py"""

    def test_cases(self):
        res = load_results()
        by_n = {c["n"]: c for c in res["cases"]}
        self.assertEqual(sorted(by_n), [14, 15])
        for n, c in by_n.items():
            self.assertEqual(c["runners"], n + 1)
            best, arg, _ = C.capped_min(n)
            kappa = best / C.K(n)
            self.assertEqual(F(c["kappa"]), kappa, n)
            self.assertLess(abs(c["kappa_float"] - float(kappa)), 1e-5, n)
            self.assertEqual([F(x) for x in c["argmin_tail"]], arg[-2:], n)
            self.assertEqual(F(c["old_t_d"]), C.c_list(n)[-1], n)
            g = C.gain_nats(n)
            self.assertLess(abs(c["gain_nats"] - g), 1e-4, n)
            self.assertLess(abs(c["target_after"] - (c["target_before"] - g)), 1e-3, n)
        self.assertEqual(by_n[14]["target_before"], 401.9846)
        self.assertEqual(by_n[15]["target_before"], 483.239)

    def test_scale_and_negatives(self):
        res = load_results()
        self.assertLess(abs(res["scale"]["ln_800"] - math.log(800)), 1e-4)
        g15 = C.gain_nats(15)
        self.assertLess(abs(res["scale"]["gain_16_runners_in_gate_primes_near_800"]
                            - g15 / math.log(800)), 1e-4)
        neg = res["negative_results"]
        _, arg, _ = C.capped_min(15)
        self.assertEqual(F(neg["tail_product_t13_t14_n15"]), arg[-2] * arg[-1])
        self.assertEqual(F(neg["rank2_cap"]), F(1, 8))
        self.assertEqual(neg["rank2_cap_binds"], arg[-2] * arg[-1] >= F(1, 8))
        self.assertFalse(neg["rank2_cap_binds"])
        u = 1 - math.sqrt(F(19, 30))
        self.assertLess(abs(neg["sum_relation_speed_threshold_u_star_n15"] - u), 1e-6)
        self.assertEqual(neg["hyperplane_coupling_gain_nats"], 0.0)


class Coupling(unittest.TestCase):
    """Lemma 11.1: V = span(v, z_1..z_{d-1}) is h^perp for the relation h dual to b_d"""

    def test_hyperplane_is_h_perp(self):
        for v in ([1, 3, 4, 7], [1, 2, 5, 9, 11], [1, 6, 4, 9]):
            n = len(v)
            for order in itertools.permutations(range(1, n)):
                _, h, _ = C.e_gram_last(v, order)
                zs = []
                for k in order[:-1]:
                    e = [0] * n
                    e[k] = 1
                    zs.append(e)
                self.assertEqual(rank([v] + zs), n - 1)
                self.assertEqual(dot(h, v), 0)
                for z in zs:
                    self.assertEqual(dot(h, z), 0)
                g = 0
                for x in h:
                    g = gcd(g, abs(x))
                self.assertEqual(g, 1)


class CaseTable(unittest.TestCase):
    """Prop 11.2: relation types by L = ||h||_1 and N = sum h^2"""

    def test_classification(self):
        for h in itertools.product(range(-3, 4), repeat=4):
            if not (any(x > 0 for x in h) and any(x < 0 for x in h)):
                continue
            g = 0
            for x in h:
                g = gcd(g, abs(x))
            if g != 1:
                continue
            L = sum(abs(x) for x in h)
            N = sum(x * x for x in h)
            self.assertGreaterEqual(N, L)
            self.assertGreaterEqual(L, 2)
            if L == 2:
                # e_a - e_b: forces equal speeds, excluded by Lemma 10.1 (iv)
                self.assertEqual(sorted(abs(x) for x in h), [0, 0, 1, 1])
            if N == 3:
                self.assertEqual(sorted(abs(x) for x in h), [0, 1, 1, 1])
                self.assertEqual(L, 3)
            if L == 3 and N != 3:
                self.assertEqual(N, 5)
                self.assertEqual(sorted(abs(x) for x in h), [0, 0, 1, 2])

    def test_deltas(self):
        self.assertEqual(C.hyperplane_delta((1, 1, -1)), F(1, 3))
        self.assertEqual(C.hyperplane_delta((2, -1)), F(1, 3))
        self.assertEqual(C.hyperplane_delta((1, 1, -1, -1)), F(1, 2))
        self.assertEqual(C.hyperplane_delta((1, 1, 1, 1, -1)), F(2, 5))
        for L in range(4, 40):
            d = C.hyperplane_delta((1,) * (L - 1) + (-1,))
            self.assertGreaterEqual(d, F(2, 5) if L % 2 else F(1, 2))

    def test_stronger_rows_cannot_go_lower(self):
        # a smaller cap only shrinks the feasible set (monotonicity)
        base = C.capped_min(15)[0]
        b4 = C.capped_min(15, F(1, 4))[0]
        self.assertIsNotNone(b4)
        self.assertGreaterEqual(b4, base)

    def test_remark_11_3(self):
        # 3 + 4u - 2u^2 = 56/15 at u = 1 - sqrt(19/30), and q_a + q_b + q_c is at least that
        u = 1 - math.sqrt(19 / 30)
        self.assertLess(abs(3 + 4 * u - 2 * u * u - 56 / 15), 1e-12)
        self.assertTrue(0.2041 < u < 0.2042)
        for a in range(1, 30):
            for b in range(1, 30):
                for M in (a + b, a + b + 1, 2 * (a + b), 7 * (a + b)):
                    ua, ub = F(a, M), F(b, M)
                    uc = ua + ub
                    q = [1 + 2 * x - x * x for x in (ua, ub, uc)]
                    self.assertGreaterEqual(sum(q), 3 + 4 * uc - 2 * uc * uc)


class RankTwo(unittest.TestCase):
    """Lemma 11.4: two independent relations of distinct speeds have Gram det >= 8"""

    def test_gram_det_at_least_8(self):
        for v in ([1, 2, 3, 4, 5], [2, 3, 5, 7, 11], [1, 3, 4, 7, 11], [1, 2, 4, 8, 9]):
            hs = relations(v, 2)
            for h in hs:
                self.assertGreaterEqual(dot(h, h), 3, (v, h))
            low = None
            for g, gp in itertools.combinations(hs, 2):
                det = dot(g, g) * dot(gp, gp) - dot(g, gp) ** 2
                if det == 0:
                    continue
                self.assertGreaterEqual(det, 8, (v, g, gp))
                low = det if low is None else min(low, det)
            if v == [1, 2, 3, 4, 5]:
                self.assertEqual(low, 8)

    def test_example_attains_8(self):
        v = (1, 2, 3, 4, 5)
        g, gp = (1, 1, -1, 0, 0), (1, 0, 0, 1, -1)
        self.assertEqual(dot(g, v), 0)
        self.assertEqual(dot(gp, v), 0)
        self.assertEqual(dot(g, g) * dot(gp, gp) - dot(g, gp) ** 2, 8)

    def test_not_binding_at_minimiser(self):
        _, arg, _ = C.capped_min(15)
        self.assertEqual(arg[-2] * arg[-1], F(75, 784))
        self.assertLess(F(75, 784), F(1, 8))
        # rank 3: Hermite gives det >= 27/2; the tail product is far below 2/27
        self.assertLess(arg[-3] * arg[-2] * arg[-1], F(2, 27))


if __name__ == "__main__":
    unittest.main()
