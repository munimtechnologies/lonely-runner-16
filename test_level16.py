# Copyright 2026 Munim, Inc. Licensed under the Apache License, Version 2.0 (Apache-2.0).
# MV2 of Munim, Inc. Made with AI agents working in MV2's name; not yet checked by a human.
"""Exact checks for THEORY_18.md: the tight orbit (1..15) has no improper lift at
level 16 at any prime p >= 251.

Standard library only; imports no repository code. Reads
level16_certificate.json (the windows) and, if present, the committed raw output
results/lrc16-uniform-v1/summary_uniform.json (to compare the class list).
"""
import json
import math
import os
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
K = 15
LEVEL = 16
SIXTEENTH = F(1, 16)


def load_cert():
    with open(os.path.join(HERE, "level16_certificate.json"), encoding="utf-8") as fh:
        return json.load(fh)


def frac(s):
    return F(s)


def primes_between(lo, hi):
    out = []
    for n in range(max(lo, 2), hi + 1):
        if all(n % d for d in range(2, int(math.isqrt(n)) + 1)):
            out.append(n)
    return out


def window_ok(alpha, beta, speeds, centres):
    """True iff ||s x - c|| >= 1/16 for every (s, c) and every x in [alpha, beta]."""
    assert alpha <= beta
    for s, c in zip(speeds, centres):
        lo = s * alpha - c
        hi = s * beta - c
        for n in range(math.floor(lo) - 1, math.ceil(hi) + 2):
            # [lo, hi] meets the open arc (n - 1/16, n + 1/16)?
            if lo < n + SIXTEENTH and hi > n - SIXTEENTH:
                return False
    return True


def lift(z, p):
    """w in Z_{16p}^15 with w_i = i (mod p) and w_i = z_i (mod 16)."""
    inv = pow(p, -1, LEVEL)
    out = []
    for i, zi in enumerate(z, start=1):
        w = (i + p * (((zi - i) * inv) % LEVEL)) % (LEVEL * p)
        assert w % p == i % p and w % LEVEL == zi % LEVEL
        out.append(w)
    return out


def is_witness(b, w, p):
    n = LEVEL * p
    for wi in w:
        r = (b * wi) % n
        if min(r, n - r) < p:  # ||b wi / (16p)|| < 1/16
            return False
    return True


def gcd_clause(z):
    return sum(1 for zi in z if zi % 2) <= 1


class Certificate(unittest.TestCase):
    def setUp(self):
        self.cert = load_cert()
        self.classes = self.cert["classes"]

    def test_nine_classes_and_shapes(self):
        self.assertEqual(len(self.classes), 9)
        for c in self.classes:
            z = c["z"]
            self.assertEqual(len(z), K)
            self.assertFalse(gcd_clause(z))
            diffs = [(z[i - 1] - i) % LEVEL for i in range(1, K + 1)]
            if c["kind"] == "step":
                self.assertEqual([d for d in diffs if d], [2])
                self.assertEqual(diffs[13], 2)  # coordinate 14: 0 = 14 + 2 (mod 16)
            else:
                self.assertTrue(set(diffs) <= {0, 8})
                D = sorted(i for i in range(1, K + 1) if diffs[i - 1] == 8)
                self.assertEqual(D, c["D"])
                self.assertIn(8, D)

    def test_matches_committed_job_output(self):
        path = os.path.join(HERE, "results", "lrc16-uniform-v1", "summary_uniform.json")
        if not os.path.exists(path):
            self.skipTest("raw job output not present in this checkout")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        runs = [r for r in data["runs"] if r["base"] == "e15" and r["P"] == 251]
        self.assertEqual(len(runs), 1)
        lv = [x for x in runs[0]["levels"] if x["level"] == 16]
        self.assertEqual(len(lv), 1)
        self.assertEqual(lv[0]["survivors"], 9)
        self.assertEqual(sorted(map(tuple, lv[0]["list"])),
                         sorted(tuple(c["z"]) for c in self.classes))

    def test_windows_exact(self):
        for c in self.classes:
            if c["kind"] != "window":
                continue
            a, b = frac(c["window"][0]), frac(c["window"][1])
            D = set(c["D"])
            speeds = list(range(1, K + 1))
            centres = [F(1, 2) if i in D else F(0) for i in speeds]
            self.assertTrue(window_ok(a, b, speeds, centres), c["name"])
            self.assertEqual(b - a, frac(c["length"]), c["name"])
            # shorter than 1/251, as U_251 requires for each single beta
            self.assertLess(b - a, F(1, 251))
            # long enough for two consecutive grid points at p >= min_prime
            self.assertGreaterEqual(16 * c["min_prime"] * (b - a), 2)

    def test_step_interval_exact(self):
        c = [c for c in self.classes if c["kind"] == "step"][0]
        a, b = frac(c["interval"][0]), frac(c["interval"][1])
        speeds = [i for i in range(1, K + 1) if i != 14]
        self.assertTrue(window_ok(a, b, speeds, [F(0)] * len(speeds)))
        self.assertEqual(b - a, F(1, 780))
        # b and b+4 both inside I whenever 16 p |I| >= 5
        self.assertGreaterEqual(16 * c["min_prime"] * (b - a), 5)
        self.assertLessEqual(c["min_prime"], 251)

    def test_step_shift_is_half_plus(self):
        # b -> b+4 moves coordinate 14 by 1/2 + 7/(2p) (mod 1)
        for p in primes_between(251, 600):
            w = lift(self.classes[0]["z"], p)
            n = LEVEL * p
            shift = F((4 * w[13]) % n, n)
            self.assertEqual(shift, F(1, 2) + F(7, 2 * p))
            self.assertGreaterEqual(min(shift, 1 - shift), F(1, 8))


