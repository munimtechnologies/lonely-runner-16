# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for grid.py (THEORY.md Sec. 9).

1. Lemma G(ii): with D = 2Q the grid test equals uniform.uniform_killed, for every
   threshold P (exhaustive for s = (1,2,3), random small cases, a few (1..7) lifts).
   This checks uniform.py's cell machinery against a second, independent method.
2. Lemma G(i): an unblocked side gives a component of length >= 1/(N max s).
3. Lemma G2: the closed form of the near-grid-blocked level-2 lifts of (1..15),
   checked against a brute-force scan of all 2^15 lifts.
"""
import random
import unittest
from fractions import Fraction
from itertools import product

import grid as G
import uniform as U


class ExactAgreesWithUniform(unittest.TestCase):
    def check(self, s, k, z, L, P):
        D = G.exact_D(s, k, L)
        self.assertEqual(D, 2 * U.qunit(L, k, s))
        want = U.uniform_killed(tuple(s), k, tuple(z), L, P)
        got = G.grid_killed(s, k, z, L, D, P)
        self.assertEqual(got, want, (s, z, L, P))
        return got

    def test_k3_exhaustive(self):
        s = (1, 2, 3)
        seen = set()
        for L in (1, 2, 4):
            for z in product(range(L), repeat=3):
                for P in (None, 5, 11, 13, 29, 101):
                    seen.add(self.check(s, 3, z, L, P))
        self.assertEqual(seen, {True, False})  # both outcomes occur

    def test_random_small(self):
        rng = random.Random(2026)
        for _ in range(40):
            k = rng.randint(2, 4)
            s = [rng.randint(1, 5) for _ in range(k)]
            L = rng.choice([1, 2, 4, 8])
            z = [rng.randrange(L) for _ in range(k)]
            P = rng.choice([None, 3, 7, 13, 29, 60, 200])
            self.check(s, k, z, L, P)

    def test_k7(self):
        s = tuple(range(1, 8))
        # linear lift at level 8 = k + 1: exact witness at t = 0 (Lemma L analogue)
        self.assertTrue(self.check(s, 7, tuple(x % 8 for x in s), 8, None))
        # linear lift at level 4: never killed (THEORY.md 8.5, k + 1 gaps)
        self.assertFalse(self.check(s, 7, tuple(x % 4 for x in s), 4, None))
        rng = random.Random(8)
        for _ in range(3):
            z = tuple(rng.randrange(8) for _ in range(7))
            for P in (None, 29):
                self.check(s, 7, z, 8, P)


class SmallGridIsSufficient(unittest.TestCase):
    def test_lower_bound_and_soundness(self):
        """an unblocked side at a small grid gives length >= 1/(N max s), and
        grid_killed at any D never kills what the exact test keeps"""
        rng = random.Random(5)
        for _ in range(30):
            k = rng.randint(2, 4)
            s = [rng.randint(1, 5) for _ in range(k)]
            L = rng.choice([1, 2, 4])
            z = [rng.randrange(L) for _ in range(k)]
            D = rng.choice([k + 1, 2 * (k + 1), 3, 5])
            for beta in range(L):
                for c in range(D):
                    N, B, a = G.positions(s, k, z, L, beta, c, D)
                    ln = G.component_at(s, k, z, L, beta, c, D)
                    if ln is not None:
                        self.assertGreaterEqual(ln, Fraction(1, N * max(s)))
            for P in (None, 7, 29):
                if G.grid_killed(s, k, z, L, D, P):
                    self.assertTrue(G.grid_killed(s, k, z, L, G.exact_D(s, k, L), P))


def closed_form_blocked(Z):
    """Lemma G2 (THEORY.md 9.3): z in {0,1}^15 (bit j-1 = z_j) is blocked by every
    near-grid test at D = 16, level 2, s = (1..15)"""
    z = {j: (Z >> (j - 1)) & 1 for j in range(1, 16)}
    if z[8] == 0:
        return all(z[i] == z[i + 8] for i in (1, 3, 5, 7))
    c1 = z[4] == 1 or z[12] == 1
    c2 = any(z[i] == 1 for i in (2, 6, 10, 14)) or any(z[i] == 0 for i in (4, 12))
    c3 = any(z[i] == 0 for i in range(1, 16))
    c4 = any(z[i] == 1 for i in range(1, 16, 2)) or any(z[i] == 0 for i in (2, 4, 6, 10, 12, 14))
    return c1 and c2 and c3 and c4


class LemmaG2(unittest.TestCase):
    def test_closed_form(self):
        s = tuple(range(1, 16))
        entries = G.blocked_masks(s, 15, 2, 16, (0, 1))
        self.assertEqual(len(entries), 2 * 16 * 2)
        full = (1 << 15) - 1
        nA = nB = 0
        for Z in range(1 << 15):
            blocked = True
            for beta, c, side, (m0, m1) in entries:
                if not ((m0 & ~Z & full) | (m1 & Z)):
                    blocked = False
                    break
            self.assertEqual(blocked, closed_form_blocked(Z), bin(Z))
            if blocked:
                if (Z >> 7) & 1:
                    nB += 1
                else:
                    nA += 1
        self.assertEqual((nA, nB), (1024, 12030))

    def test_unblocked_kills_at_251(self):
        """an unblocked near-grid test at D = 16 gives a component longer than
        1/251, so it kills in U_251 (and in U_P for every P > 240)"""
        s = tuple(range(1, 16))
        rng = random.Random(16)
        for _ in range(25):
            z = [rng.randrange(2) for _ in range(15)]
            Z = sum(z[j] << j for j in range(15))
            if closed_form_blocked(Z):
                continue
            hit = False
            for beta in range(2):
                for c in range(16):
                    ln = G.component_at(s, 15, z, 2, beta, c, 16)
                    if ln is not None:
                        self.assertGreaterEqual(ln, Fraction(1, 240))
                        hit = True
            self.assertTrue(hit)
            self.assertTrue(G.grid_killed(s, 15, z, 2, 16, 251))

    def test_linear_lift_case_A(self):
        # z = (1..15) mod 2 has z_8 = 0 and z_i = z_{i+8}: blocked, as Sec. 8.5 requires
        Z = sum((j % 2) << (j - 1) for j in range(1, 16))
        self.assertTrue(closed_form_blocked(Z))


if __name__ == "__main__":
    unittest.main()
