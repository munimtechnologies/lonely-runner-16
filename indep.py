# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Independent brute-force binary cascade J_p(L) for one level-one vector s.

Written for REVIEW_18.md. It imports NO other repository code and uses none of
the prime-free machinery (no Lemma D, no arcs, no unit reduction, no pruning):
every lift is tested against every time b in Z_{Lp} directly.

Definitions (THEORY.md 8.2, THEORY_18.md 18.1), k = len(s), threshold 1/(k+1):
  level 1:  w = s mod p in Z_p; proper iff some b in Z_p has ||b w_i / p|| >= 1/(k+1)
            for every i.
  level L (a power of 2, L >= 2): w in Z_{Lp}; proper iff at most one w_i mod L is
            odd (gcd clause) or some b in Z_{Lp} has ||b w_i/(Lp)|| >= 1/(k+1) for all i.
  J_p(1) = {s} if s is improper at level 1, else empty;
  J_p(2L) = the improper lifts w' (w' = w or w + Lp, mod 2Lp, coordinatewise) of the
            members w of J_p(L).
||y|| is the distance to the nearest integer; with r = b w_i mod n, ||b w_i/n|| >=
1/(k+1) iff (k+1) * min(r, n - r) >= n, so everything is integer arithmetic.

indep_brute.c is the same algorithm in C (same order of children, same output);
test_indep.py checks the two against each other and against hand-proved facts.
"""
import json
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
C_SOURCE = os.path.join(HERE, "indep_brute.c")


# ---------------------------------------------------------------- definitions

def is_witness(b, w, n, k1):
    for wi in w:
        r = (b * wi) % n
        if k1 * min(r, n - r) < n:
            return False
    return True


def gcd_clause(w, L):
    return L >= 2 and sum(1 for wi in w if (wi % L) % 2) <= 1


def proper(w, n, L, k1):
    if gcd_clause(w, L):
        return True
    for b in range(1, n // 2 + 1):  # b and n - b give the same distances
        if is_witness(b, w, n, k1):
            return True
    return False


def cascade(s, p, lmax, cap=None):
    """Pure-Python cascade. Returns (levels, cut): levels is a list of
    (L, count, list of z = w mod L) for L = 1, 2, 4, ... until the count is 0 or
    lmax is reached; cut is None or {"level": L, "reason": "cap"} when more than
    cap improper lifts were found at level L (the list then holds the first cap)."""
    k1 = len(s) + 1
    w0 = [x % p for x in s]
    if proper(w0, p, 1, k1):
        return [(1, 0, [])], None
    levels = [(1, 1, [[0] * len(s)])]
    cur = [w0]
    L = 1
    while 2 * L <= lmax and cur:
        n, step = 2 * L * p, L * p
        nxt, count = [], 0
        for w in cur:
            for mask in range(1 << len(s)):
                c = [(wi + step) % n if (mask >> i) & 1 else wi for i, wi in enumerate(w)]
                if not proper(c, n, 2 * L, k1):
                    count += 1
                    if cap is None or len(nxt) < cap:
                        nxt.append(c)
        L *= 2
        levels.append((L, count, [[x % L for x in c] for c in nxt]))
        if cap is not None and count > len(nxt):
            return levels, {"level": L, "reason": "cap"}
        cur = nxt
    return levels, None


# ---------------------------------------------------------------- the C engine

def build_c(required=False):
    """Compile indep_brute.c; return the executable path, or None if no compiler
    (raises instead when required)."""
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        if required:
            raise RuntimeError("no C compiler found")
        return None
    out_dir = tempfile.mkdtemp(prefix="indep_")
    exe = os.path.join(out_dir, "indep_brute" + (".exe" if os.name == "nt" else ""))
    try:
        subprocess.run([cc, "-O2", "-std=c99", "-o", exe, C_SOURCE], check=True,
                       capture_output=True, timeout=300)
    except Exception:
        if required:
            raise
        return None
    return exe


def parse_c_output(text):
    levels, cut = [], None
    cur = None
    ended = False
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "LEVEL":
            L, count = int(parts[1]), int(parts[2])
            cur = (L, count, [])
            levels.append(cur)
            if len(parts) > 3 and parts[3] == "CAP":
                cut = {"level": L, "reason": "cap"}
        elif parts[0] == "Z":
            cur[2].append([int(x) for x in parts[1:]])
        elif parts[0] == "END":
            ended = True
    if not ended:
        raise RuntimeError("C output has no END line")
    return levels, cut


def run_c(exe, s, p, lmax, cap):
    args = [exe, str(p), str(lmax), str(cap)] + [str(x) for x in s]
    r = subprocess.run(args, check=True, capture_output=True, text=True)
    return parse_c_output(r.stdout)


# ---------------------------------------------------------------- unit classes

def unit_class(z, L):
    """Canonical member of {lambda z mod L : lambda odd} (lexicographic minimum).
    The unit Lambda = lambda (mod L), 1 (mod p) maps a lift to a lift and permutes
    the times b, so properness and membership of J_p(L) are constant on a class."""
    if L <= 2:
        return tuple(x % L for x in z)
    return min(tuple((lam * x) % L for x in z) for lam in range(1, L, 2))


def closed_under_units(zs, L):
    js = set(tuple(z) for z in zs)
    for z in zs:
        for lam in range(1, L, 2):
            if tuple((lam * x) % L for x in z) not in js:
                return False
    return True


def u_classes(data, base, P):
    """{level: (set of unit classes, complete?)} for the run with this base and P
    in a summary_uniform.json of job lrc16-uniform-v1. Empty dict if the base is
    killed at level 1."""
    runs = [r for r in data["runs"] if r["base"] == base and r["P"] == P]
    if len(runs) != 1:
        raise ValueError(f"expected one run for {base}, P={P}, found {len(runs)}")
    run = runs[0]
    out = {}
    if run.get("base_killed"):
        return out
    for lv in run["levels"]:
        L = lv["level"]
        lst = lv.get("list") or []
        complete = len(lst) == lv["survivors"]
        out[L] = (set(unit_class(z, L) for z in lst), complete)
    return out


# ---------------------------------------------------------------- grading

def grade_prime(base, p, levels, cut, u251, uinf=None):
    """One record per (base, prime). u251/uinf as returned by u_classes."""
    rec = {"base": base, "p": p, "cut": cut,
           "counts": {str(L): c for L, c, _ in levels}}
    death = None
    for L, c, _ in levels:
        if c == 0:
            death = L
            break
    rec["death_level"] = death
    classes = {}
    closure_ok = True
    for L, c, zs in levels:
        if L == 1:
            continue
        classes[L] = sorted(set(unit_class(z, L) for z in zs))
        if not (cut and cut["level"] == L) and not closed_under_units(zs, L):
            closure_ok = False
    rec["classes"] = {str(L): [list(z) for z in cl] for L, cl in classes.items()}
    rec["I5_closure_ok"] = closure_ok
    outside, untested_levels = [], []
    for L, cl in classes.items():
        if L not in u251:
            if cl and u251:  # cascade went deeper than the U file: no claim there
                untested_levels.append(L)
            elif cl and not u251:  # U says the base is killed at level 1
                outside += [{"level": L, "z": list(z)} for z in cl]
            continue
        allowed, complete = u251[L]
        if not complete:
            untested_levels.append(L)
            continue
        outside += [{"level": L, "z": list(z)} for z in cl if z not in allowed]
    if not u251 and rec["counts"].get("1") == 1:
        outside.append({"level": 1, "z": "base improper but U_251 kills it at level 1"})
    rec["I2_outside_U251"] = outside
    rec["I2_untested_levels"] = untested_levels
    if uinf is not None:
        missing, untested = [], []
        for L, (ucl, complete) in sorted(uinf.items()):
            if not ucl:
                continue
            if L in classes:
                have = set(classes[L])
                missing += [{"level": L, "z": list(z)} for z in sorted(ucl) if z not in have]
            elif cut is not None:
                untested.append(L)
            else:
                missing += [{"level": L, "z": list(z)} for z in sorted(ucl)]
        rec["I3_missing_Uinf"] = missing
        rec["I3_untested_levels"] = untested
    return rec


def primes_between(lo, hi):
    out = []
    for n in range(max(lo, 2), hi + 1):
        d, ok = 2, True
        while d * d <= n:
            if n % d == 0:
                ok = False
                break
            d += 1
        if ok:
            out.append(n)
    return out


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
