# REVIEW_18: an adversarial pass over THEORY_18 (the tight orbit dies at level 16)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; text CC BY 4.0.
Written 2026-11-24 (run 27). The reviewing agent was told to break `THEORY_18.md`:
re-derive every step without reusing its code, look for the weakest premise, and
report anything that changes a claim. **This is an AI review, not a human one.**

Companion test: `test_review18.py` (standard library only; it imports no repository
code and reads no data file; it starts from the 9 residue vectors alone and finds
the windows by a different algorithm, an exact sweep over all bad arcs).

## Verdict

**No error found in THEORY_18's own steps.** Every window, the lift form, the
parity step and the assembly of the proof re-derive by hand. The weakest premise is
not in THEORY_18 at all: it is input (ii), the computer list U_251(16) from
`uniform.py`. A wrong kill there (a lift declared proper that is not) would remove a
class before THEORY_18 ever sees it. No brute-force check of that list at k = 15 has
run yet. This run builds one (`indep.py`, `indep_brute.c`) and queues it as job
`lrc16-indep-v1`, with predictions registered before it runs (`PLAN_addendum15.md`).
One wording point in `PLAN_addendum14.md` is corrected below (R5d).

## R1. Lemma 18.1 (fixed windows for odd b): correct

- Lift form. For the 8 classes of D-shape (z_i = i or i + 8 mod 16), the unique lift
  with w_i = i (mod p) and w_i = z_i (mod 16) is w_i = i + 8p[i in D]: since p is
  odd, i + 8p = i + 8 (mod 16), and the lift is unique by CRT. `test_review18`
  finds the lift by search (w_i = i + p t, 0 <= t < 16) and confirms the form at
  every prime 251..400.
- For odd m and x = m/(16p): m w_i/(16p) = i x + m[i in D]/2 = i x + [i in D]/2
  (mod 1), and ||y + 1/2|| = ||y - 1/2||. So m is a witness iff x is in W_D. Correct.
- Grid claim. A closed interval of length >= 2/(16p) contains two consecutive points
  of (1/(16p))Z, one with an odd numerator. Correct.
- Side claims checked: every D contains 8 (if not, beta = 1 at t = 0 puts every
  coordinate at a nonzero multiple of 1/16, a witness, so U_inf would have killed
  the class: correct); no D contains 1 or 4 (read off the data; not used).

## R2. The windows: all 9 re-derived coordinate by coordinate

Each window was redone by hand at x = c + e (c = 1/8, 5/8, 3/8, 1/6, 1/14), listing
all 15 positions and the side each one moves toward. Results:

| class | window | lower end binds | upper end binds | all other coordinates |
|---|---|---|---|---|
| 2, 3, 5, 7 | [1/8 + 1/192, 1/8 + 1/112] | i = 12 (in D): 12e = 1/16 | i = 7 (not in D): 1/8 - 7e = 1/16 | class 7's i = 3 (in D) at 1/8 - 3e >= 11/112; the rest move away or start >= 2/8 from their centre |
| 8 | [1/8 - 1/144, 1/8 - 1/192] | i = 9: 1/8 - 9f = 1/16 | i = 12: 12f = 1/16 | i = 1, 5 need f <= 1/16, 1/80: slack |
| 4 | [5/8 - 1/144, 5/8 - 1/192] | i = 9 (in D): 1/8 - 9f | i = 12 (in D): 12f | i = 5 needs f <= 1/80: slack |
| 6 | [1/6 - 1/96, 1/6 - 1/144] | i = 10 (in D): 1/6 - 10f | i = 9 (in D): 9f | closest other: i = 1 at 1/6 - f >= 15/96 |
| 9 | [3/8 - 1/112, 3/8 - 1/192] | i = 7 (in D): 1/8 - 7f | i = 12 (in D): 12f | i = 15 lies in [0.491, 0.547]: slack |
| 1 | [1/14 - 1/1680, 1/14 + 1/1456], speeds without 14 | i = 15: 1/14 + 15e = 1/16 | i = 13: 1/14 - 13e = 1/16 | i = 1 needs e >= -1/112; others >= 2/14 - 15/1456 |

(e > 0 means x above the centre, f = -e.) Every window is a whole component of the
good set: both of its ends are binding, and the coordinate moves toward its bad
centre just outside. `test_review18` confirms this with an exact sweep: for each
class it lists every maximal component of W_D on the circle and finds that the hand
window **is** one of them, of length at least 2/(16 * 251) (classes 2-9) or
5/(16 * 251) (class 1). The class-1 margin is thin but exact: 1/780 = 0.0012821
against 5/4016 = 0.0012450.

## R3. Lemma 18.2 (class 1, parity step): correct

