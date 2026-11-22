# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Engine 3 job (PLAN_addendum7.md): cross-check, speed, and the tau scans that
engine 2 could not finish.

  python job_engine3.py --out-dir /out --workers 4 [--quick]

Part X  gates of the engine-2 cross-check, cover search with LRC_PRUNE=0 and 3
        (A1: identical results wherever both finish).
Part T  tau at the primes that lrc16-tau-v2 decided in 3.5 s or more, with
        LRC_PRUNE=0 and 3 on the same machine (A2: same answers as tau-v2;
        S1: median speed-up >= 3).
Part S  k = 15, tau_15(p) <= 13 or not, at every prime that tau-v2 left
        undecided (269 ... 997), LRC_PRUNE=3, 400 s cap (P3 re-graded).
Part R  k = 14, the 47 primes of the paper's Table 2 that tau-v2 left
        undecided, LRC_PRUNE=3, 300 s cap (R1 completed).
Writes xcheck3.jsonl, speed3.jsonl, tau3_k15.jsonl, tau3_k14.jsonl,
sha256.txt and summary_engine3.json.
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
GATE_LOGSUM_K15 = 483.239
P3_FROM = 400
DEADLINE_MIN = 420

XGATES = [(8, 61), (8, 73), (9, 83), (9, 101), (10, 103), (10, 131), (11, 137),
          (11, 163), (12, 173), (12, 199), (13, 211), (14, 241)]
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
TAU_V2_K15_LE = (17, 19, 23, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
                 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
                 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 241, 251,
                 257, 263, 277)
TAU_V2_K15_GT = (29, 31, 239)


def primes_between(a, b):
    return [n for n in range(max(a, 2), b + 1)
            if all(n % d for d in range(2, int(n ** 0.5) + 1))]


