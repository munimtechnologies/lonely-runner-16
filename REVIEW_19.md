# REVIEW 19: an adversarial pass on THEORY_19 (the orbit (1..13, 15, 28) at level 16)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written 2026-11-24 (run 29). The reviewing agent was told to break `THEORY_19.md`, not
to confirm it. **This is an AI review, not a human one.** Companion test:
`test_review19.py` (standard library only; shares no code with `test_level16_gw.py` and
imports no repository module).

## Verdict

**No error found that changes a claim.** Theorem 19 (at every prime p >= 251, no lift
of the orbit of gw15 = (1, ..., 13, 15, 28) to level 16 is improper) follows from its
two stated inputs, Lemma U(i) and the list U_251(16) of job `lrc16-uniform-v1`. One gap
in how it had been checked is closed here (R1).

## What was attacked, and how

### R1. The class list (input (ii)) had not been compared with the raw output in CI

`test_level16_gw.py` compares its 5 classes with
`results/lrc16-uniform-v1/summary_uniform.json` only when that file is present, and the
commit that added THEORY_19 did not include it, so the publish gate **skipped** that
comparison. This review compared the list by hand with the raw job output
(base "gw15", P = 251, level 16: "survivors": 5, all 5 vectors identical, in the order
g1..g5) and adds the raw file to the same commit as `test_review19.py`, whose
`test_class_list_matches_raw_output` then runs. The raw output also shows 2 classes
surviving U_251 at level 32 (both children of g1); that is the over-approximation of the
prime-free cascade, not a contradiction, since Theorem 19 shows the true set is already
empty at level 16.

### R2. The lift form

Re-derived by CRT: w_j = s_j + p t_j with t_j = (z_j - s_j) p^{-1} (mod 16). For an
offset z_j - s_j of 8, t_j = 8 p^{-1} = 8 (mod 16) because p^{-1} is odd; for offset 0,
t_j = 0. For g1 the speed-28 offset is 0 - 28 = 4 (mod 16), so t = 4 p^{-1} (mod 16)
= 4 (p^{-1} mod 4), which is 4 or 12, matching 28 + 4 t' p with t' odd. The test computes
the lift by this formula (not by search, as the first test does) and checks it at 40
primes.

### R3. The odd-time reduction

For odd b and w_j = s_j + 8p [s_j in D]: b w_j / (16p) = s_j x + b/2 [s_j in D] with
x = b/(16p), and b/2 = 1/2 (mod 1). Exact, and it is the only place where "b odd" is
used. Consecutive odd b give x values 1/(8p) apart, so a closed window of length at
least 1/(8p) holds one. Correct.

### R4. The residue rule (19.2) and the four windows

Recomputed r_s = (j s - 4 [s in D]) mod 8 for every speed of every class at the stated
centre (g5 through its mirror at j = 7):

- g2 and g3 at j = 3: the smallest upper end is 1/9 (s = 9, r = 7); r_11, r_13, r_15 =
  (5, 3, 1) for g2 and (5, 3, 5) for g3.
- g4 at j = 1: smallest upper end 1/7 (s = 7, r = 7); r_11, r_13, r_15 = (3, 5, 3).
- g5 at j = 7: smallest upper end 1/9 (s = 9, r = 7); r_11, r_13, r_15 = (5, 3, 1).
- The only r_s = 0 is s = 12 in every case: odd s give odd r; s = 2, 6, 10 (2 or 6 mod 8)
  give 2 or 6; for s = 4, 12, 28 (all 4 mod 8) r = 0 exactly when s is in D, and only 12 is;
  for s = 8, r = 4 because 8 is in every D.
- The claim that (15 - 2r)/s < 1/12 + 2/251 forces r = 7 and s in {11, 13, 15}: for
  r = 6 it would need s > 32.9 and for r = 5, s > 54; no speed is that large. Correct.

Independently of the rule, `test_review19.py` checks each window by the image of a
linear map: for every speed s and centre c (0 or 1/2), s [a, b] + c must lie inside one
arc [k + 1/16, k + 15/16]. It also checks that each window is tight: one named speed sits
exactly on 1/16 at the left end and another exactly on 15/16 at the right end
(g2, g3: 12 and 9; g4: 12 and 7; g5: 9 and 12; g1: 15 and 13).

### R5. Class g1 and Lemma 19.1

- The interval I = [1/14 - 1/1680, 1/14 + 1/1456] of Lemma 18.2 serves the 14 speeds
  {1, ..., 13, 15} (14 is not a speed of gw15). Re-derived: only s = 13 (upper end,
  13/14 + 13e <= 15/16 gives e <= 1/1456) and s = 15 (lower end, 1/14 + 15e >= 1/16 gives
  e >= -1/1680) bind; s = 1 keeps 1/14 - 1/1680 > 1/16, and every other speed has
  ||s/14|| >= 1/7. Length 13/21840 + 15/21840 = 1/780.
- Step of 2: 2 w_28 = 56 + 8 t' p = 56 + 8p (mod 16p) for t' = 1 or 3, of norm
  (8p - 56)/(16p) = 1/2 - 7/(2p) >= 1/8 for p >= 10. Two points of the open bad arc
  (-1/16, 1/16) are less than 1/8 apart, so b and b + 2 cannot both be bad.
- Room for b and b + 2 inside I: 16p/780 >= 3, true from p = 147 (146 gives 2.995).
  The time b need not be odd here, because the other 14 coordinates are linear.

### R6. Assembly and scope

- Units: multiplying a lift by a unit of Z_{16p} permutes the times, so properness is a
  property of the class; the orbit (lambda s mod p) reduces to s itself by a unit that is
  1 mod 16. Correct, and the same as in Theorem 18.
- The theorem's content is the primes 251 to 1,327; above 1,344 the orbit is already
  proper at level 1 by `THEORY.md` 7.3 (reviewed in `REVIEW_THEORY_2_7.md`). The section
  says so. No overstatement found: THEORY_19 says plainly that it proves no case of the
  conjecture and does not touch the level-one cover search.

## What the test does at every prime

At every prime from 251 to 1,500 and for each class, `test_review19.py` tests **every**
odd time in the g2..g5 windows and every pair b, b + 2 in the g1 interval against the
actual integer lift (a stronger statement than the theorem needs: one time per prime
would do). It also runs a plain search over all times at 251, 257, 1,321 and 1,327, the
last two being the largest primes where the theorem has content.

## What a human must still check

1. Lemma U(i) (`THEORY.md` 8.2 and `THEORY_9.md`): that the prime-free cascade contains
   J_p(L) for every p >= 251. Every claim here rests on it.
2. The code that produced U_251(16) (`uniform.py`). The queued brute-force job
   `lrc16-indep-v1` tests it from the bare definition (predictions I2 and I6 of
   `PLAN_addendum15.md` and `PLAN_addendum16.md`).
3. That gw15 and (1..15) are the right orbits to single out for 16 runners (they follow
   Zhang's and Goddyn and Wong's tight-set analysis); other orbits are not treated.
