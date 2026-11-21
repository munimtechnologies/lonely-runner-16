# THEORY: the 16-runner case (n = k = 15 speeds)

MV2 of Munim, Inc. Text CC BY 4.0. Written 2026-11-21 by AI agents working in
MV2's name. **No human expert has checked this yet.** Every inequality in
Sections 1-3 is re-checked in exact rational arithmetic by
`bounds.shape_n15_exact()` and `bounds.check_quartic_factor_n15()` (tests in
`test_bounds.py`); Section 5 is checked by `test_shift.py` and `test_c.py`;
Section 6 by `test_ext.py`; Section 7 by `test_tight.py`; Section 8 by
`test_uniform.py`.

Sections 1-3 carry Section 3 of J. Allikvere, *Fourteen and fifteen lonely runners*,
arXiv:2609.02604 v2 (the "flag bound") from n = 14 to n = 15 speeds, i.e. from 15 to
16 runners. Everything structural is the paper's. What is new here is the
n = 15 case of the shape lemma (the paper's Lemma 3.7 is stated and proved only for
n = 13, 14) and the resulting constants. Section 5 (added in run 3) prepares the
argument for the orbits that survive binary lifting. Section 6 (run 4) closes the
gap left by primes whose level-one covers can be small. Section 7 (run 5) asks
which tight sets exist for 16 runners, since tight sets are what survived binary
lifting for 14 and 15 runners. Section 8 (run 6) separates the prime from the
lifting problem, so one computation covers every gate prime at once.

Notation as in the paper: n speeds, v positive and primitive, S = sum v_i,
x_i = v_i/S, u_i = v_i / max_j v_j, q_i = q(u_i) with q(u) = 1 + 2u - u^2,
F_n(x)^2 = (prod q_i) sum x_i^2/q_i, R_n(x) = n (prod x_i)^{1/n} / F_n(x).

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

Put a(u) = q(u) u^{-2/15}, w(u) = u^2/q(u),
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
u^{-2/15} decreases, a(alpha) > q(0.0846) * 0.0847^{-2/15} > 1.6149 > 8/5
(checked exactly as (q(0.0846)/(8/5))^15 * 0.0847^{-2} > 1). With j >= 2 ones,
H >= (j/2) 2^j (8/5)^{15-j}, which increases with j, and at j = 2 equals
4 (8/5)^13 > 1801 > 937.11.

*Erratum (run 3):* the run-2 text said "> 1.615" here; the chain as written gives
1.61499..., so the right statement is "> 1.6149". Only "> 8/5" is used, and that
is what `shape_n15_exact()["a_gt_8_5"]` checks, so nothing downstream changes.

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

**Second reading (run 3).** A fresh pass re-derived by hand, independently of the
run-2 text: all six coefficients of the general-n polynomial in (a) (from
q' gamma u(1+u) + gamma' q u(1+u) - q gamma (2+3u)); the quartic in (c) and its
factorisation; the sign pattern of a'; the brackets for alpha and t_0; and the
lower bound in (c) (942.53). All agree with the text above, apart from the
erratum in (b). This second reader is also an AI agent, so a human reader or a
formal (Lean or interval-arithmetic) check is still needed.

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
  or by Lemma 2.2(ii) and its chained form in Section 5). Distinct coordinates may
  be assumed because a repeated speed leaves at most 14 distinct speeds and
  LRC(14) gives a witness at distance 1/15 > 1/16.
- **Size of the job:** consecutive primes from 281 reach the sum somewhere near
  800 (around 80 primes; `bounds.py` prints the exact set). Allikvere needed 71 gate
  primes for 15 runners.

## 4. What is still open in the 16-runner plan

1. The gates themselves: J(15, p) for about 80 primes, with an archive and an
   audit (jobs `lrc16-pilot-v1`, `lrc16-engine2-v1` and `lrc16-shift-v1` measure
   cost and survivors first).
2. The orbits that survive binary lifting. Section 5 gives the tools: Lemma L
   (the tight orbit's linear lifts die at level 16), Lemma S (a shift lemma for
   composite d, including d = 4, 8, 16, 32) and the chained form of
   Lemma 2.2(ii) that lets the cascade drop what Lemma S certifies. What survives
   all of them is measured by `lrc16-shift-v1`. Section 7 explains why we expect
   nothing to survive. Section 8 turns the question for the orbit of (1..15) into
   one computation that holds at every prime p >= 251 (job `lrc16-uniform-v1`).
