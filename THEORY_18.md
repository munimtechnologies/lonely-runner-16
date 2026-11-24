# THEORY, Section 18: the tight orbit (1..15) dies at level 16 at every prime p >= 251

MV2 of Munim, Inc. Made with AI agents working in MV2's name; text CC BY 4.0.
Written 2026-11-24 (run 26). **No human expert has checked this yet.** Every
interval and every inequality below is checked in exact rational arithmetic by
`test_level16.py` (standard library only, imports no repository code), which also
checks the whole argument against the actual integer vectors at every prime from
251 to 3,000. The data it checks are in `level16_certificate.json`.

## 18.0 What this section does

`lrc16-uniform-v1` (graded in `RESULTS_run16.md`) found that the prime-free upper
cascade U_251 of `THEORY.md` Section 8 does not empty at level 16 for the tight
orbit s = (1, ..., 15): U_251(16) has 9 unit classes, all nonlinear (prediction P5
failed). Lemma U only says that each of them has strict witness intervals shorter
than 1/251 for each fixed beta. `THEORY_15.md` and the queued job
`lrc16-uniform-v2` settle such classes prime by prime.

Here the 9 classes are settled **by hand, for every prime at once**. The point
missed by U_P is that U_P looks at one beta at a time, so at one prime its grid
of times has spacing 1/p; but for these classes the conditions depend on beta
only through its parity, so the 8 odd values of beta together form a grid with
spacing 1/(8p). One class needs a different argument, a parity step.

**Theorem 18.** Let p >= 251 be prime. Then no lift of the orbit of (1, ..., 15)
to level 16 is improper at p: J_p(16) is empty for this orbit.

The theorem is conditional on (i) Lemma U (`THEORY.md` 8.2) and (ii) the
computation of U_251(16) by `uniform.py` in job `lrc16-uniform-v1` (raw output
`results/lrc16-uniform-v1/summary_uniform.json`, committed unchanged). Both have
had adversarial AI reviews (`REVIEW_9.md`, `REVIEW_15.md`, `REVIEW_THEORY_2_7.md`),
not a human one. It is a statement about one step of the 16-runner plan (the
binary cascade of one level-one orbit). **It is not a proof of any case of the
Lonely Runner Conjecture.**

## 18.1 Set-up

k = 15, L = 16, p an odd prime > 15. A level-16 lift of s is a vector w in
(Z_{16p})^15 with w_i = i (mod p); write z_i = w_i mod 16. w is **proper** if the
gcd clause holds (at most one z_i odd) or some b in Z_{16p} has
||b w_i / (16p)|| >= 1/16 for every i (non-strict, as in arXiv:2609.02604). Units
Lambda = lambda (mod 16), 1 (mod p) with lambda odd preserve properness, so it is
enough to treat one representative z of each class. By Lemma U(i) and Lemma R
(`THEORY_15.md` 15.4), for p >= 251,

  J_p(16) = { z in U_251(16) : the lifts with residue z mod 16 are improper at p },

and U_251(16) consists of these 9 classes (copied from the job output; the test
compares them with the committed file):

| # | z (mod 16) | D = { i : z_i = i + 8 (mod 16) } |
|---|---|---|
| 1 | (1,2,3,4,5,6,7,8,9,10,11,12,13,**0**,15) | (z_14 = 14 + 2; see 18.3) |
| 2 | (1,2,3,4,5,14,7,0,9,2,11,4,13,6,7) | {6, 8, 10, 12, 14, 15} |
| 3 | (1,2,3,4,5,14,7,0,9,10,11,4,13,6,7) | {6, 8, 12, 14, 15} |
| 4 | (1,2,3,4,5,14,15,0,1,2,3,4,5,6,7) | {6, ..., 15} |
| 5 | (1,2,3,4,13,14,7,0,9,10,11,4,13,6,7) | {5, 6, 8, 12, 14, 15} |
| 6 | (1,2,3,4,13,14,15,0,1,2,3,4,5,6,15) | {5, ..., 14} |
| 7 | (1,2,11,4,5,14,7,0,9,2,11,4,13,6,7) | {3, 6, 8, 10, 12, 14, 15} |
| 8 | (1,2,11,4,13,14,7,0,9,2,11,4,13,6,15) | {3, 5, 6, 8, 10, 12, 14} |
| 9 | (1,2,11,4,13,14,15,0,1,2,3,4,5,6,15) | {3, 5, 6, ..., 14} |

