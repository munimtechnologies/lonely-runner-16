# Results, run 32 (2026-11-24): lrc16-uniform-v2

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Every number below is read from the raw
outputs committed unchanged in `results/lrc16-uniform-v2/` (`summary.json`,
`stdout.txt`, `stderr.txt`, `out/summary_uniform2.json`, `out/pinned_sha256.txt`).
Rules: `PLAN_addendum9.md` (T1-T4, S2-S6, R1, X5; written 2026-11-22 before the job
ran) and `PLAN_addendum14.md` (T5, X6; written 2026-11-24 before the job ran).

## The run

Blade, 2026-11-24 21:21-21:30 UTC (557 s; 1 CPU, 1 GB cap; peak memory not
reported). Step 1 fetched `uniform.py` at commit 026f1ee and recorded its SHA-256
(0110b558...). Step 2 ran the 9 tests of `test_thresh.py` (exact per-prime test
against brute force, thresholds against `uniform.py`): all OK. Step 3
(`job_uniform2.py`) exited 0. Neither base was cut: both reached level 128 and
scanned every prime from 251 to 2,999 (377 primes; scan bound B = 3,000).

## Raw readings

| | e15 = (1..15) | gw15 = (1..13, 15, 28) |
|---|---|---|
| U_251(L) sizes, L = 1, 2, 4, 8, 16, 32, 64, 128 | 1, 20, 13, 17, 9, 2, 4, 8 | 1, 10, 8, 12, 5, 2, 4, 8 |
| P*_L (kill threshold of the whole level) | inf, inf, inf, inf, **288**, 264, 264, 264 | 1344, 1344, 1344, 1344, 288, 264, 264, 264 |
| U_inf(L) sizes | 1, 1, 1, 1, **0 at 16** | 0 at level 1 |
| primes scanned | 377 (251..2,999) | 377 (251..2,999) |
| primes with a lift surviving to level 128 | **0** | **0** |
| death level histogram | 16: **377** | 1: 306, 2: 46, 4: 21, 8: 4 |
| latest death | level 16 at every prime | level 8 at p = 257, 269, 281, 293 |
| pilot J16 (10 primes) | 0 at all 10 | 0 at all 10 |
| sanity S2 / S4 / S5 / S6 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| `L_uniform` / `statement.holds` | 16 / false (see T2) | 1 / false (see T2) |

The 9 classes of U_251(16) for e15 thresholds (longest witness cell): 264, 260,
260, 288, 260, 1344/5, 1344/5, 288, 260.

## Grades

- **T1 (primary): HOLDS.** For e15 the exact cascade is empty by level 128 at all
  377 primes from 251 to 2,999 (`n_persist_to_last_level` = 0). No prime untested.
- **T2: the stated condition holds; the pre-registered flag is defective.** T2 asks
  that some P*_L with L <= 128 be at most `scanned_to`. It is: P*_16 = 288 <= 2,999.
  But the reading `statement.holds` came out **false**, and not for the reason the
  plan names (P*_128 = 264 lies inside the scanned range, and the run was not cut).
  The cause is a bug in `job_uniform2.py` line 162: the flag also requires
  `scanned_to >= B_MIN` with B_MIN = 3,000, while `scanned_to` is the last prime
  scanned below B = 3,000, which is 2,999. The flag could never be true. We do
  **not** count T2 as a clean pass; we report that its defining condition holds in
  the raw numbers and that the flag meant to record it was wrong.
- **T3: T1 HOLDS for gw15** (0 primes persist; every prime dies by level 8). T2
  for gw15: same as above (P*_1 = 1344 <= 2,999; flag false by the same bug).
- **T4: HOLDS at 10 of 10 pilot primes** (`J16` = 0 at 251, 283, 307, 353, 401,
  449, 503, 601, 701, 809).
- **T5 (addendum 14): HOLDS.** At every one of the 377 primes 251 <= p <= 2,999 the
  per-prime record of e15 has level-16 count 0 and death level 16. The exact
  per-prime test of `thresh.py` agrees with Theorem 18 (`THEORY_18.md`) at every
  scanned prime. Theorem 18 stays.
- **S2, S4, S5, S6: all 0.** No lift is improper above its threshold; no listed lift
  is killed at P = 251; U_inf(L) matches the infinite-threshold lifts; every improper
  lift has an improper parent.
- **R1: HOLDS.** U_251 sizes for levels 2-32 equal those of `lrc16-uniform-v1`
  (e15: 20, 13, 17, 9, 2; gw15: 10, 8, 12, 5, 2); U_inf for e15 is 1, 1, 1, 1 and
  empty at 16; gw15's base is killed for P = infinity.
- **X5: HOLDS.** At each of the ten pilot primes the (1..15) probe of
  `lrc16-shift-v2` (`RESULTS_run17.md`) keeps 0 lifts at level 16, and `pilot[].J16`
  = 0 here. Two separate codes (`lrc.c`, `thresh.py`) agree.
- **X6 (addendum 14): HOLDS.** The 9 residue vectors of U_251(16) for e15 in this
  re-run are identical, vector by vector, to the 9 classes of
  `level16_certificate.json` (taken from `lrc16-uniform-v1`). Theorem 18's input is
  unchanged.

## What it means

1. **(1..15): the death level is exactly 16 at every prime p >= 251.** Upper
   bound: for p > 288 every class of U_251(16) is past its kill threshold, and for
   251 <= p <= 2,999 the exact test finds none improper. Lower bound: U_inf(8) is
   not empty (the linear lift), and Lemma U puts U_inf(8) inside J_p(8) at every
   prime. So level 16 is both needed and enough. This is a computer statement,
   reached by a route separate from the hand proof of `THEORY_18.md` (thresholds and
   exact per-prime tests instead of odd-time windows), with the same inputs: Lemma U
   and the `uniform.py` class list.
2. **(1..13, 15, 28): dies by level 8 at every prime p >= 251.** For p > 1,344 the
   base is proper at level 1 (P*_1 = 1344); from 251 to 2,999 the exact test finds
   the latest death at level 8 (p = 257, 269, 281, 293). This sharpens Theorem 19
   (level 16) to level 8, as a computer statement with the same inputs.
3. **What it does not do.** Both statements rest on `uniform.py`'s lists, which this
   job re-ran rather than re-derived. The from-scratch brute-force check of those
   lists (`lrc16-indep-v1`, `PLAN_addendum15.md`) is still queued. Nothing here
   reduces the main cost of a 16-runner proof (the level-one cover search at about
   80 gate primes) or proves any case of the conjecture.

## Fix for the flag

The correct condition is "the scan was not cut by the deadline" (all primes below B
were scanned). It will be fixed in the next version of the job if one is run; this
run's grades are read from the raw numbers above, not from the flag.
