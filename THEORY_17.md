# THEORY, Section 17: a faster non-binary lift (unit symmetry, C engine)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Written 2026-11-24 (run 19), after grading job
lrc-nb (`RESULTS_run19.md`) and before any result of the job this sets up.
Revised 2026-11-24 (run 21): 17.1 item 3 now includes the step that `REVIEW_17.md`
found missing (the cells of beta are cut from the arcs of every alternative). No
statement, code or prediction changed.

## 17.0 Why

Job lrc-nb ran `uniform_nb.lift_children` in pure Python. It decided U_inf(15) for
(1..14) (empty, as the published 15-runner proof forces), but every other
computation hit its deadline. Lifting from level 1 to level 7 (7^13 lifts) for
the k = 13 tight vectors did not finish even with P = inf. The P0 runs of (1..14)
did not finish the level-5 lift. This section gives two changes that keep every
output the same and make the search faster. It also states the lifting order
that the job will use first.

## 17.1 Lemma S (unit symmetry of the children)

Let z be a class at level L, c a prime with gcd(c, L) = 1, and L2 = cL. The
children of z are the vectors z' in Z_{L2}^k with z' = z (mod L). By the CRT,
z' corresponds to (z, y) with y = z' mod c in Z_c^k, and every y occurs exactly
once.

For mu in Z_c^*, let lambda be the unit of Z_{L2} with lambda = 1 (mod L) and
lambda = mu (mod c). Then:

1. lambda z' is again a child of z, with y replaced by mu y.
2. lambda z' and z' have the same canonical form (`uniform_nb.canon`, the minimum
   over all units of Z_{L2}).
3. lambda z' is P-killed by the test that `lift_children` applies exactly when z'
   is. That test uses only the betas in Z_{L2} not divisible by c. The map
   beta -> beta lambda permutes this set, because lambda is a unit, and
   (beta lambda) z'_i = beta (lambda z'_i). The cells of a beta are cut from the
   arcs of **every** alternative {z_i + L a : a = 0..c-1} of every coordinate, not
   only the chosen ones. Because lambda = 1 (mod L), multiplication by lambda
   permutes the alternatives of each coordinate. So the cells (and the big cells)
   of beta lambda are the cells of beta. Hence the two vectors meet the same list
   of position vectors in the same cell partitions, with the same masks and exact
   bits. The gcd clause depends only on which coordinates each prime d | L2
   divides, and multiplying by a unit does not change that.

Every orbit {mu y} with y != 0 contains exactly one y whose first nonzero
coordinate, in any fixed order, equals 1. Take mu = (that coordinate)^{-1}. So
the search may skip every child whose first nonzero y-coordinate is not 1, and
the set of canonical forms it returns is unchanged. (y = 0 is its own orbit and is
always searched.) It visits about 1/(c-1) of the leaves: 1/6 for c = 7, 1/4 for
c = 5, 1/2 for c = 3. []

Pruning stays sound because the prune test (some big cell that no remaining
alternative can cover) is computed over all alternatives. That set contains the
restricted ones, so the test can only prune less. It never prunes a node that has
a surviving leaf below it.

## 17.2 Search order

The search fixes coordinates one at a time. Any fixed order visits the same
leaves, so it returns the same set. The default is largest speed first. The
remaining coordinates then have few arcs, so the prune test finds an uncoverable
big cell sooner. This is a heuristic for speed only. `test_nbc.py` checks three
orders against the published code.

## 17.3 C engine

`nbc.c` is `nbc.dfs_py` written in C, node for node. Each mask is a fixed array
of 64-bit words, and the leaf test is `uniform.Cells.killed` written out. Python
builds every cell, arc and mask (`nbc.prepare`, the same code path as the
reference), so the C program does no geometry of its own. `test_nbc.py` checks:

- `nbc.lift` in pure Python (with and without Lemma S, in three orders) equals
  the published `uniform_nb.lift_children` on every parent of 18 small chains
  (k = 3, 4, 5; levels 2 to 15; P = inf and 11; with and without the gcd clause);
- Lemma S never visits more nodes;
- the C engine returns the same children in the same order and visits the same
  number of nodes and leaves as `nbc.dfs_py`, on the same cascades and on k = 7
  cases whose masks span several 64-bit words.

## 17.4 Lifting order

U(L) can be reached as 1 -> f1 -> L, as 1 -> f2 -> L, or by the CRT combination
of the two factor levels (Lemma N4). Job lrc-nb used 1 -> f1 -> L. That costs
|U(f1)| searches of f2^k leaves each: 7^13 per parent for k = 13 (f1 = 2, f2 = 7).
The other order lifts U(7) by 2, which is 2^13 leaves per parent. U(7) has to be
computed anyway, for the combination. So job lrc-nb2 first computes U(f1) and
U(f2), then lifts U(f2) by f1 (route B). After that, while time is left, it runs
route A (1 -> f1 -> L) and route C (the combination) as cross-checks (C1). By
Lemma N3 all three routes give the same set.
