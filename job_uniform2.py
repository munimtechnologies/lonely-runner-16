# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc16-uniform-v2: from the uniform cascade U_251 to an exact answer at
every prime (THEORY_15.md, PLAN_addendum9.md).

For s = (1..15) and s = (1..13,15,28):
  1. U_251(L) for L = 1, 2, ..., 128 (uniform.cascade, as in lrc16-uniform-v1,
     two more levels) and U_inf(L) up to L = 32;
  2. for every listed lift z its kill threshold P*(z) (exact fraction) and, per
     level, P*_L = max P*(z): for every prime p > max(P*_L, 250), J_p(L) is empty;
  3. for every prime p from 251 to B (B >= 3000, raised up to 20000 so that it
     reaches P*_128 when that is finite), the exact sets J_p(L) and the level at
     which the orbit dies at p;
  4. sanity checks S4, S5, S6, S2 (failure of any one means a bug).

  python job_uniform2.py --out-dir /out
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
import uniform as U

BASES = {
    "e15": (tuple(range(1, 16)), 15),
    "gw15": (tuple(list(range(1, 14)) + [15, 28]), 15),
}
P0 = 251
NLEVELS = 7          # levels 2 .. 128
NLEVELS_INF = 5      # U_inf levels 2 .. 32 (for S5)
PILOT = [251, 283, 307, 353, 401, 449, 503, 601, 701, 809]
B_MIN, B_MAX = 3000, 20000


def fstr(x):
    if x is None:
        return "inf"
    return str(x)


