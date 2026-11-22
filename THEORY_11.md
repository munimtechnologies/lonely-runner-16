# Section 11: re-check of the dual cap, and where the arithmetic route stops (run 11, 2026-11-22)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
**No human expert has checked this yet.** The finite facts below are checked
exactly by `test_theory11.py`. The numbers in `dual_cap_results.json` are
recomputed from `capped.py` by the same test.

Notation as in `THEORY_10.md` and Allikvere, arXiv:2609.02604, Section 3: n speeds,
d = n - 1, H = v^perp, Lambda = P Z^n, q_k = 1 + 2u_k - u_k^2, u_k = v_k / max v,
t_i = ||b_i*||_E^2 for a basis b of Lambda, h the integer relation dual to b_d.

## 11.1 Adversarial re-reading of THEORY_10

This was a fresh pass whose only goal was to break Lemma 10.1, Proposition 10.2
and Corollary 10.3. Nothing broke. What was checked:

- **Lemma 10.1 (i).** Lambda^* = Z^n intersected with H. Allikvere states the same
  duality in Section 3 ("Z^n cap H has covolume ||v||_2, and P Z^n is its dual in
  H").
- **Lemma 10.1 (ii).** The Riesz vector of phi = (last coordinate) is b_d*/t_d, so
  the dual norm of phi is t_d^(-1/2).
- **Lemma 10.1 (iii).** h_E(y) = (sum q_k y_k^2)^(1/2) on H. This is the support
  function in the proof of his Lemma 3.1.
- **Lemma 10.1 (iv).** A relation with sum h^2 <= 2 is e_a - e_b, which would force
  v_a = v_b. Also q_k - 1 = u_k(2 - u_k) > 0, which gives strictness.
- **h is primitive.** h . z_d = h . b_d = 1 for an integer lift z_d.
- **The structural lemma.** Its premise c_{r+1} > (3/4) c_r holds for n = 5..15
  (`test_capped.py`).
- **Vertex completeness.** Dropping a block-end prefix P_{e_j} with j < k-1
  leaves P_{e_{k-1}}, P_{e_k} and C together. P_{e_k} - P_{e_{k-1}} is a multiple
  of C, so that system is singular. Hence (A), (B1) and (B2) are the only
  systems.
- **The hand values.** n = 15 gives c_13 = 11/72, c_14 = 17/36,
  x = (4/7)(5/8) = 5/14, ratio 12150/9163. n = 14 gives c_12 = 3/20, c_13 = 7/15,
  x = 37/105, ratio 1369/1029.
- **The exponent chain against his Theorem 3.8.** (S F_n)^(-2) = prod t_i >= K_n
  kappa_n gives S F_n <= A_n kappa_n^(-1/2). Then n (v_1...v_n)^(1/n) = S F_n R_n <
  r_n A_n kappa_n^(-1/2), so the bound on log(v_1...v_n) drops by exactly
  (n/2) ln kappa_n. The hypothesis c_{i+1}/c_i > 4/3 of his Lemma 3.6 is not
  needed, because Proposition 10.2 replaces that lemma.

**Consequence for planning.** The 16-runner gate target becomes 481.123 (from
483.239), and the 15-runner target 399.986 (from 401.9846). This holds
*conditionally on THEORY_10*, which a human still has to check, and any final
proof must cite it. `COST.md` is not edited. This section is the addendum.

## 11.2 The prefix bound at r = d-1 uses the same relation h

**Lemma 11.1.** In the proof of Allikvere's Proposition 3.4 with r = d - 1, the
subspace V = span(v, z_1, ..., z_{d-1}) is exactly h^perp.

*Proof.* V is a rational subspace of dimension d = n - 1, so V^perp = R g for a
primitive g in Z^n. Then g . v = 0, so g is in H. For i < d we have
g . z_i = g . P z_i = g . b_i = 0, because g is in H. Inside H the vectors
orthogonal to b_1, ..., b_{d-1} form a line, which contains h. Both g and h are
primitive, so g = +-h. []

So at r = d - 1 Lemma 3.3's constant 1/3 can be replaced by the exact hyperplane
constant of Lemma 10.4, delta(h) = 1/2 - 1/(2L) (L = ||h||_1 odd) or 1/2 (L even):
t_1 + ... + t_{d-1} > (2 (delta(h) - 1/(n+1)))^2. The cap 1/t_d = sum q h^2 and
this prefix bound depend on the *same* h, so they can be combined case by case.

**Proposition 11.2 (the combined bound gains nothing).** Write N = sum h_k^2.
Since every |h_k| is 0 or at least 1, N >= L, and L >= 3. The cases are:

| relation type | L | N | delta(h) | cap on t_d |
|---|---|---|---|---|
| v_c = v_a + v_b, h = e_a + e_b - e_c | 3 | 3 | 1/3 | < 1/3 |
| v_b = 2 v_a, h = 2e_a - e_b | 3 | 5 | 1/3 | < 1/5 |
| L even | >= 4 | >= 4 | 1/2 | < 1/4 |
| L odd | >= 5 | >= 5 | >= 2/5 | < 1/5 |

Every row has delta >= 1/3 and cap <= 1/3. So its feasible set lies inside that of
Proposition 10.2, and its minimum is at least K_n kappa_n. The first row *is*
Proposition 10.2's problem: delta = 1/3 leaves B_{d-1} unchanged. So the minimum
over all cases is K_n kappa_n, the THEORY_10 bound, exactly. []

So the arithmetic route through the last basis vector ends at THEORY_10, unless
the first row can be excluded. That would take a lemma saying that the relation
dual to b_d of a KZ basis of a counterexample's lattice is not a 3-term sum
relation v_c = v_a + v_b. We have no such lemma. A plain "no v_c = v_a + v_b"
statement looks as hard as the conjecture: tight sets like (1, ..., n) are full
of such relations.

**Remark 11.3 (where a sum relation must sit).** In the first row,
1/t_d = q_a + q_b + q_c = 3 + 4u_c - (u_a^2 + u_b^2) - u_c^2 >= 3 + 4u_c - 2u_c^2,
using u_a^2 + u_b^2 <= (u_a + u_b)^2 = u_c^2. The capped minimiser for n = 15 has
1/t_d = 56/15. So the cap stays slack there only if 3 + 4u_c - 2u_c^2 <= 56/15,
that is u_c <= u* = 1 - sqrt(38/15)/2 = 0.20418 (that is, 1 - sqrt(152/15)/4). In
words: the THEORY_10 minimiser is feasible only when the sum relation dual to b_d
involves speeds below about a fifth of the fastest speed. This is a structural
fact about near-extremal counterexamples, not an improvement of the bound,
because the flag bound does not yet control u.

## 11.3 The rank-2 dual cap does not bind

**Lemma 11.4.** For distinct positive speeds and any basis, t_{d-1} t_d < 1/8.

*Proof.* Project Lambda E-orthogonally away from b_1, ..., b_{d-2}. The image
has squared covolume t_{d-1} t_d, and its dual is the rank-2 lattice of relations
vanishing on b_1, ..., b_{d-2}. So t_{d-1} t_d = 1 / det(G), where
G = [sum q_k g_k g'_k] is the Gram matrix of a basis g, g' of that lattice in the
pairing of Lemma 10.1(iii). Write the basis as an integer matrix M (n x 2). Then
G = M^T Q M = M^T M + M^T (Q - I) M, and Q - I is positive definite, so
det G > det(M^T M). Take a Lagrange-reduced basis: |g|^2 = m <= |g'|^2 and
2|g . g'| <= m. Every nonzero vector is a relation of distinct speeds, so m >= 3.
If m = 3 then |g . g'| <= 1 and det >= 9 - 1 = 8. If m >= 4 then det >= 3m^2/4
>= 12. []

The value 8 is attained in Euclidean terms: v = (1, 2, 3, 4, 5) with
g = (1, 1, -1, 0, 0) and g' = (1, 0, 0, 1, -1). At the capped minimiser for n = 15,
t_13 t_14 = (5/14)(15/56) = 75/784, which is below 1/8 = 98/784. The constraint
holds there, so adding it leaves the minimum unchanged. Hermite's bound makes
rank-3 caps weaker still: det >= 27/2, against a tail product of about 0.0062
there.

## 11.4 Status

- THEORY_10 survived a deliberate attempt to break it. It still needs a human
  check.
- The two natural ways to push the same idea further fail. One is coupling the
  cap with the exact hyperplane constant (Prop 11.2). The other is rank-2 dual
  caps (Lemma 11.4). In both cases the obstruction is a counterexample whose last
  dual vector is a 3-term sum relation among slow speeds (Remark 11.3).
- The next real lever stays computational: the gates. The open theory lever is
  Allikvere's Proposition 3.4 at r = 13, 14 through Lemma 3.3 itself, not through
  the relation lattice.
