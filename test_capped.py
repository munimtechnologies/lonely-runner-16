# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for THEORY_10.md (the dual cap): exact rational arithmetic throughout."""
import itertools
import unittest
from fractions import Fraction as F

import capped as C


class TestStructure(unittest.TestCase):
    def test_structural_condition(self):
        for n in range(5, 16):
            self.assertTrue(C.structural_condition(C.B_list(n)), n)

    def test_blocks_vs_bruteforce(self):
        # the block method (structural lemma) against plain vertex enumeration
        for n in (5, 6, 7):
            Bs = C.B_list(n)
            cd = C.c_list(n)[-1]
            for U in (F(10), cd, cd * F(9, 10), cd * F(3, 4), cd / 2, cd / 4, cd / 10):
                b1, a1, _ = C.capped_min_blocks(Bs, U)
                b2, a2 = C.capped_min_bruteforce(Bs, U)
                self.assertEqual(b1, b2, (n, U))
                if b1 is not None:
                    self.assertTrue(C.feasible(a1, Bs, U))

    def test_uncapped_is_allikvere(self):
        # with the cap out of the way the minimum is K_n at t = c (his Lemma 3.6)
        for n in (14, 15):
            best, arg, _ = C.capped_min_blocks(C.B_list(n), F(10))
            self.assertEqual(best, C.K(n))
            self.assertEqual(arg, C.c_list(n))


class TestCappedMinimum(unittest.TestCase):
    def test_old_minimiser_violates_cap(self):
        self.assertEqual(C.c_list(15)[-1], F(17, 36))
        self.assertEqual(C.c_list(14)[-1], F(7, 15))
        self.assertGreater(F(17, 36), F(1, 3))
        self.assertGreater(F(7, 15), F(1, 3))

    def test_n15(self):
        c = C.c_list(15)
        best, arg, _ = C.capped_min(15)
        self.assertEqual(arg, c[:12] + [F(5, 14), F(15, 56)])
        self.assertEqual(best, C.prod(c[:12]) * F(75, 784))
        self.assertEqual(best / C.K(15), F(12150, 9163))
        g = C.gain_nats(15)
        self.assertTrue(2.1161 < g < 2.1163, g)

    def test_n14(self):
        c = C.c_list(14)
        best, arg, _ = C.capped_min(14)
        self.assertEqual(arg, c[:11] + [F(37, 105), F(37, 140)])
        self.assertEqual(best, C.prod(c[:11]) * F(1369, 14700))
        self.assertEqual(best / C.K(14), F(1369, 1029))
        g = C.gain_nats(14)
        self.assertTrue(1.9984 < g < 1.9986, g)

    def test_hand_vertices_n15(self):
        c = C.c_list(15)
        Bs = C.B_list(15)
        # case (B2) by hand: t_14 = 1/3, t_13 = 5/8 - 1/3 = 7/24
        t = c[:12] + [F(7, 24), F(1, 3)]
        self.assertTrue(C.feasible(t, Bs, F(1, 3)))
        self.assertEqual(C.prod(t) / C.K(15), F(7, 72) / F(187, 2592))
        self.assertGreater(C.prod(t), C.capped_min(15)[0])
        # the minimiser has 1/t_14 = 56/15 < 4, so sum h^2 = 3 there (THEORY_10 10.4)
        self.assertLess(1 / F(15, 56), 4)


class TestDualCap(unittest.TestCase):
    def test_identity(self):
        # t_d * sum q_k h_k^2 = 1 for explicit lattices and several basis orders
        for v in ([1, 2], [1, 3, 4, 7], [1, 2, 5, 9, 11], [1, 6, 4, 9]):
            n = len(v)
            for order in itertools.permutations(range(1, n)):
                t_d, h, sq = C.e_gram_last(v, order)
                self.assertEqual(t_d * sq, 1, (v, order))
        t_d, h, sq = C.e_gram_last([1, 2])
        self.assertEqual((t_d, h, sq), (F(1, 9), [-2, 1], F(9)))

    def test_relations_of_distinct_speeds(self):
        # every nonzero integer relation of distinct positive speeds has sum h^2 >= 3
        for v in ([1, 2, 3, 4], [2, 3, 5, 7], [1, 3, 4, 7], [1, 2, 4, 8]):
            for h in itertools.product(range(-2, 3), repeat=4):
                if any(h) and sum(a * b for a, b in zip(h, v)) == 0:
                    self.assertGreaterEqual(sum(a * a for a in h), 3, (v, h))
        # and sum q h^2 > 3 on a lattice built from them: t_d < 1/3
        for v in ([1, 3, 4, 7], [1, 2, 5, 9, 11], [1, 6, 4, 9]):
            n = len(v)
            for order in itertools.permutations(range(1, n)):
                t_d, _, _ = C.e_gram_last(v, order)
                self.assertLess(t_d, F(1, 3))


class TestHyperplane(unittest.TestCase):
    def test_lemma_10_4(self):
        for h1 in range(-2, 3):
            for h2 in range(-2, 3):
                if h1 == 0 and h2 == 0:
                    continue
                got = C.hyperplane_grid_max(h1, h2, 30)
                self.assertEqual(got, C.hyperplane_delta((h1, h2, 1)), (h1, h2))
        self.assertEqual(C.hyperplane_delta((1, 1, 1)), F(1, 3))
        self.assertEqual(C.hyperplane_delta((2, 2, 1)), F(2, 5))


if __name__ == "__main__":
    unittest.main()
