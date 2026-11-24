# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""REVIEW_19.md: an adversarial re-check of THEORY_19 (gw15 = (1..13, 15, 28)).

Standard library only. Shares no code with test_level16_gw.py and imports no
repository module. Different methods from that test:
  - lifts by the CRT formula w = s + p * ((z - s) * p^-1 mod 16), not by search;
  - each window is checked by the image of a linear map: for every speed the
    image interval s*[a, b] + c must sit inside one arc [k + 1/16, k + 15/16];
  - the binding speed at each end is checked to sit exactly on 1/16 or 15/16;
  - at every prime 251..1500, EVERY odd time in the g2..g5 windows (every time
    pair b, b + 2 in the g1 interval) is tested on the actual integer lift;
  - a plain search over all times at four primes, including the two largest
    primes (1321, 1327) of the range where the theorem has content.
Reads results/lrc16-uniform-v1/summary_uniform.json when present.
"""
import json
import math
import os
import unittest
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
S = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 28)
LO, HI = Q(1, 16), Q(15, 16)

Z = {
    "g1": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 0),
    "g2": (1, 2, 3, 4, 5, 14, 15, 0, 1, 2, 3, 4, 5, 7, 12),
    "g3": (1, 2, 3, 4, 13, 14, 15, 0, 1, 2, 3, 4, 5, 15, 12),
    "g4": (1, 2, 11, 4, 5, 14, 7, 0, 9, 2, 11, 4, 13, 7, 12),
    "g5": (1, 2, 11, 4, 13, 14, 7, 0, 9, 2, 11, 4, 13, 15, 12),
}
WIN = {
    "g1": (Q(1, 14) - Q(1, 1680), Q(1, 14) + Q(1, 1456)),
    "g2": (Q(3, 8) + Q(1, 192), Q(3, 8) + Q(1, 144)),
    "g3": (Q(3, 8) + Q(1, 192), Q(3, 8) + Q(1, 144)),
    "g4": (Q(1, 8) + Q(1, 192), Q(1, 8) + Q(1, 112)),
    "g5": (Q(1, 8) - Q(1, 144), Q(1, 8) - Q(1, 192)),
}
# speed sitting on 1/16 at the left end, speed sitting on 15/16 at the right end
BIND = {"g1": (15, 13), "g2": (12, 9), "g3": (12, 9), "g4": (12, 7), "g5": (9, 12)}


def prime_list(lo, hi):
    sieve = bytearray([1]) * (hi + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(hi) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [n for n in range(lo, hi + 1) if sieve[n]]


def crt_lift(z, p):
    inv = pow(p, -1, 16)
    return [s + p * (((zj - s) * inv) % 16) for s, zj in zip(S, z)]


def offsets(z):
    return [(zj - s) % 16 for s, zj in zip(S, z)]


def centres(name):
    """(speed, centre) pairs that the window must keep good: c = 1/2 for an
    offset of 8, c = 0 for offset 0; g1 drops its speed-28 coordinate."""
    out = []
    for s, d in zip(S, offsets(Z[name])):
        if name == "g1" and s == 28:
            continue
        out.append((s, Q(1, 2) if d == 8 else Q(0)))
    return out


def frac(x):
    return x - math.floor(x)


def image_good(s, c, a, b):
    lo, hi = s * a + c, s * b + c
    k = math.floor(lo)
    return lo - k >= LO and hi - k <= HI


def good(b, w, n):
    for wj in w:
        r = (b * wj) % n
        if 16 * min(r, n - r) < n:
            return False
    return True


PRIMES = prime_list(251, 1500)


class Review19(unittest.TestCase):
    def test_offsets(self):
        off1 = offsets(Z["g1"])
        self.assertEqual([(s, d) for s, d in zip(S, off1) if d], [(28, 4)])
        for name in ("g2", "g3", "g4", "g5"):
            off = offsets(Z[name])
            self.assertTrue(set(off) <= {0, 8}, name)
            D = {s for s, d in zip(S, off) if d == 8}
            self.assertTrue({8, 12} <= D, name)
            self.assertFalse({4, 28} & D, name)

    def test_crt_lift(self):
        for p in PRIMES[:40]:
            n = 16 * p
            for name, z in Z.items():
                w = crt_lift(z, p)
                for s, zj, wj in zip(S, z, w):
                    self.assertTrue(0 <= wj < n)
                    self.assertEqual(wj % p, s % p)
                    self.assertEqual(wj % 16, zj % 16)
                off = offsets(z)
                if name == "g1":
                    self.assertEqual(w[:-1], list(S[:-1]))
                    tp = pow(p, -1, 4)
                    self.assertIn(tp, (1, 3))
                    self.assertEqual(w[-1], 28 + 4 * tp * p)
                else:
                    self.assertEqual(w, [s + 8 * p * (d == 8) for s, d in zip(S, off)])

    def test_windows_by_image(self):
        for name, (a, b) in WIN.items():
            self.assertLess(a, b)
            for s, c in centres(name):
                self.assertTrue(image_good(s, c, a, b), (name, s))

    def test_windows_are_tight_at_both_ends(self):
        for name, (a, b) in WIN.items():
            cs = dict(centres(name))
            left, right = BIND[name]
            self.assertEqual(frac(left * a + cs[left]), LO, name)
            self.assertEqual(frac(right * b + cs[right]), HI, name)

    def test_lengths(self):
        for name in ("g2", "g3", "g4", "g5"):
            a, b = WIN[name]
            self.assertGreaterEqual(b - a, Q(1, 8 * 251), name)
        a, b = WIN["g1"]
        self.assertEqual(b - a, Q(1, 780))
        self.assertGreaterEqual(16 * 251 * (b - a), 3)
        self.assertLess(16 * 146 * (b - a), 3)
        self.assertGreaterEqual(16 * 147 * (b - a), 3)

    def test_g1_step_of_two(self):
        for p in PRIMES:
            n = 16 * p
            w28 = crt_lift(Z["g1"], p)[-1]
            r = (2 * w28) % n
            # norm of 2 w28 / n is 1/2 - 7/(2p) >= 1/8
            self.assertEqual(min(r, n - r), 8 * p - 56)
            self.assertGreaterEqual(8 * min(r, n - r), n)

    def test_every_time_in_window_at_every_prime(self):
        for p in PRIMES:
            n = 16 * p
            for name, z in Z.items():
                w = crt_lift(z, p)
                a, b = WIN[name]
                first, last = math.ceil(n * a), math.floor(n * b)
                if name == "g1":
                    pairs = list(range(first, last - 1))
                    self.assertTrue(pairs, (name, p))
                    for t in range(first, last + 1):
                        self.assertTrue(good(t, w[:-1], n), (name, p, t))
                    for t in pairs:
                        self.assertTrue(good(t, w, n) or good(t + 2, w, n),
                                        (name, p, t))
                else:
                    odd = [t for t in range(first, last + 1) if t % 2]
                    self.assertTrue(odd, (name, p))
                    for t in odd:
                        self.assertTrue(good(t, w, n), (name, p, t))

    def test_plain_search(self):
        for p in (251, 257, 1321, 1327):
            n = 16 * p
            for name, z in Z.items():
                w = crt_lift(z, p)
                self.assertTrue(any(good(t, w, n) for t in range(1, n)), (name, p))

    def test_class_list_matches_raw_output(self):
        path = os.path.join(HERE, "results", "lrc16-uniform-v1", "summary_uniform.json")
        if not os.path.exists(path):
            self.skipTest("raw output not in this checkout")
        with open(path, encoding="utf-8") as fh:
            runs = json.load(fh)["runs"]
        hit = [r for r in runs if r["base"] == "gw15" and r["P"] == 251]
        self.assertEqual(len(hit), 1)
        self.assertEqual(tuple(hit[0]["s"]), S)
        lv = [x for x in hit[0]["levels"] if x["level"] == 16]
        self.assertEqual(len(lv), 1)
        self.assertEqual(lv[0]["survivors"], 5)
        self.assertEqual(sorted(tuple(v) for v in lv[0]["list"]), sorted(Z.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
