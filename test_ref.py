# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
"""Self-consistency of the brute-force reference (pure Python, tiny cases)."""
import unittest

import lrc_ref as R


class Reference(unittest.TestCase):
    def test_each_class_covers_m_times(self):
        for k, p in [(3, 11), (4, 13), (5, 23), (6, 29)]:
            m = (p - 1) // (k + 1)
            for v in R.folded(p):
                self.assertEqual(len(R.cover_set(v, k, p)), m)

    def test_one_to_k_is_level1_improper(self):
        # (1,...,k) is a tight instance: no witness on the grid 1/p when p > k+1
        for k, p in [(3, 11), (4, 13), (5, 23), (6, 29), (7, 31)]:
            self.assertTrue(R.level1_improper(tuple(range(1, k + 1)), k, p))

    def test_orbit_expansion_equals_bruteforce(self):
        for k, p in [(3, 11), (3, 13), (4, 13), (4, 17), (4, 19)]:
            covs = R.canonical_covers(k, p)
            self.assertEqual(R.expand_orbits(covs, k, p),
                             R.all_level1_improper_multisets(k, p), (k, p))

    def test_level_witness_one_over_kplus1(self):
        # (1,...,7) has witness t = 1/8 once 8 | l
        k, p = 7, 31
        self.assertTrue(R.proper(tuple(range(1, 8)), k, p, 8))

    def test_cascade_monotone(self):
        counts, _ = R.cascade((1, 2, 3), 3, 11, [2])
        self.assertEqual(len(counts), 1)


if __name__ == "__main__":
    unittest.main()
