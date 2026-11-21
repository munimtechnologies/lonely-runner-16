# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""tau(p) scans (PLAN.md addendum 3).

  python job_tau.py --out-dir /out --workers 4

Part R (re-check of a published table): for k = 14 (15 runners), decide for
  every prime in Table 2 of Allikvere, arXiv:2609.02604 v2, whether a cover of
  the folded times by at most 12 speed classes exists.  The paper states
  tau(p) <= 12 for its 19-prime block (89 ... 241) and tau(p) >= 13 for every
  prime from 239 to 569 except 241 (52 primes).
Part S (16 runners): for k = 15, exact tau(p) when it is <= 13, or a
  certificate that no cover on <= 13 classes exists, for every prime from 17
  to 1000.  Primes with tau(p) >= 14 can use the old gate enumeration; the
  others need the general completion (lrc.c ext = 1).
Writes tau_k14.jsonl, tau_k15.jsonl (one line per prime, as soon as it is
decided) and summary_tau.json.
"""
import argparse
import json
import math
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER_LE12 = (89, 131, 149, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211,
              223, 227, 229, 233, 241)
GATE_LOGSUM_K15 = 483.239   # THEORY.md Sec. 3 (strictly greater is needed)
P3_FROM = 400               # PLAN.md addendum 3, prediction P3
CAP14 = 300                 # seconds per prime
CAP15 = 400
DEADLINE_MIN = 420          # stop starting new primes after this many minutes


def primes_between(a, b):
    out = []
    for n in range(max(a, 2), b + 1):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            out.append(n)
    return out


PAPER_GE13 = tuple(p for p in primes_between(239, 569) if p != 241)
K15_PRIMES = tuple(primes_between(17, 1000))


def build(binpath):
    subprocess.run(["cc", "-O3", "-march=native", "-o", binpath, os.path.join(HERE, "lrc.c")],
                   check=True)


def tau_one(binpath, k, p, maxsize, cap):
    t0 = time.time()
    rec = {"k": k, "p": p, "maxsize": maxsize, "cap": cap}
    try:
        r = subprocess.run([binpath, "tau", str(k), str(p), str(maxsize), str(cap)],
                           capture_output=True, text=True, timeout=cap + 300)
        for ln in r.stdout.splitlines():
            if ln.startswith("T "):
                for kv in ln.split()[1:]:
                    a, b = kv.split("=")
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
    # status: "le" (a cover on tau <= maxsize classes was found), "gt" (none on
    # <= maxsize classes: tau > maxsize), "unknown" (time cap)
    if rec.get("tau"):
        rec["status"] = "le"
    elif rec.get("unknown") == 0 and rec.get("none_upto") == maxsize:
        rec["status"] = "gt"
    else:
        rec["status"] = "unknown"
    return rec


def run_part(binpath, k, primes, maxsize, cap, path, workers, deadline):
    lock = threading.Lock()

    def one(p):
        if time.time() > deadline:
            rec = {"k": k, "p": p, "maxsize": maxsize, "status": "skipped (deadline)"}
        else:
            rec = tau_one(binpath, k, p, maxsize, cap)
        with lock:
            with open(path, "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(json.dumps({x: rec.get(x) for x in ("k", "p", "status", "tau", "none_upto",
                                                  "seconds")}), flush=True)
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, primes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--quick", action="store_true", help="tiny smoke run")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    binpath = os.path.join(a.out_dir, "lrc")
    build(binpath)
    t_start = time.time()
    deadline = t_start + DEADLINE_MIN * 60

    p14 = sorted(set(PAPER_LE12) | set(PAPER_GE13))
    p15 = list(K15_PRIMES)
    cap14, cap15 = CAP14, CAP15
    if a.quick:
        p14, p15, cap14, cap15 = [89, 239], [17, 101], 20, 20

    r14 = run_part(binpath, 14, p14, 12, cap14, os.path.join(a.out_dir, "tau_k14.jsonl"),
                   a.workers, deadline)
    r15 = run_part(binpath, 15, p15, 13, cap15, os.path.join(a.out_dir, "tau_k15.jsonl"),
                   a.workers, deadline)

    # ---- Part R: compare with the paper's Table 2 ----
    agree, disagree, unknown = [], [], []
    for r in r14:
        p = r["p"]
        expected = "le" if p in PAPER_LE12 else "gt"
        if r["status"] == expected:
            agree.append(p)
        elif r["status"] in ("le", "gt"):
            disagree.append({"p": p, "paper": "tau<=12" if expected == "le" else "tau>=13",
                             "ours": r["status"], "tau": r.get("tau"), "cover": r.get("cover")})
        else:
            unknown.append(p)
    part_r = {"primes": len(r14), "agree": len(agree), "disagree": disagree,
              "unknown": unknown,
              "R1": ("holds" if not disagree and not unknown else
                     "falsified" if disagree else "partly untested")}

    # ---- Part S: k = 15 ----
    le = [r for r in r15 if r["status"] == "le"]
    gt = [r for r in r15 if r["status"] == "gt"]
    unk = [r["p"] for r in r15 if r["status"] not in ("le", "gt")]
    tau_hist = {}
    for r in le:
        tau_hist[str(r["tau"])] = tau_hist.get(str(r["tau"]), 0) + 1
    largest_le = max((r["p"] for r in le), default=None)
    # smallest P0 such that every decided prime >= P0 has tau >= 14 and none is unknown
    decided = sorted(r15, key=lambda r: r["p"])
    p0 = None
    for i in range(len(decided)):
        if all(r["status"] == "gt" for r in decided[i:]):
            p0 = decided[i]["p"]
            break
    gt_sorted = sorted(r["p"] for r in gt)
    acc, plan = 0.0, []
    for p in gt_sorted:
        if acc > GATE_LOGSUM_K15:
            break
        acc += math.log(p)
        plan.append(p)
    p3_le = [r["p"] for r in le if r["p"] >= P3_FROM]
    p3_unk = [p for p in unk if p >= P3_FROM]
    part_s = {
        "primes": len(r15), "tau_le_13": len(le), "tau_ge_14": len(gt), "unknown": unk,
        "tau_histogram_le_13": tau_hist,
        "largest_prime_with_tau_le_13": largest_le,
        "all_primes_from_this_on_have_tau_ge_14": p0,
        "logsum_all_tau_ge_14": round(sum(math.log(p) for p in gt_sorted), 4),
        "gate_plan_tau_ge_14": {"primes": plan, "count": len(plan),
                                "logsum": round(acc, 4),
                                "reaches_483_239": acc > GATE_LOGSUM_K15},
        "logsum_tau_le_13": round(sum(math.log(r["p"]) for r in le), 4),
        "P3": {"statement": f"every prime p in [{P3_FROM}, 1000] has tau_15(p) >= 14",
               "counterexamples": p3_le, "untested": p3_unk,
               "result": ("falsified" if p3_le else "holds" if not p3_unk else
                          "holds where tested")},
    }
    summary = {"part_R_k14_vs_paper": part_r, "part_S_k15": part_s,
               "caps_seconds": {"k14": cap14, "k15": cap15},
               "wall_minutes": round((time.time() - t_start) / 60, 1)}
    with open(os.path.join(a.out_dir, "summary_tau.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == "__main__":
    main()
