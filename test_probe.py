# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Tests for the pure helpers of probe.py (no network, no compiler)."""
import unittest

import probe


class SafeName(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(probe.safe_name("a/b/c.cpp"), "a/b/c.cpp")
        self.assertEqual(probe.safe_name("./a//b.txt"), "a/b.txt")
        self.assertEqual(probe.safe_name("a\\b.log"), "a/b.log")

    def test_unsafe(self):
        for bad in ("", "/etc/passwd", "../x", "a/../../x", "C:/x", "c:\\x", ".", "./"):
            self.assertIsNone(probe.safe_name(bad), bad)


class Parsers(unittest.TestCase):
    def test_modes_v6_usage(self):
        u = ("usage: prog p mode(direct|decomp|both|12|12roots|12root|irroots|irroot|"
             "irsubroots|irsubroot|irsubrootraw) [args]")
        m = probe.parse_modes(u)
        self.assertEqual(len(m), 11)
        self.assertEqual(m[0], "direct")
        self.assertIn("irsubroots", m)
        self.assertEqual(probe.parse_modes("no usage here"), [])

    def test_kv(self):
        d = probe.parse_kv("direct=163507 decomp=163507 missing=0 extra=0")
        self.assertEqual(d, {"direct": "163507", "decomp": "163507", "missing": "0", "extra": "0"})
        d = probe.parse_kv("S k=15 p=401 n=200 seconds=1.250 timed_out=0")
        self.assertEqual(d["p"], "401")
        self.assertEqual(d["seconds"], "1.250")

    def test_index_lines(self):
        txt = "bt=3 roots=3\n0 1\n1 5\n 2  17 \nnot 3 4\n4 5 6\n"
        self.assertEqual(probe.parse_index_lines(txt), [0, 1, 2])

    def test_flatten(self):
        f = probe.flatten({"a": {"b": 1, "c": [2, 3]}, "s": "x", "big": list(range(60))})
        self.assertEqual(f, {"a.b": 1, "a.c[0]": 2, "a.c[1]": 3, "s": "x", "big.len": 60})


if __name__ == "__main__":
    unittest.main()
