# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Pilot runs for the 16-runner (LRC(15)) project.

  python job.py repro --out-dir /out   # independent re-check of k=13,14 gates
  python job.py pilot --out-dir /out   # k=15 (16 runners) cost and survivor survey

Each gate runs `lrc gate K P levels timecap liftcap` and its JSON line is saved
under <out>/gates/k<K>_p<P>.json.  A summary is written to <out>/summary_<mode>.json.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))

REPRO = {
    # k=14: Allikvere's tau>=13 block (every prime 239..569 except 241); the
    # binary cascade alone should leave only the orbit of (1,...,14)
    "gates": [(14, p) for p in (569, 503, 449, 401, 353, 307, 271, 239)]
             + [(13, p) for p in (479, 401)],
    "levels": "2,2,2,2,2",
    "timecap": 1500,
    "liftcap": 1000000,
}

PILOT = {
    "gates": [(15, p) for p in (809, 701, 601, 503, 449, 401, 353, 307, 283, 251)],
    "levels": "2,2,2,2,2",
    "timecap": 1500,
    "liftcap": 1000000,
}


def build(binpath):
    subprocess.run(["cc", "-O3", "-march=native", "-o", binpath, os.path.join(HERE, "lrc.c")],
                   check=True)


def run_gate(binpath, k, p, levels, timecap, liftcap, outdir):
    t0 = time.time()
    try:
        r = subprocess.run([binpath, "gate", str(k), str(p), levels, str(timecap), str(liftcap)],
                           capture_output=True, text=True, timeout=timecap * 5 + 600)
        line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "{}"
        d = json.loads(line)
        d["returncode"] = r.returncode
        if r.stderr:
            d["stderr"] = r.stderr[-2000:]
    except subprocess.TimeoutExpired:
        d = {"k": k, "p": p, "error": "wall timeout"}
    except Exception as e:  # keep going on any single-gate failure
        d = {"k": k, "p": p, "error": repr(e)}
    d["wall_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(outdir, "gates"), exist_ok=True)
    with open(os.path.join(outdir, "gates", f"k{k}_p{p}.json"), "w") as f:
        json.dump(d, f, indent=1)
    brief = {x: d.get(x) for x in ("k", "p", "tau", "orbits_by_size", "cover_seconds",
                                   "cover_timed_out", "tuples", "killed", "survived",
                                   "overflow", "complete", "wall_seconds", "error")}
    print(json.dumps(brief), flush=True)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["repro", "pilot"])
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = os.path.join(a.out_dir, "lrc")
    build(binpath)

    sys.path.insert(0, HERE)
    import bounds
    from fractions import Fraction
    t0 = time.time()
    bres = {}
    for n in (13, 14, 15):
        r = {13: Fraction(101, 200), 14: Fraction(1, 2)}.get(n)
        bres[n] = bounds.report(n, r, gate_start=251 if n == 15 else None)
        bres[n]["random_search_min_H"] = bounds.random_search(n, trials=60, iters=4000)
    with open(os.path.join(a.out_dir, "bounds.json"), "w") as f:
        json.dump(bres, f, indent=1, default=str)
    print("bounds done in %.1fs" % (time.time() - t0), flush=True)
    print(json.dumps({n: {x: bres[n][x] for x in ("H_lower_bound", "r_n_used",
                                                   "log_product_bound", "required_gate_logsum")}
                      for n in bres}, default=str), flush=True)

    cfg = REPRO if a.mode == "repro" else PILOT
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_gate, binpath, k, p, cfg["levels"], cfg["timecap"],
                          cfg["liftcap"], a.out_dir) for k, p in cfg["gates"]]
        results = [f.result() for f in futs]
    summary = {"mode": a.mode, "config": cfg, "bounds_n15": {
        x: bres[15][x] for x in ("H_lower_bound", "r_n_used", "log_product_bound",
                                 "required_gate_logsum", "example_gate_set")},
        "gates": [{x: d.get(x) for x in ("k", "p", "tau", "orbits_by_size", "cover_seconds",
                                         "cover_timed_out", "tuples", "killed", "survived",
                                         "overflow", "complete", "small_orbits_unhandled",
                                         "max_improper_by_level", "wall_seconds", "error")}
                  for d in results],
        "survivor_examples": {f"k{d.get('k')}_p{d.get('p')}": d.get("survivors", [])[:10]
                              for d in results}}
    with open(os.path.join(a.out_dir, f"summary_{a.mode}.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print("done", flush=True)


if __name__ == "__main__":
    main()
