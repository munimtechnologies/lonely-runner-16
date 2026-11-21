# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc16-uniform-v1: binary lifting of the tight orbits, uniformly in p.

For each base vector s and each threshold P (None = U_inf), computes the canonical
survivors of binary lifting at levels 2, 4, ..., using uniform.py.  See
THEORY.md Sec. 8 and PLAN.md addendum 5 for what each number means.

  python job_uniform.py --out-dir /out
"""
import argparse
import json
import os
import platform
import sys
import time

import uniform as U

BASES = {
    "e15": (tuple(range(1, 16)), 15),
    "gw15": (tuple(list(range(1, 14)) + [15, 28]), 15),
    "e14": (tuple(range(1, 15)), 14),
    "e13": (tuple(range(1, 14)), 13),
    "gw13": (tuple(list(range(1, 12)) + [13, 24]), 13),
    "e7": (tuple(range(1, 8)), 7),
}

# (base, P, levels, minutes); run in this order
CONFIGS = [
    ("e7", None, 4, 5), ("e7", 29, 4, 5),
    ("e15", None, 5, 35), ("e15", 251, 5, 35),
    ("gw15", None, 5, 15), ("gw15", 251, 5, 15),
    ("e14", 239, 4, 15), ("e14", None, 4, 10),
    ("e13", 89, 4, 10), ("gw13", 89, 4, 10),
    ("e15", 17, 5, 15),
]


def summarise(name, s, k, P, levels, res, secs):
    out = {"base": name, "s": list(s), "k": k, "P": P, "levels_requested": levels,
           "base_killed": res["base_killed"], "cut": res["cut"], "seconds": round(secs, 1),
           "levels": []}
    empty_at = None
    for lv in res["levels"]:
        L, sv = lv["level"], lv["survivors"]
        lin = sum(1 for z in sv if U.is_linear(z, s, L))
        out["levels"].append({"level": L, "survivors": len(sv), "linear": lin,
                              "nonlinear": len(sv) - lin,
                              "list": [list(z) for z in sv[:60]]})
        if not sv and empty_at is None:
            empty_at = L
    out["empty_at_level"] = 1 if res["base_killed"] else empty_at
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"job": "lrc16-uniform-v1", "python": sys.version, "machine": platform.machine(),
               "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}
    for name, P, levels, minutes in CONFIGS:
        if a.only and name not in a.only.split(","):
            continue
        s, k = BASES[name]
        t0 = time.time()
        res = U.cascade(s, k, levels, P, max_parents=3000, deadline=t0 + 60 * minutes, clock=time.time)
        row = summarise(name, s, k, P, levels, res, time.time() - t0)
        summary["runs"].append(row)
        print(json.dumps({x: row[x] for x in ("base", "P", "base_killed", "cut", "empty_at_level", "seconds")}),
              [(lv["level"], lv["survivors"], lv["nonlinear"]) for lv in row["levels"]], flush=True)
        with open(os.path.join(a.out_dir, "summary_uniform.json"), "w") as f:
            json.dump(summary, f, indent=1)
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(a.out_dir, "summary_uniform.json"), "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
