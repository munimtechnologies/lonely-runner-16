# Section 12: exact loneliness constants of the flag subspaces cannot sharpen the flag bound (run 12, 2026-11-22)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
**No human expert has checked this yet.** Every finite fact below is checked in
exact arithmetic by `test_theory12.py`.

Notation as in `THEORY_10.md`, `THEORY_11.md` and Allikvere, arXiv:2609.02604,
Section 3: n speeds, d = n - 1, H = v^perp, Lambda = P Z^n, b_1, ..., b_d a basis of
Lambda with integer lifts z_i, t_i = ||b_i*||_E^2, q_k = 1 + 2u_k - u_k^2 with
u_k = v_k / max v, and B_r = (2r / ((n+1)(n+1-r)))^2.

## 12.1 The question

Allikvere's Proposition 3.4 applies his Lemma 3.3 to the subspace
V_r = span(v, z_1, ..., z_r), of codimension c = d - r in R^n. Lemma 3.3 gives a
point s in V_r with ||s_k|| >= 1/(c+2) for every k, and this constant is what
produces B_r. The playbook of this project listed one open theory lever: replace
1/(c+2) by the *exact* constant

  delta(V) = max over s in V of min_k ||s_k||

of the particular subspace V_r, which can only be larger, and combine it with the
dual caps of Sections 10 and 11. Section 11 did this for c = 1 (the hyperplane at
r = d-1) and found no gain. This section does it for every codimension at once.

Two facts make the general version precise.

- V_r^perp intersected with Z^n is M_c, the rank-c lattice of integer relations of
  the speeds that vanish on b_1, ..., b_r (the proof of Lemma 11.1 works verbatim
  for any r). So the exact constant at level r is delta(M_c^perp), and Proposition
  3.4 holds with B_r replaced by (2(delta(M_c^perp) - 1/(n+1)))^2.
