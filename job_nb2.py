# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc-nb2 (THEORY_17.md, PLAN_addendum11.md): job lrc-nb again, with the C
engine nbc.c, the unit-symmetry reduction, and the cheap lifting order first.

For a14 = (1..14) at level 15 = 3*5 and a13 = (1..13), b13 = (1..11,13,24) at
level 14 = 2*7, in this order of priority:

Phase 1 (with the gcd clause; P = inf, then P = P0):
  U at f1 and at f2 (lifted from level 1), then route B: U(L) by lifting the
  level-f2 set by f1 (5 -> 15 for a14, 7 -> 14 for a13 and b13).
  Then the thresholds P*(z) on U_P0(L) and the exact sets J_p(L) at every prime
  from P0 to B (B >= 3000, raised to cover P*_L, at most 20,000).
Phase 2 (cross-checks, while time is left):
  route A: U(L) by lifting the level-f1 set by f2; route C: uniform_nb.combine.
  C1: every route that finishes gives the same set.
  The gcd-free modes (S7, I1, I2).

The three bases run in parallel worker processes (--workers).  Each base writes
/out/base_<name>.json after each phase; summary_nb2.json collects them.

  python job_nb2.py --out-dir /out --workers 3
"""
import argparse
import json
import math
import os
import platform
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

import nbc
import thresh as T
import uniform_nb as N

BASES = {
    "a14": (tuple(range(1, 15)), 14, (3, 5), 239),
    "a13": (tuple(range(1, 14)), 13, (2, 7), 199),
    "b13": (tuple(list(range(1, 12)) + [13, 24]), 13, (2, 7), 199),
}
# the paper's gate primes (arXiv:2609.02604): k = 14 tau >= 13 block, k = 13 P_13
PAPER_PRIMES = {
    14: [p for p in T.primes_between(239, 569) if p != 241],
    13: [83, 139, 167, 181, 191] + T.primes_between(199, 479)
        + [487, 491, 499, 503, 509, 521, 523, 541, 547],
}
B_MIN, B_MAX = 3000, 20000
LIST_CAP = 2000
# seconds per step (each step also stops at the job deadline)
CAPS_MAIN = {"inf": {"f1": 900, "f2": 1800, "B": 1800},
             "P0": {"f1": 900, "f2": 3600, "B": 3600}}
CAPS_X = {"A": 3600, "comb": 900}
CAPS_FREE = {"f1": 600, "f2": 1200, "B": 1200}
SCAN_SECONDS = 900
JOB_MINUTES = 390

BIN = None
JOB_DEADLINE = None


def fstr(x):
    return "inf" if x is None else str(x)


def lst(S):
    return None if S is None else [list(z) for z in sorted(S)[:LIST_CAP]]


def size(S):
    return None if S is None else len(S)


def step(s, k, parents, L, c, P, g, cap):
    deadline = min(JOB_DEADLINE, time.time() + cap)
    S, st = nbc.lift_set(s, k, parents, L, c, P, g, engine="c", binpath=BIN, deadline=deadline)
    return S, st


def factor_sets(s, k, f1, f2, P, g, caps):
    """U at f1 and f2 from level 1; route B (f2 -> L)"""
    out = {"P": P, "use_gcd": g}
    zero = tuple(0 for _ in s)
    if N.base_killed(s, k, P):
        out["base_killed"] = True
        e = set()
        return out, e, e, e
    S1, st1 = step(s, k, [zero], 1, f1, P, g, caps["f1"])
    S2, st2 = step(s, k, [zero], 1, f2, P, g, caps["f2"])
    out["f1_stats"], out["f2_stats"] = st1, st2
    LB = None
    if S2 is not None:
        LB, stB = step(s, k, sorted(S2), f2, f1, P, g, caps["B"])
        out["B_stats"] = stB
    out["sizes"] = {"f1": size(S1), "f2": size(S2), "L_B": size(LB)}
    out["f1_list"], out["f2_list"], out["L_B_list"] = lst(S1), lst(S2), lst(LB)
    return out, S1, S2, LB


def cross(s, k, f1, f2, P, g, S1, S2, LB):
    """route A (f1 -> L) and route C (combine); C1"""
    out = {}
    LA = None
    if S1 is not None:
        LA, stA = step(s, k, sorted(S1), f1, f2, P, g, CAPS_X["A"])
        out["A_stats"] = stA
    LC = None
    if S1 is not None and S2 is not None:
        t0 = time.time()
        dl = min(JOB_DEADLINE, t0 + CAPS_X["comb"])
        comb, tested, cut = N.combine(s, k, f1, S1, f2, S2, P, use_gcd=g, deadline=dl,
                                      clock=time.time)
        out["C_stats"] = {"tested": tested, "cut": cut, "seconds": round(time.time() - t0, 1)}
        if not cut:
            LC = comb
    out["sizes"] = {"L_A": size(LA), "L_C": size(LC)}
    done = [x for x in (LB, LA, LC) if x is not None]
    out["routes_finished"] = [n for n, x in (("B", LB), ("A", LA), ("C", LC)) if x is not None]
    out["C1_agree"] = None if len(done) < 2 else all(x == done[0] for x in done)
    if LB is None and LA is not None:
        out["L_A_list"] = lst(LA)
    return out, LA, LC


def scan(s, k, f1, f2, P0, U_L, out):
    L = f1 * f2
    infos = [N.lift_info(s, k, z, L) for z in sorted(U_L)]
    out["S4"] = [list(i.z) for i in infos if i.status != "open" or T.killed_uniform(i, P0)][:20]
    thr = [T.threshold(i) for i in infos]
    if not infos:
        pstar = Fraction(0)
    elif any(t is None for t in thr):
        pstar = None
    else:
        pstar = max(thr)
    out["P_star_L"] = fstr(pstar)
    out["P_star_L_float"] = None if pstar is None else float(pstar)
    out["thresholds"] = [{"z": list(i.z), "threshold": fstr(t),
                          "threshold_float": None if t is None else float(t)}
                         for i, t in zip(infos, thr)][:LIST_CAP]
    B = B_MIN if pstar is None else max(B_MIN, min(B_MAX, math.floor(pstar) + 1))
    out["scan_bound"] = B
    rows, s5 = [], []
    scanned_to = None
    sub_cache = {}

    def sub_info(z, X):
        key = (X, N.canon(tuple(x % X for x in z), X))
        if key not in sub_cache:
            sub_cache[key] = N.lift_info(s, k, key[1], X)
        return sub_cache[key]

    t_end = time.time() + SCAN_SECONDS
    for p in T.primes_between(P0, B):
        if time.time() > t_end:
            break
        if (infos and infos[0].Q % p == 0) or any(x % p == 0 for x in s):
            rows.append({"p": p, "skipped": "p divides Q or a speed"})
            continue
        J = [i.z for i in infos if not T.proper_at(i, p)]
        for z in J:
            for X in (f1, f2):
                if T.proper_at(sub_info(z, X), p):
                    s5.append([p, X, list(z)])
        row = {"p": p, "J_L": len(J)}
        if J:
            row["J_L_list"] = [list(z) for z in J[:50]]
        rows.append(row)
        scanned_to = p
    out["primes"] = rows
    out["scanned_to"] = scanned_to
    scanned = [r for r in rows if "skipped" not in r]
    out["n_primes"] = len(scanned)
    out["primes_with_J_L_nonempty"] = [r["p"] for r in scanned if r["J_L"]]
    paper = PAPER_PRIMES.get(k, [])
    out["X1_paper_primes_scanned"] = [r["p"] for r in scanned if r["p"] in paper]
    out["X1_paper_primes_with_J_L_nonempty"] = [r["p"] for r in scanned if r["p"] in paper and r["J_L"]]
    out["S5_violations"] = s5[:50]
    out["S5_count"] = len(s5)
    covered = pstar is not None and scanned_to is not None and pstar <= scanned_to
    holds = covered and not out["primes_with_J_L_nonempty"]
    out["statement"] = {"holds": bool(holds)}
    if holds:
        out["statement"]["text"] = (
            "for every prime p >= %d, every lift of the orbit of %s to level %d is proper "
            "(primes %d..%d checked one by one; above %d by P*_%d = %s)"
            % (P0, list(s), L, P0, scanned_to, scanned_to, L, fstr(pstar)))
    elif not covered:
        out["statement"]["reason"] = "P*_L not covered by the scan (P*_L = %s, scanned to %s)" % (
            fstr(pstar), scanned_to)
    else:
        out["statement"]["reason"] = "J_p(L) non-empty at some scanned prime"


def write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def run_base(args):
    name, out_dir, binpath, job_deadline = args
    global BIN, JOB_DEADLINE
    BIN, JOB_DEADLINE = binpath, job_deadline
    s, k, (f1, f2), P0 = BASES[name]
    L = f1 * f2
    t_start = time.time()
    path = os.path.join(out_dir, "base_%s.json" % name)
    out = {"base": name, "s": list(s), "k": k, "factors": [f1, f2], "L": L, "P0": P0,
           "phase": 1, "modes": {}}
    sets = {}
    for tag, P in (("inf", None), ("P0", P0)):
        m, S1, S2, LB = factor_sets(s, k, f1, f2, P, True, CAPS_MAIN[tag])
        out["modes"][tag] = m
        sets[tag] = [S1, S2, LB]
        print(json.dumps({"base": name, "mode": tag, "sizes": m.get("sizes"),
                          "f1": m.get("f1_stats"), "f2": m.get("f2_stats"),
                          "B": m.get("B_stats")}), flush=True)
        write(path, out)
    ui, up = sets["inf"], sets["P0"]
    lin = {X: N.canon(tuple(x % X for x in s), X) for X in (f1, f2, L)}
    out["S2"] = {
        "linear_in_U_inf_f1": None if ui[0] is None else lin[f1] in ui[0],
        "linear_in_U_inf_f2": None if ui[1] is None else lin[f2] in ui[1],
        "linear_not_in_U_inf_L": None if ui[2] is None else lin[L] not in ui[2],
        "linear_L_status": N.lift_info(s, k, lin[L], L).status,
    }
    out["S3_violations"] = {str(X): sorted(map(list, ui[i] - up[i]))[:20]
                            for i, X in enumerate((f1, f2, L))
                            if ui[i] is not None and up[i] is not None}
    out["N_inf_L_empty"] = None if ui[2] is None else len(ui[2]) == 0
    if up[2] is None:
        out["statement"] = {"holds": False, "reason": "U_P0(L) not computed (cut)"}
    else:
        scan(s, k, f1, f2, P0, up[2], out)
    out["phase1_seconds"] = round(time.time() - t_start, 1)
    print(json.dumps({"base": name, "phase1": True, "N_inf_L_empty": out["N_inf_L_empty"],
                      "statement": out["statement"], "P_star_L": out.get("P_star_L"),
                      "scanned_to": out.get("scanned_to")}), flush=True)
    write(path, out)

    # phase 2: cross-checks, then the gcd-free modes
    out["phase"] = 2
    out["cross"] = {}
    for tag, P in (("inf", None), ("P0", P0)):
        if time.time() > JOB_DEADLINE:
            out["cross"][tag] = {"skipped": "job deadline"}
            continue
        S1, S2, LB = sets[tag]
        x, LA, LC = cross(s, k, f1, f2, P, True, S1, S2, LB)
        out["cross"][tag] = x
        if sets[tag][2] is None:
            sets[tag][2] = LA if LA is not None else LC
        print(json.dumps({"base": name, "cross": tag, "sizes": x["sizes"],
                          "C1_agree": x["C1_agree"]}), flush=True)
        write(path, out)
    # if phase 1 had no U_P0(L) but a cross route found it, scan now
    if "P_star_L" not in out and sets["P0"][2] is not None:
        scan(s, k, f1, f2, P0, sets["P0"][2], out)
        out["statement"]["via"] = "phase-2 route"
    if out["N_inf_L_empty"] is None and sets["inf"][2] is not None:
        out["N_inf_L_empty"] = len(sets["inf"][2]) == 0
    free = {}
    for tag, P in (("inf_nogcd", None), ("P0_nogcd", P0)):
        if time.time() > JOB_DEADLINE:
            out["modes"][tag] = {"skipped": "job deadline"}
            continue
        m, S1, S2, LB = factor_sets(s, k, f1, f2, P, False, CAPS_FREE)
        out["modes"][tag] = m
        free[tag] = LB
        write(path, out)
    s7 = {}
    for a_tag, b_tag in (("inf", "inf_nogcd"), ("P0", "P0_nogcd")):
        A, B_ = sets[a_tag][2], free.get(b_tag)
        if A is not None and B_ is not None:
            want = {z for z in B_ if not N.gcd_clause(z, L)}
            s7[a_tag] = {"agree": A == want, "gcd_clause_members_of_free_set": len(B_) - len(want)}
    out["S7"] = s7
    fi = free.get("inf_nogcd")
    if fi is not None and k == 13:
        out["I2_all_divisible_by_7"] = all(all(x % 7 == 0 for x in z) for z in fi)
    fp = free.get("P0_nogcd")
    if fp is not None and len(fp) <= 20000:
        infos = [N.lift_info(s, k, z, L, use_gcd=False) for z in sorted(fp)]
        rows = []
        for p in PAPER_PRIMES.get(k, []):
            if p < P0:
                continue
            wf = [i.z for i in infos if not T.proper_at(i, p)]
            rows.append({"p": p, "witness_free_classes": len(wf),
                         "witness_free_failing_gcd": sum(1 for z in wf if not N.gcd_clause(z, L))})
        out["I1"] = rows
    out["seconds"] = round(time.time() - t_start, 1)
    write(path, out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", default="")
    ap.add_argument("--minutes", type=float, default=JOB_MINUTES)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = nbc.build()
    if binpath is None:
        sys.exit("no C compiler: this job needs cc")
    t0 = time.time()
    deadline = t0 + 60 * a.minutes
    names = [n for n in BASES if not a.only or n in a.only.split(",")]
    summary = {"job": "lrc-nb2", "python": sys.version, "machine": platform.machine(),
               "cpu_count": os.cpu_count(), "workers": a.workers,
               "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}
    path = os.path.join(a.out_dir, "summary_nb2.json")
    write(path, summary)
    jobs = [(n, a.out_dir, binpath, deadline) for n in names]
    if a.workers > 1:
        with Pool(min(a.workers, len(jobs))) as pool:
            for row in pool.imap_unordered(run_base, jobs):
                summary["runs"].append(row)
                write(path, summary)
    else:
        for j in jobs:
            summary["runs"].append(run_base(j))
            write(path, summary)
    summary["runs"].sort(key=lambda r: names.index(r["base"]))
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write(path, summary)
    print("done", flush=True)


if __name__ == "__main__":
    main()