For classes 2-9 every coordinate is z_i = i or z_i = i + 8 (mod 16); D is the
set of the second kind. Every D contains 8 (otherwise t = 0 with beta odd would be
a witness, and U_inf would have killed the class) and none contains 4.

## 18.2 Classes 2-9: a fixed window for odd b

**Lemma 18.1.** Let D be a subset of {1..15} and
w_i = i + 8p [i in D] (mod 16p). Put

  W_D = { x real : ||i x|| >= 1/16 for i not in D, and ||i x - 1/2|| >= 1/16 for i in D }.

If some odd integer m has m/(16p) in W_D, then w is proper (b = m is a witness).

*Proof.* w_i = i (mod p) and w_i = i + 8 (mod 16) for i in D (p is odd), so w is
the lift with residue z. For b = m odd and x = m/(16p),
b w_i/(16p) = i x + m [i in D]/2 = i x + [i in D]/2 (mod 1). Since
||y + 1/2|| = ||y - 1/2||, the witness condition for b is exactly x in W_D. []

W_D does not depend on p. A closed interval of length l contains two consecutive
points of (1/(16p))Z, hence one with odd numerator, as soon as 16 p l >= 2. So
**if W_D contains a closed interval of length l >= 1/(8p), the class is proper at
p.** The windows below are found by hand; each end point is the place where one
coordinate reaches distance exactly 1/16 (the "binding" coordinate).

| class | window in W_D | length | binding at the ends | proper at every prime p >= |
|---|---|---|---|---|
| 2, 3, 5, 7 | [1/8 + 1/192, 1/8 + 1/112] | 5/1344 | i = 12, i = 7 | 34 |
| 8 | [1/8 - 1/144, 1/8 - 1/192] | 1/576 | i = 9, i = 12 | 72 |
| 4 | [5/8 - 1/144, 5/8 - 1/192] | 1/576 | i = 9, i = 12 | 72 |
| 6 | [1/6 - 1/96, 1/6 - 1/144] | 1/288 | i = 10, i = 9 | 36 |
| 9 | [3/8 - 1/112, 3/8 - 1/192] | 5/1344 | i = 7, i = 12 | 34 |

**How the windows were found (x = 1/8 + e).** At x = 1/8 every position i/8
(or i/8 - 1/2 for i in D) is a multiple of 1/8. The only one at distance 0 from
its bad centre is i = 12 (12/8 - 1/2 = 1, and 12 is in every D), which needs
12|e| >= 1/16, i.e. |e| >= 1/192. Positions at distance 2/8 or more stay safe while
15|e| <= 3/16. The positions at distance exactly 1/8 that move toward their bad
centre when e > 0 are i in {7, 15} not in D and i in {3, 11} in D; each needs
i e <= 1/16. For classes 2, 3, 5, 7 that set is {7} or {3, 7}, which gives
e in [1/192, 1/112]. For e < 0 the moving set is i in {1, 9} not in D and i in
{5, 13} in D; for class 8 it is {1, 5, 9}, giving -e in [1/192, 1/144].
For classes 4 and 9, replacing x by x + 1/2 swaps the two kinds of condition on
the odd coordinates; the same analysis at x + 1/2 = 1/8 + e gives the windows
around 5/8 and 3/8 listed above. Class 6 (with 15 not in D and 13 in D) fails at
x near 1/8 on both sides; at x = 1/6 - f the only position at distance 0 is
i = 9 (9/6 - 1/2 = 1), which needs f >= 1/144, and the binding coordinate on the
other side is i = 10 (2/3 - 10 f >= 9/16 iff f <= 1/96). Each window was then
re-checked coordinate by coordinate, and `test_level16.py` re-checks it exactly.

