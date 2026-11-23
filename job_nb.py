# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc-nb (THEORY_16.md, PLAN_addendum10.md): the tight orbits of the 14- and
15-runner proofs at their non-binary levels, uniformly in the prime.

For a14 = (1..14) at level 15 = 3*5 and a13 = (1..13), b13 = (1..11,13,24) at
level 14 = 2*7:
  1. U_inf and U_P0 at the two factor levels and at L, computed twice: by the
     chain f1 -> f1*f2 (branch and bound) and by the CRT combination of the two
     factor levels (check C1: both must agree when both finish);
  2. the same without the gcd clause (informational; check S7);
  3. thresholds P*(z) for every z in U_P0(L), P*_L, and the exact set J_p(L) at
     every prime p from P0 to B (B >= 3000, raised to cover P*_L, at most 20000);
  4. sanity checks S2 (linear lifts), S3 (U_inf <= U_P0), S4 (U_P0 members are
     open and not P0-killed), S5 (parents of improper lifts are improper), S7.

  python job_nb.py --out-dir /out [--only a14] [--minutes 80]
"""
import argparse
import json
import math
import os
import platform
import sys
import time
from fractions import Fraction

import thresh as T
import uniform_nb as N

BASES = {
    "a14": (tuple(range(1, 15)), 14, (3, 5), 239, 80),
    "a13": (tuple(range(1, 14)), 13, (2, 7), 199, 35),
    "b13": (tuple(list(range(1, 12)) + [13, 24]), 13, (2, 7), 199, 35),
}
# the paper's gate primes (arXiv:2609.02604): k = 14 tau >= 13 block, k = 13 P_13
PAPER_PRIMES = {
    14: [p for p in T.primes_between(239, 569) if p != 241],
    13: [83, 139, 167, 181, 191] + T.primes_between(199, 479)
        + [487, 491, 499, 503, 509, 521, 523, 541, 547],
}
B_MIN, B_MAX = 3000, 20000
LIST_CAP = 2000


def fstr(x):
    return "inf" if x is None else str(x)


def lst(S):
    S = sorted(S)
    return [list(z) for z in S[:LIST_CAP]]


def run_mode(s, k, f1, f2, P, g, minutes, base_deadline):
    """U at f1, f2 and L = f1 f2 for one (P, gcd) setting"""
    L = f1 * f2
    clock = time.time
    out = {"P": P, "use_gcd": g}

    def dl(share):
        return min(base_deadline, clock() + 60 * minutes * share)

    t0 = clock()
    r1 = N.cascade_chain(s, k, [f1, f2], P, use_gcd=g, deadline=dl(0.45), clock=clock)
    out["chain_seconds"] = round(clock() - t0, 1)
    out["chain_cut"] = r1["cut"]
    set_f1 = N.last_set(r1, f1)
    set_L_chain = N.last_set(r1, L)
    t0 = clock()
    r2 = N.cascade_chain(s, k, [f2], P, use_gcd=g, deadline=dl(0.3), clock=clock)
    set_f2 = N.last_set(r2, f2)
    out["f2_seconds"] = round(clock() - t0, 1)
    out["f2_cut"] = r2["cut"]
    set_L_comb = None
    if set_f1 is not None and set_f2 is not None:
        t0 = clock()
        comb, tested, cut = N.combine(s, k, f1, set_f1, f2, set_f2, P, use_gcd=g,
                                      deadline=dl(0.25), clock=clock)
        out["combine_seconds"] = round(clock() - t0, 1)
        out["combine_tested"] = tested
        out["combine_cut"] = cut
        if not cut:
            set_L_comb = comb
    out["sizes"] = {str(f1): None if set_f1 is None else len(set_f1),
                    str(f2): None if set_f2 is None else len(set_f2),
                    "L_chain": None if set_L_chain is None else len(set_L_chain),
                    "L_combine": None if set_L_comb is None else len(set_L_comb)}
    out["C1_agree"] = (None if set_L_chain is None or set_L_comb is None
                       else set_L_chain == set_L_comb)
    set_L = set_L_chain if set_L_chain is not None else set_L_comb
    out["L_size"] = None if set_L is None else len(set_L)
    out["L_list"] = None if set_L is None else lst(set_L)
    out["f1_list"] = None if set_f1 is None else lst(set_f1)
    out["f2_list"] = None if set_f2 is None else lst(set_f2)
    return out, set_f1, set_f2, set_L


def run_base(name, s, k, f1, f2, P0, minutes):
    L = f1 * f2
    t_start = time.time()
    base_deadline = t_start + 60 * minutes
    out = {"base": name, "s": list(s), "k": k, "factors": [f1, f2], "L": L, "P0": P0,
           "minutes": minutes}
    modes = {}
    sets = {}
    for tag, P, g, share in (("inf", None, True, 0.3), ("P0", P0, True, 0.4),
                             ("inf_nogcd", None, False, 0.1), ("P0_nogcd", P0, False, 0.1)):
        if time.time() > base_deadline:
            modes[tag] = {"skipped": "base deadline"}
            sets[tag] = (None, None, None)
            continue
        m, a, b, c = run_mode(s, k, f1, f2, P, g, minutes * share, base_deadline)
        modes[tag] = m
        sets[tag] = (a, b, c)
        brief = {x: m.get(x) for x in ("sizes", "C1_agree", "chain_cut", "f2_cut", "combine_cut",
                                       "chain_seconds")}
        print(json.dumps({"base": name, "mode": tag, **brief}), flush=True)
        # the gcd-free modes are informational: compute them only after the main ones
    out["modes"] = modes

    # S2: linear lifts (THEORY.md 8.5 / Lemma L at levels f1, f2, L)
    ui = sets["inf"]
    lin = {X: N.canon(tuple(x % X for x in s), X) for X in (f1, f2, L)}
    out["S2"] = {
        "linear_in_U_inf_f1": None if ui[0] is None else lin[f1] in ui[0],
        "linear_in_U_inf_f2": None if ui[1] is None else lin[f2] in ui[1],
        "linear_not_in_U_inf_L": None if ui[2] is None else lin[L] not in ui[2],
        "linear_L_status": N.lift_info(s, k, lin[L], L).status,
    }
    # S3: U_inf <= U_P0
    up = sets["P0"]
    s3 = {}
    for i, X in enumerate((f1, f2, L)):
        if ui[i] is not None and up[i] is not None:
            s3[str(X)] = sorted(map(list, ui[i] - up[i]))[:20]
    out["S3_violations"] = s3
    # S7: with-gcd set = gcd-free set minus the gcd clause
    s7 = {}
    for a_tag, b_tag in (("inf", "inf_nogcd"), ("P0", "P0_nogcd")):
        A, B_ = sets[a_tag][2], sets[b_tag][2]
        if A is not None and B_ is not None:
            want = {z for z in B_ if not N.gcd_clause(z, L)}
            s7[a_tag] = {"agree": A == want, "gcd_clause_members_of_free_set": len(B_) - len(want)}
    out["S7"] = s7

    # thresholds and the exact per-prime cascade at level L
    U_L = up[2]
    if U_L is None:
        out["statement"] = {"holds": False, "reason": "U_P0(L) not computed (cut)"}
        out["seconds"] = round(time.time() - t_start, 1)
        return out
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
    rows = []
    s5 = []
    scanned_to = None
    sub_cache = {}

    def sub_info(z, X):
        key = (X, N.canon(tuple(x % X for x in z), X))
        if key not in sub_cache:
            sub_cache[key] = N.lift_info(s, k, key[1], X)
        return sub_cache[key]

    # informational: gcd-free witness-free classes at the paper's gate primes
    free_L = sets["P0_nogcd"][2]
    free_infos = None
    if free_L is not None and len(free_L) <= 5000:
        free_infos = [N.lift_info(s, k, z, L, use_gcd=False) for z in sorted(free_L)]
    out["I1_computed"] = free_infos is not None
    paper = set(PAPER_PRIMES.get(k, []))
    scan_deadline = t_start + 60 * minutes + 60 * 15
    for p in T.primes_between(P0, B):
        if time.time() > scan_deadline:
            break
        if infos and infos[0].Q % p == 0 or any(x % p == 0 for x in s):
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
        if p in paper and free_infos is not None:
            wf = [i.z for i in free_infos if not T.proper_at(i, p)]
            row["witness_free_classes"] = len(wf)
            row["witness_free_failing_gcd"] = sum(1 for z in wf if not N.gcd_clause(z, L))
        rows.append(row)
        scanned_to = p
    out["primes"] = rows
    out["scanned_to"] = scanned_to
    scanned = [r for r in rows if "skipped" not in r]
    out["n_primes"] = len(scanned)
    out["primes_with_J_L_nonempty"] = [r["p"] for r in scanned if r["J_L"]]
    out["S5_violations"] = s5[:50]
    out["S5_count"] = len(s5)
    covered = (pstar is not None and scanned_to is not None and pstar <= scanned_to)
    # U_L is complete here (chain or combination finished without a cut)
    holds = covered and not out["primes_with_J_L_nonempty"] and scanned_to is not None
    out["statement"] = {"holds": bool(holds)}
    if holds:
        out["statement"]["text"] = (
            "for every prime p >= %d not dividing Q, every lift of the orbit of %s to level %d "
            "is proper (primes %d..%d checked one by one; above %d by P*_%d = %s)"
            % (P0, name, L, P0, scanned_to, scanned_to, L, fstr(pstar)))
    out["seconds"] = round(time.time() - t_start, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--only", default="")
    ap.add_argument("--minutes", type=float, default=None, help="override every base's budget")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"job": "lrc-nb", "python": sys.version, "machine": platform.machine(),
               "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}
    path = os.path.join(a.out_dir, "summary_nb.json")
    for name, (s, k, (f1, f2), P0, minutes) in BASES.items():
        if a.only and name not in a.only.split(","):
            continue
        row = run_base(name, s, k, f1, f2, P0, a.minutes if a.minutes else minutes)
        summary["runs"].append(row)
        brief = {x: row.get(x) for x in ("base", "L", "P0", "P_star_L", "scan_bound", "scanned_to",
                                         "n_primes", "primes_with_J_L_nonempty", "S2",
                                         "S3_violations", "S4", "S5_count", "S7", "statement",
                                         "seconds")}
        brief["sizes"] = {t: m.get("sizes") for t, m in row["modes"].items()}
        brief["C1"] = {t: m.get("C1_agree") for t, m in row["modes"].items()}
        print(json.dumps(brief), flush=True)
        with open(path, "w") as f:
            json.dump(summary, f, indent=1)
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(path, "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
