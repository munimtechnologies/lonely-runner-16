# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""THEORY_19.md: exact checks for the 5 level-16 classes of gw15 = (1..13, 15, 28).

Standard library only; imports no repository code; exact Fractions. Reads, if
present, the committed raw output results/lrc16-uniform-v1/summary_uniform.json
(to compare the class list), and skips that one comparison otherwise.

What it checks:
  - the shapes of the 5 classes (D sets; class g1 off by 4 at speed 28);
  - the lift form w_j = s_j + 8p [s_j in D] and, for g1, w = 28 + 4 t' p;
  - the r-rule of THEORY_19 19.2 reproduces every hand window;
  - an exact sweep of all bad arcs: each hand window is one whole maximal
    component of W_D (of S' for g1) and is long enough at p = 251;
  - the parity step of Lemma 19.1 at every prime 251..1500;
  - a brute-force witness of the actual integer lift, inside the window, at every
    prime 251..1500, and a plain search over all times at the first five primes.
"""
import json
import math
import os
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
SPEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 28]
SIX = F(1, 16)

# the 5 classes of U_251(16) for gw15, z mod 16 in the order of SPEEDS
CLASSES = [
    ("g1", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 0]),
    ("g2", [1, 2, 3, 4, 5, 14, 15, 0, 1, 2, 3, 4, 5, 7, 12]),
    ("g3", [1, 2, 3, 4, 13, 14, 15, 0, 1, 2, 3, 4, 5, 15, 12]),
    ("g4", [1, 2, 11, 4, 5, 14, 7, 0, 9, 2, 11, 4, 13, 7, 12]),
    ("g5", [1, 2, 11, 4, 13, 14, 7, 0, 9, 2, 11, 4, 13, 15, 12]),
]

D_EXPECTED = {
    "g2": [6, 7, 8, 9, 10, 11, 12, 13, 15],
    "g3": [5, 6, 7, 8, 9, 10, 11, 12, 13],
    "g4": [3, 6, 8, 10, 12, 15],
    "g5": [3, 5, 6, 8, 10, 12],
}

# THEORY_19 19.2 table (centre j/8, side) and 19.3 interval
HAND = {
    "g2": (F(3, 8) + F(1, 192), F(3, 8) + F(1, 144)),
    "g3": (F(3, 8) + F(1, 192), F(3, 8) + F(1, 144)),
    "g4": (F(1, 8) + F(1, 192), F(1, 8) + F(1, 112)),
    "g5": (F(1, 8) - F(1, 144), F(1, 8) - F(1, 192)),
    "g1": (F(1, 14) - F(1, 1680), F(1, 14) + F(1, 1456)),
}
RULE = {"g2": (3, "right"), "g3": (3, "right"), "g4": (1, "right"), "g5": (1, "left")}
FIRST_PRIME = {"g2": 72, "g3": 72, "g4": 34, "g5": 72}


def primes(lo, hi):
    return [n for n in range(max(lo, 2), hi + 1)
            if all(n % d for d in range(2, math.isqrt(n) + 1))]


def d_of(z):
    diffs = [(zj - s) % 16 for s, zj in zip(SPEEDS, z)]
    if set(diffs) <= {0, 8}:
        return sorted(s for s, d in zip(SPEEDS, diffs) if d == 8)
    return None


def good_components(speeds, centres):
    """Maximal closed components [a, b] of {x in [0, 1] : ||s x - c|| >= 1/16 for
    every (s, c)}, by an exact sweep over the open bad arcs."""
    bad = []
    for s, c in zip(speeds, centres):
        for m in range(-2, s + 3):
            lo, hi = (m + c - SIX) / s, (m + c + SIX) / s
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


def rule_right(D, j):
    """THEORY_19 19.2: window to the right of j/8 from the residues r_s."""
    r = {s: (j * s - 4 * (s in D)) % 8 for s in SPEEDS}
    zeros = [s for s in SPEEDS if r[s] == 0]
    lo = max(F(1, s) for s in zeros)
    hi = min(F(15 - 2 * r[s], s) for s in SPEEDS)
    if lo > hi:
        return None, zeros
    return (F(j, 8) + lo / 16, F(j, 8) + hi / 16), zeros


def lift_by_search(z, p):
    """w_j = s_j + p t with 0 <= t < 16 and w_j = z_j (mod 16), found by search."""
    out = []
    for s, zj in zip(SPEEDS, z):
        ts = [t for t in range(16) if (s + p * t) % 16 == zj % 16]
        assert len(ts) == 1
        out.append(s + p * ts[0])
    return out


def witness(b, w, n):
    for wj in w:
        r = (b * wj) % n
        if 16 * min(r, n - r) < n:
            return False
    return True


class LevelSixteenGw(unittest.TestCase):
    def test_shapes(self):
        self.assertIsNone(d_of(CLASSES[0][1]))
        diffs1 = [(zj - s) % 16 for s, zj in zip(SPEEDS, CLASSES[0][1])]
        self.assertEqual([(s, d) for s, d in zip(SPEEDS, diffs1) if d], [(28, 4)])
        for name, z in CLASSES[1:]:
            D = d_of(z)
            self.assertEqual(D, D_EXPECTED[name], name)
            self.assertIn(8, D)
            self.assertIn(12, D)
            self.assertNotIn(4, D)
            self.assertNotIn(28, D)

    def test_lift_form(self):
        for p in primes(251, 400):
            for name, z in CLASSES[1:]:
                D = set(d_of(z))
                self.assertEqual(lift_by_search(z, p),
                                 [s + 8 * p * (s in D) for s in SPEEDS], (p, name))
            w = lift_by_search(CLASSES[0][1], p)
            tp = pow(p, -1, 4)
            self.assertEqual(tp % 2, 1)
            self.assertEqual(w, SPEEDS[:-1] + [28 + 4 * tp * p], p)

    def test_rule_gives_hand_windows(self):
        for name, (j, side) in RULE.items():
            D = set(D_EXPECTED[name])
            if side == "right":
                win, zeros = rule_right(D, j)
            else:
                mirror, zeros = rule_right(D, 8 - j)
                win = (1 - mirror[1], 1 - mirror[0])
            self.assertEqual(zeros, [12], name)
            self.assertEqual(win, HAND[name], name)
            # first prime from which the window is guaranteed to hold an odd time
            length = win[1] - win[0]
            self.assertEqual(math.ceil(F(1, 8) / length), FIRST_PRIME[name], name)
        # the j = 1 window of g2 is too short for p = 251, as 19.2 says
        win, _ = rule_right(set(D_EXPECTED["g2"]), 1)
        self.assertEqual(win, (F(1, 8) + F(1, 192), F(1, 8) + F(1, 176)))
        self.assertLess(win[1] - win[0], F(1, 8 * 251))

    def test_sweep_hand_windows_are_whole_components(self):
        for name, z in CLASSES:
            D = d_of(z)
            if D is None:
                speeds = SPEEDS[:-1]
                centres = [F(0)] * len(speeds)
                need = F(3, 16 * 251)
            else:
                speeds = SPEEDS
                centres = [F(1, 2) if s in D else F(0) for s in speeds]
                need = F(2, 16 * 251)
            a, b = HAND[name]
            comps = good_components(speeds, centres)
            inside = [c for c in comps if c[0] <= a and b <= c[1]]
            self.assertEqual(len(inside), 1, name)
            self.assertEqual(inside[0], (a, b), name)
            self.assertGreaterEqual(b - a, need, name)
            self.assertGreater(comps[0][0], 0, name)

    def test_g1_parity_step(self):
        z = CLASSES[0][1]
        for p in primes(251, 1500):
            w = lift_by_search(z, p)
            n = 16 * p
            r = (2 * w[-1]) % n
            self.assertEqual(r, 8 * p + 56, p)
            self.assertGreaterEqual(8 * min(r, n - r), n, p)
        # Lemma 19.1 holds from p = 147: 16p/780 >= 3
        self.assertEqual(math.ceil(F(3 * 780, 16)), 147)

    def test_every_prime_251_to_1500(self):
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
                    self.assertLessEqual(m + 2, n * b, (name, p))
                    self.assertTrue(witness(m, w, n) or witness(m + 2, w, n),
                                    (name, p, m))

    def test_full_brute_force_at_first_primes(self):
        for p in (251, 257, 263, 269, 271):
            n = 16 * p
            for name, z in CLASSES:
                w = lift_by_search(z, p)
                self.assertTrue(any(witness(b, w, n) for b in range(1, n // 2 + 1)),
                                (name, p))

    def test_matches_committed_job_output(self):
        path = os.path.join(HERE, "results", "lrc16-uniform-v1", "summary_uniform.json")
        if not os.path.exists(path):
            self.skipTest("raw job output not present in this checkout")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        runs = [r for r in data["runs"] if r["base"] == "gw15" and r["P"] == 251]
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["s"], SPEEDS)
        lv = [x for x in runs[0]["levels"] if x["level"] == 16]
        self.assertEqual(len(lv), 1)
        self.assertEqual(sorted(map(tuple, lv[0]["list"])),
                         sorted(tuple(z) for _, z in CLASSES))


if __name__ == "__main__":
    unittest.main(verbosity=2)
