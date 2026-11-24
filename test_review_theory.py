# test_review_theory.py -- exact re-checks behind REVIEW_THEORY_2_7.md
# MV2 of Munim, Inc. Apache-2.0. Made with AI agents working in MV2's name.
# Self-contained (standard library only), written independently of bounds.py.
# Every assertion here is an arithmetic fact that REVIEW_THEORY_2_7.md also
# derives by hand; nothing here is a prediction.
import math
import unittest
from fractions import Fraction as F


# ---- tiny polynomial helpers (coefficients low -> high) -------------------
def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def padd(*ps):
    n = max(len(p) for p in ps)
    out = [0] * n
    for p in ps:
        for i, x in enumerate(p):
            out[i] += x
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def pscale(a, c):
    return [c * x for x in a]


def peval(a, x):
    return sum(c * x ** i for i, c in enumerate(a))


Q = [1, 2, -1]          # q(u) = 1 + 2u - u^2
DQ = [2, -2]            # q'(u)
U1U = [0, 1, 1]         # u(1+u)


def q(u):
    return 1 + 2 * u - u * u


class Section1(unittest.TestCase):
    def c64(self):
        b = [F(r, 16 - r) for r in range(0, 15)]
        return [b[r] ** 2 - b[r - 1] ** 2 for r in range(1, 15)]

    def test_table(self):
        given = [F(1, 225), F(176, 11025), F(272, 8281), F(88, 1521),
                 F(104, 1089), F(464, 3025), F(496, 2025), F(32, 81),
                 F(32, 49), F(496, 441), F(464, 225), F(104, 25),
                 F(88, 9), F(272, 9)]
        self.assertEqual(self.c64(), given)

    def test_ratio(self):
        c = self.c64()
        ratios = [c[i + 1] / c[i] for i in range(13)]
        self.assertEqual(min(ratios), F(3751, 2349))
        self.assertEqual(ratios.index(min(ratios)), 5)   # c_7 / c_6
        self.assertTrue(min(ratios) > F(4, 3))

    def test_logs(self):
        c = self.c64()
        s = sum(math.log(float(x)) for x in c)
        self.assertAlmostEqual(s, -14.84867, delta=1e-5)
        lnA = (14 * math.log(64) - s) / 2
        self.assertAlmostEqual(lnA, 36.53652, delta=1e-5)
        bound = 15 * (lnA + math.log(0.49) - math.log(15))
        self.assertAlmostEqual(bound, 496.727, delta=5e-4)
        self.assertEqual(math.lcm(*range(2, 17)), 720720)
        self.assertEqual(720720, 2 ** 4 * 3 ** 2 * 5 * 7 * 11 * 13)
        self.assertAlmostEqual(bound - math.log(720720), 483.239, delta=5e-4)


class Section2(unittest.TestCase):
    def test_target(self):
        # (15/0.49)^2 = 937.1095..., so "= 937.11" is a rounding up; the
        # proved lower bounds (942.5 and 1801) clear 937.11 anyway.
        t = F(225) / F(49, 100) ** 2
        self.assertTrue(t < F("937.11"))
        self.assertTrue(t > F("937.10"))

    def test_derivative_identity(self):
        # (n/2) u^{1+2/n} phi'(u) = -(C gamma - (n-1) u^2), coefficient form:
        # C((n/2) q' u - q) + (n-1)u^2  and  (n/2) q' u - q = -gamma.
        for n in range(3, 30):
            gamma = [1, -(n - 2), n - 1]
            lhs = padd(pscale(pmul(DQ, [0, 1]), F(n, 2)), pscale(Q, -1))
            self.assertEqual(lhs, [F(x) for x in pscale(gamma, -1)])
            # (n-1) q + gamma = n (1 + u)
            self.assertEqual(padd(pscale(Q, n - 1), gamma), [n, n])

    def test_logderiv_poly(self):
        for n in range(4, 30):
            m = n - 1
            gamma = [1, -(n - 2), n - 1]
            dgamma = [-(n - 2), 2 * (n - 1)]
            t = padd(pmul(pmul(DQ, gamma), U1U),
                     pmul(pmul(dgamma, Q), U1U),
                     pscale(pmul(pmul(Q, gamma), [2, 3]), -1))
            self.assertEqual(t, [-2, m - 6, 2 * m - 6, 4 * m - 2, -2 * m, -m])
        p15 = [1, -4, -11, -27, 14, 7]
        self.assertEqual([-2 * x for x in p15], [-2, 8, 22, 54, -28, -14])

    def test_alpha_bracket(self):
        self.assertTrue(F("10.6284") ** 2 < 113 < F("10.6312") ** 2)
        self.assertTrue((13 - F("10.6312")) / 28 >= F("0.0846"))
        self.assertTrue((13 - F("10.6284")) / 28 <= F("0.0847"))

    def test_P15_positive(self):
        u = F("0.0847")
        low = 1 - 4 * u - 11 * u ** 2 - 27 * u ** 3
        self.assertTrue(low > F("0.565"))

    def test_part_b(self):
        a = q(F("0.0846"))
        self.assertTrue((a / F(8, 5)) ** 15 / F("0.0847") ** 2 > 1)
        self.assertTrue((a / F("1.6149")) ** 15 / F("0.0847") ** 2 > 1)
        self.assertTrue(4 * F(8, 5) ** 13 > 1801)
        # (j/2) 2^j (8/5)^(15-j) increases with j
        vals = [F(j, 2) * 2 ** j * F(8, 5) ** (15 - j) for j in range(2, 16)]
        self.assertEqual(vals, sorted(vals))

    def test_part_c_quartic(self):
        A = [1, 2, 27]                          # 1 + 2t + 27t^2
        dA = [2, 54]
        t1 = pscale(pmul(pmul([0, 1], Q), dA), 15)
        t2 = pscale(pmul(pmul([0, 1], DQ), A), 13 * 15)
        t3 = pscale(pmul(Q, A), -28)
        quart = padd(t1, t2, t3)
        self.assertEqual(quart, [-28, 308, 420, 9884, -10584])
        cubic = [-1, 10, 25, 378]
        self.assertEqual(pscale(pmul([1, -1], cubic), 28), quart)
        # q + 28 t^2 = 1 + 2t + 27t^2
        self.assertEqual(padd(Q, [0, 0, 28]), A)
        self.assertTrue(peval(cubic, F("0.0724")) < 0 < peval(cubic, F("0.0725")))

    def test_part_c_bound(self):
        a, b = F("0.0724"), F("0.0725")
        A = 1 + 2 * a + 27 * a * a
        # A q(a)^13 b^(-28/15) > 942.5  <=>  A^15 q(a)^195 > 942.5^15 b^28
        self.assertTrue(A ** 15 * q(a) ** 195 > F("942.5") ** 15 * b ** 28)
        self.assertTrue(F("942.5") > F("937.11"))


