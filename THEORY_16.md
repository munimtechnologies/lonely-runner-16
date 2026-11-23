# THEORY, Section 16: the uniform cascade at non-binary levels

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Written 2026-11-23 (run 18), before any result
of the job it sets up.

## 16.0 Why

The 14- and 15-runner proofs (Allikvere, arXiv:2609.02604) lift every level-one
orbit through the binary levels 2, 4, ..., 32. Three tight orbits survive every
binary level: a13 = (1..13) and b13 = (1..11,13,24) for k = 13, and a14 = (1..14)
for k = 14. THEORY.md 8.5 proves that this must happen, at every prime, whenever
k + 1 is not a power of 2. The paper therefore runs two extra searches **at every
gate prime**. One is at level 14 for a13 and b13 (Section 4.3: 7^13 lifts of each
improper level-2 member). The other is at level 15 for a14 (Section 4.4, split as
15 = 3 * 5 by its Lemma 4.5). At each of its primes, every witness-free tuple then
fails the gcd condition (Definition 2.1(a)).

Section 8 (Lemma U) and Section 15 (Lemmas E, T, R) do the binary cascade once
for all primes. Their proofs never use that L is a power of 2. This section
states the general version. `uniform_nb.py` implements it, and job `lrc-nb`
(PLAN_addendum10.md) applies it to the three tight orbits. If the job succeeds,
each per-prime fibre search becomes a single prime-free computation that holds at
every prime above an explicit bound. It also re-checks the paper's Section 4.3-4.4
outcome independently at all of its gate primes.

## 16.1 Setting (any level L)

k speeds, a level-one vector s, a prime p dividing neither
Q = lcm(L, k+1) lcm(s) nor any s_i, and a level L with gcd(L, p) = 1. A lift is
w in Z_{Lp}^k with w = s (mod p); write z = w mod L. As in `uniform.py`, the CRT
writes a time b in Z_{Lp} as (beta, sigma) in Z_L x Z_p, so

    b w_i / (Lp) = beta z_i / L + t s_i (mod 1),   t = sigma / p.

**Lemma N1 (units).** For a unit lambda of Z_L, z and lambda z are proper or
improper together. *Proof.* Let Lambda be the unit of Z_{Lp} with Lambda = lambda
(mod L) and Lambda = 1 (mod p). Then Lambda w lifts the same s, and b -> b Lambda^{-1}
maps the witnesses of Lambda w onto those of w. The gcd condition depends only on
which coordinates a prime d | L divides, and multiplying by a unit does not change
that. []

**Lemma N2 (gcd clause).** Definition 2.1(a) says gcd(L, w_j : j != i) > 1 for
some i. This holds iff some prime d | L divides every z_j except at most one,
since w_j = z_j (mod d) for d | L. For L = 2^a this is `uniform.gcd_clause`.

With these, "P-killed" (gcd clause, exact witness at t = 0, or an open interval of
strict witnesses longer than 1/P) and U_P(L), U_inf(L) are defined exactly as in
Section 8. **Lemma U holds verbatim:** U_inf(L) <= J_p(L) <= U_P(L) for every prime
p >= P as above. The proof only uses that t = j/p (p not dividing j) is never an
arc end point, because p does not divide Q. Lemmas A, E, T and R of Section 15
hold verbatim too: `thresh.proper_at` and `thresh.threshold` apply unchanged to
`uniform_nb.lift_info`.

## 16.2 Divisor chains

**Lemma N3 (monotone).** Let L' | L. If the reduction z mod L' is P-killed at
level L', then z is P-killed at level L, and if it is proper at p, so is z.
*Proof.* Take beta = (L/L') beta'. Then beta z_i / L = beta' z_i / L' (mod 1), so a
witness (beta', t) gives the same positions. An open interval keeps its length,
and t = 0 stays exact. A prime d | L' also divides L, and the same coordinates
are divisible by it. []

So at any prime the improper lifts at level L are exactly the improper lifts of
improper parents along any chain 1 | L_1 | L_2 | ... | L. **Lifting from L to cL
only needs the betas that are not multiples of c**, because the others repeat
positions the parent already failed with (`lift_children`).

**Lemma N4 (CRT combination; the uniform form of the paper's Lemma 4.5).** Let
gcd(L1, L2) = 1. A class at level L1 L2 that is not P-killed has both reductions
not P-killed (N3). Up to a unit, it equals CRT(a, mu b) with a, b canonical
members of U_P(L1), U_P(L2) and mu a unit mod L2 (take a unit of Z_{L1 L2} that
is lambda^{-1} mod L1 and 1 mod L2). Only betas divisible by neither L1 nor L2
need testing (`combine`).

The job computes U(L) twice, by the chain f1 -> f1 f2 and by `combine`. They are
independent routes to the same set (check C1).

## 16.3 What the computation can establish

Let s be one of a13, b13 (L = 14) or a14 (L = 15), and P0 = 199 or 239. If
1. U_P0(L) is computed without a cut,
2. at every prime P0 <= p <= B the exact set J_p(L) = {z in U_P0(L) : improper
   at p} is empty, and
3. P*_L = max over U_P0(L) of 1/(longest witness interval) is at most B,

then **for every prime p >= P0, every lift of the orbit of s to level L is
proper**, and the paper's level-L fibre search for that orbit is unnecessary at
every prime p >= P0. For a14 the paper's 52 tau >= 13 gates are exactly the
primes 239..569 except 241. For a13 and b13 the paper's second gate set P_13 also
has five primes below 199 (83 to 191), which P0 = 199 leaves out. The condition "p divides neither Q nor any s_i" holds for every
p >= 199, because every prime factor of Q and of the speeds is at most 13.

**Consistency with the paper.** By Lemma U, U_inf(L) <= J_p(L) at each of the
paper's gate primes, and the paper reports J_p(L) empty after the gcd test.
So **U_inf(L) must be empty** for all three orbits. If it is not, either our
code or the paper's search is wrong, and either way this needs a bug hunt before
anything is said.

This is a step in re-checking the published 14- and 15-runner proofs. It does
not re-check their level-one generation, which is where most of the cost is.
It is not a proof of any new case.

## 16.4 Tests (`test_uniform_nb.py`)

- At binary levels the general code reproduces `uniform.cascade` exactly.
- The sandwich U_inf(L) <= J_p(L) <= U_p(L) holds against a brute force over all
  times of Z_{Lp} with the general gcd clause. This is checked for chains
  [3, 5], [5, 3], [2, 3], [3, 2], [2, 5], [2, 7], [5] and [3], for k = 3, 4 and 5
  (including (1..5) at level 6 = k + 1), with and without the gcd clause.
- Branch and bound equals direct enumeration. `combine` equals both chain orders.
- `thresh.proper_at` on `uniform_nb.lift_info` equals the brute force at levels
  3, 5, 6 and 15, and is proper above every threshold.
- The linear lifts of (1..4), (1..5), a13, b13 and a14 are killed at the level
  k + 1 (t = 0) and survive at its proper divisors (THEORY.md 8.5).
