# THEORY: the 16-runner case (n = k = 15 speeds)

MV2 of Munim, Inc. Text CC BY 4.0. Written 2026-11-21 by AI agents working in
MV2's name. **No human expert has checked this yet.** Every inequality in
Sections 1-3 is re-checked in exact rational arithmetic by
`bounds.shape_n15_exact()` and `bounds.check_quartic_factor_n15()` (tests in
`test_bounds.py`); Section 5 is checked by `test_shift.py` and `test_c.py`;
Section 6 by `test_ext.py`.

Sections 1-3 carry Section 3 of J. Allikvere, *Fourteen and fifteen lonely runners*,
arXiv:2609.02604 v2 (the "flag bound") from n = 14 to n = 15 speeds, i.e. from 15 to
16 runners. Everything structural is the paper's. What is new here is the
n = 15 case of the shape lemma (the paper's Lemma 3.7 is stated and proved only for
n = 13, 14) and the resulting constants. Section 5 (added in run 3) prepares the
argument for the orbits that survive binary lifting. Section 6 (run 4) closes the
gap left by primes whose level-one covers can be small.

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
   all of them is measured by `lrc16-shift-v1`.
3. Primes where tau_15(p) <= 13 (covers on at most 13 classes exist). Section 6
   makes their gates complete, at a cost, and job `lrc16-tau-v1` finds which
   primes they are.
4. An independent check of this note by a human reader, or a Lean/interval
   formalisation of Sections 2, 5 and 6.

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
tight vector whose tight witness has denominator 16, for example (1,...,13,15,28)
(at t = a/16 with a odd, 28a/16 is 1/4 or 3/4 mod 1).

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
