# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fetch the engine files of this repository at a pinned commit, so a compete
job runs exactly the published code plus the local test fix (test_c.py is
never overwritten).

  python fetch_pinned.py [--commit SHA] [--out-dir /out]

Writes the files into the current directory and their SHA-256 into
<out-dir>/pinned_sha256.txt.
"""
import argparse
import hashlib
import os
import sys
import urllib.request

REPO = "munimtechnologies/lonely-runner-16"
# commit c5cfb60 (2026-11-21): lrc.c with ext=1, job_tau.py, test_ext.py
COMMIT = "c5cfb60bc9248c24a3850ac5e37114bf40e3fa36"
FILES = ("lrc.c", "lrc_ref.py", "test_ext.py", "test_shift.py", "job_tau.py",
         "job_shift.py")
KEEP_LOCAL = ("test_c.py",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=COMMIT)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    lines = []
    for name in FILES:
        if name in KEEP_LOCAL:
            continue
        url = f"https://raw.githubusercontent.com/{REPO}/{a.commit}/{name}"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        if len(data) < 100:
            sys.exit(f"suspiciously short file {name}: {len(data)} bytes")
        with open(name, "wb") as f:
            f.write(data)
        h = hashlib.sha256(data).hexdigest()
        lines.append(f"{h}  {name}  ({a.commit})")
        print(lines[-1], flush=True)
    for name in KEEP_LOCAL:
        with open(name, "rb") as f:
            lines.append(f"{hashlib.sha256(f.read()).hexdigest()}  {name}  (local)")
            print(lines[-1], flush=True)
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "pinned_sha256.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
