# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Engine 4 job (PLAN_addendum8.md): does early orbit pruning (LRC_PRUNE bit 4,
THEORY_14.md) keep every answer, and how much does it save on top of engine 3?

  python job_orbit.py --out-dir /out --workers 4 [--quick]

Part X  8 small gates (k = 8 to 11) with LRC_PRUNE = 0 and 7: identical results
        wherever both finish (M1).
Part T  the 24 tau rows that lrc16-tau-v2 decided in 3.5 s or more, with
        LRC_PRUNE = 3 and 7 on the same machine: same answers as tau-v2 (M1),
        search nodes (M2), speed (S2).
Writes xcheck4.jsonl, speed4.jsonl, sha256.txt and summary_orbit.json.
"""
import argparse
import hashlib
import json
import os
import statistics
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = 300

XGATES = [(8, 61), (8, 73), (9, 83), (9, 101), (10, 103), (10, 131), (11, 137), (11, 163)]
XKEYS = ("tau", "orbits_by_size", "tuples", "killed", "survived", "overflow",
         "complete", "max_improper_by_level", "sum_improper_by_level")

# lrc16-tau-v2 (2026-11-22, Dell, engine 2): (k, p) -> (status, tau, seconds)
TAU_V2 = {
    (15, 191): ("le", 13, 4.119), (15, 199): ("le", 12, 7.913),
    (15, 181): ("le", 13, 11.8), (15, 223): ("le", 13, 10.265),
    (15, 211): ("le", 13, 25.001), (15, 233): ("le", 13, 39.281),
    (15, 251): ("le", 13, 43.103), (15, 241): ("le", 13, 65.405),
    (15, 257): ("le", 13, 75.232), (15, 263): ("le", 13, 62.817),
    (15, 277): ("le", 13, 92.01), (15, 239): ("gt", 0, 250.002),
    (14, 197): ("le", 12, 3.612), (14, 181): ("le", 12, 4.268),
    (14, 211): ("le", 12, 4.396), (14, 227): ("le", 12, 5.699),
    (14, 223): ("le", 12, 6.389), (14, 229): ("le", 12, 12.393),
    (14, 241): ("le", 12, 10.491), (14, 239): ("gt", 0, 74.206),
    (14, 251): ("gt", 0, 148.187), (14, 269): ("gt", 0, 134.496),
    (14, 263): ("gt", 0, 226.746), (14, 283): ("gt", 0, 291.599),
}


def build(binpath):
    subprocess.run(["cc", "-O3", "-march=native", "-o", binpath,
                    os.path.join(HERE, "lrc.c")], check=True)


def run_bin(binpath, prune, args, timeout):
    env = dict(os.environ, LRC_PRUNE=str(prune))
    return subprocess.run([binpath] + [str(a) for a in args], capture_output=True,
                          text=True, timeout=timeout, env=env)


def tau_one(binpath, k, p, maxsize, cap, prune):
    t0 = time.time()
    rec = {"k": k, "p": p, "maxsize": maxsize, "cap": cap, "prune": prune}
    try:
        r = run_bin(binpath, prune, ["tau", k, p, maxsize, cap], cap + 300)
        for ln in r.stdout.splitlines():
            if ln.startswith("T "):
                for item in ln.split()[1:]:
                    a, b = item.split("=")
                    rec[a] = float(b) if a == "seconds" else int(b)
            elif ln.startswith("F"):
                rec["cover"] = [int(x) for x in ln.split()[1:]]
        rec["returncode"] = r.returncode
        if r.stderr:
            rec["stderr"] = r.stderr[-500:]
    except subprocess.TimeoutExpired:
        rec["error"] = "wall timeout"
        rec["unknown"] = 1
    rec["wall_seconds"] = round(time.time() - t0, 2)
    if rec.get("tau"):
        rec["status"] = "le"
    elif rec.get("unknown") == 0 and rec.get("none_upto") == maxsize:
        rec["status"] = "gt"
    else:
        rec["status"] = "unknown"
    return rec


def verify_cover(k, p, cover):
    """independent check of a tau certificate: it covers every folded time and
    every class has a private time"""
    n = (p - 1) // 2
    sets = []
    for v in cover:
        s = set()
        for a in range(1, n + 1):
            x = (a * v) % p
            if (k + 1) * min(x, p - x) < p:
                s.add(a)
        sets.append(s)
    union = set().union(*sets) if sets else set()
    if union != set(range(1, n + 1)):
        return False
    for i in range(len(sets)):
        others = set().union(*(sets[j] for j in range(len(sets)) if j != i))
        if not (sets[i] - others):
            return False
    return True


def gate_one(binpath, k, p, prune, cap):
    t0 = time.time()
    try:
        r = run_bin(binpath, prune, ["gate", k, p, "2,2,2,2,2", cap, 1000000, 1, 1],
                    4 * cap + 300)
        d = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001 - recorded, never hidden
        d = {"k": k, "p": p, "prune": prune, "error": repr(e)[:300]}
    d["wall_seconds"] = round(time.time() - t0, 2)
    return d


def pmap(fn, items, workers):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def speed_ratio(s3, s7, cap):
    """seconds(prune 3) / seconds(prune 7); a run that hits the cap counts as
    the cap (so the ratio is a bound in the direction of the run that finished)"""
    if s3 is None and s7 is None:
        return None
    a = cap if s3 is None else s3
    b = cap if s7 is None else s7
    return round(a / max(b, 0.001), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = os.path.join(a.out_dir, "lrc")
    build(binpath)
    with open(os.path.join(a.out_dir, "sha256.txt"), "w") as f:
        for name in ("lrc.c", "job_orbit.py", "test_orbit.py"):
            with open(os.path.join(HERE, name), "rb") as g:
                f.write(f"{hashlib.sha256(g.read()).hexdigest()}  {name}\n")
    t_start = time.time()
    lock = threading.Lock()

    def log(path, rec):
        with lock:
            with open(os.path.join(a.out_dir, path), "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(json.dumps({x: rec.get(x) for x in ("part", "k", "p", "agree",
                                                  "seconds_prune3", "seconds_prune7",
                                                  "speedup")}), flush=True)

    xgates, tkeys, cap = XGATES, sorted(TAU_V2), CAP
    if a.quick:
        xgates, tkeys, cap = XGATES[:2], [(14, 197)], 30

    # ---- Part X ----
    def xone(kp):
        k, p = kp
        d0 = gate_one(binpath, k, p, 0, cap)
        d7 = gate_one(binpath, k, p, 7, cap)
        both = d0.get("cover_timed_out") == 0 and d7.get("cover_timed_out") == 0 \
            and not d0.get("cascade_cut") and not d7.get("cascade_cut")
        diff = [key for key in XKEYS if d0.get(key) != d7.get(key)] if both else None
        rec = {"part": "X", "k": k, "p": p, "both_finished": both,
               "agree": (not diff) if both else None, "differences": diff,
               "cover_seconds_prune0": d0.get("cover_seconds"),
               "cover_seconds_prune7": d7.get("cover_seconds"),
               "cover_nodes_prune0": d0.get("cover_nodes"),
               "cover_nodes_prune7": d7.get("cover_nodes"),
               "prune0": d0, "prune7": d7}
        log("xcheck4.jsonl", rec)
        return rec

    xres = pmap(xone, xgates, a.workers)

    # ---- Part T ----
    def tone(kp):
        k, p = kp
        ms = k - 2
        r3 = tau_one(binpath, k, p, ms, cap, 3)
        r7 = tau_one(binpath, k, p, ms, cap, 7)
        exp = TAU_V2[kp]

        def ok(r):
            if r["status"] == "unknown":
                return None
            return r["status"] == exp[0] and (exp[0] != "le" or r.get("tau") == exp[1])

        cert = verify_cover(k, p, r7["cover"]) if r7.get("cover") else None
        s3 = r3.get("seconds") if r3["status"] != "unknown" else None
        s7 = r7.get("seconds") if r7["status"] != "unknown" else None
        rec = {"part": "T", "k": k, "p": p, "expected": exp[0], "tau_expected": exp[1],
               "agree": ok(r7), "agree_prune3": ok(r3), "certificate_verified": cert,
               "seconds_prune3": s3, "seconds_prune7": s7,
               "speedup": speed_ratio(s3, s7, cap),
               "nodes_prune3": r3.get("nodes"), "nodes_prune7": r7.get("nodes"),
               "prune3": r3, "prune7": r7}
        log("speed4.jsonl", rec)
        return rec

    tres = pmap(tone, tkeys, a.workers)

    # ---- grading (PLAN_addendum8.md) ----
    xboth = [r for r in xres if r["both_finished"]]
    x_bad = [{"k": r["k"], "p": r["p"], "differences": r["differences"]}
             for r in xboth if not r["agree"]]
    t_bad = [{"k": r["k"], "p": r["p"], "expected": r["expected"],
              "got": r["prune7"]["status"], "tau": r["prune7"].get("tau")}
             for r in tres if r["agree"] is False]
    t_decided = [r for r in tres if r["agree"] is not None]
    cert_bad = [(r["k"], r["p"]) for r in tres if r["certificate_verified"] is False]
    m1_bad = bool(x_bad or t_bad or cert_bad)
    both_dec = [r for r in tres if r["seconds_prune3"] is not None
                and r["seconds_prune7"] is not None]
    fewer = [r for r in both_dec if r["nodes_prune7"] <= r["nodes_prune3"]]
    speeds = [r["speedup"] for r in tres if r["speedup"] is not None]
    med = statistics.median(speeds) if speeds else None
    summary = {
        "M1_same_answers": {"x_gates": len(xres), "x_both_finished": len(xboth),
                            "x_disagreements": x_bad,
                            "t_rows": len(tres), "t_decided_prune7": len(t_decided),
                            "t_disagreements": t_bad,
                            "certificates_failing_check": cert_bad,
                            "result": "falsified" if m1_bad else
                                      ("holds" if xboth and t_decided else "untested")},
        "M2_fewer_nodes": {"rows_both_decided": len(both_dec), "rows_fewer_or_equal": len(fewer),
                           "needed": 20,
                           "result": None if len(both_dec) < 20 else
                                     ("holds" if len(fewer) >= 20 else "falsified")},
        "S2_speedup_3_over_7": {"rows": len(speeds), "median": med, "all": speeds,
                                "result": None if med is None else
                                          ("holds" if med >= 1.5 else "falsified")},
        "cap_seconds": cap,
        "wall_minutes": round((time.time() - t_start) / 60, 1),
    }
    with open(os.path.join(a.out_dir, "summary_orbit.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