3. Primes where tau_15(p) <= 13 (covers on at most 13 classes exist). Section 6
   makes their gates complete, at a cost, and job `lrc16-tau-v1` finds which
   primes they are.
4. An independent check of this note by a human reader, or a Lean/interval
   formalisation of Sections 2, 5, 6 and 8.

## 5. Tools for the surviving orbits (run 3)

Throughout, k = 15, p > 16 is prime, levels l are positive integers prime to p,
and a vector w at level l lives in Z_{lp}^k with no coordinate divisible by p.
"LR property" for an integer vector u means: some real t has
||t u_i|| >= 1/(k+1) for every i. LRC(m) for m <= 14 is a theorem (Section 1).

### 5.1 Lemma L: linear lifts of a tight vector die once its witness is on the grid

**Lemma L.** Let s be an integer vector with an LR witness t* = j/D (j, D
integers), and let D | l. If lambda is an integer with p not dividing lambda and
w = lambda s mod lp has no coordinate divisible by p, then w is (k,p,l)-proper.

*Proof.* If g = gcd(lambda, l) > 1, then g divides lp and lambda s_i, hence every
w_i, so the gcd clause (a) holds. Otherwise lambda is a unit mod lp; put
b = lambda^{-1} j (lp/D) mod lp. Then b w_i = j s_i (lp/D) mod lp, so
t = b/(lp) satisfies ||t w_i|| = ||j s_i / D|| >= 1/(k+1) for every i. []

For 16 runners take s = (1, ..., 15), t* = 1/16, D = 16: **at level 16, and at
every level divisible by 16, every lift of the orbit of (1,...,15) that is
congruent to a multiple of (1,...,15) mod 16p is proper.** The same holds for any
vector with an LR witness of denominator 16, for example (1,...,13,15,28)
(at t = a/16 with a odd, 28a/16 is 1/4 or 3/4 mod 1).

*Erratum (run 5):* the run-3 text called (1,...,13,15,28) "tight", by analogy with
the 14-runner orbit (1,...,11,13,24). It is not tight: Section 7.3 gives an open
interval of strict witnesses. Lemma L never used tightness, so nothing in this
section changes; the label "gw_15" and the word "tight" in `job_shift.py` (already
queued, so left as it is) refer to this vector.

This is the structural difference from 14 and 15 runners. There the natural
denominators are 14 = 2 * 7 and 15 = 3 * 5, which binary lifting never reaches, so the
tight orbits (1..13), (1..11,13,24) and (1..14) survive every binary level and the
paper needs separate level-14 and level-15 fibre searches (its Section 4). For 16
runners, 16 = 2^4, and the binary cascade itself reaches the denominator.
Lemma L says nothing about *nonlinear* lifts (congruent to c(1..15) mod p but not
to a multiple of (1..15) mod 16p); whether those die is what `lrc16-shift-v1`
measures. `test_shift.LemmaL` checks Lemma L by brute force for p = 17, 19, 23
at levels 16 and 32.

**2-adic necessary conditions (k = 15).** Let 16 | l and let w be improper at
level l. The times j/16 (j odd) are on the grid, and ||j w_i/16|| < 1/16 iff
16 | w_i; so **some coordinate is divisible by 16**, and since the gcd clause fails,
**at least two coordinates are odd**. If also 32 | l, the times j/32 (j odd) show
that either some coordinate is divisible by 32, or the odd coordinates satisfy
{+-w_i^{-1} mod 32} = all 16 odd residues, which needs **at least 8 odd
coordinates**.

### 5.2 Lemma S: a shift lemma for composite moduli

Allikvere's Lemma 4.6 handles a prime d with few coordinates not divisible by d.
For 16 runners its only binary case, d = 2, is useless (it needs e * 1 < 2, i.e.
e <= 1, which the gcd clause already covers). The following version allows
composite d and weights each exception by its gcd with d.

For an integer x and d >= 2 let g = gcd(x, d), N = d/g, and
cost_k(x, d) = 0 if d | x, and g * ceil(2N/(k+1)) otherwise.

