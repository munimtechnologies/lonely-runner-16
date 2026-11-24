# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Compete job lrc16-indep-v1 (PLAN_addendum15.md): the brute-force cascade J_p(L)
for (1..15) and (1..13,15,28) at every prime from 251 upward, graded against
THEORY_18 (I1), Lemma U(i) with the lrc16-uniform-v1 lists (I2), Lemma U(ii) (I3)
and unit closure (I5).

  python indep_job.py --summary summary_uniform.json --out-dir /out --minutes 330
"""
import argparse
import json
import os
import time

import indep as I

BASES = (("e15", list(range(1, 16))), ("gw15", list(range(1, 14)) + [15, 28]))


def summarise(records, scanned, stop_reason, minutes_used):
    out = {"scanned": scanned, "stop_reason": stop_reason,
           "wall_minutes": round(minutes_used, 1), "bases": {}}
    for base, _ in BASES:
        rs = [r for r in records if r["base"] == base]
        b = {"primes": len(rs),
             "first": rs[0]["p"] if rs else None,
             "last": rs[-1]["p"] if rs else None,
             "cuts": [{"p": r["p"], "cut": r["cut"]} for r in rs if r["cut"]],
             "I2_outside_U251": [{"p": r["p"], "outside": r["I2_outside_U251"]}
                                 for r in rs if r["I2_outside_U251"]],
             "I2_untested": [{"p": r["p"], "levels": r["I2_untested_levels"]}
                             for r in rs if r["I2_untested_levels"]],
             "I5_closure_failures": [r["p"] for r in rs if not r["I5_closure_ok"]],
             "death_levels": {}}
        for r in rs:
            key = str(r["death_level"])
            b["death_levels"][key] = b["death_levels"].get(key, 0) + 1
        b["max_count_by_level"] = {}
        for r in rs:
            for L, c in r["counts"].items():
                b["max_count_by_level"][L] = max(b["max_count_by_level"].get(L, 0), c)
        if base == "e15":
            lvl1 = [r["p"] for r in rs if r["counts"].get("1") != 1]
            b["I0_level1_proper_primes"] = lvl1
            b["I3_missing_Uinf"] = [{"p": r["p"], "missing": r["I3_missing_Uinf"]}
                                    for r in rs if r.get("I3_missing_Uinf")]
            b["I3_untested"] = [r["p"] for r in rs if r.get("I3_untested_levels")]
            # counts are true counts even when the stored list is capped
            bad16 = [r["p"] for r in rs if r["counts"].get("16", 0) > 0]
            untested16 = [r["p"] for r in rs
                          if "16" not in r["counts"] and r["death_level"] is None]
            b["I1_level16_nonempty_primes"] = bad16
            b["I1_untested_primes"] = untested16
            b["I1"] = ("falsified" if bad16 else
                       ("holds where tested" if rs and len(untested16) < len(rs) else
                        "untested"))
        else:
            b["level1_improper_primes_max"] = max(
                (r["p"] for r in rs if r["counts"].get("1") == 1), default=None)
            b["level1_proper_primes_min"] = min(
                (r["p"] for r in rs if r["counts"].get("1") == 0), default=None)
            b["J32_nonempty_primes"] = [r["p"] for r in rs if r["counts"].get("32", 0) > 0]
        out["bases"][base] = b
    e = out["bases"]["e15"]
    allb = out["bases"].values()
    out["I2"] = ("falsified" if any(x["I2_outside_U251"] for x in allb) else
                 ("holds where tested" if records else "untested"))
    out["I3"] = "falsified" if e.get("I3_missing_Uinf") else (
        "holds where tested" if records else "untested")
    out["I5"] = "falsified" if any(x["I5_closure_failures"] for x in allb) else (
        "holds where tested" if records else "untested")
    out["I0_level1"] = "falsified" if e.get("I0_level1_proper_primes") else (
        "holds where tested" if records else "untested")
    out["I1"] = e.get("I1", "untested")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", default="summary_uniform.json")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--minutes", type=float, default=330)
    ap.add_argument("--pmin", type=int, default=251)
    ap.add_argument("--pmax", type=int, default=5000)
    ap.add_argument("--lmax", type=int, default=32)
    ap.add_argument("--cap", type=int, default=5000)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    exe = I.build_c(required=True)
    data = I.load_json(a.summary)
    u251 = {base: I.u_classes(data, base, 251) for base, _ in BASES}
    uinf = I.u_classes(data, "e15", None)
    records, scanned, stop = [], [], "pmax reached"
    with open(os.path.join(a.out_dir, "indep.jsonl"), "w") as fh:
        for p in I.primes_between(a.pmin, a.pmax):
            if time.time() - t0 > a.minutes * 60:
                stop = "time cap"
                break
            for base, s in BASES:
                t1 = time.time()
                levels, cut = I.run_c(exe, s, p, a.lmax, a.cap)
                rec = I.grade_prime(base, p, levels, cut, u251[base],
                                    uinf if base == "e15" else None)
                rec["seconds"] = round(time.time() - t1, 2)
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                records.append(rec)
            scanned.append(p)
            if len(scanned) % 25 == 0:
                print(f"p = {p}: {len(scanned)} primes, "
                      f"{(time.time() - t0) / 60:.1f} min", flush=True)
    summary = summarise(records, {"from": scanned[0] if scanned else None,
                                  "to": scanned[-1] if scanned else None,
                                  "n_primes": len(scanned)},
                        stop, (time.time() - t0) / 60)
    with open(os.path.join(a.out_dir, "summary_indep.json"), "w") as f:
        json.dump(summary, f, indent=1)
    short = {k: summary[k] for k in ("scanned", "stop_reason", "wall_minutes",
                                     "I0_level1", "I1", "I2", "I3", "I5")}
    short["e15_death_levels"] = summary["bases"]["e15"]["death_levels"]
    short["gw15_death_levels"] = summary["bases"]["gw15"]["death_levels"]
    print(json.dumps(short, indent=1))
    print("done")


if __name__ == "__main__":
    main()
