# REVIEW_THEORY_2_7: adversarial re-derivation of THEORY.md Sections 1-3 and 5-8

MV2 of Munim, Inc. Text CC BY 4.0. Written 2026-11-24 by an AI agent working in
MV2's name, told to look for errors, not to confirm. **This is not a human review.**
It closes the "still unreviewed" item listed since run 22 (THEORY.md Sections 2-7,
and Lemma U's Section 8 statement for binary levels), so every section of the
16-runner method has now had at least one adversarial pass. Section 4 is a to-do
list and has nothing to check.

Method: every inequality, polynomial identity and lemma was re-derived by hand from
the definitions in THEORY.md, without reading `bounds.py`, `test_bounds.py` or the
earlier readings first. Each arithmetic fact used below is asserted again, in exact
rational arithmetic, by the new self-contained `test_review_theory.py` (standard
library only, independent of `bounds.py`).

## Verdict

**No error that changes any claim.** One cosmetic rounding (R1). Four dependency
remarks (D1-D4) say what a human reader must check against the cited papers, because
this review did not have their full texts.

## Section 1 (hypotheses of the flag bound)

- With b_r = r/(16-r), all fourteen entries 64 c_r = b_r^2 - b_{r-1}^2 match the
  table (exact). The consecutive ratios are 3.592, 2.058, 1.761, 1.651, 1.606,
  **1.5969**, 1.613, 1.653, 1.722, 1.834, 2.017, 2.350, 3.091; the minimum is
  c_7/c_6 = 3751/2349 > 4/3, as stated.
- sum ln(64 c_r) = -14.848672 (recomputed term by term), so
  ln A_15 = (14 ln 64 + 14.848672)/2 = 36.536518.

## Section 2 (shape lemma, R_15 < 49/100)

- **Reduction.** With u_i = x_i / max x, R_15^2 = 225/H(u) is scale-invariant (both
  (prod x)^{2/15} and sum x^2/q scale by c^2). A minimiser exists because a(u) -> inf
  as u -> 0 and sum w >= w(1) = 1/2. w is increasing ((u^2/q)' = 2u(1+u)/q^2), so
  C <= 14 * 1/2 = 7.
- **R1 (cosmetic).** (15/0.49)^2 = 2250000/2401 = 937.1095..., written "= 937.11".
  Every lower bound proved (942.5 and 1801) is above 937.11, so nothing changes.
- **(a).** Differentiating phi = C q u^{-2/n} + u^{2-2/n} gives
  (n/2) u^{1+2/n} phi' = C((n/2) q' u - q) + (n-1) u^2, and (n/2) q' u - q = -gamma.
  Correct. beta'' = 28(C - 1): concave for C < 1 (the chord argument gives a unique
  root in (0, alpha)), linear for C = 1 (root 1/13 < alpha), convex for C > 1 with
  beta(1) = 2C - 14 <= 0 (so beta <= 0 on [alpha, 1]). The identity
  (n-1) q + gamma = n(1+u) and the critical-point form L(u) = 1/A check. The
  logarithmic-derivative polynomial was expanded in full for n = 15 and for n = 4
  by hand: (-2, 8, 22, 54, -28, -14) = -2 P_15, and the general-m form holds (the
  test checks n = 4..29). gamma > 0 on (0, alpha), so L is decreasing there. The
  bracket 10.6284^2 < 113 < 10.6312^2 gives alpha in (0.0846, 0.0847). Note that
  (13 - 10.6312)/28 is exactly 0.0846, so the lower end is strict only because the
  square-root bracket is strict; it is. 1 - 4u - 11u^2 - 27u^3 at 0.0847 is 0.5659.
- **(b).** a'(u) has the sign of -gamma; gamma's roots are alpha and
  (13 + sqrt 113)/28 = 0.844, so a falls, rises and falls again on (0, 1], and
  min a = min(a(alpha), 2). q(0.0846) * 0.0847^{-2/15} = 1.61499 > 1.6149 > 8/5
  (matching the run-3 erratum). (j/2) 2^j (8/5)^{15-j} grows with j (ratio
  1.25 (j+1)/j), and 4 (8/5)^13 = 1801.44 > 1801.
- **(c).** H(t) = (1/2 + 14 t^2/q) * 2 * q^14 t^{-28/15} = (1 + 2t + 27t^2) q^13
  t^{-28/15}. The quartic and its factorisation 28(1 - t)(378t^3 + 25t^2 + 10t - 1)
  were re-expanded term by term and agree; the coefficient pattern
  s(2s-1), 2s-3, s-4 reproduces the n = 13 and n = 14 cubics quoted from the
  paper. cubic(0.0724) = -0.0015 < 0 < cubic(0.0725) = +0.0005. The monotone
  bound evaluates to ln H >= 6.848567 against ln 942.5 = 6.848536, so
  H(t_0) >= 942.53 > 942.5. **The margin is thin (about 3e-5 in ln) but exact**;
  the test asserts it as A^15 q^195 > 942.5^15 * 0.0725^28 in Fractions.

## Section 3 (consequences)

- log(v_1...v_15) < 15 (ln A_15 + ln(49/100) - ln 15) = 496.7268 follows from
  S F_15 <= A_15 and prod v = (S R F / 15)^15. lcm(2..16) = 720720
  = 2^4 3^2 5 7 11 13, ln = 13.48801, so the gate target is 483.2388 -> 483.239.
  Gate primes must be > 16 so that they are coprime to 720720; "p > 13" says the
  same thing because 14-16 are not prime.
- The distinct-coordinates remark is right: a repeated speed leaves at most 14
  distinct speeds, and LRC(14) gives distance 1/15 > 1/16.

## Section 5 (Lemmas L, S, C; orbit reduction)

- **Lemma L.** Both cases re-derived (g = gcd(lambda, l) > 1 divides every residue
  w_i because g | lp; otherwise b = lambda^{-1} j (lp/D) gives t w_i = j s_i / D
  mod 1). The example (1..13,15,28) at t = 1/16 is a valid witness of denominator
  16 (28/16 = 7/4).
- **2-adic conditions.** At level 16 the times j/16 (j odd) force a coordinate
  divisible by 16, and failure of the gcd clause forces two odd coordinates. At
  level 32, ||j w/32|| < 1/16 iff j w = 0, +-1 mod 32; an odd w blocks exactly two
  odd j (w^{-1} != -w^{-1} mod 32), so 8 odd coordinates are needed. Correct.
- **Lemma S.** The open-arc count r <= ceil(LN) holds in both cases (test: exhaustive
  for N <= 24). Each point of the coset is hit g times. The k = 15 cost table
  (15 binary entries and 5 odd primes) recomputes exactly. "7 odd exceptions when
  the rest are divisible by 8" needs LRC(8), which is available.
- **Lemma C and orbit reduction.** Divisibility of v_i by d | l_j is determined by
  w_i mod l_j p; the induction is right; units preserve gcd(., d) for d | l.

## Section 6 (small covers)

- tau_15(p) >= ceil(n/m) >= 8 with n = (p-1)/2, m = floor((p-1)/16): a class
  covers the residues |r| < p/16, and p/16 is never an integer, so
  m = floor((p-1)/16). The completion claim's proof is right (prune to an
  irredundant cover inside the support, map by a unit, list the rest in
  non-decreasing order). C(201, 2) = 20,100 is right for p = 401, s = 13.