**Lemma S.** Let u be a vector of k positive integers and d >= 2. Let
E = {i : d does not divide u_i}, e = |E|, and suppose 1 <= e and LRC(m) holds for
every m <= k - e. If sum_{i in E} cost_k(u_i, d) < d, then u has the LR property.

*Proof.* The coordinates outside E take at most m <= k - e distinct values, all
divisible by d. If m >= 1, LRC(m) gives t_0 with ||t_0 u_i|| >= 1/(m+1) >= 1/(k+1)
for all i outside E; if m = 0 take t_0 = 0. For q = 0, ..., d-1 put
t_q = t_0 + q/d. Outside E, t_q u_i = t_0 u_i mod 1, so those coordinates stay
good. Fix i in E, g = gcd(u_i, d), N = d/g. As q runs over 0..d-1, q u_i/d mod 1
runs over the N-point subgroup (1/N)Z/Z, hitting each point exactly g times, so
t_q u_i runs over a coset of (1/N)Z/Z. The bad set {x : ||x|| < 1/(k+1)} is an
open arc of length 2/(k+1) < 1, and an open arc of length L contains at most
ceil(L N) points of a coset of (1/N)Z/Z (if it contains r points, their spread
(r-1)/N is < L). So at most g * ceil(2N/(k+1)) = cost_k(u_i, d) shifts are bad for
coordinate i. In total fewer than d of the d shifts are bad, so some t_q is a
witness. []

For k = 15 the costs are:

| d | odd x | x = 2 mod 4 | x = 4 mod 8 | x = 8 mod 16 | x = 16 mod 32 |
|---|---|---|---|---|---|
| 2 | 1 | | | | |
| 4 | 1 | 2 | | | |
| 8 | 1 | 2 | 4 | | |
| 16 | 2 | 2 | 4 | 8 | |
| 32 | 4 | 4 | 4 | 8 | 16 |

and for odd primes cost 1 (d = 3, 5, 7) or 2 (d = 11, 13). So for example
**up to 7 odd coordinates are allowed when all the others are divisible by 8**,
and at d = 3 the paper's case "exactly 13 of 15 coordinates divisible by 3"
carries over. `test_shift.py` checks the counting step exhaustively for d <= 40
and k in {3, 7, 14, 15}, and the whole construction (LR time for the divisible
part, then a shift) on random vectors with k = 7 and k = 15.

### 5.3 Chained form of Lemma 2.2(ii)

Call a level-l vector w **certified** if d | l for some d that satisfies
Lemma S for w. Divisibility of w_i by any d | l depends only on w_i mod lp, so if
w is certified, every integer vector congruent to w mod lp has the LR property.

**Lemma C.** Let 1 = l_0 | l_1 | ... | l_r be levels, and define F'_0 as the
level-1 improper vectors and F'_j as the lifts to level l_j of members of
F'_{j-1} that are neither proper nor certified. If F'_r is empty, then p divides
v_1 ... v_k for every primitive counterexample v to LRC(k) (assuming LRC(m) for
m < k).

*Proof.* Suppose p divides no v_i and let w_j = v mod l_j p. A grid witness for
w_j would be a witness for v; the gcd clause for w_j gives one for v by the
argument of Lemma 2.2 (LRC on the other speeds, then a shift of order g); and a
certified w_j gives one by Lemma S. So every w_j is neither proper nor certified.
w_0 is level-1 improper, and w_j is a lift of w_{j-1}, so by induction
w_j is in F'_j for every j; in particular F'_r is not empty. []

**Orbit reduction.** Multiplying by a unit Lambda of Z_{l_r p}, permuting
coordinates and negating coordinates all preserve properness (witness b becomes
b Lambda^{-1}; gcd(l, Lambda w_i) = gcd(l, w_i)) and certification
(gcd(Lambda w_i, d) = gcd(w_i, d) for d | l). Choosing Lambda = lambda mod p and
Lambda = 1 mod l_r (CRT) maps the cascade of a representative r bijectively onto
the cascade of lambda r, as in the paper's Remark 2.3. So it is enough to run the
filtered cascade on one representative per level-1 orbit.

