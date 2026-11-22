# COST addendum 1: two ways to make 16 runners cheaper, checked and closed (run 9, 2026-11-22)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
No human expert has checked this yet. The numerical facts are checked in exact
integer arithmetic by `test_cost_addendum1.py`.

`COST.md` shows that the price of a 16-runner proof is set by the gate target
(log-sum of gate primes > 483.239) and by the level-one generation cost at the
largest gates (about p^6). Two ideas could lower that price without any new
computation. This note shows that neither works as stated, so later runs do not
spend time on them.

## 1. Beck-Everett relations cannot prune the gate search

Beck and Everett (arXiv:2609.06259, *Lonely Runner Relations*) prove that every
counterexample or tight instance n in Z_{>0}^k satisfies an integer relation
m . n = 0 with 0 < ||m||_1 <= min(2k + 3, ((k+1)/(k-1)) flt(k)). For k = 15 this
is ||m||_1 <= 33. The idea was to use this relation inside the gates: the reduction
w = v mod lp of a counterexample v would also satisfy m . w = 0 (mod lp), so the
generator could skip residue vectors that satisfy no such relation.

**Claim.** At every modulus M <= 39,142, every w in (Z/MZ)^15 satisfies
m . w = 0 (mod M) for some nonzero integer m with ||m||_1 <= 13. Every gate level
planned for 16 runners has M = l p <= 32 * 1000 = 32,000, so this condition rules
out nothing.

*Proof.* The set Gamma = {m in Z^15 : m . w = 0 mod M} is the kernel of a
homomorphism Z^15 -> Z/MZ, so it is a lattice of index (determinant) at most M.
The l1 ball of radius r in R^15 is compact, convex and symmetric, with volume
(2r)^15 / 15!. By Minkowski's convex body theorem it contains a nonzero point of
Gamma once (2r)^15 / 15! >= 2^15 M, that is, once r^15 >= 15! M. For r = 13,
13^15 = 51,185,893,014,090,757 and 15! = 1,307,674,368,000, so the condition holds
for every M <= floor(13^15 / 15!) = 39,142. []

The condition ||m||_1 <= 33 starts to constrain residues only when M exceeds
33^15 / 15!, about 4.6 * 10^10, which is far beyond any lifting level. The
relation does hold for the integer counterexample itself. But there it only says
the lattice Lambda = P Z^n of the flag bound contains a short vector (m is
orthogonal to v and integral). That bounds t_1 from above, while the flag bound
needs lower bounds, so it does not sharpen the product bound either.

## 2. Korkine-Zolotarev constraints cannot sharpen the flag bound

The bound S F_15(x) <= A_15 = (prod c_r)^{-1/2} (arXiv:2609.02604, Theorem 3.8;
`THEORY.md` Sec. 1) minimises prod t_i (Gram-Schmidt norms of a KZ basis) subject
to the prefix inequalities t_1 + ... + t_r >= B_r and the KZ ratio constraints
t_{i+1} >= (3/4) t_i. The minimiser is t_i = c_i = B_i - B_{i-1} (Lemma 3.6).
One might hope that stronger facts about KZ bases (higher Hermite constants,
block conditions) could raise the minimum.

**Claim.** No inequality that holds for all KZ bases can raise this minimum.

*Proof.* For n = 15 the c_r increase (smallest ratio c_7/c_6 = 3751/2349 > 1,
`test_bounds.py`). Take an orthogonal lattice whose basis vectors have squared
lengths c_1 <= ... <= c_14. Its shortest vector has squared length c_1 (since
||sum a_i b_i||^2 = sum a_i^2 c_i), every projected lattice is again orthogonal,
and the basis is size-reduced (all mu_ij = 0). So it is a KZ basis with profile
exactly t = c, and every valid KZ inequality holds at t = c. The prefix
inequalities hold there with equality, so t = c stays feasible and the minimum
stays prod c_r. For the same lattice the nearest-plane bound used in
Proposition 3.4 (distance at most (1/2) sqrt(t_1 + ... + t_r)) is attained, so
that step has no slack in the worst case either. []

So a smaller gate target must come from a stronger Proposition 3.4 (larger B_r),
from the ellipsoid step (E inside D, Lemma 3.1), or from the shape bound. The
shape bound is already nearly sharp: R_15 = 0.48796 against the 0.49 used, worth
only 15 ln(0.49/0.48796) = 0.06 nats. The prefix bound is where the leverage is.
If every B_r is multiplied by f, then K_15 is multiplied by f^14 and the product
bound falls by 15 * 7 * ln f = 105 ln f nats. A 10% gain is about 10 nats, which
is one or two of the most expensive gates near p = 800. For a single r, the
derivative of the product bound with respect to ln B_r is
-7.5 (B_r / c_r - B_r / c_{r+1}) (for r = 14 only the first term). It is largest
at r = 14 (about -12.2) and r = 13 (about -9.7), so a sharper version of
Lemma 3.3 for subspaces of dimension 14 and 15 would pay the most. We have no such
lemma. Lemma 3.3's constant 1/(n + 2 - q) is attained for some subspaces (for
example n = 3, q = 2: the plane x_1 + x_2 + x_3 = 0, best value 1/3). Any gain must
therefore use the particular subspaces that occur in a KZ flag. This is an open
idea, not a result.

## 3. What this changes

Nothing in the plan changes. The deciding number is still the measured level-one
cost at k = 15 (`COST.md` Sec. 4, job `lrc16-allik-probe-v1`, still queued). The
two routes above are closed. The only cost lever left that needs no computation is
a stronger prefix inequality, which would be new mathematics.
