# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
"""Cross-check the C engine (lrc.c) against the brute-force reference.
Skipped when no C compiler is available."""
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


@unittest.skipUnless(CC, "no C compiler")
class CEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def c_covers(self, k, p):
        lines = run("covers", k, p)
        covs = [tuple(int(x) for x in ln.split()[2:]) for ln in lines if ln.startswith("C ")]
        return sorted(covs), lines[-1]

    def test_covers_match_reference(self):
        for k, p in [(3, 11), (3, 13), (4, 13), (4, 17), (4, 19), (5, 23), (5, 29), (6, 29)]:
            got, summary = self.c_covers(k, p)
            self.assertEqual(got, R.canonical_covers(k, p), (k, p, summary))

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
            lines = run("cascade", k, p, ",".join(map(str, mults)), *v)
            ccounts = [int(ln.split()[2]) for ln in lines if ln.startswith("L ")]
            ccounts = ccounts[:len(counts)]
            self.assertEqual(ccounts, counts, (k, p, mults, v, lines))

    def test_gate_json(self):
        import json
        line = run("gate", 4, 17, "2,2", 30, 100000)[-1]
        d = json.loads(line)
        self.assertEqual(d["k"], 4)
        self.assertIn("tau", d)


if __name__ == "__main__":
    unittest.main()
