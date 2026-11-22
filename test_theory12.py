# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for THEORY_12.md: the flag F* (exact loneliness constants equal to the
Lemma 3.3 values at every codimension) and the slack of every dual cap at the
THEORY_10 minimiser.  Exact integer / rational arithmetic throughout."""
import itertools
import unittest
from fractions import Fraction as F

import capped as C


def dist(a, N):
    """N * ||a / N|| for an integer a"""
    r = a % N
    return min(r, N - r)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det(rows):
    """exact determinant of a square matrix (Fractions)"""
    M = [[F(x) for x in r] for r in rows]
    n = len(M)
    out = F(1)
    for c in range(n):
        piv = next((i for i in range(c, n) if M[i][c] != 0), None)
        if piv is None:
            return F(0)
        if piv != c:
            M[c], M[piv] = M[piv], M[c]
            out = -out
        out *= M[c][c]
        for i in range(c + 1, n):
            f = M[i][c] / M[c][c]
            M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    return out


def gram_det(basis):
    return det([[dot(g, h) for h in basis] for g in basis])


def sigma(m):
    """1^2 + ... + m^2"""
    return m * (m + 1) * (2 * m + 1) // 6


def rel_basis(m, n):
    """basis of the relations of (1, 2, ..., m), padded with zeros to length n:
    g_k = k e_1 - e_k for k = 2..m"""
    out = []
    for k in range(2, m + 1):
        g = [0] * n
        g[0] = k
        g[k - 1] = -1
        out.append(g)
    return out


M1 = [(1, 1, -1, 0)]
M2 = [(1, 1, -1, 0), (2, 1, 0, -1)]
V2 = [(1, 0, 1, 2), (0, 1, 1, 1)]          # (x, y) -> (x, y, x+y, 2x+y)


class Lemma12_2(unittest.TestCase):
    def test_forms(self):
        for g in M2:
            for s in V2:
                self.assertEqual(dot(g, s), 0)

    def test_grid_max_is_quarter(self):
        # every grid point has min <= 1/4 (as Lemma 12.2 proves for all points),
        # and (1/4, 1/4) attains it
        for N in (40, 60, 120):
            best = 0
            for a in range(N):
                for b in range(N):
                    m = min(dist(a, N), dist(b, N), dist(a + b, N), dist(2 * a + b, N))
                    best = max(best, m)
            self.assertEqual(F(best, N), F(1, 4), N)
            q = N // 4
            self.assertEqual(min(dist(q, N), dist(q, N), dist(2 * q, N), dist(3 * q, N)), q)

    def test_case_inequalities(self):
        # the two inequalities used in case (A) hold exactly when delta > 1/4
        for delta in (F(1, 4) + F(1, 1000), F(2, 7), F(3, 10), F(1, 3)):
            self.assertGreater(3 * delta, 1 - delta)
            self.assertLess(2 - 3 * delta, 1 + delta)
        delta = F(1, 4)
        self.assertEqual(3 * delta, 1 - delta)


class Lattices(unittest.TestCase):
    def test_m2_saturated_and_det(self):
        self.assertEqual(gram_det(M2), 9)
        # every integer g in a box orthogonal to V2 is an integer combination of M2
        for g in itertools.product(range(-4, 5), repeat=4):
            if all(dot(g, s) == 0 for s in V2):
                a, b = -g[2], -g[3]
                comb = [a * x + b * y for x, y in zip(M2[0], M2[1])]
                self.assertEqual(tuple(comb), g)

    def test_nesting(self):
        w4 = (1, 2, 3, 4)
        for g in M1:
            self.assertIn(g, M2)
        for g in M2:
            self.assertEqual(dot(g, w4), 0)
        self.assertEqual(dot((1, 1, -1), (1, 2, 3)), 0)
        # (1,2,3,4) lies in M2^perp, so M2 is inside the relations of (1,2,3,4)
        self.assertEqual([dot(g, w4) for g in M2], [0, 0])

    def test_relation_lattice_det(self):
        for m in range(2, 15):
            B = rel_basis(m, m)
            self.assertEqual(gram_det(B), sigma(m), m)
            for g in B:
                self.assertEqual(dot(g, list(range(1, m + 1))), 0)
        self.assertEqual(sigma(4), 30)

    def test_flag_realised_by_v(self):
        # v = (1, ..., n-1, w) is orthogonal to every M_c of F*
        for n in (14, 15):
            v = list(range(1, n)) + [10 ** 6]
            pad = lambda g: list(g) + [0] * (n - len(g))
            for g in M2:
                self.assertEqual(dot(pad(g), v), 0)
            for c in range(3, n - 1):
                for g in rel_basis(c + 1, n):
                    self.assertEqual(dot(g, v), 0)


class LineConstants(unittest.TestCase):
    def test_delta_one_to_k(self):
        # max over t in (1/2520) Z of min_j ||j t|| is 1/(k+1) for k = 2..8
        N = 2520
        for k in range(2, 9):
            best = max(min(dist(j * a, N) for j in range(1, k + 1)) for a in range(N))
            self.assertEqual(F(best, N), F(1, k + 1), k)

    def test_constants_reproduce_B(self):
        for n in (14, 15):
            for c in range(1, n - 1):
                r = n - 1 - c
                self.assertEqual((2 * (F(1, c + 2) - F(1, n + 1))) ** 2, C.B(n, r), (n, c))
        self.assertEqual(C.hyperplane_delta((1, 1, -1)), F(1, 3))


class CapsSlack(unittest.TestCase):
    def check(self, n):
        best, t, _ = C.capped_min(n)
        d = n - 1
        self.assertEqual(len(t), d)
        self.assertTrue(C.feasible(t, C.B_list(n), F(1, 3)))
        self.assertEqual(best / C.K(n), {14: F(1369, 1029), 15: F(12150, 9163)}[n])
        dets = {1: 3, 2: 9}
        for c in range(3, d):
            dets[c] = sigma(c + 1)
        tails = {}
        for c in range(1, d):
            tail = C.prod(t[d - c:])
            tails[c] = tail
            self.assertLess(tail, F(1, dets[c]), (n, c))
        return t, tails

    def test_n15(self):
        t, tails = self.check(15)
        self.assertEqual(tails[1], F(15, 56))
        self.assertEqual(tails[2], F(75, 784))
        self.assertEqual(tails[3], F(975, 156800))

    def test_n14(self):
        t, tails = self.check(14)
        self.assertEqual(tails[1], F(37, 140))
        self.assertEqual(tails[2], F(1369, 14700))
        self.assertLess(tails[3], F(6, 1000))

    def test_quarter_cap_would_bind(self):
        # Sec. 12.3: a cap t_d < 1/4 is violated by the THEORY_10 minimiser
        self.assertGreater(F(15, 56), F(1, 4))
        self.assertGreater(F(37, 140), F(1, 4))


if __name__ == "__main__":
    unittest.main()