class Section5(unittest.TestCase):
    @staticmethod
    def cost(x, d, k=15):
        if x % d == 0:
            return 0
        g = math.gcd(x, d)
        N = d // g
        return g * (-(-2 * N // (k + 1)))

    def test_cost_table(self):
        table = {2: [1], 4: [1, 2], 8: [1, 2, 4], 16: [2, 2, 4, 8],
                 32: [4, 4, 4, 8, 16]}
        reps = [1, 2, 4, 8, 16]                  # odd, 2 mod 4, 4 mod 8, ...
        for d, row in table.items():
            for x, want in zip(reps, row):
                self.assertEqual(self.cost(x, d), want, (d, x))
        for d, want in [(3, 1), (5, 1), (7, 1), (11, 2), (13, 2)]:
            self.assertEqual(self.cost(1, d), want)
        # 7 odd exceptions with everything else divisible by 8: 7 < 8
        self.assertTrue(7 * self.cost(1, 8) < 8)

    def test_arc_count(self):
        # an open arc of length L holds at most ceil(L N) points of (1/N)Z/Z
        # integer form, circle scaled by 4N: points 4j, arc (s, s + 2 num),
        # length L = num / (2N) < 1, so ceil(L N) = ceil(num / 2)
        for N in range(1, 25):
            M = 4 * N
            for num in range(1, 2 * N):
                for s in range(M):
                    pts = sum(1 for j in range(N)
                              if 0 < (4 * j - s) % M < 2 * num)
                    self.assertTrue(pts <= -(-num // 2), (N, num, s))

    def test_two_adic_level32(self):
        for w in range(1, 32, 2):
            inv = pow(w, -1, 32)
            self.assertNotEqual(inv % 32, (-inv) % 32)


class Section7(unittest.TestCase):
    @staticmethod
    def dist(x):
        x = x % 1
        return min(x, 1 - x)

    V = list(range(1, 14)) + [15, 28]

    def test_witness(self):
        t = F(993, 2800)
        self.assertTrue(all(self.dist(t * v) > F(1, 16) for v in self.V))

    def test_interval(self):
        lo, hi = F(5, 14) - F(1, 336), F(5, 14) - F(1, 448)
        self.assertEqual((lo, hi), (F(17, 48), F(159, 448)))
        self.assertEqual(hi - lo, F(1, 1344))
        self.assertEqual(self.dist(3 * lo), F(1, 16))
        self.assertEqual(self.dist(28 * hi), F(1, 16))
        for i in range(1, 200):
            t = lo + (hi - lo) * F(i, 200)
            self.assertTrue(all(self.dist(t * v) > F(1, 16) for v in self.V))
        self.assertTrue(16 * 85 > 1344 and not 16 * 84 > 1344)

    @staticmethod
    def gw_tight(n, r, m):
        s = n - r
        return all(math.gcd(r, b) > 1 for b in range(s, m * s))

    def test_lemma_N_table(self):
        def tight(n):
            return [(r, m) for r in range(1, n) for m in range(2, 61)
                    if m * r >= n and self.gw_tight(n, r, m)]
        self.assertEqual(tight(14), [(12, 2)])
        self.assertEqual(tight(15), [])
        self.assertEqual(tight(16), [])

    def test_lemma_N(self):
        for n in range(7, 200):
            if all((n + 1) % d for d in range(2, int((n + 1) ** 0.5) + 1)):
                for r in range(1, n):
                    for m in range(2, 12):
                        if m * r >= n:
                            self.assertFalse(self.gw_tight(n, r, m), (n, r, m))


class Section8(unittest.TestCase):
    def test_lemma_D_bijection(self):
        for L in (2, 4, 8, 14, 15, 16):
            for p in (17, 19, 23, 29):
                A = pow(L, -1, p)
                B = (1 - A * L) // p
                self.assertEqual(A * L + B * p, 1)
                pairs = {((b * B) % L, (b * A) % p) for b in range(L * p)}
                self.assertEqual(len(pairs), L * p)

    def test_linear_lift_not_killable(self):
        # Section 8.5: for s = (1..k) a dyadic time x has ||i x|| >= 1/(k+1)
        # for all i = 1..k only if k + 1 is a power of 2 (then x = j/16, j odd).
        def ok(x, k):
            return all(Section7.dist(i * x) >= F(1, k + 1)
                       for i in range(1, k + 1))
        for k in (13, 14, 15):
            hits = [a for a in range(512) if ok(F(a, 512), k)]
            if k == 15:
                self.assertEqual(hits, [32 * j for j in range(1, 16, 2)])
            else:
                self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
