# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for nbc.py / nbc.c (THEORY_17.md).

PyMatchesPublished: nbc.lift (pure Python, with and without the unit-symmetry
  reduction, three search orders) gives exactly uniform_nb.lift_children, the
  published code of job lrc-nb, on every parent of several small cascades.
CMatchesPy: the C engine visits the same nodes and leaves and returns the same
  children as nbc.dfs_py.  Skipped when no C compiler is found, unless
  NBC_REQUIRE_C=1 (set in the compete job, where cc exists).
"""
import os
import unittest

import nbc
import uniform_nb as N

CASES = [
    ((1, 2, 3), 3, ([3], [5], [7], [2, 3], [3, 5], [5, 3], [2, 7])),
    ((1, 2, 3, 4), 4, ([3], [5], [3, 5], [5, 3], [2, 7], [7])),
    ((1, 2, 4), 3, ([3, 5], [5, 3])),
    ((1, 2, 3, 4, 5), 5, ([2, 3], [3, 2], [5])),
]


def parents_and_steps(s, k, chain, P, g):
    """(parent z, level L, c) for every lift step of the chain, parents from the
    published cascade"""
    out = []
    L = 1
    parents = [] if N.base_killed(tuple(s), k, P) else [tuple(0 for _ in s)]
    for c in chain:
        for z in parents:
            out.append((z, L, c))
        nxt = set()
        for z in parents:
            nxt |= N.lift_children(s, k, z, L, c, P, g)
        parents = sorted(nxt)
        L *= c
    return out


class Basics(unittest.TestCase):
    def test_sym_ok(self):
        self.assertTrue(nbc.sym_ok(7, 1))
        self.assertTrue(nbc.sym_ok(5, 3))
        self.assertTrue(nbc.sym_ok(3, 5))
        self.assertTrue(nbc.sym_ok(7, 2))
        self.assertFalse(nbc.sym_ok(2, 7))   # nothing to save
        self.assertFalse(nbc.sym_ok(3, 3))   # c divides L
        self.assertFalse(nbc.sym_ok(15, 1))  # not prime

    def test_orders(self):
        s = (1, 2, 3, 4, 5, 7, 12)
        self.assertEqual(nbc.search_order(s, 7, "desc"), [6, 5, 4, 3, 2, 1, 0])
        self.assertEqual(nbc.search_order(s, 7, "id"), list(range(7)))
        self.assertEqual(nbc.search_order((2, 1, 2), 3, "asc"), [1, 0, 2])

    def test_spec_words(self):
        prep = nbc.prepare((1, 2, 3, 4, 5, 6, 7), 7, (0,) * 7, 1, 5, None)
        txt = nbc.spec_text(prep, True, True).split()
        self.assertEqual(txt[:8], ["7", "5", "5", "0", str(prep["Q"]), "1", "1", "1"])
        W = int(txt[9])
        self.assertGreater(W, 1)  # several words per mask: exercises the multiword path


class PyMatchesPublished(unittest.TestCase):
    def test_cases(self):
        compared = 0
        nonempty = 0
        for s, k, chains in CASES:
            for chain in chains:
                for P in (None, 11):
                    for g in (True, False):
                        for z, L, c in parents_and_steps(s, k, chain, P, g):
                            want = N.lift_children(s, k, z, L, c, P, g)
                            nodes = {}
                            for order in ("desc", "id", "asc"):
                                for sym in ((False, True) if nbc.sym_ok(c, L) else (False,)):
                                    got, st = nbc.lift(s, k, z, L, c, P, g, sym, order)
                                    self.assertEqual(got, want, (s, chain, P, g, z, L, c, order, sym))
                                    nodes[(order, sym)] = st["nodes"]
                            for order in ("desc", "id", "asc"):
                                if (order, True) in nodes:
                                    self.assertLessEqual(nodes[(order, True)], nodes[(order, False)])
                            compared += 1
                            nonempty += bool(want)
        self.assertGreater(compared, 50)
        self.assertGreater(nonempty, 0)


class CMatchesPy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bin = nbc.build()
        if cls.bin is None and os.environ.get("NBC_REQUIRE_C") == "1":
            raise RuntimeError("NBC_REQUIRE_C=1 but no C compiler found")

    def setUp(self):
        if self.bin is None:
            self.skipTest("no C compiler")

    def same(self, s, k, z, L, c, P, g, order="desc", via_lift=False):
        prep = nbc.prepare(s, k, z, L, c, P, order)
        for sym in ((False, True) if nbc.sym_ok(c, L) else (False,)):
            a = nbc.dfs_py(prep, g, sym)
            b = nbc.dfs_c(prep, self.bin, g, sym)
            self.assertEqual(a, b, (s, z, L, c, P, g, order, sym))
            if via_lift:
                S1, _ = nbc.lift(s, k, z, L, c, P, g, sym, order, engine="py")
                S2, _ = nbc.lift(s, k, z, L, c, P, g, sym, order, engine="c", binpath=self.bin)
                self.assertEqual(S1, S2)
                self.assertEqual(S1, N.lift_children(s, k, z, L, c, P, g))

    def test_small_cases(self):
        n = 0
        for s, k, chains in CASES:
            for chain in chains:
                for P in (None, 11):
                    for g in (True, False):
                        for z, L, c in parents_and_steps(s, k, chain, P, g):
                            self.same(s, k, z, L, c, P, g, ("desc", "id")[n % 2],
                                      via_lift=(n % 3 == 0))
                            n += 1
        self.assertGreater(n, 50)

    def test_multiword(self):
        # masks of several 64-bit words; first step of a few chains
        for s, k in (((1, 2, 3, 4, 5, 6, 7), 7), ((1, 2, 3, 4, 5, 7, 12), 7)):
            self.same(s, k, (0,) * k, 1, 5, None, True, via_lift=True)
            self.same(s, k, (0,) * k, 1, 5, 29, False)
            for P in (None, 29):
                for g in (True, False):
                    self.same(s, k, (0,) * k, 1, 3, P, g)
            lvl3 = N.lift_children(s, k, (0,) * k, 1, 3, 29)
            for z in sorted(lvl3)[:2]:
                self.same(s, k, z, 3, 5, 29, True)

    def test_cut(self):
        # a deliberately large search with a tiny time limit reports CUT or finishes
        s = tuple(range(1, 14))
        prep = nbc.prepare(s, 13, (0,) * 13, 1, 7, 199)
        out, nodes, leaves = nbc.dfs_c(prep, self.bin, True, True, seconds=0.001)
        if out is None:
            self.assertGreaterEqual(nodes, 65536)


if __name__ == "__main__":
    unittest.main()