w_14 = 14 + p t with p t = 2 (mod 16), so t = 2 p^{-1} (mod 16) is 2 times an odd
number, 4t = 8 (mod 16), and 4 w_14 = 56 + 8p (mod 16p). So b -> b + 4 moves
coordinate 14 by (8p + 56)/(16p) = 1/2 + 7/(2p), at distance 1/2 - 7/(2p) >= 1/8
from the nearest integer once p >= 10. Two points of the open arc (-1/16, 1/16) are
less than 1/8 apart, so b or b + 4 clears coordinate 14. The other 14 coordinates are
w_i = i and are cleared by I. Both b/(16p) and (b + 4)/(16p) fit in I when
16p/780 >= 5, i.e. p >= 243.75. `test_review18` checks 4 w_14 = 56 + 8p with the
lift found by search, at every prime 251..1500.

## R4. Assembly: correct, and it needs less than stated

The proof needs only J_p(16) ⊆ U_251(16) (Lemma U(i)) plus properness of the 9
classes; the equality "J_p(16) = {z in U_251(16) : improper}" quoted from Lemma R
is true but not needed. Properness is constant on a unit class (Lambda = lambda mod
16, 1 mod p maps lifts to lifts and permutes the times b), so one representative per
class suffices. Primes covered: classes 2-9 from 72 (or 34/36), class 1 from 244,
all below 251. Correct.

## R5. Where it could still be wrong (ranked)

**(a) The U_251(16) list itself (input ii). Highest risk, now being tested.** Lemma
U(i) is proved (R5b), but THEORY_18 also needs `uniform.py` never to over-kill at
levels 2, 4, 8, 16 for this orbit. Evidence so far: `test_uniform.py` compares the
cascade with brute force, but only for 3- to 7-speed sets; and the per-prime run in
jerryckim16/Math-Research pull request 5 (independent code) found (1..15) dead by
level 16 at the 79 primes 251..743, which is what Theorem 18 predicts there. Neither
is a k = 15 brute-force check of U_251 itself. **New:** `indep.py` and
`indep_brute.c` compute J_p(L) from the bare definition (every lift, every time b,
no Lemma D, no arcs, no units, no pruning) and compare its unit classes with the
committed U_251 lists at every level, at every prime from 251 up to the time cap
(job `lrc16-indep-v1`, `PLAN_addendum15.md`).

**(b) Lemma U(i): re-read, correct.** A P-killed class is proper at every prime
p >= P: (a) is the gcd clause; (b) is a time with sigma = 0; (c) an open arc longer
than 1/P >= 1/p contains a point of (1/p)Z, which is a strict, hence non-strict,
witness. Induction over levels holds because each cascade lifts only its own
survivors.

**(c) The definition of "proper"** (non-strict 1/(k+1), and "at most one odd z_i"
as the gcd clause at binary levels) is meant to match arXiv:2609.02604. That match
was reviewed in `REVIEW_THEORY_2_7.md` and remains one of the items a human must
check against the paper.

**(d) Correction to `PLAN_addendum14.md` (wording only).** It calls T5 of
`lrc16-uniform-v2` "an independent computation". `thresh.py` is independent of
THEORY_18's windows, but its exact per-prime cascade runs **inside** U_251, so it
cannot see an over-kill by `uniform.py` (R5a). T5 still tests THEORY_18's hand
argument; `lrc16-indep-v1` is the check that also tests input (ii).

## R6. Facts asserted by `test_indep.py`, with proofs

(a) (1..15) is improper at level 1 at p = 251: ||i x|| >= 1/16 for i = 1..15 forces
the 16 points 0, x, ..., 15x to be pairwise >= 1/16 apart, so x = j/16 with j odd
(THEORY.md 8.5); b/251 is never such a point.
(b) The linear lift w_i = i is improper at levels 2, 4, 8 and proper at 16 (p = 251):
a witness needs b/(Lp) = j/16, i.e. 16b = jLp, impossible when L <= 8 because the
right side has 2-adic valuation v(L) <= 3; there are 8 odd z_i, so no gcd clause; at
L = 16, b = p gives x = 1/16.
(c) For s = (1, 2, 3) (k + 1 = 4) at p = 11: level 1 is improper by the same tight
argument; the linear lift (1, 0, 1) is improper at level 2 (b/22 = j/4 is impossible);
the linear lift (1, 2, 3) is proper at level 4 (b = 11).
(d) Unit invariance: Lambda = lambda (mod L), 1 (mod p) is a unit of Z_{Lp}; it fixes
w mod p and maps the time b to b Lambda. The gcd clause depends only on parities,
which odd lambda keeps.

No prediction of the job is asserted in any test.
