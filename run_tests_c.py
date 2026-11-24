# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Run test_nbc and test_uniform_nb with NBC_REQUIRE_C=1, so the C-engine tests
cannot be skipped (used by job lrc-nb2, where cc exists).

  python run_tests_c.py
"""
import os
import sys
import unittest

os.environ["NBC_REQUIRE_C"] = "1"
suite = unittest.defaultTestLoader.loadTestsFromNames(["test_nbc", "test_uniform_nb"])
res = unittest.TextTestRunner(verbosity=2).run(suite)
skipped = len(res.skipped)
print("skipped:", skipped, flush=True)
sys.exit(0 if res.wasSuccessful() and skipped == 0 else 1)