## Section 7 (tight sets)

- **Lemma N** re-proved: m >= 2 from w = mr >= n > r; s = 1 is killed by b = 1;
  s >= 2 by b = s + 1 <= ms - 1 with gcd(r, n + 1) = 1. The table was re-derived
  by hand: for n = 14 the Goddyn-Wong condition needs gcd(r, 14) > 1 and
  gcd(r, 15) > 1, so r in {6, 10, 12}, and only (12, 2) survives (r = 6 fails at
  b = 11, r = 10 at b = 7, r = 12 with m >= 3 at b = 5). For n = 15 the same
  candidates all fail. The test brute-forces n = 14, 15, 16 for m <= 60 and
  Lemma N for every n < 200 with n + 1 prime (m <= 11).
- **(1..13,15,28) is not tight.** All fifteen folded distances for t = 993/2800
  were recomputed (smallest 179 > 175, at speed 3). The interval endpoints are
  17/48 and 159/448, length exactly 1/1344, with speed 3 and speed 28 at distance
  exactly 1/16 at the two ends, and 5v mod 14 = +-1 only for v = 3, 11. Correct.
- Section 7.1 is labelled a heuristic and 7.4 a prediction (P4); both are worded
  correctly.

## Section 8 (Lemmas D and U at binary levels; 8.5)

- **Lemma D.** 1 = AL + Bp splits b w_i/(Lp) exactly as stated, and
  b -> (bB mod L, bA mod p) is a bijection (test: six levels x four primes). For
  L a power of 2, gcd(Lp, w_j : j != i) > 1 iff all those w_j are even, because no
  w_j is divisible by p.
- **Lemma U.** (i) an open arc longer than 1/P >= 1/p contains a point of (1/p)Z;
  (ii) a witness t = sigma/p with sigma != 0 has denominator exactly p, and arc
  endpoints have denominators dividing lcm(L, k+1) lcm(s), so the inequalities at t
  are strict. Both inductions are right because the s-part of w is fixed, so
  w <-> z is a bijection at each level. For s = (1..15), Q has primes 2, 3, 5, 7,
  11, 13 only.
- **8.3.** Even beta = 2b at level 2L reproduces the parent's level-L positions, so
  only odd beta are new. Correct.
- **8.5.** The equal-gaps argument is right. The test confirms it on the dyadic
  grid 1/512: for k = 13 and 14 no dyadic time is a (non-strict) witness of
  (1..k), and for k = 15 exactly the eight times j/16 (j odd) are.

## Dependencies a human must check against the papers (not errors)

- **D1.** Section 1 and Lemma S use LRC(m) for m <= 14, i.e. Allikvere's 15-runner
  result (arXiv:2609.02604 v2), which is a preprint.
- **D2.** The hypotheses and the form of Theorem 3.8 (the ratio condition 4/3, the
  definition of B_r and the shape of the prefix inequalities) are quoted from the
  paper; this review checked the arithmetic, not that the quotation is exact.
- **D3.** Lemma N uses Zhang's classification (arXiv:2608.13599 v3, Thm 1.2) and
  the Goddyn-Wong criterion as quoted.
- **D4.** Lemma 2.2(ii) of the paper (the gcd-clause argument), which Lemma C cites;
  Section 5.5 already re-derived it as the case e = 1 of Lemma S.

## What this changes

Nothing in the plan. With REVIEW_9 and REVIEW_13 to REVIEW_17, every THEORY section
used by the queued jobs has now had an adversarial AI pass. A human reader (or a
Lean or interval-arithmetic formalisation of Section 2) is still required before any
16-runner claim, as THEORY.md Section 4 item 4 says.