- Projecting Lambda E-orthogonally away from b_1, ..., b_r gives a lattice of
  squared covolume t_{r+1} ... t_d whose dual is M_c, with Gram matrix M^T Q M for
  an integer basis matrix M of M_c (Lemma 11.4's argument, any rank). Since Q > I,
  **t_{r+1} ... t_d < 1 / det(M^T M)**: a rank-c dual cap from the Euclidean
  determinant D_c of M_c.

**The information-complete relaxation.** For a nested flag of relation lattices
M_1 inside M_2 inside ... inside M_{d-1}, minimise prod t_i subject to

- (P_r) t_1 + ... + t_r >= (2(delta(M_{d-r}^perp) - 1/(n+1)))^2 for r = 1..d-1,
  and t_1 + ... + t_d >= B_d;
- (R_i) t_{i+1} >= (3/4) t_i (Korkine-Zolotarev, Allikvere's Lemma 3.5);
- (D_c) t_{d-c+1} ... t_d <= 1 / D_c for c = 1..d-1.

It uses everything Sections 10 and 11 used (the rank-1 cap is D_1 = sum h^2 >= 3,
the exact hyperplane constant is delta(M_1^perp)), and everything Lemma 3.3 could
give, but no information about the speed ratios u (the weights q are only used
through q > 1).

## 12.2 The result

**Proposition 12.1.** For n = 14 and n = 15 (15 and 16 runners), the infimum of
the information-complete relaxation over all flags of relation lattices of
distinct positive speeds is K_n kappa_n, the THEORY_10 value (kappa_14 =
1369/1029, kappa_15 = 12150/9163). Exact loneliness constants of the flag
subspaces, together with dual caps of every rank, give **nothing** beyond the
rank-1 cap of Section 10 unless they are combined with information about the
speed ratios u.

*Lower bound.* Every flag has delta(M_c^perp) >= 1/(c+2) (Lemma 3.3, with
LRC(m) known for m <= c+1) and D_1 >= 3 (Lemma 10.1 (iv)). So its feasible set lies
inside that of Proposition 10.2, whose minimum is K_n kappa_n.

*Upper bound.* We exhibit one flag F* whose constraints are all satisfied by the
THEORY_10 minimiser t*. For n = 15, t* = (c_1, ..., c_12, 5/14, 15/56); for
n = 14, t* = (c_1, ..., c_11, 37/105, 37/140) (`test_capped.py`). Define, on
coordinates 1, 2, 3, ... of Z^n (zeros elsewhere):

| c | M_c (basis) | M_c^perp, on the coordinates involved | delta(M_c^perp) | D_c |
|---|---|---|---|---|
| 1 | (1, 1, -1) | y_3 = y_1 + y_2 | 1/3 | 3 |
| 2 | (1, 1, -1, 0), (2, 1, 0, -1) | (x, y, x+y, 2x+y) | 1/4 (Lemma 12.2) | 9 |
| c >= 3 | the relations of (1, 2, ..., c+1) | the line R (1, 2, ..., c+1) | 1/(c+2) | 1^2 + ... + (c+1)^2 |

The lattices are nested: (1,1,-1,0) is in M_2, and both basis vectors of M_2
are relations of (1, 2, 3, 4). M_2 is saturated (it is the full set of integer
solutions of g_1 + g_3 + 2g_4 = 0, g_2 + g_3 + g_4 = 0, the orthogonality to
(1,0,1,2) and (0,1,1,1)). The relation lattice of a primitive w has determinant
|w|^2, which gives D_c for c >= 3. The constants are the Lemma 3.3 values
1/(c+2) at every level, so every (P_r) of F* is exactly Allikvere's B_r, which t*
satisfies. The caps hold at t* with room to spare:

| runners | rank 1: t_d vs 1/3 | rank 2: t_{d-1} t_d vs 1/9 | rank 3: tail product vs 1/30 |
|---|---|---|---|
| 15 | 37/140 = 0.264 | 1369/14700 = 0.0931 | below 0.006 |
| 16 | 15/56 = 0.268 | 75/784 = 0.0957 | 975/156800 = 0.0062 |

and every higher-rank cap is slacker still (`test_theory12.py` checks all ranks
c = 1, ..., d-1 exactly). Hence F*'s relaxed problem contains t*, and the infimum
is K_n kappa_n. []

**Lemma 12.2.** delta of {(x, y, x+y, 2x+y)} is exactly 1/4.

*Proof.* The point x = y = 1/4 gives (1/4, 1/4, 1/2, 3/4), so delta >= 1/4.
Suppose all four values have ||.|| >= delta > 1/4. Write 2x + y = x + (x + y);
after swapping the names of x and y the forms are x, y, x+y, x+2y, so it is enough
to treat those. Take x, y in [delta, 1-delta].
(A) If x + y <= 1 - delta, then y <= 1 - 2delta and x + 2y = (x+y) + y lies in
[3delta, 2 - 3delta]. Since delta > 1/4, 3delta > 1 - delta and 2 - 3delta <
1 + delta, so ||x + 2y|| < delta, a contradiction.
(B) Otherwise x + y >= 1 + delta. Replace (x, y) by (1-x, 1-y): this keeps every
||.|| and moves the pair into case (A). []

**Realisability.** F* is not an artefact of the relaxation. Take
v = (1, 2, ..., n-1, w) with w > n-1. The flag F* extends by M_d = all relations of
v, and a basis of Lambda dual to a basis of Lambda* adapted to the flag has exactly
these M_c (the dual basis in reverse order). As w grows, u_k = k/w tends to 0 for
k <= n-1, so the weights q_k tend to 1 and the true q-weighted caps tend to the
Euclidean ones used above. We do not claim that such a basis is Korkine-Zolotarev,
or that v is a counterexample (it is not). The point is that the *listed
information* cannot exclude this flag type. Excluding it would need a new lemma
about KZ bases of counterexamples.

## 12.3 What this closes and what is left

- **Closed.** The "stronger Lemma 3.3 / Proposition 3.4" lever of the playbook.
  Sections 11 and 12 together show that the exact loneliness constants of all
  flag subspaces, the exact hyperplane constant, and dual caps of every rank
  reproduce the THEORY_10 bound and no more. The worst case is a flag built on the
  tight speed sets (1, 2, 3), (1, 2, 3, 4), ..., where every exact constant
  equals the Lemma 3.3 constant.
- **Left (not quantified).** Only information that couples the flag to the speed
  ratios u can go further. One concrete coupling: Allikvere's shape bound (his
  Lemma 3.7, R_14 < 1/2) is nearly attained when one speed is the maximum and all
  others are close to the same value, about 0.078 of it. Among speeds that close
  together, below half the maximum and within a factor 2 of each other, no 3-term
  relation v_c = v_a + v_b exists, so every relation has sum h^2 >= 4 and the cap
  becomes t_d < 1/4, which binds (15/56 > 1/4). The flag's worst case and the
  shape's worst case are therefore incompatible. A joint bound would need the
  supremum of R_n over shapes that do allow a 3-term relation. We have not
  computed it, and we make no claim about its size.
- **The practical consequence** is unchanged: the 16-runner gate target stays
  481.123 (conditional on THEORY_10), and a 16-runner proof is a computation.
