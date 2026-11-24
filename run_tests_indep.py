# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Run test_indep with the C tests required (no skips), then exit non-zero on any
failure or skip, so the compete job stops before it computes anything."""
import os
import sys
import unittest

os.environ["INDEP_REQUIRE_C"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import test_indep  # noqa: E402

suite = unittest.defaultTestLoader.loadTestsFromModule(test_indep)
result = unittest.TextTestRunner(verbosity=2).run(suite)
skipped = [t for t, _ in result.skipped if "C" in type(t).__name__]
if not result.wasSuccessful() or skipped:
    sys.exit(f"tests failed or C tests skipped: {len(result.failures)} failures, "
             f"{len(result.errors)} errors, {len(skipped)} C skips")
print("all indep tests passed with the C engine")