S_PRIMES = [p for p in primes_between(269, 1000) if p != 277]
R_PRIMES = [p for p in primes_between(257, 569) if p not in (263, 269, 283)]


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
        for name in ("lrc.c", "job_engine3.py", "test_prune.py", "lrc_ref.py"):
            path = os.path.join(HERE, name)
            if os.path.exists(path):
                with open(path, "rb") as g:
                    f.write(f"{hashlib.sha256(g.read()).hexdigest()}  {name}\n")
    t_start = time.time()
    deadline = t_start + DEADLINE_MIN * 60
    lock = threading.Lock()

    def log(path, rec):
        with lock:
            with open(os.path.join(a.out_dir, path), "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(json.dumps({x: rec.get(x) for x in ("part", "k", "p", "prune", "status",
                                                  "tau", "seconds", "cover_seconds",
                                                  "agree")}), flush=True)

    xgates, tkeys, sprimes, rprimes = XGATES, sorted(TAU_V2), S_PRIMES, R_PRIMES
    xcap, scap, rcap = 300, 400, 300
    if a.quick:
        xgates, tkeys, sprimes, rprimes = XGATES[:2], [(14, 197)], [281], [271]
        xcap, scap, rcap = 30, 20, 20

    # ---- Part X ----
    def xone(kp):
        k, p = kp
        d0 = gate_one(binpath, k, p, 0, xcap)
        d3 = gate_one(binpath, k, p, 3, xcap)
        both = d0.get("cover_timed_out") == 0 and d3.get("cover_timed_out") == 0 \
            and not d0.get("cascade_cut") and not d3.get("cascade_cut")
        diff = [key for key in XKEYS if d0.get(key) != d3.get(key)] if both else None
        rec = {"part": "X", "k": k, "p": p, "both_finished": both,
               "agree": (not diff) if both else None, "differences": diff,
               "cover_seconds_prune0": d0.get("cover_seconds"),
               "cover_seconds_prune3": d3.get("cover_seconds"),
               "cover_nodes_prune0": d0.get("cover_nodes"),
               "cover_nodes_prune3": d3.get("cover_nodes"),
               "prune0": d0, "prune3": d3}
        log("xcheck3.jsonl", rec)
        return rec

    xres = pmap(xone, xgates, a.workers)

    # ---- Part T ----
    def tone(kp):
        k, p = kp
        ms = k - 2
        r0 = tau_one(binpath, k, p, ms, 400, 0)
        r3 = tau_one(binpath, k, p, ms, 400, 3)
        exp = TAU_V2[kp]
        ok3 = r3["status"] == exp[0] and (exp[0] != "le" or r3.get("tau") == exp[1])
        ok0 = r0["status"] == exp[0] and (exp[0] != "le" or r0.get("tau") == exp[1])
        cert = verify_cover(k, p, r3["cover"]) if r3.get("cover") else None
        s0 = r0.get("seconds") if r0["status"] != "unknown" else None
        s3 = r3.get("seconds") if r3["status"] != "unknown" else None
        if s0 is not None and s3 is not None:
            speed = s0 / max(s3, 0.001)
        elif s0 is not None:
            speed = s0 / 400.0  # prune 3 hit the cap: counted against S1
        else:
            speed = None
        rec = {"part": "T", "k": k, "p": p, "expected": exp[0], "tau_expected": exp[1],
               "tau_v2_seconds": exp[2], "agree": ok3, "agree_prune0": ok0,
               "certificate_verified": cert, "seconds_prune0": s0, "seconds_prune3": s3,
               "speedup": None if speed is None else round(speed, 3),
               "nodes_prune0": r0.get("nodes"), "nodes_prune3": r3.get("nodes"),
               "prune0": r0, "prune3": r3}
        log("speed3.jsonl", rec)
        return rec

    tres = pmap(tone, tkeys, a.workers)

    # ---- Parts S and R ----
    def scan(k, primes, maxsize, cap, path, part):
        def one(p):
            if time.time() > deadline:
                rec = {"part": part, "k": k, "p": p, "status": "skipped (deadline)"}
            else:
                rec = tau_one(binpath, k, p, maxsize, cap, 3)
                rec["part"] = part
                if rec.get("cover"):
                    rec["certificate_verified"] = verify_cover(k, p, rec["cover"])
            log(path, rec)
            return rec
        return pmap(one, primes, a.workers)

    sres = scan(15, sprimes, 13, scap, "tau3_k15.jsonl", "S")
    rres = scan(14, rprimes, 12, rcap, "tau3_k14.jsonl", "R")

    # ---- grading ----
    xboth = [r for r in xres if r["both_finished"]]
    a1_bad = [{"k": r["k"], "p": r["p"], "differences": r["differences"]}
              for r in xboth if not r["agree"]]
    t_bad = [{"k": r["k"], "p": r["p"], "expected": r["expected"],
              "got": r["prune3"]["status"], "tau": r["prune3"].get("tau")}
             for r in tres if r["prune3"]["status"] != "unknown" and not r["agree"]]
    t_unk = [(r["k"], r["p"]) for r in tres if r["prune3"]["status"] == "unknown"]
    cert_bad = [(r["k"], r["p"]) for r in tres + sres + rres
                if r.get("certificate_verified") is False]
    speeds = [r["speedup"] for r in tres if r["speedup"] is not None]
    med = statistics.median(speeds) if speeds else None

    s_le = sorted(r["p"] for r in sres if r["status"] == "le")
    s_gt = sorted(r["p"] for r in sres if r["status"] == "gt")
    s_unk = sorted(r["p"] for r in sres if r["status"] not in ("le", "gt"))
    all_le = sorted(set(TAU_V2_K15_LE) | set(s_le))
    all_gt = sorted(set(TAU_V2_K15_GT) | set(s_gt))
    acc, plan = 0.0, []
    for p in all_gt:
        if p < 100:
            continue  # p = 29, 31: m = 1, trivially tau > 13; useless as gates
        if acc > GATE_LOGSUM_K15:
            break
        acc += math.log(p)
        plan.append(p)
    p3_le = [p for p in s_le if p >= P3_FROM]
    p3_unk = [p for p in s_unk if p >= P3_FROM]
    p3_tested = len([p for p in s_le + s_gt if p >= P3_FROM])
    tau_hist = {}
    for r in sres:
        if r["status"] == "le":
            tau_hist[str(r["tau"])] = tau_hist.get(str(r["tau"]), 0) + 1

    r_agree = [r["p"] for r in rres if r["status"] == "gt"]
    r_dis = [{"p": r["p"], "tau": r.get("tau"), "cover": r.get("cover")}
             for r in rres if r["status"] == "le"]
    r_unk = [r["p"] for r in rres if r["status"] not in ("le", "gt")]
    # tau-v2 already agreed at 24 primes (19 'le' + 239, 251, 263, 269, 283)
    r1_agree_total = 24 + len(r_agree)

    summary = {
        "A1_crosscheck": {"gates": len(xres), "both_finished": len(xboth),
                          "disagreements": a1_bad,
                          "result": "holds" if xboth and not a1_bad else
                                    ("falsified" if a1_bad else "untested")},
        "A2_consistency_with_tau_v2": {"rows": len(tres), "disagreements": t_bad,
                                       "prune3_unknown": t_unk,
                                       "result": "falsified" if t_bad else
                                                 ("holds" if not t_unk else "holds where decided")},
        "certificates_failing_independent_check": cert_bad,
        "S1_speedup": {"rows_with_speedup": len(speeds), "median": med,
                       "all": speeds,
                       "result": None if med is None else ("holds" if med >= 3 else "falsified")},
        "part_S_k15": {"primes": len(sres), "tau_le_13": s_le, "tau_ge_14": s_gt,
                       "unknown": s_unk, "tau_histogram_le_13": tau_hist,
                       "largest_prime_with_tau_le_13_all_runs": max(all_le) if all_le else None,
                       "all_tau_ge_14_primes_all_runs": all_gt,
                       "gate_plan_tau_ge_14_from_100": {"primes": plan, "count": len(plan),
                                                        "logsum": round(acc, 4),
                                                        "reaches_483_239": acc > GATE_LOGSUM_K15}},
        "P3": {"statement": f"every prime p in [{P3_FROM}, 1000] has tau_15(p) >= 14",
               "counterexamples": p3_le, "decided": p3_tested, "untested": p3_unk,
               "result": ("falsified" if p3_le else
                          "untested" if p3_tested == 0 else
                          "holds" if not p3_unk else "holds where tested")},
        "R1_k14_table": {"new_primes": len(rres), "new_agree": len(r_agree),
                         "disagree": r_dis, "unknown": r_unk,
                         "agree_total_of_71": r1_agree_total,
                         "result": ("falsified" if r_dis else
                                    "holds" if not r_unk else "partly untested")},
        "caps_seconds": {"x": xcap, "t": 400, "s": scap, "r": rcap},
        "wall_minutes": round((time.time() - t_start) / 60, 1),
    }
    with open(os.path.join(a.out_dir, "summary_engine3.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
