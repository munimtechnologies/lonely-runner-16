# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Speed-product bound for a primitive counterexample to LRC(n) (n speeds,
n+1 runners), following Section 3 of Allikvere, arXiv:2609.02604 ("flag bound").

  B_r = (2r / ((n+1)(n+1-r)))^2,  c_r = B_r - B_{r-1},  K_n = prod_{r<n} c_r,
  A_n = K_n^(-1/2),  v_1...v_n < (A_n r_n / n)^n,
where r_n bounds R_n = n (prod x_i)^(1/n) / F_n on the simplex (Lemma 3.7).
Equivalently R_n^2 = n^2 / H(u) with
  H(u) = (sum w(u_i)) prod a(u_i),  q = 1+2u-u^2,  a = q / u^(2/n),  w = u^2/q,
minimised over u in (0,1]^n with max u_i = 1.

Exact rational arithmetic is used for K_n; logarithms use Decimal at 60 digits.
The shape bound here is computed numerically with a rigorous interval sweep of
the one-parameter families (j coordinates equal to 1, the rest equal to t) that
the paper's Lemma 3.7 reduces to; the reduction itself is the paper's argument
and must be re-derived for each new n before a bound is relied upon.
"""
import json
import math
import random
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60


def B(n, r):
    return Fraction(2 * r, (n + 1) * (n + 1 - r)) ** 2


def c_list(n):
    return [B(n, r) - B(n, r - 1) for r in range(1, n)]


def K(n):
    out = Fraction(1)
    for c in c_list(n):
        out *= c
    return out


def min_ratio(n):
    cs = c_list(n)
    return min(cs[i + 1] / cs[i] for i in range(len(cs) - 1))


def dln(fr):
    fr = Fraction(fr)
    return Decimal(fr.numerator).ln() - Decimal(fr.denominator).ln()


def lnA(n):
    return -dln(K(n)) / 2


def product_log_bound(n, r):
    """log of the bound on v_1...v_n, i.e. n (ln A_n + ln r_n - ln n)"""
    return n * (lnA(n) + dln(Fraction(r)) - Decimal(n).ln())


def lcm_upto(m):
    out = 1
    for i in range(2, m + 1):
        out = out * i // math.gcd(out, i)
    return out


def required_gate_logsum(n, r):
    return product_log_bound(n, r) - Decimal(lcm_upto(n + 1)).ln()


# ---------------- shape bound ----------------

def q(u):
    return 1 + 2 * u - u * u


def a_fun(u, n):
    return q(u) / u ** (2.0 / n)


def w_fun(u):
    return u * u / q(u)


def H(us, n):
    s = sum(w_fun(u) for u in us)
    pr = 1.0
    for u in us:
        pr *= a_fun(u, n)
    return s * pr


def H_family(n, j, t):
    """j coordinates equal to 1, n-j equal to t"""
    return (j / 2 + (n - j) * w_fun(t)) * 2 ** j * a_fun(t, n) ** (n - j)


def family_min(n, j, grid=20000):
    best = (float("inf"), None)
    for i in range(1, grid + 1):
        t = i / grid
        h = H_family(n, j, t)
        if h < best[0]:
            best = (h, t)
    # golden-section refine around the best grid point
    lo, hi = max(1e-12, best[1] - 1.0 / grid), min(1.0, best[1] + 1.0 / grid)
    g = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        x1 = hi - g * (hi - lo)
        x2 = lo + g * (hi - lo)
        if H_family(n, j, x1) < H_family(n, j, x2):
            hi = x2
        else:
            lo = x1
    t = (lo + hi) / 2
    return min(best[0], H_family(n, j, t)), t


def family_lower_bound(n, j, pieces=200000):
    """rigorous (up to float rounding, guarded by a 1e-9 relative margin) lower
    bound of H_family(n, j, t) over t in (0, 1].  Uses q and w increasing and
    u^(-2/n) decreasing on (0, 1]."""
    if j == n:
        return n / 2 * 2 ** n
    eps = 1.0 / pieces
    # t in (0, eps]: a(t) >= t^(-2/n) >= eps^(-2/n), w >= 0
    lb = (j / 2) * 2 ** j * (eps ** (-2.0 / n)) ** (n - j)
    for i in range(1, pieces):
        t0, t1 = i * eps, (i + 1) * eps
        a_lo = q(t0) * t1 ** (-2.0 / n)
        h = (j / 2 + (n - j) * w_fun(t0)) * 2 ** j * a_lo ** (n - j)
        if h < lb:
            lb = h
    return lb * (1 - 1e-9)


def random_search(n, trials=200, iters=3000, seed=1):
    """numerical sanity check over the full cube (max coordinate fixed at 1)"""
    rng = random.Random(seed)
    best = float("inf")
    for _ in range(trials):
        us = [1.0] + [rng.uniform(0.01, 1.0) for _ in range(n - 1)]
        h = H(us, n)
        step = 0.2
        for it in range(iters):
            i = rng.randrange(1, n)
            old = us[i]
            us[i] = min(1.0, max(1e-6, old + rng.gauss(0, step)))
            h2 = H(us, n)
            if h2 < h:
                h = h2
            else:
                us[i] = old
            if it % 500 == 499:
                step *= 0.5
        best = min(best, h)
    return best


def shape(n, pieces=200000):
    fam = []
    for j in range(1, n + 1):
        m, t = family_min(n, j)
        lb = family_lower_bound(n, j, pieces if j == 1 else max(1000, pieces // 10))
        fam.append({"j": j, "min": m, "argmin_t": t, "rigorous_lower_bound": lb})
    hlb = min(f["rigorous_lower_bound"] for f in fam)
    return fam, hlb


def primes_between(a, b):
    out = []
    for x in range(max(2, a), b + 1):
        if all(x % d for d in range(2, int(x ** 0.5) + 1)):
            out.append(x)
    return out


def report(n, r=None, pieces=200000, gate_start=None):
    fam, hlb = shape(n, pieces)
    r_suggest = Fraction(math.ceil(n / math.sqrt(hlb) * 10000), 10000)
    if r is None:
        r = r_suggest
    r = Fraction(r)
    out = {
        "n_speeds": n,
        "runners": n + 1,
        "K_n": str(K(n)),
        "ln_A_n": str(lnA(n)),
        "A_n": str(lnA(n).exp()),
        "min_c_ratio": str(min_ratio(n)),
        "min_c_ratio_float": float(min_ratio(n)),
        "ratio_condition_gt_4_3": min_ratio(n) > Fraction(4, 3),
        "shape_families": fam,
        "H_lower_bound": hlb,
        "R_n_upper_from_H": n / math.sqrt(hlb),
        "r_n_used": str(r),
        "r_n_valid": float(r) > n / math.sqrt(hlb),
        "log_product_bound": str(product_log_bound(n, r)),
        "forced_divisor_lcm": lcm_upto(n + 1),
        "required_gate_logsum": str(required_gate_logsum(n, r)),
    }
    if gate_start:
        need = float(required_gate_logsum(n, r))
        acc, gates = 0.0, []
        for pr in primes_between(gate_start, 5000):
            gates.append(pr)
            acc += math.log(pr)
            if acc > need + math.log(pr):
                break
        out["example_gate_set"] = {"from": gate_start, "to": gates[-1], "count": len(gates),
                                   "logsum": acc}
    return out


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [13, 14, 15]
    res = {}
    for n in ns:
        r = {13: Fraction(101, 200), 14: Fraction(1, 2)}.get(n)
        res[n] = report(n, r, gate_start=281 if n == 15 else None)
        res[n]["random_search_min_H"] = random_search(n, trials=40, iters=3000)
    json.dump(res, sys.stdout, indent=1, default=str)
