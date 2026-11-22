# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for engine 3 (LRC_PRUNE in lrc.c; THEORY_13.md).

Part 1 needs no compiler: the two pruning rules are checked by brute force in
pure Python against lrc_ref.py.
  - Lemma F (fractional bound): at random search states, the smallest number of
    allowed classes that covers the uncovered times is never below
    sum_a 1/G(a).
  - Lemma P (forbidden classes): for every irredundant cover S containing
    class 1 and every C ⊂ S containing 1, no class of S \\ C is forbidden by C
    (so pruning never loses a reportable cover); with norm=1, the same for the
    q_s rule on covers where class 1 keeps at least q_s private times.
Part 2 needs a C compiler: lrc.c prints the same covers, tau and gate results
for LRC_PRUNE = 0, 1, 2, 3, and agrees with the brute-force reference.
"""
import itertools
import json
import os
import random
import shutil
import subprocess
import tempfile
import unittest
from fractions import Fraction

import lrc_ref as R

HERE = os.path.dirname(os.path.abspath(__file__))
CC = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
BIN = os.path.join(tempfile.gettempdir(), "lrc_prune_test_bin")


# ---------------- Part 1: the rules themselves, by brute force ----------------

def cover_sets(k, p):
    return {v: R.cover_set(v, k, p) for v in R.folded(p)}


def min_cover_size(target, sets, allowed, limit):
    """fewest classes from `allowed` covering `target`, or None if more than limit"""
    if not target:
        return 0
    for s in range(1, limit + 1):
        for comb in itertools.combinations(allowed, s):
            u = set()
            for v in comb:
                u |= sets[v]
            if target <= u:
                return s
    return None


def fractional_bound(target, sets, allowed):
    """sum over a in target of 1/G(a); None if some a has no allowed class"""
    gains = {v: len(sets[v] & target) for v in allowed}
    tot = Fraction(0)
    for a in target:
        mg = max((gains[v] for v in allowed if a in sets[v]), default=0)
        if mg == 0:
            return None
        tot += Fraction(1, mg)
    return tot


def private_times(C, sets):
    out = {}
    for v in C:
        others = set()
        for x in C:
            if x != v:
                others |= sets[x]
        out[v] = sets[v] - others
    return out


def qs_value(k, p, maxsize):
    n = (p - 1) // 2
    m = (p - 1) // (k + 1)
    slack = 2 * n - maxsize * m
    return -(-slack // maxsize) if slack > 0 else 0


def forbidden(C, sets, classes, norm, qs):
    """classes outside C that rule P removes at a node whose chosen set is C"""
    priv = private_times(C, sets)
    out = set()
    for u in classes:
        if u in C:
            continue
        for v in C:
            if priv[v] and priv[v] <= sets[u]:
                out.add(u)
        if norm and qs > 0 and 1 in C:
            lim = len(priv[1]) - qs
            if len(sets[u] & priv[1]) > lim:
                out.add(u)
    return out


class RulesByBruteForce(unittest.TestCase):
    def test_fractional_bound_never_exceeds_true_minimum(self):
        rng = random.Random(2026)
        checked = 0
        for k, p in [(3, 11), (4, 13), (4, 17), (5, 23), (6, 29), (7, 31), (5, 37)]:
            sets = cover_sets(k, p)
            classes = list(R.folded(p))
            times = set(R.folded(p))
            for _ in range(40):
                C = [1] + rng.sample(classes[1:], rng.randint(0, 2))
                covered = set()
                for v in C:
                    covered |= sets[v]
                target = times - covered
                pool = [v for v in classes if v not in C]
                allowed = [v for v in pool if rng.random() < 0.7]
                fb = fractional_bound(target, sets, allowed)
                mc = min_cover_size(target, sets, allowed, 6)
                if mc is not None:
                    self.assertIsNotNone(fb, (k, p, C, allowed))
                    self.assertLessEqual(fb, mc, (k, p, C, allowed))
                    checked += 1
        self.assertGreater(checked, 50)

    def test_forbidden_rule_never_removes_a_class_of_an_irredundant_cover(self):
        hits = 0
        for k, p in [(3, 11), (3, 13), (4, 13), (4, 17), (4, 19), (5, 23), (5, 29),
                     (6, 29), (6, 37)]:
            sets = cover_sets(k, p)
            classes = list(R.folded(p))
            qs = qs_value(k, p, k)
            for S in R.irredundant_covers(k, p):
                rest = [v for v in S if v != 1]
                privS = private_times(S, sets)
                class1_ok = len(privS[1]) >= qs
                for r in range(0, len(rest)):
                    for sub in itertools.combinations(rest, r):
                        C = (1,) + sub
                        f0 = forbidden(C, sets, classes, 0, qs)
                        self.assertFalse(f0 & set(S), (k, p, S, C, f0 & set(S)))
                        if class1_ok:
                            f1 = forbidden(C, sets, classes, 1, qs)
                            self.assertFalse(f1 & set(S), (k, p, S, C, "norm", f1 & set(S)))
                        hits += len(f0)
        self.assertGreater(hits, 0)  # the rule is not vacuous on these cases

    def test_symmetry_used_by_the_engine(self):
        # forbid_classes() reads "classes covering time a" from who[a] and the
        # fractional bound reads it from covlist[a]: both rely on
        # "v covers a iff a covers v"
        for k, p in [(4, 13), (7, 31), (15, 101)]:
            for v in R.folded(p):
                for a in R.folded(p):
                    self.assertEqual(R.covers(v, a, k, p), R.covers(a, v, k, p))


# ---------------- Part 2: the C engine ----------------

def build():
    subprocess.run([CC, "-O2", "-o", BIN, os.path.join(HERE, "lrc.c")], check=True)


def run(prune, *args):
    env = dict(os.environ, LRC_PRUNE=str(prune))
    out = subprocess.run([BIN] + [str(a) for a in args], check=True, env=env,
                         capture_output=True, text=True).stdout
    return out.splitlines()


def kv(line):
    d = {}
    for item in line.split()[1:]:
        a, b = item.split("=")
        d[a] = float(b) if a == "seconds" else int(b)
    return d


def covers(prune, k, p, maxsize, norm):
    lines = run(prune, "covers", k, p, maxsize, 0, norm)
    covs = sorted(tuple(int(x) for x in ln.split()[2:]) for ln in lines if ln.startswith("C "))
    return covs, kv(lines[-1])


def tau(prune, k, p, maxsize):
    lines = run(prune, "tau", k, p, maxsize, 0)
    t = kv([ln for ln in lines if ln.startswith("T ")][0])
    f = [ln for ln in lines if ln.startswith("F")]
    cov = [int(x) for x in f[0].split()[1:]] if f else None
    return t, cov


@unittest.skipUnless(CC and os.path.exists(os.path.join(HERE, "lrc.c")),
                     "no C compiler or no lrc.c")
class EngineThree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_covers_match_reference_with_pruning(self):
        for prune in (1, 2, 3):
            for norm in (0, 1):
                for k, p in [(3, 11), (4, 13), (4, 17), (5, 23), (5, 29), (6, 29)]:
                    got, s = covers(prune, k, p, k, norm)
                    self.assertEqual(got, R.canonical_covers(k, p), (prune, norm, k, p, s))

    def test_covers_identical_for_every_prune_value(self):
        for norm in (0, 1):
            for k, p, ms in [(5, 31, 5), (6, 37, 6), (7, 43, 7), (8, 53, 8), (8, 59, 8),
                             (9, 61, 9), (9, 67, 8), (10, 73, 10), (10, 83, 9)]:
                base, s0 = covers(0, k, p, ms, norm)
                for prune in (1, 2, 3):
                    got, s = covers(prune, k, p, ms, norm)
                    self.assertEqual(got, base, (prune, norm, k, p, ms))
                    self.assertEqual(s["raw"], s0["raw"], (prune, norm, k, p, ms))
                    self.assertEqual(s["tau"], s0["tau"], (prune, norm, k, p, ms))
                    self.assertEqual(s["prune"], prune)

    def test_tau_identical_and_certificate_is_an_irredundant_cover(self):
        cases = [(14, 89, 12), (14, 131, 12), (14, 163, 12), (14, 199, 12),
                 (15, 101, 13), (15, 137, 13), (15, 163, 13), (15, 191, 13),
                 (9, 83, 7), (10, 103, 8), (11, 137, 9)]
        for k, p, ms in cases:
            t0, c0 = tau(0, k, p, ms)
            for prune in (1, 3):
                t, c = tau(prune, k, p, ms)
                for key in ("tau", "none_upto", "unknown"):
                    self.assertEqual(t[key], t0[key], (prune, k, p, ms, key))
                if t["tau"]:
                    self.assertEqual(len(c), t["tau"])
                    self.assertTrue(R.level1_improper(c, k, p), (k, p, c))
                    sets = cover_sets(k, p)
                    priv = private_times(c, sets)
                    self.assertTrue(all(priv[v] for v in c), (k, p, c))
            if ms < k - 1 and not t0["tau"]:
                self.assertEqual(t0["none_upto"], ms)  # a real "gt" certificate case

    def test_gate_identical(self):
        keys = ("tau", "orbits_by_size", "tuples", "killed", "survived", "overflow",
                "complete", "max_improper_by_level", "sum_improper_by_level")
        for k, p in [(6, 37), (7, 47), (8, 61), (9, 83)]:
            d0 = json.loads(run(0, "gate", k, p, "2,2,2", 120, 100000, 1, 1)[-1])
            d3 = json.loads(run(3, "gate", k, p, "2,2,2", 120, 100000, 1, 1)[-1])
            self.assertEqual(d0["cover_timed_out"], 0)
            self.assertEqual(d3["cover_timed_out"], 0)
            for key in keys:
                self.assertEqual(d0[key], d3[key], (k, p, key))
            self.assertEqual(d3["prune"], 3)


if __name__ == "__main__":
    unittest.main()