def run_base(name, s, k, minutes):
    t_start = time.time()
    deadline = t_start + 60 * minutes
    out = {"base": name, "s": list(s), "k": k, "P0": P0}
    levels, cut = T.level_infos(s, k, NLEVELS, P0, max_parents=3000,
                                deadline=t_start + 60 * min(30, minutes / 3), clock=time.time)
    out["cut"] = cut
    out["levels_reached"] = [L for L, _ in levels]
    out["U_seconds"] = round(time.time() - t_start, 1)

    # S4: nothing listed in U_251 is killed at P0 by the threshold rule
    s4 = [[L, list(inf.z)] for L, infos in levels for inf in infos if T.killed_uniform(inf, P0)]
    # S5: U_inf(L) == {z in U_251(L): threshold None}
    linf, cutinf = T.level_infos(s, k, NLEVELS_INF, None, max_parents=3000)
    inf_sets = {L: {i.z for i in infos} for L, infos in linf}
    s5 = []
    for L, infos in levels:
        if L > 2 ** NLEVELS_INF or cutinf is not None:
            continue
        mine = {i.z for i in infos if T.threshold(i) is None}
        if mine != inf_sets.get(L, set()):
            s5.append([L, sorted(map(list, mine ^ inf_sets.get(L, set())))])
    out["U_inf_sizes"] = [[L, len(v)] for L, v in sorted(inf_sets.items())]
    out["U_inf_cut"] = cutinf

    # thresholds
    lev_rows = []
    pstar = {}
    for L, infos in levels:
        thr = [T.threshold(i) for i in infos]
        if not infos:
            ps = Fraction(0)
        elif any(t is None for t in thr):
            ps = None
        else:
            ps = max(thr)
        pstar[L] = ps
        lev_rows.append({"level": L, "size": len(infos), "P_star": fstr(ps),
                         "P_star_float": None if ps is None else float(ps),
                         "lifts": [i.as_dict() for i in infos]})
    out["levels"] = lev_rows
    Lmax = levels[-1][0]
    p_last = pstar[Lmax]
    if p_last is None:
        B = B_MIN
    else:
        B = max(B_MIN, min(B_MAX, math.floor(p_last) + 1))
    out["scan_bound"] = B

    # per-prime exact cascade
    rows = []
    s2 = 0
    s6 = []
    scanned_to = None
    all_infos = [(L, i) for L, infos in levels for i in infos]
    for p in T.primes_between(P0, B):
        if time.time() > deadline:
            break
        if any(math.gcd(p, x) != 1 for x in s) or any(i.Q % p == 0 for _, i in all_infos):
            rows.append({"p": p, "skipped": "p divides Q or a speed"})
            continue
        sets = {}
        for L, infos in levels:
            st = set()
            for i in infos:
                pr = T.proper_at(i, p)
                thr = T.threshold(i)
                if thr is not None and thr != 0 and p > thr and not pr:
                    s2 += 1
                if not pr:
                    st.add(i.z)
            sets[L] = st
        # S6: every improper lift has an improper parent
        for L, _ in levels:
            if L < 2:
                continue
            for z in sets[L]:
                par = U.canon(tuple(x % (L // 2) for x in z), L // 2)
                if par not in sets.get(L // 2, set()):
                    s6.append([p, L, list(z)])
        sizes = [[L, len(sets[L])] for L, _ in levels]
        death = None
        for L, n in sizes:
            if n == 0:
                death = L
                break
        row = {"p": p, "sizes": sizes, "death_level": death}
        if death is None:
            row["survivors_at_last_level"] = [list(z) for z in sorted(sets[Lmax])]
        rows.append(row)
        scanned_to = p
    out["scanned_to"] = scanned_to
    out["primes"] = rows
    scanned = [r for r in rows if "skipped" not in r]
    deaths = [r["death_level"] for r in scanned]
    out["n_primes"] = len(scanned)
    out["n_persist_to_last_level"] = sum(1 for d in deaths if d is None)
    out["max_death_level"] = (None if any(d is None for d in deaths) or not deaths
                              else max(deaths))
    hist = {}
    for d in deaths:
        hist[str(d)] = hist.get(str(d), 0) + 1
    out["death_level_histogram"] = hist
    out["pilot"] = [{"p": r["p"], "J16": dict((L, n) for L, n in r["sizes"]).get(16, 0),
                     "death_level": r["death_level"]} for r in scanned if r["p"] in PILOT]
    # uniform statement (PLAN_addendum9 T2)
    L_unif = None
    for L, _ in levels:
        ps = pstar[L]
        if ps is not None and (scanned_to is not None and ps <= scanned_to):
            L_unif = L
            break
    out["L_uniform"] = L_unif
    if (cut is None and L_unif is not None and out["max_death_level"] is not None
            and scanned_to is not None and scanned_to >= B_MIN):
        out["statement"] = {
            "holds": True,
            "text": ("for every prime p >= %d, J_p(%d) is empty for the orbit of %s "
                     "(primes %d..%d checked one by one; above %d by P*_%d = %s)")
            % (P0, max(L_unif, out["max_death_level"]), name, P0, scanned_to, scanned_to,
               L_unif, fstr(pstar[L_unif])),
            "level": max(L_unif, out["max_death_level"])}
    else:
        out["statement"] = {"holds": False}
    out["sanity"] = {"S2_violations": s2, "S4": s4, "S5": s5, "S6": s6[:50],
                     "S6_count": len(s6)}
    out["seconds"] = round(time.time() - t_start, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--only", default="")
    ap.add_argument("--minutes", type=float, default=45)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    summary = {"job": "lrc16-uniform-v2", "python": sys.version, "machine": platform.machine(),
               "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}
    path = os.path.join(a.out_dir, "summary_uniform2.json")
    for name, (s, k) in BASES.items():
        if a.only and name not in a.only.split(","):
            continue
        row = run_base(name, s, k, a.minutes)
        summary["runs"].append(row)
        brief = {x: row[x] for x in ("base", "cut", "levels_reached", "scan_bound", "scanned_to",
                                     "n_primes", "n_persist_to_last_level", "max_death_level",
                                     "death_level_histogram", "L_uniform", "statement",
                                     "pilot", "seconds")}
        brief["P_star"] = [[r["level"], r["size"], r["P_star"]] for r in row["levels"]]
        brief["sanity"] = {kk: (len(v) if isinstance(v, list) else v)
                           for kk, v in row["sanity"].items()}
        print(json.dumps(brief), flush=True)
        with open(path, "w") as f:
            json.dump(summary, f, indent=1)
    summary["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(path, "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
