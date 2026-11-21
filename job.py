# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Runs for the 16-runner (LRC(15)) project.

  python job.py repro   --out-dir /out   # k=13,14 re-check (engine 1: norm=0, bb=0)
  python job.py pilot   --out-dir /out   # k=15 survey     (engine 1)
  python job.py engine2 --out-dir /out   # small cross-check of engine 1 vs engine 2,
                                         # then repro + pilot gates with engine 2
                                         # (norm=1: Lemma 4.1 normalisation,
                                         #  bb=1: branch-and-bound lifting)

Each gate runs `lrc gate K P levels timecap liftcap norm bb` and its JSON line is
saved under <out>/gates/k<K>_p<P>_e<norm><bb>.json.  A summary is written to
<out>/summary_<mode>.json.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))

REPRO_GATES = [(14, p) for p in (569, 503, 449, 401, 353, 307, 271, 239)] + \
              [(13, p) for p in (479, 401)]
PILOT_GATES = [(15, p) for p in (809, 701, 601, 503, 449, 401, 353, 307, 283, 251)]

REPRO = {"gates": REPRO_GATES, "levels": "2,2,2,2,2", "timecap": 1500, "liftcap": 1000000}
PILOT = {"gates": PILOT_GATES, "levels": "2,2,2,2,2", "timecap": 1500, "liftcap": 1000000}

# engine-vs-engine cross-check on gates small enough for the brute-force engine
XCHECK = {"gates": [(8, 61), (8, 73), (9, 83), (9, 101), (10, 103), (10, 131),
                    (11, 137), (11, 163), (12, 173), (12, 199), (13, 211), (14, 241)],
          "levels": "2,2,2,2,2", "timecap": 240, "liftcap": 1000000}
ENGINE2 = {"gates": PILOT_GATES + REPRO_GATES, "levels": "2,2,2,2,2",
           "timecap": 800, "liftcap": 2000000}

COMPARE_KEYS = ("tau", "orbits_by_size", "tuples", "killed", "survived", "overflow",
                "complete", "max_improper_by_level", "sum_improper_by_level")


def build(binpath):
    subprocess.run(["cc", "-O3", "-march=native", "-o", binpath, os.path.join(HERE, "lrc.c")],
                   check=True)


def run_gate(binpath, k, p, levels, timecap, liftcap, outdir, norm=0, bb=0):
    t0 = time.time()
    try:
        r = subprocess.run([binpath, "gate", str(k), str(p), levels, str(timecap), str(liftcap),
                            str(norm), str(bb)],
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
    d["engine"] = {"norm": norm, "bb": bb}
    d["wall_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(outdir, "gates"), exist_ok=True)
    with open(os.path.join(outdir, "gates", f"k{k}_p{p}_e{norm}{bb}.json"), "w") as f:
        json.dump(d, f, indent=1)
    brief = {x: d.get(x) for x in ("k", "p", "engine", "tau", "orbits_by_size", "cover_seconds",
                                   "cover_timed_out", "tuples", "killed", "survived",
                                   "overflow", "complete", "wall_seconds", "error")}
    print(json.dumps(brief), flush=True)
    return d


def brief(d):
    return {x: d.get(x) for x in ("k", "p", "engine", "tau", "orbits_by_size", "cover_seconds",
                                  "cover_timed_out", "tuples", "killed", "survived",
                                  "overflow", "complete", "small_orbits_unhandled",
                                  "max_improper_by_level", "sum_improper_by_level",
                                  "total_seconds", "wall_seconds", "error")}


def bounds_report(outdir):
    sys.path.insert(0, HERE)
    import bounds
    t0 = time.time()
    bres = {}
    for n in (13, 14, 15):
        bres[n] = bounds.report(n, bounds.R_USED.get(n), gate_start=251 if n == 15 else None)
        bres[n]["random_search_min_H"] = bounds.random_search(n, trials=60, iters=4000)
    with open(os.path.join(outdir, "bounds.json"), "w") as f:
        json.dump(bres, f, indent=1, default=str)
    print("bounds done in %.1fs" % (time.time() - t0), flush=True)
    return bres


def run_set(binpath, cfg, outdir, workers, norm, bb):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_gate, binpath, k, p, cfg["levels"], cfg["timecap"],
                          cfg["liftcap"], outdir, norm, bb) for k, p in cfg["gates"]]
        return [f.result() for f in futs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["repro", "pilot", "engine2"])
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = os.path.join(a.out_dir, "lrc")
    build(binpath)
    bres = bounds_report(a.out_dir)
    b15 = {x: bres[15].get(x) for x in ("H_lower_bound", "r_n_used", "log_product_bound",
                                         "required_gate_logsum", "example_gate_set",
                                         "shape_n15_exact", "quartic_factor_n15")}

    if a.mode in ("repro", "pilot"):
        cfg = REPRO if a.mode == "repro" else PILOT
        results = run_set(binpath, cfg, a.out_dir, a.workers, 0, 0)
        summary = {"mode": a.mode, "config": cfg, "bounds_n15": b15,
                   "gates": [brief(d) for d in results],
                   "survivor_examples": {f"k{d.get('k')}_p{d.get('p')}": d.get("survivors", [])[:10]
                                         for d in results}}
    else:
        # 1. cross-check: the same gates with both engines
        e1 = run_set(binpath, XCHECK, a.out_dir, a.workers, 0, 0)
        e2 = run_set(binpath, XCHECK, a.out_dir, a.workers, 1, 1)
        xc = []
        for d1, d2 in zip(e1, e2):
            both = (d1.get("complete") == 1 and d2.get("complete") == 1)
            diff = [key for key in COMPARE_KEYS if d1.get(key) != d2.get(key)]
            s1 = sorted(json.dumps(s.get("tuple")) for s in d1.get("survivors", []))
            s2 = sorted(json.dumps(s.get("tuple")) for s in d2.get("survivors", []))
            if both and (d1.get("survived", 0) or 0) <= 200 and s1 != s2:
                diff.append("survivors")
            xc.append({"k": d1.get("k"), "p": d1.get("p"), "both_complete": both,
                       "agree": both and not diff, "differences": diff,
                       "seconds_engine1": d1.get("total_seconds"),
                       "seconds_engine2": d2.get("total_seconds"),
                       "engine1": brief(d1), "engine2": brief(d2)})
            print(json.dumps({"xcheck": [d1.get("k"), d1.get("p")], "both_complete": both,
                              "differences": diff}), flush=True)
        # 2. the repro and pilot gates with engine 2
        results = run_set(binpath, ENGINE2, a.out_dir, a.workers, 1, 1)
        summary = {"mode": a.mode, "xcheck_config": XCHECK, "config": ENGINE2,
                   "bounds_n15": b15,
                   "xcheck": xc,
                   "xcheck_all_complete_agree": all(x["agree"] for x in xc if x["both_complete"]),
                   "xcheck_complete_count": sum(1 for x in xc if x["both_complete"]),
                   "gates": [brief(d) for d in results],
                   "survivor_examples": {f"k{d.get('k')}_p{d.get('p')}": d.get("survivors", [])[:10]
                                         for d in results}}
    with open(os.path.join(a.out_dir, f"summary_{a.mode}.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print("done", flush=True)


if __name__ == "__main__":
    main()
