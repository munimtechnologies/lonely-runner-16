# THEORY, Section 15: from the uniform cascade to every prime

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Written 2026-11-22 (run 16), after
`lrc16-uniform-v1` reported (graded in `RESULTS_run16.md`) and before any result of
`lrc16-uniform-v2`.

## 15.0 Why this section exists

`lrc16-uniform-v1` found that the prime-free upper cascade U_251 does **not** empty
by level 16 for s = (1..15): U_251(16) has 9 unit classes and U_251(32) has 2
(prediction P5 failed). The lower cascade U_inf is empty at level 16 (P5b held).
So every lift that U_251 keeps does have strict witnesses, but each of its
witness intervals is at most 1/251 long, and Lemma U alone cannot tell whether a
grid point j/p falls into one. This section turns the uniform computation into an
exact answer at each prime, and into a uniform answer above an explicit bound.

Notation as in `THEORY.md` Section 8: k = 15, a level-one vector s, a binary level
L, a lift class z in (Z_L)^k up to odd unit multiples, Q = lcm(L, k+1) lcm(s); for
beta in Z_L the closed bad arcs A_{i,beta} = {t : ||s_i t + beta z_i / L|| <= 1/(k+1)};
`uniform.Cells` cuts the circle at all their end points.

## 15.1 Lemma A (cells are components)

Two adjacent cells are never both uncovered. *Proof.* Their common end point E
is an end point of some arc A (cells are cut only at arc end points). If E is the
start of A, the cell to the right of E lies in A; if E is its end, the cell to the
left does (arcs have positive length 2/((k+1)s_i) and every end point is a cut).
So the open set of strict witnesses for a given beta is exactly the union of the
uncovered open cells, and each uncovered cell is one of its components. []

(`uniform.Cells.killed` merges runs of uncovered cells; by Lemma A every run is a
single cell, so `thresh.killed_uniform` returns the same answer, which
`test_thresh.Threshold.test_matches_uniform` checks.)

## 15.2 Lemma E (exact test at one prime)

Let p be a prime dividing neither Q nor any s_i. The lift z is proper at p iff
(a) the gcd clause holds (at most one odd z_i), or (b) for some beta, t = 0 is an
exact witness (no i has ||beta z_i / L|| < 1/(k+1)), or (c) for some beta, some
uncovered cell (a/Q, b/Q) contains a point j/p.

*Proof.* By the CRT decomposition of `uniform.py` (b <-> (beta, sigma), t =
sigma/p), w is proper iff the gcd clause holds or some (beta, t) with t in
(1/p)Z is a witness. t = 0 is (b). For t = j/p with p not dividing j: j/p is not a
rational with denominator dividing Q, so it is not an arc end point; it is a
witness iff it lies in no closed bad arc, i.e. in an uncovered open cell. []

Test (c) is one integer comparison per cell: j = floor(a p / Q) + 1, and the cell
contains j/p iff j Q < b p. `thresh.proper_at` implements it;
`test_thresh.ExactPerPrime` compares it with a brute force over all of Z_{Lp}
(k = 3 and 4, L up to 8, several primes, about 4,000 cases).

## 15.3 Lemma T (kill threshold)

For a lift z with neither (a) nor (b), let lambda(z) be the length of its longest
uncovered cell over all beta, and P*(z) = 1/lambda(z) (infinity if there is no
uncovered cell). Then z is proper at every prime p > P*(z) that divides neither Q
nor any s_i, and z is killed in U_P exactly when P > P*(z).
*Proof.* An open interval longer than 1/p contains a point j/p, and j != 0 mod p
because the cell does not contain an exact multiple of 1 (t = 0 is not a witness
when (b) fails, so 0 lies in a bad arc). The second claim is the definition of
U_P with Lemma A. []

For a level, write P*_L = max of P*(z) over z in U_251(L) (0 if U_251(L) is
empty). Since the even betas of a child repeat its parent's cells,
P*(child) <= P*(parent), so P*_L does not increase with L.

## 15.4 Lemma R (the exact cascade inside the uniform one)

For a prime p >= P dividing neither Q nor any s_i,
J_p(L) = { z in U_P(L) : z is improper at p }.

*Proof.* "Contained in U_P(L)" is Lemma U. Conversely the true cascade at p keeps
exactly the improper lifts of improper parents, and an improper lift always has
an improper parent: if the parent w' (level L/2) had a witness b, then 2b is a
witness of every lift w of w' (2b w_i / (Lp) = b w'_i / (Lp/2) mod 1), and the
gcd clause is the same at all levels L >= 2 (parity of the coordinates). []

`job_uniform2.py` re-checks the parent property at every prime (check S6), and
`test_thresh.PrimeLevels` compares Lemma R with a brute-force cascade.

## 15.5 Consequence (what the job can establish)

Let B be the largest prime checked. If, for the orbit of s,
1. U_251 is computed to level L_max without a cut;
2. at every prime 251 <= p <= B the exact cascade is empty by level L_1; and
3. P*_{L_2} <= B for some L_2 <= L_max,

then for **every** prime p >= 251, J_p(max(L_1, L_2)) is empty: the orbit of s
has no improper lift at that level, at any prime a 16-runner gate could use. For
14 and 15 runners the tight orbits (1..13), (1..11,13,24) and (1..14) survive every
binary level and need separate fibre searches (arXiv:2609.02604). For 16 runners
this would show the tight orbit (1..15) needs none. The statement is conditional
on Lemma U (`THEORY.md` 8), Lemmas A, E, T, R above, and the code; it is a step of
the plan (`PLAN.md` step 4), not a proof of any case of the conjecture.

## 15.6 A heuristic for what to expect (not used by any claim)

The two lifts left in U_251(32) are (1..13, 0, 15) and (1..13, 16, 15) mod 32 for
s = (1..15), and (1..13, 15, 0) and (1..13, 15, 16) for s = (1..13, 15, 28). In
both, every coordinate except one is linear, so with u = beta/L + t the conditions
read ||i u|| >= 1/16 for i in S' = {1..13, 15}, plus one condition on the free
coordinate that depends on u through beta = m p^{-1} mod L (u = m/(Lp)). S' has 14
speeds, so by the 15-runner theorem it has a witness with gap 1/15 > 1/16, hence
witness intervals of positive length, of rough size (1/15 - 1/16)/15 = 1/3600.
Each such interval holds about Lp/3600 grid points u, each passing the free
coordinate's condition with probability about 7/8 if beta behaves randomly.
This suggests (a) the orbit dies at every prime by level 64 or 128, and (b)
P*_L is of order a few thousand, so B must reach that far. Both are tested in
`PLAN_addendum9.md`, not assumed.
