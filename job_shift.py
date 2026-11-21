# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""16-runner (k = 15) persistent-orbit probe and shift-filtered pilot gates.

  python job_shift.py --out-dir /out --workers 4

Part A (orbits): the tight tuples (1..15) and (1..13,15,28) are lifted through
  levels 2,4,...,64 and through 2,4,8,16,48, with and without the shift filter
  (THEORY.md Sec. 5), at the ten pilot primes.  Pre-registered prediction
  (PLAN.md addendum 2): every LINEAR lift dies at level 16 (Lemma L), so the
  orbit of (1..15) is expected to empty by level 16 or 32 at most primes;
  nonlinear lifts may survive, and that is what this measures.
Part B (gates): the full pilot gates for k = 15 with engine 2 (norm 1, bb 1) and
  the shift filter on, so the survivors that remain are the ones that would
  need a new argument.
"""
import argparse
import json
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PRIMES = (251, 283, 307, 353, 401, 449, 503, 601, 701, 809)
TUPLES = {"one_to_15": list(range(1, 16)),
          "gw_15": list(range(1, 14)) + [15, 28]}
LEVELS = {"bin64": "2,2,2,2,2,2", "l48": "2,2,2,2,3"}
LIFTCAP = 400000  # vectors kept per level; about 50 MB each, so 4 workers fit in 2 GB
PROBE_TIMEOUT = 600
GATE_TIMECAP = 600


def build(binpath):
    subprocess.run(["cc", "-O3", "-march=native", "-o", binpath, os.path.join(HERE, "lrc.c")],
                   check=True)


def orbit_probe(binpath, p, name, levels, mode):
    t0 = time.time()
    env = dict(os.environ, LRC_LIFTCAP=str(LIFTCAP))
    rec = {"p": p, "tuple": name, "levels": levels, "mode": mode}
    try:
        r = subprocess.run([binpath, mode, "15", str(p), LEVELS[levels]] +
                           [str(x) for x in TUPLES[name]],
                           capture_output=True, text=True, timeout=PROBE_TIMEOUT, env=env)
        lines = r.stdout.splitlines()
        rec["kept_by_level"] = [[int(x) for x in ln.split()[1:]] for ln in lines if ln.startswith("L ")]
        rec["shift_removed_by_level"] = [[int(x) for x in ln.split()[1:]]
                                         for ln in lines if ln.startswith("X ")]
        st = [int(ln.split()[1]) for ln in lines if ln.startswith("R ")]
        rec["status"] = st[0] if st else None
        rec["survivor_examples"] = [[int(x) for x in ln.split()[1:]]
                                    for ln in lines if ln.startswith("W")][:10]
        rec["returncode"] = r.returncode
        if r.stderr:
            rec["stderr"] = r.stderr[-1000:]
    except subprocess.TimeoutExpired:
        rec["error"] = "timeout"
    rec["seconds"] = round(time.time() - t0, 2)
    # level at which the cascade emptied (None if it did not)
    dead = None
    if rec.get("status") == 0:
        for lev, cnt in rec.get("kept_by_level", []):
            if cnt == 0:
                dead = lev
                break
        if dead is None and rec.get("kept_by_level") == []:
            dead = 1
    rec["empty_at_level"] = dead
    print(json.dumps({x: rec.get(x) for x in ("p", "tuple", "levels", "mode", "status",
                                              "empty_at_level", "seconds")}), flush=True)
    return rec


def gate(binpath, p, outdir, timecap=GATE_TIMECAP):
    t0 = time.time()
    try:
        r = subprocess.run([binpath, "gate", "15", str(p), "2,2,2,2,2", str(timecap),
                            str(LIFTCAP), "1", "1", "1"],
                           capture_output=True, text=True, timeout=timecap * 5 + 600)
        line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "{}"
        d = json.loads(line)
        d["returncode"] = r.returncode
        if r.stderr:
            d["stderr"] = r.stderr[-2000:]
    except subprocess.TimeoutExpired:
        d = {"k": 15, "p": p, "error": "wall timeout"}
    except Exception as e:
        d = {"k": 15, "p": p, "error": repr(e)}
    d["wall_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(outdir, "gates"), exist_ok=True)
    with open(os.path.join(outdir, "gates", f"k15_p{p}_e11_shift.json"), "w") as f:
        json.dump(d, f, indent=1)
    print(json.dumps({x: d.get(x) for x in ("k", "p", "tau", "orbits_by_size", "tuples", "killed",
                                            "survived", "overflow", "complete",
                                            "shift_removed_by_level", "tuples_using_shift",
                                            "wall_seconds", "error")}), flush=True)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--skip-gates", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = os.path.join(a.out_dir, "lrc")
    build(binpath)

    # in priority order; each probe is capped at PROBE_TIMEOUT seconds
    jobs = [(p, "one_to_15", "bin64", m) for p in PRIMES for m in ("cascadebb", "scascadebb")]
    jobs += [(p, "gw_15", "bin64", m) for p in PRIMES for m in ("cascadebb", "scascadebb")]
    jobs += [(p, "one_to_15", "l48", "scascadebb") for p in PRIMES]
    lock = threading.Lock()
    jl = os.path.join(a.out_dir, "orbits.jsonl")

    def one(j):
        rec = orbit_probe(binpath, *j)
        with lock:
            with open(jl, "a") as f:
                f.write(json.dumps(rec) + "\n")
        return rec

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        orbits = list(ex.map(one, jobs))
    summary = {"part": "A", "primes": PRIMES, "tuples": TUPLES, "levels": LEVELS,
               "liftcap": LIFTCAP, "orbits": orbits}
    # pre-registered reading (PLAN.md addendum 2)
    one = [o for o in orbits if o["tuple"] == "one_to_15" and o["levels"] == "bin64"
           and o["mode"] == "cascadebb"]
    summary["one_to_15_bin64_plain"] = {
        "primes": len(one),
        "empty_by_16": sum(1 for o in one if o.get("empty_at_level") and o["empty_at_level"] <= 16),
        "empty_by_32": sum(1 for o in one if o.get("empty_at_level") and o["empty_at_level"] <= 32),
        "empty_by_64": sum(1 for o in one if o.get("empty_at_level") and o["empty_at_level"] <= 64),
        "survives_64": sum(1 for o in one if o.get("status") == 1),
        "overflow_or_error": sum(1 for o in one if o.get("status") not in (0, 1)),
    }
    with open(os.path.join(a.out_dir, "summary_orbits.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps({"partA": summary["one_to_15_bin64_plain"]}), flush=True)

    if not a.skip_gates:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            gates = list(ex.map(lambda p: gate(binpath, p, a.out_dir), PRIMES))
        keys = ("k", "p", "tau", "orbits_by_size", "cover_seconds", "cover_timed_out", "tuples",
                "killed", "survived", "overflow", "complete", "small_orbits_unhandled",
                "max_improper_by_level", "sum_improper_by_level", "shift_removed_by_level",
                "tuples_using_shift", "total_seconds", "wall_seconds", "error")
        with open(os.path.join(a.out_dir, "summary_gates_shift.json"), "w") as f:
            json.dump({"part": "B", "gates": [{x: d.get(x) for x in keys} for d in gates],
                       "survivor_examples": {f"p{d.get('p')}": d.get("survivors", [])[:20]
                                             for d in gates}}, f, indent=1)
    print("done", flush=True)


if __name__ == "__main__":
    main()
