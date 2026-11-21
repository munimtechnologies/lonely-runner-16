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
the paper's Lemma 3.7 reduces to.  The reduction for n = 15 is written out in
THEORY.md (it gives R_15 < 49/100); shape_n15_exact() checks its final
inequality in exact rational arithmetic.
"""
import json
import math
import random
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60

# r_n used for the product bound (paper values for n = 13, 14; THEORY.md for 15)
R_USED = {13: Fraction(101, 200), 14: Fraction(1, 2), 15: Fraction(49, 100)}


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


# ---------------- exact checks for the n = 15 shape lemma (THEORY.md) ----------------

def shape_n15_exact():
    """Exact rational versions of the inequalities used in THEORY.md, Sec. 2.
    Returns a dict of booleans; every value must be True."""
    F = Fraction
    out = {}
    # alpha_15 = (13 - sqrt 113)/28 lies in (0.0846, 0.0847): 10.6284^2 < 113 < 10.6312^2
    out["alpha_bracket"] = F(106284, 10000) ** 2 < 113 < F(106312, 10000) ** 2
    # P15(u) = 7u^5+14u^4-27u^3-11u^2-4u+1 > 0 on (0, 0.0847]: drop the positive
    # terms; 1-4u-11u^2-27u^3 is decreasing, so check it at u = 0.0847
    u = F(847, 10000)
    out["P15_positive"] = 1 - 4 * u - 11 * u ** 2 - 27 * u ** 3 > 0
    # a(u) > 8/5 on (0,1]: min(a(alpha), a(1)=2); a(alpha) > q(0.0846) * 0.0847^(-2/15).
    # Check (q(0.0846)/(8/5))^15 * (1/0.0847)^2 > 1 exactly.
    ql = 1 + 2 * F(846, 10000) - F(846, 10000) ** 2
    out["a_gt_8_5"] = (ql / F(8, 5)) ** 15 * (F(10000, 847)) ** 2 > 1
    # two or more ones: H >= 4 (8/5)^13 > (15/(49/100))^2
    thr = (F(15) / F(49, 100)) ** 2
    out["two_ones"] = 4 * F(8, 5) ** 13 > thr
    # one coordinate 1, fourteen equal to t: sign of dlogH/dt is that of
    # h(t) = 378t^3 + 25t^2 + 10t - 1 (times the positive factor 28(1-t));
    # its root t0 lies in (0.0724, 0.0725)
    h = lambda t: 378 * t ** 3 + 25 * t ** 2 + 10 * t - 1
    t_lo, t_hi = F(724, 10000), F(725, 10000)
    out["t0_bracket"] = h(t_lo) < 0 < h(t_hi)
    # H(t0) >= g(t_lo) q(t_lo)^13 t_hi^(-28/15) with g = 1+2t+27t^2.  Compare the
    # 15th powers: (g q^13)^15 / t_hi^28 > thr^15
    g = 1 + 2 * t_lo + 27 * t_lo ** 2
    qq = 1 + 2 * t_lo - t_lo ** 2
    out["one_one"] = (g * qq ** 13) ** 15 > thr ** 15 * t_hi ** 28
    return out


def check_quartic_factor_n15():
    """numerator of dlogH/dt for the one-1 family equals 28(1-t)h(t) (exact)"""
    # coefficients of -10584 t^4 + 9884 t^3 + 420 t^2 + 308 t - 28 (derived in THEORY.md)
    # recomputed here from the definition with polynomial arithmetic
    def mul(a, b):
        r = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                r[i + j] += x * y
        return r

    def add(*ps):
        n = max(len(p) for p in ps)
        return [sum(p[i] if i < len(p) else 0 for p in ps) for i in range(n)]

    def scale(p, c):
        return [c * x for x in p]

    n, s = 15, 14
    qp = [1, 2, -1]               # q = 1 + 2t - t^2
    g = [1, 2, 2 * s - 1]         # g = 1 + 2t + 27 t^2
    gp = [2, 2 * (2 * s - 1)]     # g'
    qprime = [2, -2]
    t = [0, 1]
    # n t q g' + n t g (s-1) q' - 2 s g q   (logderivative times n t g q)
    A = scale(mul(mul(t, qp), gp), n)
    Bp = scale(mul(mul(t, g), qprime), n * (s - 1))
    C = scale(mul(g, qp), -2 * s)
    num = add(A, Bp, C)
    target = scale(mul([1, -1], [-1, 10, 25, 378]), 28)
    while num and num[-1] == 0:
        num.pop()
    return num == target


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
    if n == 15:
        out["shape_n15_exact"] = shape_n15_exact()
        out["quartic_factor_n15"] = check_quartic_factor_n15()
    if gate_start:
        need = float(required_gate_logsum(n, r))
        acc, gates = 0.0, []
        for pr in primes_between(gate_start, 5000):
            gates.append(pr)
            acc += math.log(pr)
            if acc > need:
                break
        out["example_gate_set"] = {"from": gate_start, "to": gates[-1], "count": len(gates),
                                   "logsum": acc}
    return out


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [13, 14, 15]
    res = {}
    for n in ns:
        res[n] = report(n, R_USED.get(n), gate_start=281 if n == 15 else None)
        res[n]["random_search_min_H"] = random_search(n, trials=40, iters=3000)
    json.dump(res, sys.stdout, indent=1, default=str)
