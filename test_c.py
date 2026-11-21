# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
"""Cross-check the C engine (lrc.c) against the brute-force reference, and its
two cover normalisations and two lifting methods against each other.
Skipped when no C compiler is available."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

import lrc_ref as R

HERE = os.path.dirname(os.path.abspath(__file__))
CC = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
BIN = os.path.join(tempfile.gettempdir(), "lrc_test_bin")


def build():
    subprocess.run([CC, "-O2", "-o", BIN, os.path.join(HERE, "lrc.c")], check=True)


def run(*args):
    out = subprocess.run([BIN] + [str(a) for a in args], check=True,
                         capture_output=True, text=True).stdout
    return out.splitlines()


def c_covers(k, p, maxsize=None, norm=0):
    maxsize = k if maxsize is None else maxsize
    lines = run("covers", k, p, maxsize, 0, norm)
    covs = [tuple(int(x) for x in ln.split()[2:]) for ln in lines if ln.startswith("C ")]
    return sorted(covs), lines[-1]


def c_cascade(mode, k, p, mults, v):
    lines = run(mode, k, p, ",".join(map(str, mults)), *v)
    counts = [int(ln.split()[2]) for ln in lines if ln.startswith("L ")]
    status = [int(ln.split()[1]) for ln in lines if ln.startswith("R ")][0]
    surv = sorted(tuple(int(x) for x in ln.split()[1:]) for ln in lines if ln.startswith("W"))
    return counts, status, surv


@unittest.skipUnless(CC, "no C compiler")
class CEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_covers_match_reference(self):
        for norm in (0, 1):
            for k, p in [(3, 11), (3, 13), (4, 13), (4, 17), (4, 19), (5, 23), (5, 29), (6, 29)]:
                got, summary = c_covers(k, p, norm=norm)
                self.assertEqual(got, R.canonical_covers(k, p), (k, p, norm, summary))

    def test_two_normalisations_agree(self):
        # independent orbit normalisations (any class -> 1, versus Lemma 4.1's
        # most-private class -> 1) must give the same set of orbits
        for k, p in [(5, 31), (5, 37), (6, 37), (6, 41), (7, 43), (7, 47), (8, 53), (8, 59)]:
            a, sa = c_covers(k, p, norm=0)
            b, sb = c_covers(k, p, norm=1)
            self.assertEqual(a, b, (k, p, sa, sb))
            self.assertGreater(len(a), 0, (k, p))

    def test_cascade_matches_reference(self):
        cases = [
            (3, 11, [2, 2], (1, 2, 3)),
            (3, 13, [2, 2], (1, 2, 3)),
            (4, 13, [2], (1, 2, 3, 4)),
            (4, 17, [2], (1, 2, 3, 4)),
            (3, 11, [3], (1, 2, 3)),
            (4, 11, [5], (1, 2, 3, 4)),
        ]
        for k, p, mults, v in cases:
            counts, surv = R.cascade(v, k, p, mults)
            for mode in ("cascade", "cascadebb"):
                ccounts, _, _ = c_cascade(mode, k, p, mults, v)
                self.assertEqual(ccounts[:len(counts)], counts, (mode, k, p, mults, v))

    def test_bb_lifting_equals_bruteforce_lifting(self):
        # every level-1 improper tuple built from the covers of a few gates
        for k, p, mults in [(5, 31, [2, 2, 2]), (6, 37, [2, 2, 2]), (6, 41, [2, 3]),
                            (7, 43, [2, 2, 2, 2]), (5, 29, [3, 2]), (4, 23, [5])]:
            covs, _ = c_covers(k, p)
            tuples = [c for c in covs if len(c) == k]
            for c in covs:
                if len(c) == k - 1:
                    tuples += [c + (x,) for x in range(1, (p - 1) // 2 + 1, 3)]
            self.assertGreater(len(tuples), 0, (k, p))
            for v in tuples[:60]:
                a = c_cascade("cascade", k, p, mults, v)
                b = c_cascade("cascadebb", k, p, mults, v)
                self.assertEqual(a[0], b[0], (k, p, mults, v))
                self.assertEqual(a[1], b[1], (k, p, mults, v))
                if a[0] and a[0][-1] < 50:
                    self.assertEqual(a[2], b[2], (k, p, mults, v))

    def test_one_to_k_lifts(self):
        # (1..k) survives level 1 and the two lifting methods agree on it
        for k, p, mults in [(7, 59, [2, 2, 2, 2]), (8, 71, [3, 3]), (6, 43, [7])]:
            v = tuple(range(1, k + 1))
            a = c_cascade("cascade", k, p, mults, v)
            b = c_cascade("cascadebb", k, p, mults, v)
            self.assertEqual(a[:2], b[:2], (k, p, mults))

    def test_gate_json_engines_agree(self):
        for k, p in [(4, 17), (5, 31), (6, 37), (7, 47)]:
            d0 = json.loads(run("gate", k, p, "2,2,2", 60, 100000, 0, 0)[-1])
            d1 = json.loads(run("gate", k, p, "2,2,2", 60, 100000, 1, 1)[-1])
            for key in ("tau", "orbits_by_size", "tuples", "killed", "survived", "overflow",
                        "complete", "max_improper_by_level", "sum_improper_by_level"):
                self.assertEqual(d0[key], d1[key], (k, p, key))
            self.assertEqual(d0["k"], k)


if __name__ == "__main__":
    unittest.main()
