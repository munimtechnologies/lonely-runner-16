# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Fast lifting for the non-binary uniform cascade (THEORY_17.md).

`uniform_nb.lift_children` (THEORY_16) lifts one class z at level L to level cL
by branch and bound, in pure Python.  Job lrc-nb (2026-11-23) showed that this is
too slow for the 7^13 lifts of the k = 13 tight vectors and for the P0 runs of
(1..14).  This module does the same computation two ways:

  * `dfs_py`: a pure-Python reference with two result-preserving changes:
      - unit-symmetry reduction (THEORY_17 Lemma S): when c is an odd prime with
        gcd(c, L) = 1, only children whose first nonzero digit y = z' mod c (in
        search order) equals 1 are visited;
      - a search order of the coordinates (default: largest speed first).
  * `nbc.c` (compiled with cc): the same search in C, node for node.

`lift` returns the canonical classes (uniform_nb.canon) of the children that are
not P-killed, in the original coordinate order: the same set as
uniform_nb.lift_children.  test_nbc.py checks this against uniform_nb, and the C
engine against dfs_py (same set, same node count).
"""
import os
import shutil
import subprocess
import tempfile
import time
from math import gcd

import uniform as U
import uniform_nb as N

HERE = os.path.dirname(os.path.abspath(__file__))


class Cut(Exception):
    pass


def is_prime(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def sym_ok(c, L):
    """Lemma S applies: c an odd prime coprime to L (for c = 2 it saves nothing)"""
    return c > 2 and is_prime(c) and gcd(c, L) == 1


def search_order(s, k, order):
    if order is None or order == "id":
        return list(range(k))
    if order == "desc":
        return sorted(range(k), key=lambda i: (-s[i], i))
    if order == "asc":
        return sorted(range(k), key=lambda i: (s[i], i))
    idx = list(order)
    assert sorted(idx) == list(range(k))
    return idx


def prepare(s, k, z, L, c, P, order="desc"):
    """the data of uniform_nb.lift_children, with coordinates in search order"""
    s = tuple(s)
    L2 = c * L
    Q = U.qunit(L2, k, s)
    idx = search_order(s, k, order)
    vals0 = [tuple((z[i] + L * a) % L2 for a in range(c)) for i in range(k)]
    vals = [vals0[i] for i in idx]
    per = []
    for beta in range(1, L2):
        if beta % c == 0:
            continue
        arcs = [[U.arcs_for(s[i], (beta * v) % L2, L2, k, Q) for v in vals0[i]] for i in range(k)]
        cells = U.Cells([a for row in arcs for a in row], Q)
        ex = 1 << cells.M
        masks0 = [tuple(cells.mask(arcs[i][a]) | (ex if U.exact_bad(beta * vals0[i][a], L2, k) else 0)
                        for a in range(c)) for i in range(k)]
        masks = [masks0[i] for i in idx]
        big = cells.big(P)
        suf = [0] * (k + 1)
        for d in range(k - 1, -1, -1):
            u = suf[d + 1]
            for m in masks[d]:
                u |= m
            suf[d] = u
        per.append((cells, masks, big, suf))
    return {"s": s, "k": k, "z": tuple(z), "L": L, "c": c, "L2": L2, "Q": Q, "P": P,
            "idx": idx, "vals": vals, "per": per, "primes": N.prime_factors(L2) if L2 > 1 else []}


def dfs_py(prep, use_gcd=True, sym=True, deadline=None, clock=time.time):
    """reference search; returns (children in search order, nodes, leaves)"""
    k, c, P = prep["k"], prep["c"], prep["P"]
    vals, per, primes = prep["vals"], prep["per"], prep["primes"]
    nb = len(per)
    out = []
    choice = [0] * k
    cnt = [0, 0]

    def leaf(cur):
        cnt[1] += 1
        zz = tuple(vals[d][choice[d]] for d in range(k))
        if use_gcd:
            for q in primes:
                if sum(1 for x in zz if x % q) <= 1:
                    return
        for j in range(nb):
            if per[j][0].killed(cur[j], P):
                return
        out.append(zz)

    def dfs(d, cur, nz):
        cnt[0] += 1
        if deadline is not None and cnt[0] & 4095 == 0 and clock() > deadline:
            raise Cut()
        for j in range(nb):
            big = per[j][2]
            if (cur[j] | per[j][3][d]) & big != big:
                return
        if d == k:
            leaf(cur)
            return
        for a in range(c):
            nz2 = nz
            if sym:
                y = vals[d][a] % c
                if not nz and y > 1:
                    continue
                if y:
                    nz2 = True
            choice[d] = a
            dfs(d + 1, [cur[j] | per[j][1][d][a] for j in range(nb)], nz2)

    dfs(0, [0] * nb, False)
    return out, cnt[0], cnt[1]


def spec_text(prep, use_gcd, sym):
    """the input of nbc.c (whitespace-separated integers)"""
    k, c, L2, P, Q = prep["k"], prep["c"], prep["L2"], prep["P"], prep["Q"]
    per = prep["per"]
    W = max((cells.M + 1 + 63) // 64 for cells, _, _, _ in per) if per else 1
    full = (1 << 64) - 1
    parts = [k, c, L2, 0 if P is None else P, Q, 1 if use_gcd else 0, 1 if sym else 0,
             len(prep["primes"])] + list(prep["primes"]) + [W, len(per)]
    for d in range(k):
        parts.extend(prep["vals"][d])

    def words(x):
        return [(x >> (64 * w)) & full for w in range(W)]

    for cells, masks, big, _ in per:
        parts.append(cells.M)
        parts.extend(cells.lengths)
        parts.extend(words(big))
        for d in range(k):
            for a in range(c):
                parts.extend(words(masks[d][a]))
    return " ".join(map(str, parts)) + "\n"


def build(binpath=None, src=None):
    """compile nbc.c; returns the binary path, or None if no C compiler"""
    if os.name == "nt" and os.environ.get("NBC_REQUIRE_C") != "1":
        return None  # nbc.c uses POSIX clock_gettime; the C tests run in the Linux job
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        return None
    src = src or os.path.join(HERE, "nbc.c")
    binpath = binpath or os.path.join(tempfile.gettempdir(), "nbc_%d" % os.getpid())
    subprocess.run([cc, "-O3", "-o", binpath, src], check=True)
    return binpath


def dfs_c(prep, binpath, use_gcd=True, sym=True, seconds=None):
    """returns (children in search order or None if cut, nodes, leaves)"""
    arg = "0" if seconds is None else "%.3f" % max(seconds, 0.001)
    r = subprocess.run([binpath, arg], input=spec_text(prep, use_gcd, sym),
                       capture_output=True, text=True, check=True)
    out = []
    end = None
    for line in r.stdout.splitlines():
        if line.startswith("Z "):
            out.append(tuple(int(x) for x in line.split()[1:]))
        elif line.startswith("END "):
            end = line.split()
    assert end is not None, r.stderr[-2000:]
    nodes, leaves, nout = int(end[2]), int(end[3]), int(end[4])
    if end[1] == "CUT":
        return None, nodes, leaves
    assert end[1] == "DONE" and nout == len(out), end
    return out, nodes, leaves


def lift(s, k, z, L, c, P, use_gcd=True, sym=None, order="desc", engine="py",
         binpath=None, seconds=None):
    """canonical classes of the children of z (level L) at level cL that are not
    P-killed.  Returns (set or None if cut, stats)."""
    s = tuple(s)
    if sym is None:
        sym = sym_ok(c, L)
    assert not sym or sym_ok(c, L)
    t0 = time.time()
    prep = prepare(s, k, z, L, c, P, order)
    if engine == "c":
        left = None if seconds is None else seconds - (time.time() - t0)
        raw, nodes, leaves = dfs_c(prep, binpath, use_gcd, sym, left)
    else:
        try:
            raw, nodes, leaves = dfs_py(prep, use_gcd, sym,
                                        None if seconds is None else t0 + seconds)
        except Cut:
            raw, nodes, leaves = None, None, None
    stats = {"nodes": nodes, "leaves": leaves, "seconds": round(time.time() - t0, 3),
             "raw": None if raw is None else len(raw), "cut": raw is None}
    if raw is None:
        return None, stats
    idx = prep["idx"]
    out = set()
    for zz in raw:
        w = [0] * k
        for d, i in enumerate(idx):
            w[i] = zz[d]
        out.add(N.canon(tuple(w), c * L))
    return out, stats


def lift_set(s, k, parents, L, c, P, use_gcd=True, engine="py", binpath=None,
             deadline=None, order="desc"):
    """union of `lift` over all parents; (None, stats) if the deadline passed"""
    out = set()
    tot = {"parents": len(parents), "done": 0, "nodes": 0, "leaves": 0, "seconds": 0.0,
           "cut": False}
    for z in sorted(parents):
        left = None if deadline is None else deadline - time.time()
        if left is not None and left <= 0:
            tot["cut"] = True
            return None, tot
        S, st = lift(s, k, z, L, c, P, use_gcd, None, order, engine, binpath, left)
        tot["seconds"] = round(tot["seconds"] + st["seconds"], 3)
        if S is None:
            tot["cut"] = True
            return None, tot
        tot["nodes"] += st["nodes"]
        tot["leaves"] += st["leaves"]
        tot["done"] += 1
        out |= S
    return out, tot
