# Section 10: the dual cap, a sharper flag bound for 15 and 16 runners (run 10, 2026-11-22)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
**No human expert has checked this yet.** The optimisation in Proposition 10.2 is
solved exactly (rational arithmetic) by `capped.py` and checked by `test_capped.py`,
which also checks the structural lemma against a brute-force vertex enumeration in
small dimensions, the identity behind Lemma 10.1 on explicit lattices, and
Lemma 10.4 on a grid that contains its maximisers.

Notation follows Allikvere, arXiv:2609.02604, Section 3 (summarised in `THEORY.md`
Sec. 1): n speeds, d = n - 1, H = v^perp, P the orthogonal projection onto H,
Lambda = P Z^n, q_k = 1 + 2u_k - u_k^2 with u_k = v_k / max v, the ellipsoid
E = P Q^(1/2) B_2^n, and t_i = ||b_i*||_E^2 the squared Gram-Schmidt lengths of a
basis of Lambda in the inner product of E. The flag bound minimises prod t_i
subject to

- (P_r) t_1 + ... + t_r >= B_r = (2r / ((n+1)(n+1-r)))^2 for r = 1..d (Proposition 3.4),
- (R_i) t_{i+1} >= (3/4) t_i (Lemma 3.5, a KZ basis),

and the minimum is K_n = prod c_r with c_r = B_r - B_{r-1}, attained at t = c
(Lemma 3.6). `COST_addendum1.md` showed that no further *KZ* inequality can raise
this minimum, because an orthogonal lattice with profile c is itself KZ. This
section adds an inequality of a different kind: an arithmetic one. It uses the fact
that Lambda is the projection of Z^n, so its dual lattice is the lattice of integer
relations of v.

## 10.1 The dual cap

**Lemma 10.1.** Let v in Z_{>0}^n be primitive with distinct entries. For every
basis b_1, ..., b_d of Lambda,

    t_d = ||b_d*||_E^2 = 1 / (sum_k q_k h_k^2) < 1/3,

where h in Z^n is the integer relation (h . v = 0) with h . b_i = 0 for i < d and
h . b_d = 1.

*Proof.* (i) The dual of Lambda = P Z^n, for the standard inner product on H, is
Z^n intersected with H: for h in H and x in Z^n, h . Px = h . x, and h . x is an
integer for every x in Z^n exactly when h is in Z^n. So the linear functional
phi(x) = a_d (the last coordinate in the basis b) is x -> h . x for an integer
relation h of v, and h is nonzero.

(ii) In the Euclidean space (H, <.,.>_E), phi vanishes on b_1, ..., b_{d-1}, so its
Riesz vector is a multiple of b_d*. From phi(b_d) = 1 and <b_d*, b_d>_E = t_d,
the Riesz vector is b_d*/t_d, so the dual norm of phi is 1/sqrt(t_d).