**Engine.** `lrc.c` implements the filter (`scascade`, `scascadebb`, and the
`shift` argument of `gate`): at every level l of the cascade, an improper lift
is dropped if `shift_ok` finds a d | l satisfying Lemma S. The gate JSON reports
`shift_removed_by_level` and `tuples_using_shift`, because a gate closed with the
filter's help proves p | v_1 ... v_k through Lemma C, not through J(k,p) = {}.
The C function is checked against the Python reference on random vectors, and
the filtered cascade against a brute-force Python cascade.

### 5.4 What this does and does not settle

Nothing in this section is computed yet. Lemma L explains why the tight orbits
that needed special fibre searches for 14 and 15 runners should be easier for 16
runners, and Lemma S is the 16-runner substitute for the paper's Lemma 4.6. The
prediction, its test and what counts as each outcome are in `PLAN.md`
(addendum 2), written before any k = 15 lifting result exists.

### 5.5 Third reading, written to break Section 5 (run 4)

A separate pass (again an AI agent, told to look for errors rather than confirm)
re-derived every step of 5.1-5.3 and the engine code that implements them. It
found no error. What it checked, so a human reader can check the same points:

- **Lemma L.** b = lambda^{-1} j (lp/D) needs D | l (so lp/D is an integer) and
  lambda a unit mod lp (gcd(lambda, l) = 1 and p does not divide lambda). The case
  gcd(lambda, l) = g > 1 uses that g divides every residue w_i mod lp, which holds
  because g | lp. Witness inequalities are non-strict (||t v_i|| >= 1/(k+1)),
  matching the paper's strict cover condition (k+1) d_p(av) < p.
- **2-adic conditions.** At level 32, for j odd, ||j w_i/32|| < 1/16 iff
  j w_i = 0 or +-1 mod 32: an even w_i that is not 0 mod 32 gives
  ||j w_i/32|| >= 2/32 = 1/16, so only odd coordinates (two bad j each) and
  multiples of 32 matter. Eight odd coordinates are needed to block all 16 odd j.
- **Lemma S.** Counting lattice points in an open arc: r points of a coset of
  (1/N)Z/Z in an open arc of length L satisfy (r-1)/N < L, so r <= ceil(LN) in both
  cases (LN an integer or not). All 15 entries of the k = 15 cost table were
  recomputed as g * ceil(N/8).
- **The gcd clause is the case e = 1 of Lemma S.** If gcd(l, w_j : j != i) = g > 1
  and v is primitive, then g does not divide v_i; with g' = gcd(v_i, g) and
  N = g/g' >= 2 the cost is g' ceil(2N/16) < g' N = g. So Lemma S with d = g,
  E = {i} gives the LR property. This is the argument Lemma C cites for the gcd
  clause, made explicit.
- **Lemma C and orbit reduction.** F'_0 needs no certification check (d | 1 is
  impossible), and the CRT unit Lambda exists because gcd(p, l_r) = 1.
- **Engine.** `gcd_proper` tests the prime factors of l (equivalent to
  gcd(l, ...) > 1); `shift_ok` computes g * ceil(2n/(K+1)) as
  g * ((2n + K) / (K + 1)) in integer division, which is the same number; the
  branch-and-bound lifter only re-tests times b not divisible by the level
  multiplier, which is valid because those are the old level's times, already
  covered by the improper parent.

## 6. Small covers and the choice of gate primes (run 4)

### 6.1 The gap

Let tau_k(p) be the fewest speed classes that cover all folded times (the
paper's tau(p)). Every level-one improper k-multiset contains an irredundant
cover on s classes, tau_k(p) <= s <= k. The paper's shortcut (its Sec. 4.1) is
that when tau_k(p) >= k - 1 it suffices to take every irredundant cover on k
classes and every irredundant cover on k - 1 classes plus one arbitrary class.
Our engine did exactly this, and flagged a gate incomplete
(`small_orbits_unhandled`) when a cover on <= k - 2 classes exists. For 15
runners the paper needed the general enumeration at 19 of its 71 primes (all
between 89 and 241). For 16 runners we did not yet know which primes need it.

A cover on s classes needs s m >= n with n = (p-1)/2 and m = floor((p-1)/16), so
tau_15(p) >= ceil(n/m) >= 8 for every p; that bound is far below 14, so only a
computation can tell which primes have tau_15(p) <= 13.

### 6.2 General completion (engine option `ext`)

**Claim.** Let T be the list of level-one tuples formed from every canonical
irredundant cover C (one per unit orbit, |C| = s <= k) followed by every
non-decreasing sequence of k - s classes in 1..n. Then every level-one improper
k-multiset is, after multiplication by a unit, sign changes and a permutation, a
member of T.

*Proof.* The support of an improper multiset covers all folded times. Removing
redundant classes one at a time leaves an irredundant cover C' inside the support,
with |C'| = s <= k. The cover search lists one representative C of the unit orbit
of C' (`test_c.test_covers_match_reference` and
`test_c.test_two_normalisations_agree` check this against brute force), so some
unit lambda has lambda C' = C after folding. lambda maps the other k - s elements
of the multiset to some multiset of folded classes, which T lists in
non-decreasing order. []

