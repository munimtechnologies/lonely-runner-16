# REVIEW of THEORY_16 (non-binary levels) against uniform_nb.py

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written 2026-11-24 (run 21), before job `lrc16-engine2-v4` (lrc-nb2) has reported.
This is a second agent's attempt to **break** Lemmas N1-N4 and the consequence in
16.3, which the job's predictions (`PLAN_addendum11.md`) rest on. No human expert
has checked it yet.

Files read: `THEORY_16.md`, `uniform_nb.py` (commit a138b85), `uniform.py`
(026f1ee), `thresh.py` (c51d4fb), `THEORY_17.md`, `REVIEW_17.md`.

## Verdict

**N1-N4 and 16.3 are correct as written and as implemented.** No gap that changes
a claim, no code change. Two remarks on scope are below. They should be repeated
in any article that uses the lrc-nb2 result.

## N1 (units)

Lambda = lambda (mod L), 1 (mod p) exists by the CRT. Lambda w = w = s (mod p),
so Lambda w lifts the same s, and b -> b Lambda^{-1} maps witnesses onto
witnesses. A prime d | L divides lambda x iff it divides x. **Holds.** The same
argument shows that P-killing and P* are class invariants: beta -> beta lambda
permutes Z_L and moves the same arc sets.

**Units of the level and of the prime are separate.** The level-one orbit of s at
a prime p also contains mu s (mod p) for every unit mu of Z_p, and coordinate
sign changes. Mu is absorbed by M = mu (mod p), 1 (mod L): M w lifts mu s with
the same z. A sign change in coordinate i replaces z_i by -z_i, and ||-x|| = ||x||.
So deciding the integer vector s decides its whole orbit at every admissible p.
**Holds.**

## N2 (gcd clause)

Definition 2.1(a), as quoted in `THEORY.md` 5, is gcd(L, w_j : j != i) > 1 for
some i, i.e. some prime d | L divides every w_j with j != i. Since d | L and
w_j = z_j (mod L), that is z_j = 0 (mod d). `gcd_clause` tests exactly "some prime
d | L has at most one coordinate not divisible by d", which is the same as "for
some i, d divides all j != i". At L = 1 there is no clause. At L = 2^a it reduces
to `uniform.gcd_clause`. **Holds.**

## N3 (monotone along divisors)

For L' | L, beta = (L/L') beta' gives beta z_i/L = beta' z_i/L' = beta' z'_i/L'
(mod 1), with z' = z mod L'. The arcs are geometrically identical (only the unit
1/Q changes), the exact bit is identical, and a prime d | L' divides the same
coordinates of z and z'. For properness at p, b = (L/L') b' in Z_{Lp} turns a
witness b' of w' into one of w, because w = w' (mod L'p). **Holds.**

Consequence used by `lift_children`: betas that are multiples of c reproduce
positions where the parent was not killed, so skipping them changes nothing. When
c is composite, betas that are multiples of a proper divisor of c are still
tested. That is sound (it can only kill more of what must be killed) and only
costs time.

## N4 (CRT combination)

For a class z at level L1 L2 that is not killed, z mod L1 = lambda a and
z mod L2 = nu b for canonical a, b and units lambda, nu. Since the reductions of
z are not killed, a and b are in U(L1) and U(L2) by N1 and N3. Take the unit Lambda
that is lambda^{-1} (mod L1) and 1 (mod L2). Then Lambda z = CRT(a, nu b), so
`combine`'s loop over mu in the units of Z_{L2} reaches the class. Units of
Z_{L1 L2} reduce onto the units of each factor, so Lambda exists. Betas divisible
by L1 (or by L2) give positions of the L2 (or L1) reduction, which is not killed
by N1, so skipping them is sound. **Holds.** Several mu can give the same class.
That costs time and changes no answer.

## 16.3 (what lrc-nb2 can establish)

The three conditions (U_P0(L) uncut, J_p(L) empty for P0 <= p <= B,
P*_L <= B) give "every lift of the orbit of s to level L is proper at every prime
p >= P0" by Lemma U, E and T, exactly as in `REVIEW_15.md`. Admissibility (p does
not divide Q or any s_i): the speeds of a13, b13 and a14 have prime factors at most
13 (24 = 8 * 3), and k + 1 is 14 or 15. **Holds.**

## Remarks on scope (for the write-up, not errors)

1. **Weaker pruning than the paper, so emptiness is the strong direction.** Our
   cascade kills only by the gcd clause, t = 0 and grid witnesses, and the
   paper's Definition 2.1(a) is the same gcd clause. If the paper or `lrc.c`
   ever also prunes by Lemma S with e > 1 (certification, `THEORY.md` 5.3), our
   sets can only be larger. So "our J_p(L) is empty" implies theirs is, but a
   non-empty set of ours does not contradict an empty set of theirs. This is the
   same one-directional point as X5 in `REVIEW_15.md`. For N3 of
   `PLAN_addendum11.md` (U_inf(14) must be empty for a13 and b13) the direction is
   the safe one: U_inf <= J_p <= the paper's empty set **if** the paper prunes
   only by Definition 2.1. If its level-14 search also certifies, a non-empty
   U_inf(14) would first need a check of what the paper's search removes before
   it is called a disagreement. The decision tree in `playbook.md` already says
   "bug hunt, do not publish" for that case. This sharpens what the hunt must
   look at first.
2. **The gates below P0 are not covered.** For a13 and b13 the paper's second gate
   set includes five primes below 199 (83 to 191). The statement of 16.3 starts at
   P0 = 199 and says so. Any write-up must keep that sentence.

## Interaction with THEORY_17

Lemma S of `THEORY_17.md` (unit symmetry of the children) is used by job lrc-nb2
only when lifting by an odd prime c coprime to L: route A (U(2) lifted by 7) and
U(3) -> U(15)-type steps. Route B lifts U(7) by c = 2, where `sym_ok` turns the
filter off. `REVIEW_17.md` covers the filter. Its missing proof step (R2) is now
folded into `THEORY_17.md` 17.1 (this run).