*Consistency with the job.* Every window is shorter than 1/251 (5/1344 =
0.00372 < 0.00398), as it must be: U_251 kept these classes because, for each
single beta, no witness interval is longer than 1/251. The union over the 8 odd
beta is what makes the windows catch a grid point.

## 18.3 Class 1: a parity step

Class 1 is z = (1, ..., 13, 0, 15): w_i = i (mod 16p) for i != 14, and
w_14 = 14 + p k with p k = 2 (mod 16), so k = 2k' with k' = p^{-1} (mod 8) odd.

**Lemma 18.2.** For every prime p >= 244 this lift is proper.

*Proof.* Put S' = {1..13, 15} and I = [1/14 - 1/1680, 1/14 + 1/1456] (length
1/780). For x = 1/14 + e in I and i in S': the positions with ||i/14|| = 1/14 are
i = 1, 13, 15; i = 13 needs 1/14 - 13e >= 1/16 (e <= 1/1456) and i = 15 needs
1/14 + 15e >= 1/16 (e >= -1/1680), while i = 1 only needs e >= -1/112; every other
i has ||i/14|| >= 2/14 and moves by at most 15|e| < 9/112 = 2/14 - 1/16. So
||i x|| >= 1/16 for all i in S' and x in I.

For b in Z_{16p}, b w_14/(16p) = 14 b/(16p) + b k/16. Going from b to b + 4 adds
7/(2p) + k/4 = 7/(2p) + k'/2 = 1/2 + 7/(2p) (mod 1), whose norm is
1/2 - 7/(2p) >= 1/8 for p >= 10. Two points of the open arc (-1/16, 1/16) are
less than 1/8 apart, so of b and b + 4 at least one has ||b w_14/(16p)|| >= 1/16.
If both b/(16p) and (b+4)/(16p) lie in I, that one is a witness. Such a b exists
when 16p/780 >= 5, i.e. p >= 243.75. []

## 18.4 Proof of Theorem 18

For p >= 251, J_p(16) is contained in the 9 classes of U_251(16). Classes 2-9 are
proper at p by Lemma 18.1 and the table (p >= 72), class 1 by Lemma 18.2
(p >= 244), and properness does not depend on the representative of a class. So
J_p(16) is empty. []

## 18.5 What it means for the 16-runner plan

- For 14 and 15 runners the tight orbits survive every binary level at every
  prime (`THEORY.md` 8.5), so the published proof (arXiv:2609.02604, Section 4)
  runs a separate level-14 or level-15 fibre search at each gate prime. For 16
  runners, **the tight orbit (1..15) needs no fibre search at any prime p >= 251**:
  binary lifting alone removes it by level 16. A public per-prime check
  (jerryckim16/Math-Research pull request 5, 2026-11-23) reported the same at the
  79 candidate gates 251..743, one prime at a time; this section proves it for
  every prime from 251 on.
- It also proves prediction P1 (`PLAN.md`, addendum 2) and T4
  (`PLAN_addendum9.md`) at all ten pilot primes, and gives a sharp new check for
  the queued job `lrc16-uniform-v2`: its exact cascade must be empty at level 16
  at every prime it scans (`PLAN_addendum14.md`, prediction T5, written before the
  job reports). A single prime where it is not would refute this section or the
  code.
- It says nothing about the level-one cover search, which is where almost all of
  the 16-runner cost lies, nor about the other level-one orbits.

## 18.6 Not covered

- The same argument should apply to the 5 classes U_251(16) keeps for
  (1..13, 15, 28); four of them have the same "i or i + 8" shape, one has a
  coordinate off by 4. Not done here.
- Primes below 251 (where U_251 does not apply).
