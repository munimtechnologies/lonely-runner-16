# REVIEW of THEORY_17 Lemma S: an adversarial read of the proof and the code

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written 2026-11-24 (run 20). This is a second agent's attempt to **break** Lemma S
(the unit-symmetry reduction used by job lrc-nb2) before the job produces any
result. No human expert has checked it yet.

## Verdict

**Lemma S is correct as implemented** in `nbc.py` / `nbc.c` at commit 57f59b9.
The written proof in `THEORY_17.md` Sec. 17.1 has **one gap**, closed below
(step R2). No change to the code or to the pre-registered predictions of
`PLAN_addendum11.md` is needed.

## What the code actually tests

For a parent z at level L, a prime c with gcd(c, L) = 1, and L2 = cL,
`nbc.prepare` builds, for every beta in B = {1 <= beta < L2 : c does not divide beta}:

- the **alternatives** of coordinate i: A_i = {z_i + L a mod L2 : a = 0..c-1};
- the **cells** of beta: `U.Cells` of the union of
  `arcs_for(s_i, beta v mod L2, L2, k, Q)` over **all** i and **all** v in A_i;
- the mask of choosing v in A_i: the cells covered by that arc, plus the exact
  bit `exact_bad(beta v, L2, k)`;
- `big(P)`: the big cells of that partition.

A leaf (one choice z'_i in A_i per coordinate) is reported unless the gcd clause
over the primes of L2 fails, or some beta in B kills it (`Cells.killed`, written
out in C as `killed_beta`).

## The argument, step by step

Let mu be in Z_c^* and lambda the unit of Z_{L2} with lambda = 1 (mod L) and
lambda = mu (mod c) (CRT, since gcd(c, L) = 1).

- **R1 (children go to children).** If v is in A_i, then lambda v = v = z_i (mod L),
  so lambda v is in A_i. Multiplication by lambda is injective on Z_{L2}, so
  **v -> lambda v permutes A_i**. In particular lambda z' is again a child of z.
- **R2 (the gap: the cell partition is the same).** `THEORY_17` says the two
  vectors "meet the same list of position vectors". That is true, but the kill test
  does not only look at the chosen positions: the cells of beta are cut from the
  arcs of **every** alternative of every coordinate. So one also needs the
  partition at beta*lambda to equal the partition at beta. It does: the arcs at
  beta*lambda are arcs_for(s_i, beta (lambda v)) for v in A_i, and by R1,
  lambda v runs over A_i again. So the arc multiset, hence `Cells`, hence `big(P)`,
  at beta*lambda equal those at beta. (`arcs_for` depends only on s_i, the
  position, L2, k and Q; none of them changes.)
- **R3 (masks match).** The mask of choosing lambda z'_i at beta is the cell set of
  arcs_for(s_i, beta lambda z'_i) plus exact_bad(beta lambda z'_i): exactly the mask
  of choosing z'_i at beta*lambda, in the same partition (R2). So the covered set
  of (lambda z', beta) equals the covered set of (z', beta*lambda).
- **R4 (the beta set is closed).** beta -> beta*lambda permutes B, since lambda is a
  unit and lambda = mu != 0 (mod c). (The same holds for any beta set closed under
  units, so the argument does not depend on the choice "c does not divide beta".)
  With R3: lambda z' is killed iff z' is killed.
- **R5 (gcd clause).** lambda z'_i = mu y_i (mod c) and lambda z'_i = z'_i (mod q)
  for every prime q | L. So every prime of L2 divides the same coordinates of
  lambda z' as of z'.
- **R6 (canonical form).** `uniform_nb.canon(w, L2)` is a minimum over the units of
  Z_{L2}, and lambda is one of them, so canon(lambda z') = canon(z').
- **R7 (one representative per orbit).** On y = z' mod c in Z_c^k, mu acts by
  scaling. y = 0 is fixed and is kept: the filter rejects a value only when no
  nonzero digit has been seen yet **and** the digit is > 1, so a run of zero
  digits is never rejected. For y != 0, the orbit {mu y} has exactly one member
  whose first nonzero digit (in the search order) is 1. The code uses the search
  order consistently: `vals` and `masks` are both permuted by `idx` in `prepare`,
  and `lift` maps the result back through `idx` before `canon`.
- **R8 (pruning).** The internal-node test uses the suffix union over **all** c
  alternatives (`suf` in `prepare`, `SUF` in C), a superset of the alternatives
  that the filter leaves. If the superset cannot cover a big cell, the subset
  cannot either. So pruning never removes a branch with a surviving leaf below
  it, with or without Lemma S.

So the set of canonical forms returned with the filter equals the set without it.

## Things checked that could have broken it, and did not

- c = 2: Z_2^* is trivial, and `sym_ok` turns the filter off (c > 2 required).
- c | L: no lambda with lambda = 1 (mod L) and lambda = mu (mod c) exists in
  general; `sym_ok` requires gcd(c, L) = 1, and `lift` asserts it.
- `y = vals % c` in C and Python: the values lie in [0, L2) and c | L2, so the
  residue is well defined.
- The exact-witness bit: `exact_bad(beta * v, L2, k)` depends only on the position
  beta*v mod L2, so it moves with the mask in R3.

## Evidence already on record

Job lrc16-engine2-v3 (2026-11-24, Dell, python:3.12 with cc) ran `test_nbc.py` with
the C engine forced on (`NBC_REQUIRE_C=1`): all 7 of its tests passed in 27.5 s,
including `PyMatchesPublished.test_cases` (the reference with and without the
filter equals the published `uniform_nb.lift_children` on 18 chains, three orders)
and `CMatchesPy` (C = Python node for node, including multiword masks). The job
then stopped for an unrelated reason (`RESULTS_run20.md`).

## Suggested edit to THEORY_17 (for the next revision)

In 17.1 item 3, add before "So the two vectors meet the same list of position
vectors": "Because lambda = 1 (mod L), lambda permutes the alternatives
{z_i + L a} of each coordinate, so the cells of beta*lambda (cut from the arcs of
all alternatives) are the cells of beta."
