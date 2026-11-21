# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for uniform.py (THEORY.md Sec. 8).

The key test is the sandwich  U_inf(L) <= (per-prime improper lifts) <= U_p(L),
checked level by level against lrc_ref.proper, the brute-force definition of
properness (every time b in Z_{Lp}, plus the gcd clause), for small k and p."""
import random
import unittest
from fractions import Fraction
from itertools import product

import lrc_ref
import uniform as U


def crt(si, zi, p, l):
    """w = si (mod p), w = zi (mod l), 0 <= w < l p"""
    r = si % p
    if l == 1:
        return r
    return r + p * (((zi - r) * pow(p, -1, l)) % l)


def perprime_cascade(s, k, p, nlevels):
    """canonical z-forms of the improper lifts at levels 2, 4, ..., per lrc_ref"""
    v = tuple(x % p for x in s)
    if lrc_ref.proper(v, k, p, 1):
        return [set() for _ in range(nlevels)]
    zs = {tuple(0 for _ in s)}
    l = 1
    out = []
    for _ in range(nlevels):
        nl = 2 * l
        nxt = set()
        for z in zs:
            w = tuple(crt(s[i], z[i], p, l) for i in range(k))
            assert all(w[i] % p == s[i] % p and w[i] % l == z[i] % l for i in range(k))
            for a in product((0, 1), repeat=k):
                w2 = tuple(w[i] + a[i] * l * p for i in range(k))
                if not lrc_ref.proper(w2, k, p, nl):
                    nxt.add(U.canon(tuple(x % nl for x in w2), nl))
        out.append(nxt)
        zs = nxt
        l = nl
    return out


def uniform_sets(s, k, nlevels, P, bruteforce=False):
    r = U.cascade(s, k, nlevels, P, bruteforce=bruteforce)
    sets = [set(map(tuple, lv["survivors"])) for lv in r["levels"]]
    while len(sets) < nlevels:
        sets.append(set())
    return sets


def dist(x):
    f = x - (x.numerator // x.denominator)
    return min(f, 1 - f)


class Cells(unittest.TestCase):
    def test_masks_match_fractions(self):
        rng = random.Random(7)
        for _ in range(40):
            k = rng.randint(2, 6)
            s = [rng.randint(1, 12) for _ in range(k)]
            L = rng.choice([1, 2, 4, 8])
            z = [rng.randrange(L) for _ in range(k)]
            beta = rng.randrange(L)
            Q = U.qunit(L, k, s)
            arcs = [U.arcs_for(s[i], (beta * z[i]) % L, L, k, Q) for i in range(k)]
            cells = U.Cells(arcs, Q)
            masks = [cells.mask(a) for a in arcs]
            r = Fraction(1, k + 1)
            for m in range(cells.M):
                mid = Fraction(cells.E2[m] + cells.E2[m + 1], 2 * Q)
                for i in range(k):
                    inside = dist(mid * s[i] + Fraction(beta * z[i], L)) <= r
                    self.assertEqual(bool((masks[i] >> m) & 1), inside)
            for i in range(k):  # endpoints are exactly at distance 1/(k+1)
                for a, ln in arcs[i]:
                    for e in (a, a + ln):
                        self.assertEqual(dist(Fraction(e, Q) * s[i] + Fraction(beta * z[i], L)), r)

    def test_runs_against_simple_scan(self):
        rng = random.Random(11)
        for _ in range(60):
            k = rng.randint(2, 5)
            s = [rng.randint(1, 9) for _ in range(k)]
            L = rng.choice([1, 2, 4])
            z = [rng.randrange(L) for _ in range(k)]
            Q = U.qunit(L, k, s)
            arcs = [U.arcs_for(s[i], z[i], L, k, Q) for i in range(k)]
            cells = U.Cells(arcs, Q)
            M = cells.M
            for _ in range(20):
                orv = rng.getrandbits(M + 1) | (1 << M)
                P = rng.choice([None, 5, 17, 40, 200])
                unc = [not (orv >> m) & 1 for m in range(M)]
                if P is None:
                    want = any(unc)
                elif all(unc):
                    want = True
                else:
                    want = False
                    start = unc.index(False)
                    run = 0
                    for step in range(1, M + 1):
                        m = (start + step) % M
                        run = run + cells.lengths[m] if unc[m] else 0
                        if run * P > Q:
                            want = True
                self.assertEqual(cells.killed(orv, P), want)
            self.assertTrue(cells.killed(cells.full, None))  # exact bit clear: t = 0 good
            self.assertTrue(sum(cells.lengths) == Q)

    def test_killed_runs(self):
        # speeds (1,2,3), k = 3: loneliness 1/4 exactly (tight), so no gap at L = 1
        self.assertFalse(U.base_killed((1, 2, 3), 3, None))
        self.assertFalse(U.base_killed((1, 2, 3, 4, 5, 6, 7), 7, None))
        # other 3-speed sets: killed at level 1 (an open interval of strict
        # witnesses) iff their exact loneliness exceeds 1/4
        for s in [(1, 2, 4), (1, 3, 4), (2, 3, 5), (1, 2, 5)]:
            lon, _ = lrc_ref.loneliness(list(s))
            self.assertEqual(U.base_killed(s, 3, None), lon > Fraction(1, 4))

    def test_nontight_15(self):
        s = tuple(list(range(1, 14)) + [15, 28])
        self.assertTrue(U.base_killed(s, 15, None))
        self.assertTrue(U.base_killed(s, 15, 1500))  # interval of length 1/1344
        self.assertFalse(U.base_killed(tuple(range(1, 16)), 15, None))

    def test_linear_lift_lemma_L(self):
        # Lemma L analogue: z = s mod (k+1) is killed at level k+1 = 8 (t = 0), not at 4
        s = tuple(range(1, 8))
        self.assertTrue(U.uniform_killed(s, 7, tuple(x % 8 for x in s), 8, None))
        self.assertFalse(U.uniform_killed(s, 7, tuple(x % 4 for x in s), 4, None))
        self.assertTrue(U.is_linear(tuple(3 * x % 8 for x in s), s, 8))
        self.assertFalse(U.is_linear((1, 2, 3, 4, 5, 6, 0), s, 8))


class Sandwich(unittest.TestCase):
    def check(self, s, k, p, nlevels):
        pp = perprime_cascade(s, k, p, nlevels)
        ui = uniform_sets(s, k, nlevels, None)
        up = uniform_sets(s, k, nlevels, p)
        for lv in range(nlevels):
            self.assertTrue(ui[lv] <= pp[lv], (s, p, lv, sorted(ui[lv] - pp[lv])[:3]))
            self.assertTrue(pp[lv] <= up[lv], (s, p, lv, sorted(pp[lv] - up[lv])[:3]))
        return ui, pp, up

    def test_k3(self):
        for p in (11, 13, 29, 101):
            self.check((1, 2, 3), 3, p, 4)

    def test_k7_tight(self):
        ui, pp, up = self.check(tuple(range(1, 8)), 7, 29, 3)
        # the analogue of the 16-runner question: nothing survives level 8 = k+1?
        # (recorded, not asserted: the sandwich is the test)

    def test_small_random(self):
        rng = random.Random(3)
        for _ in range(6):
            k = rng.randint(3, 5)
            s = tuple(sorted(rng.sample(range(1, 10), k)))
            p = rng.choice([17, 19, 23])
            self.check(s, k, p, 2)


class DfsMatchesDirect(unittest.TestCase):
    def test_k3(self):
        for P in (None, 13, 101):
            self.assertEqual(uniform_sets((1, 2, 3), 3, 4, P),
                             uniform_sets((1, 2, 3), 3, 4, P, bruteforce=True))

    def test_k7(self):
        s = tuple(range(1, 8))
        for P in (None, 29):
            self.assertEqual(uniform_sets(s, 7, 2, P), uniform_sets(s, 7, 2, P, bruteforce=True))

    def test_k5_other(self):
        for s in [(1, 2, 3, 4, 6), (1, 2, 3, 5, 8)]:
            self.assertEqual(uniform_sets(s, 5, 3, None), uniform_sets(s, 5, 3, None, bruteforce=True))


if __name__ == "__main__":
    unittest.main()
