# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fetch the committed raw output of job lrc16-uniform-v1 (the U_251 lists that
THEORY_18 relies on) at a pinned commit, and record its SHA-256.

  python fetch_indep.py [--out-dir /out]
"""
import argparse
import hashlib
import os
import sys
import urllib.request

REPO = "munimtechnologies/lonely-runner-16"
COMMIT = "162a7b926218a6846eace375182bb4dfd7a11b37"  # THEORY_18 commit, 2026-11-24
PATH = "results/lrc16-uniform-v1/summary_uniform.json"
MARKERS = (b'"base": "e15"', b'"base": "gw15"')
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    url = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{PATH}"
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    if len(data) < 10000 or not all(m in data for m in MARKERS):
        sys.exit(f"unexpected content: {len(data)} bytes")
    with open(os.path.join(HERE, "summary_uniform.json"), "wb") as f:
        f.write(data)
    line = f"{hashlib.sha256(data).hexdigest()}  {PATH}  ({COMMIT})"
    print(line, flush=True)
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "pinned_sha256.txt"), "w") as f:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
