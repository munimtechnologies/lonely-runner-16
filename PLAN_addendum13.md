# PLAN, addendum 13: job lrc-nb2-b13 (pre-registered 2026-11-24, run 24)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written before the job ran, right after grading lrc-nb2 (`RESULTS_run24.md`).

## Why

lrc-nb2 settled a14 = (1..14) at level 15 (every prime >= 239) and a13 = (1..13) at
level 14 (every prime >= 199). For b13 = (1..11,13,24) the prime-free core U_inf(14)
is empty (N3), but the level-7 step at P = 199 was cut at its 3,600 s cap, so N4 is
untested for b13. The same step took 1,514 s for a13 and was not cut.

## What runs

Compete job `lrc16-engine2-v5`: `fetch_nb3.py` (every file at its published
commit), `run_tests_c.py` (C tests required), then `job_b13.py`. It runs
`job_nb2.py` from commit 57f59b9 **unchanged**, for b13 only, with one worker and
these caps: P = inf: f1 900 s, f2 3,600 s, B 1,800 s; P = 199: f1 900 s,
f2 16,200 s, B 3,600 s; route A 60 s (so route C runs next); gcd-free steps 300 s;
job deadline 400 min. The caps are written to `caps_b13.json`.

## Gate (any failure means a bug; then nothing below is used)

- G0: the 22 tests pass with 0 skipped.
- R0: the b13 sets of lrc-nb2 are reproduced exactly: |U_inf(2)| = 1, |U_inf(7)| = 1
  (member (1,2,3,4,5,6,0,1,2,3,4,6,3)), U_inf(14) empty, |U_199(2)| = 5 with the
  same five members.
- S2, S3, S4, S5 as in addendum 10. C1: routes B and C agree on U_199(14) if both
  finish.

## Prediction

- **N4b:** the b13 statement holds at P0 = 199: U_199(14) is computed without a cut,
  J_p(14) is empty at every scanned prime, and P*_14 is within the scan. Then every
  lift of the orbit of (1..11,13,24) to level 14 is proper at every prime p >= 199.
- **X1b:** J_p(14) is empty at each of the 56 paper gate primes from 199 to 547.

## Outcomes

- N4b holds and the gate passes: commit the results, add them to `RESULTS` and
  update the article `lonely-runner-tight-orbits-every-prime` (same slug): all
  three tight orbits of the 14- and 15-runner proofs then reduce to one
  computation each.
- Still cut: report the seconds and do not re-file without a faster method (for
  example sharding the level-7 search by the residue of the first free coordinate).
- J_p(14) non-empty at a paper gate prime: a disagreement with arXiv:2609.02604.
  Bug hunt first (start with the question in addendum 12); no claim, no contact
  without a second independent check and Sheehan's OK.
