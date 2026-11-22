# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fetch uniform.py at the commit where it was published (026f1ee, 2026-11-21),
so job lrc16-uniform-v2 runs exactly the code that lrc16-uniform-v1 ran, and
record its SHA-256.

  python fetch_uniform.py [--out-dir /out]
"""
import argparse
import hashlib
import os
import sys
import urllib.request

REPO = "munimtechnologies/lonely-runner-16"
COMMIT = "026f1ee88edeaf1964b3126d47e2d049b1f1a68b"
FILES = ("uniform.py",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=COMMIT)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    lines = []
    for name in FILES:
        url = f"https://raw.githubusercontent.com/{REPO}/{a.commit}/{name}"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        if len(data) < 1000 or b"def cascade" not in data:
            sys.exit(f"unexpected content for {name}: {len(data)} bytes")
        with open(name, "wb") as f:
            f.write(data)
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}  ({a.commit})")
        print(lines[-1], flush=True)
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        with open(os.path.join(a.out_dir, "pinned_sha256.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
