# PLAN addendum 7 (2026-11-22, run 14, before any engine-3 result)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.

Job `lrc16-engine3-v1` (`job_engine3.py`) runs engine 3 (`lrc.c` with
LRC_PRUNE = 3, `THEORY_13.md`). No engine-3 result of any kind exists as this is
written: the code has never been compiled or run (this run has no shell; the job
compiles it). Its unit tests (`test_prune.py`, `test_c.py`) run first; if any
fails, nothing below is graded.

## Readings and what counts

**A1 (cross-check, decisive).** On every gate of Part X (the 12 gates of the
engine-2 cross-check, k = 8 to 14, p = 61 to 241) where the cover search and the
cascade finish with both LRC_PRUNE = 0 and 3: identical tau, orbit counts by
size, tuples, killed, survived, overflow, completeness and per-level improper
counts. Any disagreement is a bug: it is reported, and no engine-3 result is used
until it is explained.

**A2 (consistency).** At each of the 24 (k, p) of Part T that `lrc16-tau-v2`
decided in 3.5 s or more (12 for k = 15, 12 for k = 14): engine 3 gives the same
answer (tau <= k - 2 with the same tau, or no cover on <= k - 2 classes). Every
cover it returns passes an independent Python check (it covers every folded time
and every class has a private time). A disagreement voids engine 3 as A1 does.

**S1 (prediction: speed).** The median, over Part T rows, of
(seconds with LRC_PRUNE = 0) / (seconds with LRC_PRUNE = 3), both measured in the
same job on the same machine, is **at least 3**. Rows where LRC_PRUNE = 3 hits
the 400 s cap count as (seconds with 0) / 400. Falsified if the median is below 3.
Reason for the guess: Lemma P removes up to m - 1 classes per chosen class with
one private time, deep in the tree; we have no measurement.

**P3 (re-graded, from `PLAN.md` addendum 3).** Every prime p in [400, 1000] has
tau_15(p) >= 14. `lrc16-tau-v2` decided none of these 90 primes, so P3 was
**untested** there (its summary printed "holds where tested" because the code
only checked for counterexamples; this addendum corrects the reading). Part S
re-tests it with engine 3 at the same 400 s cap: falsified by any prime with a
cover on <= 13 classes (the cover is the evidence, and is independently checked),
untested where the cap is hit.

**R1 (completion, from addendum 3).** Part R decides the 47 primes of Table 2 of
arXiv:2609.02604 v2 that tau-v2 left open (all from 257 to 569, the paper says
tau(p) >= 13 at each). Any prime with a cover on <= 12 classes is a discrepancy
with the published proof's bookkeeping: it is reported with the cover, checked
again, and raised with the paper's author only after Sheehan's approval.

**Measurements (no prediction).** tau_15(p) at every prime of Part S that is
decided; the largest prime with tau_15(p) <= 13; the list of primes >= 100 with
tau_15(p) >= 14 and whether their log-sum passes 483.239 (the 16-runner gate
target). Primes with tau_15(p) <= 13 can still be gates, but they need the
general completion (`THEORY.md` 6.2), which is far more expensive.

## What each outcome means

- A1 and A2 hold, S1 holds: engine 3 replaces engine 2 for all later cover
  searches; the pilot and repro jobs are re-filed with it once they have run.
- A1 and A2 hold, S1 fails: engine 3 is kept only where it is faster; the
  16-runner cost question rests on Allikvere's generator (`lrc16-allik-probe-v1`).
- P3 falsified: small covers persist above 400 for 16 runners, so many planned
  gates need the general completion; the gate list must move to the primes with
  tau_15 >= 14, which Part S lists.
