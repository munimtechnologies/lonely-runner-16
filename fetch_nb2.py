# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fetch the unchanged helpers of nbc.py at the commits where they were published
(uniform.py at 026f1ee, 2026-11-21; thresh.py at c51d4fb, 2026-11-22;
uniform_nb.py at a138b85, 2026-11-23), so job lrc-nb2 runs exactly the published
code, and record their SHA-256.

  python fetch_nb2.py [--out-dir /out]
"""
import argparse
import hashlib
import os
import sys
import urllib.request

REPO = "munimtechnologies/lonely-runner-16"
FILES = (
    ("uniform.py", "026f1ee88edeaf1964b3126d47e2d049b1f1a68b", b"def cascade"),
    ("thresh.py", "c51d4fb33502ce39baf8820a6cd48871543e608e", b"def proper_at"),
    ("uniform_nb.py", "a138b85fd004f0d0ae95f28d7604667c74f0f137", b"def lift_children"),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    lines = []
    for name, commit, marker in FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{name}"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        if len(data) < 1000 or marker not in data:
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
