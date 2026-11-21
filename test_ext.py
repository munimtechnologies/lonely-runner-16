# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for the run-4 additions to lrc.c (THEORY.md Sec. 6):

  * `tau` mode (exact tau(p) up to a size, or a certificate that no cover on
    that many classes exists) against the brute-force reference;
  * the general completion (`ext`): the level-1 tuples the gate lifts must hit
    EVERY unit orbit of improper k-multisets, found here by brute force over all
    k-multisets, including primes where tau(p) <= k-2;
  * ext = 0 keeps the old behaviour exactly.

Skipped when no C compiler is available."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from itertools import combinations_with_replacement

import lrc_ref as R

HERE = os.path.dirname(os.path.abspath(__file__))
CC = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
BIN = os.path.join(tempfile.gettempdir(), "lrc_test_bin_ext")


def build():
    subprocess.run([CC, "-O2", "-o", BIN, os.path.join(HERE, "lrc.c")], check=True)


def run(*args):
    out = subprocess.run([BIN] + [str(a) for a in args], check=True,
                         capture_output=True, text=True).stdout
    return out.splitlines()


def tau_c(k, p, maxsize, cap=0):
    lines = run("tau", k, p, maxsize, cap)
    t = [ln for ln in lines if ln.startswith("T ")][0]
    d = {}
    for kv in t.split()[1:]:
        a, b = kv.split("=")
        d[a] = float(b) if a == "seconds" else int(b)
    f = [ln for ln in lines if ln.startswith("F")]
    d["cover"] = [int(x) for x in f[0].split()[1:]] if f else None
    return d


def tau_ref(k, p, maxsize):
    sizes = [len(c) for c in R.irredundant_covers(k, p, maxsize)]
    return min(sizes) if sizes else 0


def masks(k, p):
    out = {}
    for v in R.folded(p):
        m = 0
        for a in R.cover_set(v, k, p):
            m |= 1 << a
        out[v] = m
    return out


def improper_multisets(k, p):
    """every level-1 improper k-multiset of folded classes (brute force)"""
    ms = masks(k, p)
    full = 0
    for a in R.folded(p):
        full |= 1 << a
    res = []
    for m in combinations_with_replacement(list(R.folded(p)), k):
        u = 0
        for v in m:
            u |= ms[v]
        if u == full:
            res.append(m)
    return res


def orbit_key(m, p):
    n = (p - 1) // 2
    return min(tuple(sorted(R.fold(u * y, p) for y in m)) for u in range(1, n + 1))


def c_tuples(k, p, ext, norm):
    lines = run("tuples", k, p, ext, norm)
    tup = [tuple(int(x) for x in ln.split()[1:]) for ln in lines if ln.startswith("T ")]
    s = [ln for ln in lines if ln.startswith("S ")][0]
    d = dict(kv.split("=") for kv in s.split()[1:])
    return tup, {a: int(b) for a, b in d.items()}


@unittest.skipUnless(CC, "no C compiler")
class TauAndCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_tau_matches_reference(self):
        # (8, 23) and (9, 23) have m = 2 and a 6-class cover (THEORY.md Sec. 6),
        # so tau <= k - 2 there; the maxsize-4 cases must certify "no cover".
        cases = [(3, 11, 3), (3, 13, 3), (4, 13, 4), (4, 17, 4), (5, 23, 5), (5, 29, 5),
                 (6, 29, 6), (8, 23, 8), (9, 23, 9), (8, 23, 5), (6, 29, 4), (7, 31, 7)]
        for k, p, mx in cases:
            d = tau_c(k, p, mx)
            exp = tau_ref(k, p, mx)
            self.assertEqual(d["tau"], exp, (k, p, mx, d))
            self.assertEqual(d["unknown"], 0, (k, p, mx))
            if exp:
                self.assertEqual(len(d["cover"]), exp, (k, p, d))
                self.assertTrue(R.level1_improper(d["cover"], k, p), (k, p, d))
                self.assertEqual(d["none_upto"], exp - 1, (k, p, d))
            else:
                self.assertIsNone(d["cover"])
                self.assertEqual(d["none_upto"], mx, (k, p, d))

    def test_small_tau_cases_exist(self):
        # the completeness test below is only meaningful if tau <= k - 2 occurs
        for k in (8, 9):
            d = tau_c(k, 23, k)
            self.assertTrue(0 < d["tau"] <= k - 2, (k, d))

    def test_ext_tuples_hit_every_improper_orbit(self):
        for k, p in [(8, 23), (9, 23), (4, 13), (5, 23)]:
            brute = {orbit_key(m, p) for m in improper_multisets(k, p)}
            self.assertGreater(len(brute), 0, (k, p))
            for norm in (0, 1):
                tup, s = c_tuples(k, p, 1, norm)
                self.assertEqual(s["tuples"], len(tup))
                for t in tup:
                    self.assertEqual(len(t), k)
                keys = {orbit_key(t, p) for t in tup}
                # every listed tuple is improper, and every improper orbit is listed
                self.assertTrue(keys <= brute, (k, p, norm, sorted(keys - brute)[:5]))
                self.assertEqual(keys, brute, (k, p, norm, sorted(brute - keys)[:5]))

    def test_without_ext_small_orbits_are_missed(self):
        # with tau <= k-2 the old enumeration (ext = 0) misses some orbits and
        # says so; this is the gap the general completion closes
        for k, p in [(8, 23), (9, 23)]:
            brute = {orbit_key(m, p) for m in improper_multisets(k, p)}
            tup, s = c_tuples(k, p, 0, 1)
            self.assertGreater(s["small_orbits"], 0, (k, p))
            keys = {orbit_key(t, p) for t in tup}
            self.assertTrue(keys < brute, (k, p))

    def test_gate_ext_zero_is_unchanged_and_ext_completes(self):
        for k, p in [(4, 17), (5, 31), (6, 37), (8, 23)]:
            d0 = json.loads(run("gate", k, p, "2,2", 60, 100000, 1, 1, 0, 0)[-1])
            d1 = json.loads(run("gate", k, p, "2,2", 60, 100000, 1, 1, 0, 1)[-1])
            self.assertEqual(d0["ext"], 0)
            self.assertEqual(d1["ext"], 1)
            self.assertEqual(d1["small_orbits_unhandled"], 0)
            self.assertEqual(d0["small_orbits"], d1["small_orbits"])
            t0, _ = c_tuples(k, p, 0, 1)
            t1, _ = c_tuples(k, p, 1, 1)
            self.assertEqual(d0["tuples"], len(t0), (k, p))
            self.assertEqual(d1["tuples"], len(t1), (k, p))
            if d0["small_orbits"] == 0:
                for key in ("tau", "orbits_by_size", "tuples", "killed", "survived",
                            "overflow", "complete", "max_improper_by_level",
                            "sum_improper_by_level"):
                    self.assertEqual(d0[key], d1[key], (k, p, key))
            else:
                self.assertEqual(d0["complete"], 0, (k, p))
                self.assertEqual(d0["small_orbits_unhandled"], d0["small_orbits"])
                self.assertGreater(d1["tuples"], d0["tuples"], (k, p))
        self.assertGreater(json.loads(run("gate", 8, 23, "2,2", 60, 100000, 1, 1, 0, 0)[-1])
                           ["small_orbits"], 0)


if __name__ == "__main__":
    unittest.main()