(iii) The dual norm of a functional y . x on H, for the norm with unit ball E, is
the support function h_E(y) = sup over g in B of y . P Q^(1/2) g =
||Q^(1/2) P y||_2, which is (sum_k q_k y_k^2)^(1/2) for y in H (this is the formula
in the proof of Allikvere's Lemma 3.1). With (ii): sum_k q_k h_k^2 = 1/t_d.

(iv) A nonzero integer relation h of a vector with distinct positive entries has
sum h_k^2 >= 3. It has a positive and a negative entry. If it has exactly two
nonzero entries and both are +-1, then v_a = v_b, which is excluded. Otherwise it
has three nonzero entries or an entry of size at least 2. Finally q_k > 1 for every
k, so sum q_k h_k^2 > sum h_k^2 >= 3. []

A counterexample to LRC(n) may be assumed to have distinct speeds: repeated speeds
leave m < n distinct values with the same loneliness, and LRC(m), which the flag
bound assumes anyway, gives at least 1/(m+1) > 1/(n+1). So the cap t_d < 1/3 can be
added to the flag-bound minimisation.

**Why it bites.** The old minimiser has t_d = c_d. For n = 15, c_14 = 17/36 = 0.472
and for n = 14, c_13 = 7/15 = 0.467: both are above 1/3. The orthogonal lattice that
showed KZ facts cannot help (`COST_addendum1.md`) has a dual vector of squared
E*-norm 1/c_d < 3, so it is not the lattice of any vector with distinct speeds.

## 10.2 The capped minimum

**Proposition 10.2.** Let n be 14 or 15. Every t in (0, infinity)^d satisfying all
(P_r), all (R_i) and t_d <= 1/3 has

    prod t_i >= K_n kappa_n,  kappa_15 = 12150/9163 = 1.32598...,  kappa_14 = 1369/1029 = 1.33042...

with equality at t = (c_1, ..., c_{d-2}, x, (3/4)x), x = (4/7)(c_{d-1} + c_d):
for n = 15, (t_13, t_14) = (5/14, 15/56); for n = 14, (t_12, t_13) = (37/105, 37/140).
(The last two lengths merge into one geometric block, and the cap is not active
at the minimiser.)

*Proof.* Write z_i = t_i / rho^(i-1) with rho = 3/4, so that (R_i) says z is
nondecreasing. The feasible set is a polytope: z_1 = t_1 >= B_1 > 0 and z is
nondecreasing, so every t_i > 0; and t_i <= (4/3)^(d-i) t_d <= (4/3)^(d-i)/3. The
objective sum log t_i is concave, so its minimum over the polytope is attained at a
vertex. Group the indices into maximal blocks on which z is constant.

*Structural lemma.* If c_{r+1} > rho c_r for every r (true here: c is increasing),
then at every feasible point no prefix constraint P_r is active with r strictly
inside a block. Indeed, if P_r is active then t_r = B_r - T_{r-1} <= c_r, and if
r+1 is in the same block then t_{r+1} = rho t_r <= rho c_r < c_{r+1}; but P_{r+1}
needs t_{r+1} >= B_{r+1} - T_r = c_{r+1}.

So at a vertex with k blocks, the active constraints are the within-block ratio
equalities (d - k of them) plus k independent constraints among the block-end
prefixes P_{e_1}, ..., P_{e_k} = P_d and the cap C. In the block values these are
lower-triangular (P_{e_j} involves blocks 1..j) and C involves only block k. Since
P_d - P_{e_{k-1}} is a multiple of C, the only independent choices are: (A) all
block-end prefixes; (B1) C and all except P_d; (B2) C and all except P_{e_{k-1}}.
For each of the 2^(d-1) block patterns these three systems have explicit
solutions. `capped.py` computes all of them in exact rational arithmetic, keeps the
feasible ones and takes the smallest product. The minimum is the stated value. []

A second check that does not use the structural lemma: `capped.py` also enumerates
the vertices by brute force (every d-subset of the 2d constraints, solved exactly)
for n = 5, 6, 7 with caps that bind, and the test requires both methods to give the
same minimum. With the cap removed (U = 10), the block method returns K_n exactly
for n = 14 and 15, which is Allikvere's Lemma 3.6.

By hand, for n = 15: case (A) with the block {13, 14} costs a factor
(5/14)(15/56) / (c_13 c_14) = 12150/9163. The best case-(B2) vertex, t_14 = 1/3 and
t_13 = 5/8 - 1/3 = 7/24, costs 7/72 / (187/2592) = 1.3476. Every other vertex costs
more.

## 10.3 What it gives

**Corollary 10.3.** Under Allikvere's hypotheses, covol_E(Lambda)^2 >= K_n kappa_n,
so A_n becomes A_n kappa_n^(-1/2) in his Theorem 3.8, and the bound on
log(v_1 ... v_n) drops by (n/2) ln kappa_n:

| runners | n | (n/2) ln kappa_n | gate target before | gate target after |
|---|---|---|---|---|
| 15 | 14 | 1.9985 nats | 401.9846 (Allikvere, Cor. 3.11) | 399.986 |
| 16 | 15 | 2.1162 nats | 483.239 (`THEORY.md`) | 481.123 |

For 16 runners this is worth about a third of one gate prime near p = 800
(ln 800 = 6.68). It is a small saving, but it costs no computation and it is the
first improvement of the flag bound that uses arithmetic rather than KZ geometry.
The same idea could give more: any lower bound m > 3 on the squared E*-length of
the shortest integer relation of a counterexample caps t_d at 1/m. For example, a
proof that a counterexample's speeds contain no v_c = v_a + v_b would give m = 4.
We do not have such a proof.

## 10.4 A remark: the hyperplane step cannot add more here

Proposition 3.4 for r = d - 1 uses Lemma 3.3 on the hyperplane V = span(v, z_1, ...,
z_{d-1}) = h^perp. That h is exactly the relation of Lemma 10.1. For hyperplanes the
optimal constant is exact:

**Lemma 10.4.** For a primitive h in Z^n that is not a multiple of a unit vector,
with L = ||h||_1, the largest delta such that some s in h^perp has
||s_k|| >= delta for all k is 1/2 when L is even and 1/2 - 1/(2L) when L is odd.

*Proof.* Write s_k = 1/2 + z_k + x_k with z_k an integer and |x_k| <= 1/2 - delta.
Then h . x = -(sum h_k / 2 + h . z). If L is odd, so is sum h_k, the right side is
in 1/2 + Z, and |h . x| >= 1/2, so (1/2 - delta) L >= 1/2. Conversely, since h is
primitive, h . z takes every integer value, so z can be chosen with
sum h_k / 2 + h . z = 1/2 (L odd) or 0 (L even); then x_k = -sign(h_k)/(2L)
(L odd) or x = 0 (L even) works. []

Lemma 3.3 gives 1/3 for hyperplanes. Lemma 10.4 improves on this when L >= 4. But
at the capped minimiser sum q_k h_k^2 = 1/t_d = 56/15 < 4, which forces
sum h_k^2 = 3 and so L = 3, where Lemma 10.4 also gives 1/3. So it adds nothing to
Proposition 10.2. It would matter only in a regime where t_d < 1/6 (where L >= 4),
which the minimiser avoids. `test_capped.py` checks Lemma 10.4 exactly for every
h = (h_1, h_2, 1) with |h_1|, |h_2| <= 2.

## 10.5 Credit and status

The flag bound, the prefix inequalities, the KZ step and the ellipsoid are
Allikvere's (arXiv:2609.02604). The duality between projections of Z^n and
sections of Z^n is standard. We found no use of the dual lattice (the integer
relations) in the flag bound in the 2025-26 Lonely Runner papers. Beck and Everett
(arXiv:2609.06259) prove that a short relation exists, which is an upper bound on
the dual minimum, the opposite direction to what is used here. This needs a
human check before anyone relies on it. The gate target in `COST.md` is left at
483.239 until then. If the check passes, 481.123 replaces it.
