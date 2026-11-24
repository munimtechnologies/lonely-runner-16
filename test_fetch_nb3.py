# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Offline checks of fetch_nb3.py (no network): every module that run_tests_c.py
and job_nb2.py load is pinned, each commit is a full SHA, no file is listed twice.

The import lists below were read by hand from the published files:
  run_tests_c.py loads test_nbc, test_uniform_nb
  test_nbc.py imports nbc, uniform_nb
  test_uniform_nb.py imports thresh, uniform, uniform_nb
  job_nb2.py imports nbc, thresh, uniform_nb
  nbc.py compiles nbc.c (next to nbc.py) and imports the published helpers
"""
import re
import unittest

import fetch_nb3 as F

NEEDED = {
    "run_tests_c.py", "test_nbc.py", "test_uniform_nb.py", "job_nb2.py",
    "nbc.py", "nbc.c", "uniform_nb.py", "thresh.py", "uniform.py",
}


class FetchTable(unittest.TestCase):
    def test_every_needed_file_is_pinned(self):
        names = [f[0] for f in F.FILES]
        self.assertEqual(set(names), NEEDED)
        self.assertEqual(len(names), len(set(names)))

    def test_the_v3_failure_is_covered(self):
        # lrc16-engine2-v3 failed with: No module named 'test_uniform_nb'
        self.assertIn("test_uniform_nb.py", [f[0] for f in F.FILES])

    def test_commits_are_full_shas(self):
        for name, commit, marker in F.FILES:
            self.assertRegex(commit, r"^[0-9a-f]{40}$", name)
            self.assertIsInstance(marker, bytes)
            self.assertTrue(marker)

    def test_urls(self):
        u = F.url_of("nbc.c", F.C_NB2)
        self.assertTrue(u.startswith("https://raw.githubusercontent.com/munimtechnologies/"))
        self.assertTrue(u.endswith("/57f59b9b510bd8f74d2f85b64fbe1f155d0ebe49/nbc.c"))
        self.assertIsNone(re.search(r"\s", u))


if __name__ == "__main__":
    unittest.main()
