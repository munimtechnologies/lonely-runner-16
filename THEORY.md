# THEORY: the speed-product bound for 16 runners (n = 15)

MV2 of Munim, Inc. Text CC BY 4.0. Written 2026-11-21 by AI agents working in
MV2's name. **No human expert has checked this yet.** Every inequality below is
re-checked in exact rational arithmetic by `bounds.shape_n15_exact()` and
`bounds.check_quartic_factor_n15()` (tests in `test_bounds.py`).

This note carries Section 3 of J. Allikvere, *Fourteen and fifteen lonely runners*,
arXiv:2609.02604 v2 (the "flag bound") from n = 14 to n = 15 speeds, i.e. from 15 to
16 runners. Everything structural is the paper's. What is new here is the
n = 15 case of the shape lemma (the paper's Lemma 3.7 is stated and proved only for
n = 13, 14) and the resulting constants.

Notation as in the paper: n speeds, v positive and primitive, S = sum v_i,
x_i = v_i/S, q(u) = 1 + 2u - u^2, F_n(x)^2 = (prod q_i) sum x_i^2/q_i,
R_n(x) = n (prod x_i)^{1/n} / F_n(x).

## 1. Hypotheses of the flag bound (Theorem 3.8) for n = 15

1. **LRC(m) for all m < 15.** True: m <= 14 speeds is at most 15 runners, proved
   in arXiv:2609.02604 (with the earlier cases it cites). The prefix
   inequalities (Proposition 3.4) use Lemma 3.3 with q = r + 1 >= 2, which needs
   LRC(m) only for m <= n - 1 = 14.
2. **Ratio condition c_{i+1}/c_i > 4/3.** Here B_r = (r / (8(16 - r)))^2, so
   64 c_r = b_r^2 - b_{r-1}^2 with b_r = r/(16 - r):

   | r | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | 64 c_r | 1/225 | 176/11025 | 272/8281 | 88/1521 | 104/1089 | 464/3025 | 496/2025 | 32/81 | 32/49 | 496/441 | 464/225 | 104/25 | 88/9 | 272/9 |

   The smallest ratio is c_7/c_6 = (31/29)(121/81) = **3751/2349 = 1.5969 > 4/3**.
3. Then (Theorem 3.8) S F_15(x) <= A_15 = K_15^{-1/2}, K_15 = prod_{r<15} c_r, and
   **ln A_15 = 36.53652** (sum of ln(64 c_r) = -14.84867, minus 14 ln 64).

## 2. Shape lemma for n = 15: R_15 < 49/100 on the open simplex

Rescale u_i = x_i / max_j x_j and put a(u) = q(u) u^{-2/15}, w(u) = u^2/q(u),
H(u) = (sum w(u_i)) prod a(u_i). Then R_15^2 = 225 / H(u), so it suffices to show
**H > (15/0.49)^2 = 937.11** on (0,1]^15 with some u_i = 1. H tends to infinity as
any coordinate tends to 0 (a(u) does and sum w >= 1/2), so H has a minimiser.

**(a) Interior coordinates are equal.** Fix all coordinates but one interior u,
let C = sum_{j != i} w(u_j) in (0, 7] and phi(u) = a(u)(C + w(u)). Direct
differentiation (valid for every n) gives

  (n/2) u^{1+2/n} phi'(u) = -beta(u),  beta(u) = C gamma(u) - (n-1) u^2,
  gamma(u) = (n-1) u^2 - (n-2) u + 1.

For n = 15, gamma = 14u^2 - 13u + 1 with smaller root alpha = (13 - sqrt 113)/28,
and 10.6284^2 < 113 < 10.6312^2 gives **alpha in (0.0846, 0.0847)**. As in the
paper, beta(0) = C > 0 and beta(alpha) = -14 alpha^2 < 0; if C <= 1, beta is
concave (linear if C = 1) and has one positive root; if C > 1, beta is convex and
beta(1) = 2C - 14 <= 0, so its other root is >= 1. So phi has a unique critical
point u_0 in (0,1), it lies in (0, alpha), and it is a minimum. Using
(n-1) q + gamma = n(1+u), the critical-point equation becomes

  L(u) := q(u) gamma(u) / (n u^2 (1+u)) = 1/A,  A = sum_i w(u_i).

The logarithmic derivative of L, times q gamma u (1+u), is (for general n, with
m = n - 1)

  -m u^5 - 2m u^4 + (4m-2) u^3 + (2m-6) u^2 + (m-6) u - 2,

