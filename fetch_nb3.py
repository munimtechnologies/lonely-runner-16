# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fetch EVERY file job lrc-nb2 needs at the commit where it was published, so the
re-run (lrc16-engine2-v4) runs exactly the public code, and record their SHA-256.

Why: lrc16-engine2-v3 stopped at its test gate because run_tests_c.py loads
test_uniform_nb, which fetch_nb2.py did not download (ModuleNotFoundError). All 7
tests of test_nbc passed in that job, with the C engine forced on. This script adds
test_uniform_nb.py (published at a138b85) and also pins the run-19 files (57f59b9)
instead of copying them, so nothing in the job can drift from the repo.

  python fetch_nb3.py [--out-dir /out]
"""
import argparse
import hashlib
import os
import sys
import urllib.request

REPO = "munimtechnologies/lonely-runner-16"
C_UNIFORM = "026f1ee88edeaf1964b3126d47e2d049b1f1a68b"   # 2026-11-21
C_THRESH = "c51d4fb33502ce39baf8820a6cd48871543e608e"    # 2026-11-22
C_NB = "a138b85fd004f0d0ae95f28d7604667c74f0f137"        # 2026-11-23
C_NB2 = "57f59b9b510bd8f74d2f85b64fbe1f155d0ebe49"       # 2026-11-24 (run 19)

# (file, commit, a byte string the file must contain)
FILES = (
    ("uniform.py", C_UNIFORM, b"def cascade"),
    ("thresh.py", C_THRESH, b"def proper_at"),
    ("uniform_nb.py", C_NB, b"def lift_children"),
    ("test_uniform_nb.py", C_NB, b"import uniform_nb as N"),
    ("nbc.py", C_NB2, b"def lift_set"),
    ("nbc.c", C_NB2, b"static void dfs("),
    ("test_nbc.py", C_NB2, b"class CMatchesPy"),
    ("run_tests_c.py", C_NB2, b"NBC_REQUIRE_C"),
    ("job_nb2.py", C_NB2, b"def run_base"),
)
MIN_BYTES = 200


def url_of(name, commit):
    return f"https://raw.githubusercontent.com/{REPO}/{commit}/{name}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    lines = []
    for name, commit, marker in FILES:
        with urllib.request.urlopen(url_of(name, commit), timeout=60) as r:
            data = r.read()
        if len(data) < MIN_BYTES or marker not in data:
            sys.exit(f"unexpected content for {name}: {len(data)} bytes")
        with open(name, "wb") as f:
            f.write(data)
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}  ({commit})")
        print(lines[-1], flush=True)
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "pinned_sha256.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
