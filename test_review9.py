# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Checks behind REVIEW_9.md (adversarial read of THEORY_9.md and grid.py).

Self-contained on purpose: it imports nothing from this repository, so it is a
second implementation of what it checks, not a re-run of grid.py.

1. Lemma G2 (THEORY_9 Sec. 9.3), from the reduced formula of Sec. 9.2
   y_i = 8 beta z_i + c i (mod 16) instead of grid.positions/blocked_masks:
   closed form, counts 1,024 and 12,030, beta = 0 always blocked.
2. The worked example of Sec. 9.3 (all ones except z_2 = 0, t = 1/5): strictness,
   dR = 1/320, dL = 3/1040, endpoints exactly at distance 1/16, length > 1/251.
3. Review remark R2: at the thresholds the project uses, a component can never
   be exactly 1/P long, so "> 1/P" versus ">= 1/P" never matters there.
4. Review remark R3: the coarse-grid bound 1/240 of Sec. 9.2 holds for L | 16 and
   fails at L = 32 (1/480 < 1/251).
5. Sec. 9.4 sub-levels: times beta = L2 b at level L = L1 L2 are the times b of
   level L1, and the gcd clause at L1 implies it at L.
"""
import random
import unittest
from fractions import Fraction
from math import gcd


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_all(xs):
    out = 1
    for x in xs:
        out = lcm(out, x)
    return out


def primes_between(a, b):
    return [n for n in range(max(a, 2), b + 1)
            if all(n % d for d in range(2, int(n ** 0.5) + 1))]


def y_masks():
    """L = 2, D = 16, s = (1..15). One entry per (beta, c, side): the bitmask of
    coordinates i (bit i - 1) that block when z_i = 0, and when z_i = 1."""
    bad = {"R": (0, 15), "L": (0, 1)}
    out = []
    for beta in (0, 1):
        for c in range(16):
            for side in ("R", "L"):
                m = [0, 0]
                for v in (0, 1):
                    for i in range(1, 16):
                        if (8 * beta * v + c * i) % 16 in bad[side]:
                            m[v] |= 1 << (i - 1)
                out.append((beta, c, side, m[0], m[1]))
    return out


def closed_form(Z):
    """Lemma G2 exactly as stated in THEORY_9.md 9.3 (bit i - 1 of Z is z_i)."""
    z = [None] + [(Z >> (i - 1)) & 1 for i in range(1, 16)]
    if z[8] == 0:
        return z[1] == z[9] and z[3] == z[11] and z[5] == z[13] and z[7] == z[15]
    c1 = z[4] == 1 or z[12] == 1
    c2 = any(z[j] == 1 for j in (2, 6, 10, 14)) or z[4] == 0 or z[12] == 0
    c3 = 0 in z[1:]
    c4 = (any(z[j] == 1 for j in range(1, 16, 2))
          or any(z[j] == 0 for j in range(2, 16, 2) if j != 8))
    return c1 and c2 and c3 and c4


class LemmaG2Independent(unittest.TestCase):
    def test_beta0_always_blocked(self):
        for beta, c, side, m0, m1 in y_masks():
            if beta == 0:
                self.assertEqual(m0, m1)
                self.assertNotEqual(m0, 0, (c, side))

    def test_closed_form_and_counts(self):
        masks = y_masks()
        self.assertEqual(len(masks), 2 * 16 * 2)
        nA = nB = 0
        for Z in range(1 << 15):
            blocked = all((m0 & ~Z) | (m1 & Z) for _, _, _, m0, m1 in masks)
            self.assertEqual(blocked, closed_form(Z), bin(Z))
            if blocked:
                if (Z >> 7) & 1:
                    nB += 1
                else:
                    nA += 1
        self.assertEqual((nA, nB), (1024, 12030))
        # the hand count of the proof: 2^14 - 2^12 - 2^8 - 1 - 1
        self.assertEqual(2 ** 14 - 2 ** 12 - 2 ** 8 - 2, 12030)
        self.assertEqual(2 ** 10, 1024)

    def test_linear_lift_is_type_A(self):
        Z = sum((i % 2) << (i - 1) for i in range(1, 16))
        self.assertTrue(closed_form(Z))
        self.assertEqual((Z >> 7) & 1, 0)


class WorkedExample(unittest.TestCase):
    def test_t_one_fifth(self):
        z = [None] + [1] * 15
        z[2] = 0
        Z = sum(z[i] << (i - 1) for i in range(1, 16))
        self.assertTrue(closed_form(Z))          # type (B): blocked on the grid
        self.assertEqual((Z >> 7) & 1, 1)
        lo, hi = Fraction(1, 16), Fraction(15, 16)

        def pos(t):
            return {i: (Fraction(z[i], 2) + t * i) % 1 for i in range(1, 16)}

        def dist(t):
            return min(min(p, 1 - p) for p in pos(t).values())

        t = Fraction(1, 5)
        p = pos(t)
        self.assertTrue(all(lo < x < hi for x in p.values()))
        self.assertEqual(dist(t), Fraction(1, 10))
        dR = min((hi - p[i]) / i for i in p)
        dL = min((p[i] - lo) / i for i in p)
        self.assertEqual(dR, Fraction(1, 320))
        self.assertEqual(dL, Fraction(3, 1040))
        self.assertGreater(dR + dL, Fraction(1, 251))
        # the ends are exactly at distance 1/16 (coordinates 12 and 13) ...
        self.assertEqual(dist(t + dR), lo)
        self.assertEqual(dist(t - dL), lo)
        self.assertEqual(p[12] + 12 * dR, hi)
        self.assertEqual(p[13] - 13 * dL, lo)
        # ... and every sampled interior point is a strict witness
        for j in range(1, 200):
            u = t - dL + (dR + dL) * Fraction(j, 200)
            self.assertGreater(dist(u), lo)


VECTORS = {
    "e15": (15, tuple(range(1, 16))),
    "gw15": (15, tuple(range(1, 14)) + (15, 28)),
    "a14": (14, tuple(range(1, 15))),
    "a13": (13, tuple(range(1, 14))),
    "b13": (13, tuple(range(1, 12)) + (13, 24)),
}
LEVELS = (1, 2, 3, 4, 5, 7, 8, 14, 15, 16, 32, 64, 128)


class Remarks(unittest.TestCase):
    def test_R2_no_ties_at_used_thresholds(self):
        """component lengths are dL + dR with denominators dividing N lcm(s),
        N = 2Q, Q = lcm(L, k+1) lcm(s); no prime P from 199 to 3,000 divides it"""
        ps = primes_between(199, 3000)
        for name, (k, s) in VECTORS.items():
            self.assertEqual(len(s), k)
            ls = lcm_all(s)
            for L in LEVELS:
                den = 2 * lcm(L, k + 1) * ls * ls
                for P in ps:
                    self.assertNotEqual(den % P, 0, (name, L, P))

    def test_R3_coarse_grid_scope(self):
        k, s = VECTORS["e15"]
        for L in (1, 2, 4, 8, 16):
            N = lcm(lcm(L, 16), k + 1)
            self.assertEqual((N, N // (k + 1)), (16, 1))
            self.assertEqual(Fraction(1, N * max(s)), Fraction(1, 240))
            self.assertGreater(Fraction(1, 240), Fraction(1, 251))
        N = lcm(lcm(32, 16), k + 1)
        self.assertEqual(N, 32)
        self.assertLess(Fraction(1, N * max(s)), Fraction(1, 251))

    def test_sublevel_transfer(self):
        rng = random.Random(9)
        for L1, L2 in ((3, 5), (5, 3), (2, 7), (7, 2), (16, 3)):
            L = L1 * L2
            for _ in range(30):
                k = rng.randint(2, 6)
                z = [rng.randrange(L) for _ in range(k)]
                for b in range(L1):
                    for i in range(k):
                        self.assertEqual(Fraction(L2 * b * z[i], L) % 1,
                                         Fraction(b * (z[i] % L1), L1) % 1)
                # gcd clause at L1 implies it at L (same prime, same coordinates)
                for q in (2, 3, 5, 7):
                    if L1 % q == 0:
                        at_L1 = [i for i in range(k) if (z[i] % L1) % q]
                        at_L = [i for i in range(k) if z[i] % q]
                        self.assertEqual(at_L1, at_L)


if __name__ == "__main__":
    unittest.main()
