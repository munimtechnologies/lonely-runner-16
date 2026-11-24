# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""REVIEW_18.md: an adversarial re-check of THEORY_18 that shares no code and no
data file with test_level16.py.

It starts from the 9 residue vectors z alone (copied by hand from THEORY_18's
table and the job output), re-derives D, the lift form and the step from scratch,
and finds the good windows by a different algorithm: an exact sweep over all bad
arcs ||i x - c_i|| < 1/16, giving every maximal component of W_D. Standard library
only; exact Fractions.
"""
import math
import unittest
from fractions import Fraction as F

K = 15
SIX = F(1, 16)

# (name, z mod 16): the 9 classes of U_251(16) for s = (1..15)
CLASSES = [
    ("class 1", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 15]),
    ("class 2", [1, 2, 3, 4, 5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 7]),
    ("class 3", [1, 2, 3, 4, 5, 14, 7, 0, 9, 10, 11, 4, 13, 6, 7]),
    ("class 4", [1, 2, 3, 4, 5, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7]),
    ("class 5", [1, 2, 3, 4, 13, 14, 7, 0, 9, 10, 11, 4, 13, 6, 7]),
    ("class 6", [1, 2, 3, 4, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 15]),
    ("class 7", [1, 2, 11, 4, 5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 7]),
    ("class 8", [1, 2, 11, 4, 13, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15]),
    ("class 9", [1, 2, 11, 4, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 15]),
]

# THEORY_18's hand windows (18.2 table) and the class-1 interval (18.3)
HAND = {
    "class 2": (F(1, 8) + F(1, 192), F(1, 8) + F(1, 112)),
    "class 3": (F(1, 8) + F(1, 192), F(1, 8) + F(1, 112)),
    "class 5": (F(1, 8) + F(1, 192), F(1, 8) + F(1, 112)),
    "class 7": (F(1, 8) + F(1, 192), F(1, 8) + F(1, 112)),
    "class 8": (F(1, 8) - F(1, 144), F(1, 8) - F(1, 192)),
    "class 4": (F(5, 8) - F(1, 144), F(5, 8) - F(1, 192)),
    "class 6": (F(1, 6) - F(1, 96), F(1, 6) - F(1, 144)),
    "class 9": (F(3, 8) - F(1, 112), F(3, 8) - F(1, 192)),
    "class 1": (F(1, 14) - F(1, 1680), F(1, 14) + F(1, 1456)),
}


def primes(lo, hi):
    return [n for n in range(max(lo, 2), hi + 1)
            if all(n % d for d in range(2, math.isqrt(n) + 1))]


def good_components(speeds, centres):
    """Maximal closed components [a, b] of {x in [0, 1] : ||i x - c|| >= 1/16 for
    every (i, c)}, by an exact sweep over the open bad arcs."""
    bad = []
    for i, c in zip(speeds, centres):
        for m in range(-2, i + 3):
            lo, hi = (m + c - SIX) / i, (m + c + SIX) / i
            if hi > 0 and lo < 1:
                bad.append((lo, hi))
    bad.sort()
    comps, pos = [], F(0)
    for lo, hi in bad:
        if lo >= pos:
            comps.append((pos, min(lo, F(1))))
        pos = max(pos, hi)
    if pos <= 1:
        comps.append((pos, F(1)))
    return [c for c in comps if c[0] <= c[1]]


def d_of(z):
    diffs = [(z[i - 1] - i) % 16 for i in range(1, K + 1)]
    if set(diffs) <= {0, 8}:
        return sorted(i for i in range(1, K + 1) if diffs[i - 1] == 8)
    return None


def lift_by_search(z, p):
    """w_i = i + p t_i with 0 <= t_i < 16 and w_i = z_i (mod 16), found by search."""
    out = []
    for i, zi in enumerate(z, start=1):
        ts = [t for t in range(16) if (i + p * t) % 16 == zi % 16]
        assert len(ts) == 1
        out.append(i + p * ts[0])
    return out


def witness(b, w, n):
    for wi in w:
        r = (b * wi) % n
        if 16 * min(r, n - r) < n:
            return False
    return True


class Review18(unittest.TestCase):
    def test_shapes(self):
        shapes = [d_of(z) for _, z in CLASSES]
        self.assertIsNone(shapes[0])
        for D in shapes[1:]:
            self.assertIsNotNone(D)
            self.assertIn(8, D)
            self.assertNotIn(4, D)
            self.assertNotIn(1, D)
        diffs1 = [(CLASSES[0][1][i - 1] - i) % 16 for i in range(1, K + 1)]
        self.assertEqual([(i + 1, d) for i, d in enumerate(diffs1) if d], [(14, 2)])

    def test_lift_form(self):
        # R1: for a D-shaped class the lift is w_i = i + 8p [i in D], at every odd p
        for p in primes(251, 400):
            for name, z in CLASSES[1:]:
                D = set(d_of(z))
                self.assertEqual(lift_by_search(z, p),
                                 [i + 8 * p * (i in D) for i in range(1, K + 1)], (p, name))

    def test_sweep_contains_hand_windows(self):
        # R2: the component of W_D (or of S' for class 1) that contains the hand
        # window is found by the sweep, and is at least as long as needed at 251.
        for name, z in CLASSES:
            D = d_of(z)
            if D is None:
                speeds = [i for i in range(1, K + 1) if i != 14]
                centres = [F(0)] * len(speeds)
                need = F(5, 16 * 251)
            else:
                speeds = list(range(1, K + 1))
                centres = [F(1, 2) if i in D else F(0) for i in speeds]
                need = F(2, 16 * 251)
            a, b = HAND[name]
            comps = good_components(speeds, centres)
            inside = [c for c in comps if c[0] <= a and b <= c[1]]
            self.assertEqual(len(inside), 1, name)
            c = inside[0]
            self.assertGreaterEqual(c[1] - c[0], need, name)
            # every hand window is a whole component (its ends are binding)
            self.assertEqual(c, (a, b), name)
            # 0 is bad, so no component wraps around the circle
            self.assertGreater(comps[0][0], 0, name)

    def test_class1_step(self):
        # R3: b -> b + 4 moves coordinate 14 by (8p + 56)/(16p) = 1/2 + 7/(2p),
        # whose distance to the nearest integer is at least 1/8
        z = CLASSES[0][1]
        for p in primes(251, 1500):
            w = lift_by_search(z, p)
            n = 16 * p
            r = (4 * w[13]) % n
            self.assertEqual(r, 8 * p + 56, p)
            self.assertGreaterEqual(8 * min(r, n - r), n, p)
            for i in range(1, K + 1):
                if i != 14:
                    self.assertEqual(w[i - 1], i)

    def test_every_prime_251_to_1500_from_sweep(self):
        # R4: at each prime, an odd time (classes 2-9) or a pair b, b+4 (class 1)
        # inside the swept component is a brute-force witness of the actual lift
        for name, z in CLASSES:
            D = d_of(z)
            a, b = HAND[name]
            for p in primes(251, 1500):
                n = 16 * p
                w = lift_by_search(z, p)
                m = math.ceil(n * a)
                if D is not None:
                    if m % 2 == 0:
                        m += 1
                    self.assertLessEqual(m, n * b, (name, p))
                    self.assertTrue(witness(m, w, n), (name, p, m))
                else:
                    self.assertLessEqual(m + 4, n * b, (name, p))
                    self.assertTrue(witness(m, w, n) or witness(m + 4, w, n), (name, p, m))

    def test_full_brute_force_at_first_primes(self):
        # R5: plain search over all b (no windows) at the first five primes
        for p in (251, 257, 263, 269, 271):
            n = 16 * p
            for name, z in CLASSES:
                w = lift_by_search(z, p)
                self.assertTrue(any(witness(b, w, n) for b in range(1, n // 2 + 1)),
                                (name, p))


if __name__ == "__main__":
    unittest.main(verbosity=2)
