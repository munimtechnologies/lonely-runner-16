# RESULTS, run 29: job lrc-nb2-b13 (`lrc16-engine2-v5`), graded

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Graded 2026-11-24 against `PLAN_addendum13.md` (with addendum 10 for S2-S5), which was
written before the job ran. No human expert has checked this yet. Raw outputs, copied
unchanged: `results/lrc-nb2-b13/` (`summary_nb2.json`, `base_b13.json`,
`caps_b13.json`, `pinned_sha256.txt`, `summary.json`, `stdout.txt`,
`run_tests_c.stderr.txt`).

The job ran on 2026-11-24 from 12:56 to 15:36 UTC (9,581 s, 1 CPU, peak memory
0.04 GB). It fetched every file at its published commit (`pinned_sha256.txt`; `job_nb2.py`
from commit 57f59b9, unchanged), ran the C-required test gate, then `job_b13.py` with
the caps fixed in addendum 13 (`caps_b13.json`).

## Summary

**The third tight orbit of the 14-runner proof, (1..11, 13, 24), is settled at every
prime p >= 199 by one computation.** Every lift of its orbit to level 14 is proper at
every prime from 199 up. With `RESULTS_run24.md`, all three tight orbits that the
published 14- and 15-runner proof (arXiv:2609.02604) searches separately at each gate
prime now reduce to one prime-free computation each:

| orbit | level | every prime from | classes in U_P0(L) | largest kill threshold | primes checked one by one |
|---|---|---|---|---|---|
| (1..14) | 15 | 239 | 1 | 1980/7 (282.9) | 379 (239..2,999) |
| (1..13) | 14 | 199 | 5 | 1848/5 (369.6) | 385 (199..2,999) |
| **(1..11, 13, 24)** | **14** | **199** | **3** | **245** | **385 (199..2,999)** |

This re-checks one step of a published proof. **It proves no new case** of the
conjecture, and the gate primes below 199 are not covered.

## Sanity gate: passed

| check | result | evidence |
|---|---|---|
| G0 | pass | 22 tests, 0 skipped (`run_tests_c.stderr.txt`), including the C engine tests `CMatchesPy` |
| R0 | pass | U_inf(2) = 1 class, U_inf(7) = 1 class with member (1,2,3,4,5,6,0,1,2,3,4,6,3), U_inf(14) empty, U_199(2) = the same 5 members as lrc-nb2 (compared list by list with `results/lrc-nb2/summary_nb2.json`) |
| S2 | pass | the linear lift is in U_inf at levels 2 and 7, not in U_inf(14), status t0 |
| S3 | pass | no violations at 2, 7, 14 |
| S4 | pass | empty |
| S5 | pass | 0 violations |
| C1 | pass | P = inf: route B = route C = 0; P = 199: route B = route C = 3 classes (route A cut at its 60 s cap, as planned, so route C ran) |

## Predictions

| | prediction | result |
|---|---|---|
| N4b | U_199(14) computed without a cut, J_p(14) empty at every scanned prime, P*_14 inside the scan | **holds**: no step cut; U_199(14) has 3 classes with kill thresholds 2352/11 (213.8), 245 and 231, so P*_14 = 245; J_p(14) empty at all 385 primes from 199 to 2,999 |
| X1b | J_p(14) empty at the 56 paper gate primes 199..547 | **holds**: 56 of 56 |

So: **for every prime p >= 199, every lift of the orbit of (1, ..., 11, 13, 24) to
level 14 is proper** (primes 199..2,999 one by one; above 2,999 by the kill threshold
245).

## Recorded, not graded

- Time: the level-7 step took 1,949 s at P = inf and 6,632 s at P = 199 (cap 16,200 s);
  both visited 18,839,529,813 nodes, the same count as for (1..13) in lrc-nb2. The
  one-hour cap of lrc-nb2 was simply too short.
- S7 (gcd-free cross-check): untested again; both gcd-free level-7 steps were cut at
  their 300 s caps, as addendum 13 allowed.
- The three classes of U_199(14): (1,2,3,4,5,6,7,0,9,10,11,13,10),
  (1,2,3,4,5,6,7,8,9,10,11,13,0) and (1,2,3,11,12,13,0,1,2,10,11,13,3), residues mod 14
  in the order of the speeds.

## Scope (from `REVIEW_16.md`, repeated as required)

1. Our cascade prunes only by the gcd clause, t = 0 and grid witnesses. If the paper's
   search also certifies lifts by other means, our sets can only be larger, so "empty"
   is the strong direction.
2. The gates below 199 are not covered. The paper's second gate set for k = 13 also has
   83, 139, 167, 181 and 191.
3. The statement rests on Lemma U (`THEORY.md` 8, extended in `THEORY_16.md`), Lemmas E,
   T, R (`THEORY_15.md`) and Lemma S (`THEORY_17.md`), reviewed adversarially by AI
   agents in `REVIEW_15.md`, `REVIEW_16.md` and `REVIEW_17.md`, not by a human yet.

## Next

- Update the article `lonely-runner-tight-orbits-every-prime` (same slug) with the third
  orbit.
- The same method for the 16-runner orbits is `lrc16-uniform-v2` and the brute-force
  check `lrc16-indep-v1` (both queued).
