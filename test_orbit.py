# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for engine 4: LRC_PRUNE bit 4, early orbit pruning (THEORY_14.md).

Self-contained (no other module of this repository is imported), so the
brute-force side is independent of lrc_ref.py and of lrc.c.

Part 1, no compiler needed:
  - Lemma M by brute force: for every irredundant cover S containing class 1 in
    which class 1 has the most private times (and at least q_s), and every
    chosen part C of S containing 1, the rule neither prunes the node nor
    removes a class of S, even with the smallest possible allowed set S \\ C.
  - the rule is not vacuous: it does fire on covers where class 1 is not the
    class with the most private times.
  - a Python re-implementation of the whole search (all three LRC_PRUNE bits)
    finds exactly the brute-force orbits of irredundant covers with LRC_PRUNE
    = 0 and 7, and the same tau.
Part 2, needs a C compiler (runs in the compete job): lrc.c prints the same
covers, tau and gate results for LRC_PRUNE = 0, 3, 4 and 7, and never reaches
more raw covers with bit 4 than without it.
"""
import itertools
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
CC = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
BIN = os.path.join(tempfile.gettempdir(), "lrc_orbit_test_bin")


# ---------------- brute-force helpers (independent of lrc_ref.py) ----------------

def classes(p):
    return list(range(1, (p - 1) // 2 + 1))


def cover_sets(k, p):
    out = {}
    for v in classes(p):
        s = set()
        for a in classes(p):
            x = (a * v) % p
            if (k + 1) * min(x, p - x) < p:
                s.add(a)
        out[v] = frozenset(s)
    return out


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


def fold(x, p):
    x %= p
    return p - x if x > (p - 1) // 2 else x


def canonical(c, p):
    best = tuple(sorted(c))
    for x in c:
        inv = pow(x, p - 2, p)
        t = tuple(sorted(fold(inv * y, p) for y in c))
        if t < best:
            best = t
    return best


def irredundant_covers(k, p, maxsize):
    """every irredundant cover containing class 1 with at most maxsize classes"""
    sets = cover_sets(k, p)
    times = frozenset(classes(p))
    others = [v for v in classes(p) if v != 1]
    out = []
    for s in range(1, maxsize + 1):
        for rest in itertools.combinations(others, s - 1):
            fam = (1,) + rest
            u = set()
            for v in fam:
                u |= sets[v]
            if u != times:
                continue
            priv = private_times(fam, sets)
            if all(priv[v] for v in fam):
                out.append(fam)
    return out


def lemma_m(C, allowed, sets, who):
    """(lmax, priv): lmax = largest number of private times of a chosen class
    v != 1 that no allowed class covers"""
    priv = private_times(C, sets)
    lmax = 0
    for v in C:
        if v == 1:
            continue
        locked = sum(1 for a in priv[v] if not (who[a] & allowed))
        lmax = max(lmax, locked)
    return lmax, priv


def whos(sets, p):
    return {a: frozenset(v for v in classes(p) if a in sets[v]) for a in classes(p)}


SMALL = [(3, 11), (3, 13), (4, 13), (4, 17), (4, 19), (5, 23), (5, 29), (6, 29),
         (6, 37), (7, 43)]


class LemmaMByBruteForce(unittest.TestCase):
    def test_rule_never_cuts_a_cover_in_which_class_1_has_most_private_times(self):
        checked = 0
        for k, p in SMALL:
            sets = cover_sets(k, p)
            who = whos(sets, p)
            qs = qs_value(k, p, k)
            for S in irredundant_covers(k, p, k):
                privS = private_times(S, sets)
                mx = max(len(privS[v]) for v in S)
                if len(privS[1]) < max(qs, mx):
                    continue  # not reportable with class 1 normalised
                rest = S[1:]
                for r in range(len(rest)):
                    for sub in itertools.combinations(rest, r):
                        C = (1,) + sub
                        A = frozenset(S) - frozenset(C)  # smallest allowed set
                        lmax, priv = lemma_m(C, A, sets, who)
                        pc1 = len(priv[1])
                        self.assertLessEqual(lmax, pc1, (k, p, S, C))
                        T = max(qs, lmax)
                        for u in A:
                            self.assertLessEqual(len(sets[u] & priv[1]), pc1 - T,
                                                 (k, p, S, C, u))
                        checked += 1
        self.assertGreater(checked, 100)

    def test_rule_fires_on_covers_where_class_1_is_not_the_largest(self):
        fired = 0
        for k, p in SMALL:
            sets = cover_sets(k, p)
            who = whos(sets, p)
            qs = qs_value(k, p, k)
            for S in irredundant_covers(k, p, k):
                privS = private_times(S, sets)
                mx = max(len(privS[v]) for v in S)
                if not (qs <= len(privS[1]) < mx):
                    continue
                rest = S[1:]
                for r in range(len(rest)):
                    for sub in itertools.combinations(rest, r):
                        C = (1,) + sub
                        A = frozenset(S) - frozenset(C)
                        lmax, priv = lemma_m(C, A, sets, who)
                        if lmax > len(priv[1]):
                            fired += 1
        self.assertGreater(fired, 0)


# ---------------- a Python re-implementation of the search ----------------

def py_search(k, p, maxsize, prune, stop_first=False):
    """norm=1 search of lrc.c written again in Python, with LRC_PRUNE bits 1, 2
    and 4.  Returns (set of canonical covers reported, raw covers reached,
    first cover found in stop-first mode)."""
    n = (p - 1) // 2
    m = (p - 1) // (k + 1)
    sets = cover_sets(k, p)
    who = whos(sets, p)
    qs = qs_value(k, p, maxsize)
    times = frozenset(classes(p))
    found, raw, first = set(), [0], [None]

    def rec(C, allowed_in):
        if first[0] is not None:
            return
        priv = private_times(C, sets)
        if any(not priv[v] for v in C):
            return
        pc1 = len(priv[1])
        if pc1 < qs:
            return
        covered = set()
        for v in C:
            covered |= sets[v]
        U = times - covered
        if not U:
            if stop_first:
                first[0] = tuple(sorted(C))
                return
            raw[0] += 1
            if pc1 < max(len(priv[v]) for v in C):
                return
            found.add(canonical(C, p))
            return
        b = maxsize - len(C)
        if b <= 0 or b * m < len(U):
            return
        allowed = set(allowed_in)
        if prune & 2:
            for v in C:
                allowed -= {u for u in allowed if priv[v] <= sets[u]}
        T = qs
        if prune & 4:
            lmax = 0
            for v in C:
                if v == 1:
                    continue
                lmax = max(lmax, sum(1 for a in priv[v] if not (who[a] & allowed)))
            if lmax > pc1:
                return
            T = max(T, lmax)
        if (prune & 6) and T > 0:
            allowed = {u for u in allowed if len(sets[u] & priv[1]) <= pc1 - T}
        gains = {v: len(sets[v] & U) for v in allowed}
        if sum(sorted(gains.values(), reverse=True)[:b]) < len(U):
            return
        if prune & 1:
            need = Fraction(0)
            for a in U:
                mg = max((gains[v] for v in who[a] if v in allowed), default=0)
                if mg == 0:
                    return
                need += Fraction(1, mg)
            if need > b:
                return
        best = min(sorted(U), key=lambda a: len(who[a] & allowed))
        cands = sorted(who[best] & allowed)
        rem = set(allowed)
        for v in cands:
            rem.discard(v)
            rec(C + [v], frozenset(rem))

    rec([1], times - {1})
    assert n == len(times)
    return found, raw[0], first[0]


def py_tau(k, p, maxsize, prune):
    n = (p - 1) // 2
    m = (p - 1) // (k + 1)
    for s in range(-(-n // m), maxsize + 1):
        _, _, f = py_search(k, p, s, prune, stop_first=True)
        if f is not None:
            return s, f
    return 0, None


class PythonSearch(unittest.TestCase):
    def test_orbits_match_brute_force_with_and_without_pruning(self):
        for k, p in SMALL[:8]:
            truth = {canonical(S, p) for S in irredundant_covers(k, p, k)}
            f0, raw0, _ = py_search(k, p, k, 0)
            f7, raw7, _ = py_search(k, p, k, 7)
            self.assertEqual(f0, truth, (k, p, "prune 0"))
            self.assertEqual(f7, truth, (k, p, "prune 7"))
            self.assertLessEqual(raw7, raw0, (k, p))

    def test_tau_matches_brute_force(self):
        sets_cache = {}
        for k, p in SMALL[:8]:
            sets = sets_cache.setdefault((k, p), cover_sets(k, p))
            covs = irredundant_covers(k, p, k)
            true_tau = min(len(S) for S in covs)
            for prune in (0, 4, 7):
                t, f = py_tau(k, p, k, prune)
                self.assertEqual(t, true_tau, (k, p, prune))
                u = set()
                for v in f:
                    u |= sets[v]
                self.assertEqual(u, set(classes(p)))
            # below tau there is no cover, with every setting
            for prune in (0, 7):
                self.assertEqual(py_tau(k, p, true_tau - 1, prune)[0], 0, (k, p, prune))


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


def c_covers(prune, k, p, maxsize, norm):
    lines = run(prune, "covers", k, p, maxsize, 0, norm)
    covs = sorted(tuple(int(x) for x in ln.split()[2:]) for ln in lines if ln.startswith("C "))
    return covs, kv(lines[-1])


def c_tau(prune, k, p, maxsize):
    lines = run(prune, "tau", k, p, maxsize, 0)
    t = kv([ln for ln in lines if ln.startswith("T ")][0])
    f = [ln for ln in lines if ln.startswith("F")]
    cov = [int(x) for x in f[0].split()[1:]] if f else None
    return t, cov


@unittest.skipUnless(CC and os.path.exists(os.path.join(HERE, "lrc.c")),
                     "no C compiler or no lrc.c")
class EngineFour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_covers_match_brute_force(self):
        for k, p in SMALL[:8]:
            truth = sorted({canonical(S, p) for S in irredundant_covers(k, p, k)})
            for prune in (4, 7):
                for norm in (0, 1):
                    got, s = c_covers(prune, k, p, k, norm)
                    self.assertEqual(got, truth, (prune, norm, k, p, s))

    def test_covers_identical_and_fewer_raw_covers(self):
        for k, p, ms in [(5, 31, 5), (6, 37, 6), (7, 43, 7), (8, 53, 8), (8, 59, 8),
                         (9, 61, 9), (9, 67, 8), (10, 73, 10), (10, 83, 9)]:
            for norm in (0, 1):
                base, s0 = c_covers(0, k, p, ms, norm)
                _, s3 = c_covers(3, k, p, ms, norm)
                for prune in (4, 7):
                    got, s = c_covers(prune, k, p, ms, norm)
                    self.assertEqual(got, base, (prune, norm, k, p, ms))
                    self.assertEqual(s["tau"], s0["tau"], (prune, norm, k, p, ms))
                    self.assertEqual(s["prune"], prune)
                    if norm == 0:
                        self.assertEqual(s["raw"], s0["raw"], (prune, k, p, ms))
                    else:
                        self.assertLessEqual(s["raw"], s0["raw"], (prune, k, p, ms))
                        self.assertEqual(s3["raw"], s0["raw"], (k, p, ms))

    def test_python_search_agrees_with_c(self):
        for k, p in [(7, 43), (8, 53)]:
            f7, _, _ = py_search(k, p, k, 7)
            got, _ = c_covers(7, k, p, k, 1)
            self.assertEqual(got, sorted(f7), (k, p))

    def test_tau_identical_and_certificate_is_an_irredundant_cover(self):
        cases = [(14, 89, 12), (14, 131, 12), (14, 163, 12), (14, 199, 12),
                 (15, 101, 13), (15, 137, 13), (15, 163, 13), (15, 191, 13),
                 (9, 83, 7), (10, 103, 8), (11, 137, 9)]
        for k, p, ms in cases:
            t0, _ = c_tau(0, k, p, ms)
            sets = cover_sets(k, p)
            for prune in (4, 7):
                t, c = c_tau(prune, k, p, ms)
                for key in ("tau", "none_upto", "unknown"):
                    self.assertEqual(t[key], t0[key], (prune, k, p, ms, key))
                if t["tau"]:
                    self.assertEqual(len(c), t["tau"])
                    u = set()
                    for v in c:
                        u |= sets[v]
                    self.assertEqual(u, set(classes(p)), (k, p, c))
                    priv = private_times(c, sets)
                    self.assertTrue(all(priv[v] for v in c), (k, p, c))

    def test_gate_identical(self):
        keys = ("tau", "orbits_by_size", "tuples", "killed", "survived", "overflow",
                "complete", "max_improper_by_level", "sum_improper_by_level")
        for k, p in [(6, 37), (7, 47), (8, 61), (9, 83)]:
            d0 = json.loads(run(0, "gate", k, p, "2,2,2", 120, 100000, 1, 1)[-1])
            d7 = json.loads(run(7, "gate", k, p, "2,2,2", 120, 100000, 1, 1)[-1])
            self.assertEqual(d0["cover_timed_out"], 0)
            self.assertEqual(d7["cover_timed_out"], 0)
            for key in keys:
                self.assertEqual(d0[key], d7[key], (k, p, key))
            self.assertEqual(d7["prune"], 7)


if __name__ == "__main__":
    unittest.main()