With `ext = 0` the same list is restricted to s >= k - 1, which is complete exactly
when tau_k(p) >= k - 1. `test_ext.py` checks the claim end to end: for (k, p) =
(8, 23), (9, 23), (4, 13) and (5, 23) it enumerates every k-multiset of classes by
brute force, keeps the improper ones, and checks that the unit orbits hit by T
are exactly the improper orbits, for both cover normalisations. At p = 23 with
k = 8 or 9 a class covers two times, {c, 2c} folded, and the six classes with
c = 1, 3, 4, 5, 6, 7 cover all eleven, so tau = 6 <= k - 2 and the old list is
provably incomplete there. The test checks that too.

**Cost.** A cover on s classes gives C(n + k - s - 1, k - s) tuples. For k = 15,
s = 13 and p = 401 that is C(201, 2) = 20,100 tuples per cover, so the general
completion is affordable only at primes with few small covers. The paper's
private-time branch (its Lemma 4.1) is cheaper; ours is simpler and is checked
exhaustively on small cases. Which primes need it is measured next.

### 6.3 Which primes need it (job `lrc16-tau-v1`)

`lrc tau K P maxsize` decides whether a cover on <= maxsize classes exists (stop at
the first irredundant cover found, with the paper's private-time bound q_s as a
pruning rule), and so gives tau exactly when it is <= maxsize. The job runs it

- for k = 14, maxsize 12, at all 71 primes of the paper's Table 2, which states
  tau(p) <= 12 for 89, 131, ..., 241 (19 primes) and tau(p) >= 13 for every prime
  from 239 to 569 except 241: an independent check of a published table;
- for k = 15, maxsize 13, at every prime from 17 to 1000: the list of primes
  where the old enumeration is complete (tau_15 >= 14), the smallest set of such
  primes whose log-sum passes 483.239, and the primes that need Section 6.2.

The pre-registered readings are in `PLAN.md`, addendum 3.

## 7. Tight sets for 16 runners (run 5)

### 7.1 Why tight sets matter for the gates

A set V of k speeds is **tight** if its best loneliness is exactly 1/(k+1): some t
has ||t v|| >= 1/(k+1) for all v in V, but no t does so with strict inequality.
In the published computations, the level-one orbits that survived every binary
lifting level were exactly reductions of tight sets: (1..13) and (1..11,13,24) for
14 runners, (1..14) for 15 runners (arXiv:2609.02604, Sec. 4). The reason is
simple. If V is not tight, its strict witnesses form a non-empty open set, which
contains an interval of some length delta > 0, and as soon as the grid spacing
1/(lp) is below delta, the reduction of V itself mod lp has a grid witness. A tight
set has no such interval. Its witnesses are isolated points, and its reduction
survives every level whose grid misses them.

So the question for 16 runners is: **which 15-speed sets are tight, and where
are their witnesses?** (This is a heuristic for which orbits persist, not a
theorem: the cascade follows residue classes, and a class contains many integer
vectors. It is the heuristic the published survivor lists fit.)

### 7.2 One-entry modifications: none when n + 1 is prime

Write [n-1] = {1, ..., n-1} (n runners, k = n - 1 speeds). Zhang
(arXiv:2608.13599 v3, Thm 1.2) classifies the tight sets of the form
([n-1] \ {r}) U {w} with w >= n and n >= 4: they are tight exactly when
(i) r | w and, with m = w/r and s = n - r, **gcd(r, b) > 1 for every integer b
with s <= b <= ms - 1** (the criterion of Goddyn and Wong, Thm 2.3 of their 2006
paper), or (ii) the set is one of Wills' two sporadic sets, at n = 5 and n = 6.

