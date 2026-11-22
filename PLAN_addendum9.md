# PLAN, addendum 9 (2026-11-22, run 16, before any result of lrc16-uniform-v2)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` and addenda 6-8 (all unchanged and still in force).

Written at about 23:55 UTC on 2026-11-22. `lrc16-uniform-v1` and `lrc16-pilot-v1`
have reported (graded in `RESULTS_run16.md`); `lrc16-shift-v2` is running;
`lrc16-engine3-v1`, `lrc16-orbit-v1`, `lrc-repro-k14-v1` and `lrc16-allik-probe-v1`
are queued. No output of `lrc16-uniform-v2` exists.

Job `lrc16-uniform-v2` (`job_uniform2.py`, method in `THEORY_15.md`) computes, for
s = (1..15) ("e15") and s = (1..13,15,28) ("gw15"): U_251(L) to L = 128, the kill
threshold P*(z) of every listed lift and P*_L per level, and the exact sets J_p(L)
at every prime p from 251 to B (B = max(3000, min(20000, floor(P*_128) + 1)), cut
short only by the 60-minute per-orbit deadline, reported as `scanned_to`). All
readings below come from `summary_uniform2.json`.

## Predictions

**T1 (primary).** For e15, at every prime 251 <= p <= `scanned_to`, the exact
cascade is empty by level 128 (`n_persist_to_last_level` = 0). **Falsified** by
any prime with `death_level` null (its level-128 survivors are listed); untested
if the U_251 cascade is cut before level 128.

**T2.** For e15, the uniform statement of `THEORY_15.md` 15.5 holds
(`statement.holds` = true): some P*_L with L <= 128 is at most `scanned_to`.
Then the orbit of (1..15) has no improper lift at level `statement.level` at any
prime p >= 251. **Falsified** if `statement.holds` is false while T1 holds and
the run was not cut (P*_128 above the scanned range).

**T3.** T1 and T2 for gw15.

**T4 (= P1 of addendum 2, second reading).** For e15, J_p(16) is empty at each of
the ten pilot primes (`pilot[].J16` = 0). P1's own reading stays the one in
`lrc16-shift-v2`; this is an independent method. Reported as counts of primes
where it holds and fails.

## Checks (failure of any one means a bug; nothing from `thresh.py` is then used)

- **S2:** no lift is improper at a prime above its threshold (`S2_violations` = 0).
- **S4:** no lift listed in U_251 is killed by the threshold rule at P = 251.
- **S5:** U_inf(L) = {z in U_251(L) : P*(z) infinite} for L <= 32.
- **S6:** every improper lift at every prime has an improper parent (Lemma R).
- **R1 (re-run):** the U_251 and U_inf sizes for levels 1-32 equal those of
  `lrc16-uniform-v1` (e15: 20, 13, 17, 9, 2 for P = 251; 1, 1, 1, empty at 16 for
  P = infinity; gw15: 10, 8, 12, 5, 2; base killed for P = infinity).
- **X5 (with `lrc16-shift-v2`, read when both have reported).** At each pilot
  prime, the (1..15) probe of `lrc16-shift-v2` keeps 0 lifts at level 16 exactly
  when `pilot[].J16` = 0. A disagreement is a bug in `lrc.c` or in `thresh.py`.

## Measurements (no prediction)

P*_L for L = 16, 32, 64, 128; the histogram of death levels over primes; the
primes with the latest death; the run time.

## What each outcome means

- T1 and T2 hold: the tight orbit (1..15), the only one of its kind for 16
  runners (`THEORY.md` 7), dies by a fixed binary level at every prime a gate can
  use, so the 16-runner computation needs no fibre search for it, unlike 14 and 15
  runners. This settles `PLAN.md` step 4 for this orbit, conditional on Lemma U,
  `THEORY_15.md` and the code, and still to be checked by a second implementation
  (X5 covers ten primes).
- T1 holds, T2 fails: the same at every scanned prime, which already covers every
  planned gate (gates lie below about 1,000); the statement for all primes waits
  for a longer scan.
- T1 fails: the primes where (1..15) persists to level 128 are listed. At those
  primes the orbit needs either deeper lifting (level 256 and up, cheap for a
  single orbit) or a fibre search as in arXiv:2609.02604; a prime with a truly
  persistent lift cannot be a gate without one.