which reproduces the paper's polynomials for n = 14 (m = 13) and n = 13 (m = 12).
For n = 15 it is -2 P_15(u) with **P_15(u) = 7u^5 + 14u^4 - 27u^3 - 11u^2 - 4u + 1**.
On (0, alpha] we have P_15(u) > 1 - 4u - 11u^2 - 27u^3 >= its value at 0.0847,
which is 0.566 > 0. So L is strictly decreasing on (0, alpha), and all interior
coordinates of a minimiser share one value t.

**(b) Two or more coordinates equal to 1.** a'(u) has the sign of -gamma(u), so
on (0,1] the minimum of a is min(a(alpha), a(1) = 2). Since q increases and
u^{-2/15} decreases, a(alpha) > q(0.0846) * 0.0847^{-2/15} > 1.615 > 8/5
(checked exactly as (q(0.0846)/(8/5))^15 * 0.0847^{-2} > 1). With j >= 2 ones,
H >= (j/2) 2^j (8/5)^{15-j}, which increases with j, and at j = 2 equals
4 (8/5)^13 > 1801 > 937.11.

**(c) Exactly one coordinate equal to 1.** The other fourteen equal t, and

  H(t) = (1 + 2t + 27t^2) q(t)^13 t^{-28/15}.

Its logarithmic derivative, times 15 t (1 + 2t + 27t^2) q(t) > 0, is the quartic
-10584 t^4 + 9884 t^3 + 420 t^2 + 308 t - 28 = **28 (1 - t)(378 t^3 + 25 t^2 + 10 t - 1)**
(the paper's cubics are 325t^3 + 23t^2 + 9t - 1 for n = 14 and
276t^3 + 21t^2 + 8t - 1 for n = 13; the pattern is s(2s-1) t^3 + (2s-3) t^2 +
(s-4) t - 1 with s = n - 1). The cubic is increasing on t > 0 and changes sign in
**(0.0724, 0.0725)**, so H falls then rises on (0,1) with minimiser t_0 there.
By monotonicity of each factor,

  H(t_0) >= (1 + 2(0.0724) + 27(0.0724)^2) q(0.0724)^13 / 0.0725^{28/15} > 942.5 > 937.11,

checked exactly after raising to the 15th power. (Numerically min H = 944.96 at
t_0 = 0.072475, so the sharp value is R_15 = 0.48796.)

Together: **R_15 < 49/100** on the open simplex.

## 3. Consequences

- **Product bound (Theorem 3.8):** a primitive counterexample to LRC(15) has
  log(v_1 ... v_15) < 15 (ln A_15 + ln(49/100) - ln 15) = **496.727** (to 3 decimals).
  For comparison, the paper's bound for 15 runners is 414.78.
- **Forced divisor (Lemma 3.10, Rosenfeld):** lcm(2, ..., 16) = 720720 =
  2^4 3^2 5 7 11 13 divides the product; ln 720720 = 13.488.
- **Gate condition (analogue of Corollary 3.11):** LRC(15), i.e. the conjecture for
  16 runners, follows if there is a set of primes p > 13 with
  **sum of ln p > 483.239**, each of which divides v_1 ... v_15 for every
  primitive, distinct-coordinate counterexample (e.g. because J(15, p) is empty,
  or by Lemma 2.2(ii)). Distinct coordinates may be assumed because a repeated
  speed leaves at most 14 distinct speeds and LRC(14) gives a witness at
  distance 1/15 > 1/16.
- **Size of the job:** consecutive primes from 281 reach the sum somewhere near
  800 (around 80 primes; `bounds.py` prints the exact set). Allikvere needed 71 gate
  primes for 15 runners.

## 4. What is still open in the 16-runner plan

1. The gates themselves: J(15, p) for about 80 primes, with an archive and an
   audit (jobs `lrc16-pilot-v1`, `lrc16-engine2-v1` measure cost first).
2. Persistent orbits. Because 16 = 2^4, the binary lifting levels reach level 16,
   where t = 1/16 is on the grid; any lift with no coordinate divisible by 16 is
   then proper (this is the reason lcm(2..16) divides the product). Whether the
   orbit of (1, ..., 15) and Goddyn-Wong-type tight tuples die by level 32, or need
   a shift-lemma argument (the paper's Lemma 4.6 needs e m_d < d, which fails for
   d = 2), is what the pilot jobs will show.
3. An independent check of this note: a second reader, or a Lean/interval
   formalisation of Section 2.
