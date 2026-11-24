# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc-nb2-b13 (PLAN_addendum13.md): job_nb2.py, unchanged, for the base
b13 = (1..11,13,24) only, with one worker and a longer cap on the level-7 step.

In lrc16-engine2-v4 the level-7 step of b13 at P = 199 was cut at its 3,600 s cap
while three bases shared the machine. Here it gets up to 16,200 s (4.5 h). Route A
(level 2 lifted by 7) is given only 60 s, so the cheap route C (CRT combination)
runs right after it as the cross-check of route B. Nothing else changes: the code,
the theory and the predictions are those of job_nb2.py at commit 57f59b9.

  python fetch_nb3.py --out-dir /out      # fetches job_nb2.py and its imports
  python run_tests_c.py
  python job_b13.py --out-dir /out
"""
import argparse
import json
import os
import sys

import job_nb2 as J

CAPS_MAIN = {"inf": {"f1": 900, "f2": 3600, "B": 1800},
             "P0": {"f1": 900, "f2": 16200, "B": 3600}}
CAPS_X = {"A": 60, "comb": 900}
CAPS_FREE = {"f1": 300, "f2": 300, "B": 300}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--minutes", type=float, default=400)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    # run_base, cross and factor_sets read these module globals at call time
    J.CAPS_MAIN, J.CAPS_X, J.CAPS_FREE = CAPS_MAIN, CAPS_X, CAPS_FREE
    with open(os.path.join(a.out_dir, "caps_b13.json"), "w") as f:
        json.dump({"CAPS_MAIN": CAPS_MAIN, "CAPS_X": CAPS_X, "CAPS_FREE": CAPS_FREE,
                   "minutes": a.minutes, "only": "b13", "workers": 1}, f, indent=1)
    sys.argv = ["job_nb2.py", "--out-dir", a.out_dir, "--only", "b13",
                "--workers", "1", "--minutes", str(a.minutes)]
    J.main()


if __name__ == "__main__":
    main()
