# RESULTS, run 24: job lrc-nb2 (`lrc16-engine2-v4`), graded

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Graded 2026-11-24 against `PLAN_addendum11.md` (and addenda 10 and 12), which were
written before the job ran. No human expert has checked this yet. Raw outputs, copied
unchanged: `results/lrc-nb2/` (`summary_nb2.json`, `summary.json`, `stdout.txt`,
`run_tests_c.stderr.txt`, `pinned_sha256.txt`). The grading table in machine-readable
form: `results/lrc-nb2/graded_nb2.json`.

The job ran on 2026-11-24 from 02:58 to 07:03 UTC (14,714 s, 3 CPUs, peak memory
0.04 GB). It fetched every file at its published commit (`pinned_sha256.txt`), ran
the test gate, then `job_nb2.py --workers 3` (one worker per base).

## Summary

**For two of the three tight orbits of the 14- and 15-runner proofs, one prime-free
computation replaces the per-prime fibre search at every prime from 239 (15
runners) and 199 (14 runners) up.**

- (1..14), level 15: **every lift is proper at every prime p >= 239.** U_239(15) has
  one class. Its kill threshold is P* = 1980/7 (about 282.9), and the exact test
  finds no improper lift at any of the 379 primes from 239 to 2,999.
- (1..13), level 14: **every lift is proper at every prime p >= 199.** U_199(14) has
  five classes with thresholds 1848/5 (369.6), 245, 231, 231 and 245, and there is
  no improper lift at any of the 385 primes from 199 to 2,999.
- (1..11,13,24), level 14: the prime-free core U_inf(14) is empty, as the paper's
  result forces, but the level-7 search at P = 199 hit its 3,600 s cap. So the
  every-prime statement for this orbit is **untested**. `PLAN_addendum13.md` re-runs
  only this base with a longer cap.
- At all 52 gate primes of the 15-runner proof (k = 14) and the 56 gate primes of
  the 14-runner proof that are at least 199, our sets agree with the paper's outcome
  (no surviving lift). This re-checks one step of a published proof. It proves no
  new case.

## Sanity gate: passed

| check | result | evidence |
|---|---|---|
| G0 | pass | 22 tests, 0 skipped, including `CMatchesPy` (C engine) and the brute-force sandwich tests |
| R0 | pass | every set lrc-nb finished is reproduced, sizes **and** member lists (a14: 1, 1, 0, 3, and 3 without the gcd clause; a13: 1, 9; b13: 1, 5) |
| S2 | pass | all three bases: the linear lift is in U_inf at both factor levels, not in U_inf(L), status t0 |
| S3 | pass | no violations (a14 at 3, 5, 15; a13 at 2, 7, 14; b13 at 2) |
| S4 | pass | empty for a14 and a13 |
| S5 | pass | 0 violations for a14 and a13 |
| S7 | pass for a14 | inf and P0 agree (3 and 20 gcd-clause members removed); a13, b13 untested (gcd-free step cut at 1,200 s) |
| C1 | pass | a14 inf B = A = C = 0, a14 P0 B = A = C = 1; a13 inf B = A = C = 0, a13 P0 B = C = 5 (A cut); b13 inf B = A = C = 0 |

## Predictions

| | prediction | result |
|---|---|---|
| N1 | U_inf(15) empty for a14 | **holds** (three routes) |
| N2 | a14 statement at P0 = 239 | **holds**: P*_15 = 1980/7, J_p(15) empty at 379 primes 239..2999 |
| N3 | U_inf(14) empty for a13 and b13 | **holds** (three routes each) |
| N4 | a13 and b13 statements at P0 = 199 | **holds for a13** (P*_14 = 1848/5, J_p(14) empty at 385 primes 199..2999); **untested for b13** (level-7 step at P = 199 cut at 3,606 s) |
| X1 | J_p(L) empty at the paper's gate primes in range | **holds where tested**: 52 of 52 (k = 14); 56 for a13 (k = 13, primes >= 199); b13 untested |
| S | every phase-1 step at P = inf within its cap | **holds, narrowly**: a13 1,697 s and b13 1,705 s against a 1,800 s cap |

## Recorded, not graded

- I1 (a14): at each of the 52 gate primes, 3 gcd-free witness-free classes up to
  units of Z_15 (the zero class, the multiples of 3 and the multiples of 5), and all
  3 meet the gcd clause. The paper reports "seven candidates" that all fail
  Definition 2.1(a); its counting convention may differ, so this is not compared.
- I2: untested.
- Where the time went (phase 1): a14 86.8 s in all; a13 3,211.8 s, mostly the
  level-7 step (1,697 s at P = inf, 1,514 s at P = 199, 18,839,529,813 nodes each);
  b13 5,311.3 s, of which 3,606 s is the cut level-7 step at P = 199.

## Scope (from `REVIEW_16.md`, repeated as required)

1. Our cascade prunes only by the gcd clause, t = 0 and grid witnesses. If the
   paper's search also certifies lifts by other means, our sets can only be larger.
   So "empty" (all results above) is the strong direction.
2. The gates below 199 are not covered. The paper's second gate set for k = 13 also
   has 83, 139, 167, 181 and 191.

The statements rest on Lemma U (`THEORY.md` 8, extended in `THEORY_16.md`), Lemmas
E, T, R (`THEORY_15.md`) and Lemma S (`THEORY_17.md`), reviewed adversarially in
`REVIEW_15.md`, `REVIEW_16.md` and `REVIEW_17.md`. Not by a human yet.

## Next

- `lrc16-engine2-v5` (`PLAN_addendum13.md`): b13 only, one worker, the level-7 step
  at P = 199 capped at 4.5 hours.
- Then: the same method for the 16-runner tight orbit (1..15) is `lrc16-uniform-v2`
  (queued since 2026-11-22).