class EveryPrime(unittest.TestCase):
    """The argument of THEORY_18 against the actual integer vectors."""

    def setUp(self):
        self.classes = load_cert()["classes"]

    def test_window_classes_lemma_form(self):
        # w_i = i + 8p [i in D] (mod 16p), as Lemma 18.1 uses
        for p in (251, 257, 401, 809, 2003):
            for c in self.classes:
                if c["kind"] != "window":
                    continue
                w = lift(c["z"], p)
                D = set(c["D"])
                self.assertEqual(w, [(i + 8 * p * (i in D)) % (LEVEL * p)
                                     for i in range(1, K + 1)])

    def test_predicted_witness_every_prime_251_to_3000(self):
        for p in primes_between(251, 3000):
            n = LEVEL * p
            for c in self.classes:
                w = lift(c["z"], p)
                if c["kind"] == "window":
                    a, b = frac(c["window"][0]), frac(c["window"][1])
                    m = math.ceil(n * a)
                    if m % 2 == 0:
                        m += 1
                    self.assertLessEqual(m, n * b, (p, c["name"]))
                    self.assertTrue(is_witness(m, w, p), (p, c["name"], m))
                else:
                    a, b = frac(c["interval"][0]), frac(c["interval"][1])
                    b0 = math.ceil(n * a)
                    self.assertLessEqual(b0 + 4, n * b, p)
                    self.assertTrue(is_witness(b0, w, p) or is_witness(b0 + 4, w, p),
                                    (p, c["name"], b0))

    def test_brute_force_small_primes(self):
        # independent of the windows: some b in Z_{16p} is a witness
        for p in (251, 257, 263):
            for c in self.classes:
                w = lift(c["z"], p)
                self.assertTrue(any(is_witness(b, w, p) for b in range(LEVEL * p)),
                                (p, c["name"]))

    def test_tight_vector_itself_needs_level_16(self):
        # sanity: (1..15) reduced mod p has witnesses only at a/16, so at level 8
        # its linear lift is improper and at level 16 it is proper (Lemma L)
        p = 251
        w16 = [i for i in range(1, K + 1)]
        self.assertTrue(is_witness(p, w16, p))  # b = p: x = 1/16
        n8 = 8 * p
        found = False
        for b in range(n8):
            if all(min((b * i) % n8, n8 - (b * i) % n8) * 16 >= n8 for i in w16):
                found = True
                break
        self.assertFalse(found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