**Lemma N.** If n + 1 is prime, no one-entry modification of [n-1] (n >= 7) is
tight.

*Proof.* Case (ii) needs n in {5, 6}. In case (i), w >= n > r gives m >= 2. If
s = 1, then b = 1 is in [s, ms - 1] and gcd(r, 1) = 1. If s >= 2, then
b = s + 1 <= ms - 1 and gcd(r, s + 1) = gcd(r, n + 1 - r) = gcd(r, n + 1) = 1,
because 1 <= r < n + 1 and n + 1 is prime. []

For 16 runners n + 1 = 17 is prime, so **(1..15) is the only tight set among
[15] and all its one-entry modifications.** The same criterion, applied without
Lemma N, gives exactly the published survivors one and two runners earlier:

| runners n | tight one-entry modifications (r, m) | set | published binary survivors |
|---|---|---|---|
| 14 | (12, 2) only | (1..11,13,24) | (1..13), (1..11,13,24) |
| 15 | none | | (1..14) |
| 16 | none (Lemma N) | | to be measured (`lrc16-shift-v1`) |

`test_tight.py` checks the table by brute force over r < n and 2 <= m <= 60, and
Lemma N for every n < 200 with n + 1 prime.

**Two-entry modifications.** Zhang's census (Thm 6.10: 8 <= n <= 140, inserted
speeds n <= w_1 < w_2 <= 8n, 447,545 cases, exact arithmetic) found tight sets only
at n = 8 ({1,4,5,6,7,11,13}) and n = 74 (Goddyn and Wong's example). So for 16
runners there is none with inserted speeds up to 128 either. We know of no tight
15-speed set other than (1..15). We do not claim there is none.

The witnesses of (1..15) include t = a/16 (a odd), which lie on the grid from
level 16 on. That is the content of Lemma L.

### 7.3 (1..13,15,28) is not tight

This is the 16-runner analogue of the 14-runner survivor (1..11,13,24) (replace
k - 1 by 2(k - 1)), and run 3 wrongly called it tight. In Zhang's terms it is
n = 16, r = 14, m = 2, s = 2, and b = 3 is coprime to 14. An explicit strict
witness: **t = 993/2800**. With 2800 t v mod 2800 folded to [0, 1400], the
distances are 993, 814, 179, 1172, 635, 358, 1351, 456, 537, 1270, 277, 716, 1091,
895 (speeds 1-13 and 15) and 196 (speed 28), all above 2800/16 = 175.

More is true: **every t in the open interval (5/14 - 1/336, 5/14 - 1/448)**, of
length 1/1344, is a strict witness. Write t = 5/14 - e. Then 5v mod 14 is +-1
only for v = 3 (distance 1/14 - 3e, above 1/16 iff e < 1/336) and v = 11 (distance
1/14 + 11e). Speed 28 has 28t = 10 - 28e, at distance 28e, above 1/16 iff
e > 1/448. Every other speed has 5v mod 14 at distance at least 2/14 from 0 and
moves by at most 15e < 15/336, which leaves it above 2/14 - 15/336 > 1/16.
`test_tight.py` checks the witness, 199 interior points and both endpoints in
exact arithmetic.

So the reduction of this vector itself mod lp has a grid witness as soon as
1/(lp) < 1/1344. At level 16 that is every p > 84, which includes every planned
gate prime. Prediction P2 (`PLAN.md`, addendum 2) stands, now for two reasons.

### 7.4 What this predicts

If the heuristic of 7.1 holds, and (1..15) is the only tight 15-speed set that
reduces to a level-one improper orbit at the gate primes, then binary lifting to
level 32 should leave **no survivors at all** at the 16-runner gates. That
would make 16 runners structurally simpler than 14 and 15, which both needed
separate fibre searches. `PLAN.md` addendum 4 pre-registers this as P4, before
any 16-runner lifting result exists.

## 8. Binary lifting of one orbit, uniformly in p (run 6)

Sections 5 and 7 predict that the orbit of (1..15) dies by level 16, and jobs
`lrc16-shift-v1` and `lrc16-engine2-v1` test that at ten pilot primes, one prime
at a time. This section separates the prime from the problem, so one finite
computation (`uniform.py`, job `lrc16-uniform-v1`) answers the question at
every gate prime together.

### 8.1 Lemma D: where the prime enters

Fix k, a level-one vector s of positive integers with p > max s_i, and a level
L coprime to p. A lift of s to level L is w in Z_{Lp}^k with w_i = s_i (mod p);
put z_i = w_i mod L. Write 1 = AL + Bp. For b in Z_{Lp},

  b w_i / (Lp) = b w_i A / p + b w_i B / L = (bA mod p) s_i / p + (bB mod L) z_i / L  (mod 1),

and b -> (beta, sigma) = (bB mod L, bA mod p) is a bijection Z_{Lp} -> Z_L x Z_p
(B is a unit mod L because Bp = 1 mod L, A is a unit mod p, then CRT). So:

**Lemma D.** w is proper at level L iff the gcd clause holds (for L a power of
2: at most one z_i is odd) or there are beta in Z_L and t in (1/p)Z with
||beta z_i / L + t s_i|| >= 1/(k+1) for every i.

The prime enters only through the grid (1/p)Z of times t.

### 8.2 Lemma U: two prime-free sets that sandwich the true survivors

For fixed beta and z, let G_beta(z) be the set of strict witnesses,
{t : ||beta z_i / L + t s_i|| > 1/(k+1) for all i}. It is a finite union of open
arcs, and every endpoint is a point where some ||beta z_i/L + t s_i|| equals
1/(k+1), a rational whose denominator divides Q = lcm(L, k+1) lcm(s_1, ..., s_k).

For P a positive integer or infinity, call z **P-killed at level L** if
(a) at most one z_i is odd (L >= 2), or (b) some beta has
||beta z_i / L|| >= 1/(k+1) for all i (the time t = 0), or (c) for some beta,
G_beta(z) has a component longer than 1/P (for P = infinity: G_beta(z) is not
empty). Let U_P(1) = {s} if s is not P-killed at level 1 and empty otherwise,
and let U_P(2L) be the lifts to level 2L of members of U_P(L) that are not
P-killed. Let J_p(L) be the same cascade at one prime p, with "proper" in place
of "P-killed" (the cascade of the published method, restricted to this orbit).

**Lemma U.** (i) For every prime p >= P with p > max s_i: J_p(L) is contained
in U_P(L). (ii) For every prime p > max s_i that does not divide Q: U_inf(L) is
contained in J_p(L).

*Proof.* (i) If z is P-killed and p >= P, then w is proper: (a) is the gcd
clause; (b) is the time with sigma = 0; in (c), an open interval longer than
1/P >= 1/p contains a point of (1/p)Z, which is a strict witness. (ii) If w is
proper, z is inf-killed: the gcd clause is (a); a witness with sigma = 0 is (b);
a witness with sigma != 0 is t = sigma/p, whose denominator is p, so t is not an
arc endpoint (those have denominators dividing Q, and p does not divide Q). So
every inequality at t is strict, t lies in G_beta(z), and (c) holds. Both
cascades lift only their own survivors, so induction over the levels gives both
inclusions. []

For s = (1, ..., 15), Q has prime factors 2, 3, 5, 7, 11, 13 only. So **U_251
bounds the survivors from above at every prime p >= 251** (every planned gate and
pilot prime), and **U_inf bounds them from below at every prime p >= 17**.

### 8.3 Reductions used by the search

- **Units.** z -> lambda z (lambda odd) maps P-killed vectors to P-killed
  vectors (beta -> beta lambda^{-1}), and is the action of the unit
  Lambda = lambda (mod L), 1 (mod p). One representative per class is kept (the
  lexicographic minimum).
- **Only odd beta are new at level 2L.** For beta = 2b,
  2b z'_i / (2L) = b z_i / L (mod 1), the parent's positions at level L, where the
  parent was not killed. (The direct check `uniform_killed` tests every beta;
  the tests compare it with the reduced search.)
- **Branch and bound.** Each coordinate of a level-L parent has two lifts, z_i
  and z_i + L. For each odd beta the circle is cut at every arc endpoint of both
  choices. A choice covers a set of cells (a bitmask) and may make t = 0 bad. A
  partial choice is dropped when, for some beta, the remaining coordinates
  cannot cover every cell longer than 1/P together with the point t = 0. At the
  leaves the check is exact: adjacent uncovered cells are merged (their common
  endpoint is not an endpoint of a chosen arc, so it is a strict witness too).

All times are integers in units of 1/Q, so nothing is rounded.

### 8.4 Checks (`test_uniform.py`)

- The cell masks agree with exact Fraction evaluation at every cell midpoint,
  and every arc endpoint is at distance exactly 1/(k+1) (random s, z, L, beta).
- The merged-run test agrees with a plain circular scan (random masks).
- **The sandwich itself:** U_inf(L) is in J_p(L), and J_p(L) is in U_p(L), level
  by level, with J_p computed by brute force over every time b in Z_{Lp}
  (`lrc_ref.proper`): s = (1,2,3) at p = 11, 13, 29, 101 up to level 16;
  s = (1..7) at p = 29 up to level 8 (the 8-runner analogue, where k + 1 = 8 is
  also a power of 2); random 3- to 5-speed sets.
- Branch and bound agrees with the direct check of all 2^k lifts.
- (1..13,15,28) is killed at level 1 (P = infinity and P = 1500: Section 7.3's
  interval has length 1/1344), (1..15) is not; the linear lift (1..7) mod 8 is
  killed at level 8 and (1..7) mod 4 is not at level 4 (Lemma L analogue).

### 8.5 What the computation decides

**Linear lifts.** If z = lambda s (mod L): for lambda even all z_i are even
(gcd clause); for lambda odd and s = (1..15), Lemma L kills z at level 16 by
t = 0. So every member of U_P(16) for s = (1..15) is a nonlinear lift.

**Why no binary level can kill (1..k) when k + 1 is not a power of 2.** For
s = (1..k) and lambda odd, the lift z = lambda s (mod L) lies in U_P(L) for every
P and every binary level L. *Proof.* The positions are i x with
x = beta lambda / L + t. If ||i x|| >= 1/(k+1) for i = 1..k, then the k + 1 points
0, x, 2x, ..., kx are pairwise at distance >= 1/(k+1) (their differences are
i x with 1 <= i <= k), so the k + 1 gaps between them, which sum to 1, all equal
1/(k+1); the points form the group (1/(k+1))Z/Z and x = j/(k+1) with
gcd(j, k+1) = 1. So G_beta is empty (equality, never strict), and t = 0 is a
witness only if beta lambda / L, a dyadic rational, equals j/(k+1) in lowest
terms, which needs k + 1 to be a power of 2. And the odd i give odd z_i, so the
gcd clause fails. [] For k = 13, 14 (14 and 15 runners) this is the prime-free
reason the published proofs needed separate fibre searches at levels 14 and 15.
It doubles as a sanity check of the code (S1 in `PLAN.md`, addendum 5). For
k = 15, k + 1 = 16 and the same argument shows the linear lifts are killed
exactly from level 16 on (Lemma L).

**For 16 runners.**
- If U_251(16) is empty for s = (1..15), then for **every prime p >= 251** no
  lift of the orbit of (1..15) survives level 16. That proves prediction P1 at
  all ten pilot primes without using `lrc.c`, and removes this orbit from every
  16-runner gate at once.
- If U_inf(16) is not empty, its members survive level 16 at **every prime
  p >= 17**, so P1 is false at every pilot prime, and those lifts need level 32
  (computed by the same job) or another argument.
- If U_inf(16) is empty but U_251(16) is not, the answer depends on the prime
  for the listed lifts only, and the per-prime engine settles them.

**Evidence from 8 runners.** Rosenfeld's 8-runner proof (arXiv:2509.14111,
Lemma 6) works at the single level k + 1 = 8: at each of his primes
(31, 37, 43, ..., 163) every level-8 vector that fails the gcd clause is proper,
and he reports that every prime p >= 31 except 41 works. For k = 7, k + 1 = 8 is
a power of 2, as 16 is for k = 15, so this is the closest published analogue of
prediction P1. By Lemma U(ii) it also implies that U_inf(8) is empty for
s = (1..7), which the job checks (X2 in `PLAN.md`).

The same job runs (1..13,15,28) (prediction P2) and, as sanity checks, (1..14),
(1..13), (1..11,13,24) and (1..7). Its readings are pre-registered in `PLAN.md`,
addendum 5.
