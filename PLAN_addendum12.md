# PLAN, addendum 12 (2026-11-24, run 21, before any result of lrc16-uniform-v2 or lrc16-engine2-v4)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` and addenda 6-11. They all stay in force, except where this
addendum corrects a reading. Written at about 04:30 UTC on 2026-11-24.
`lrc16-uniform-v2` is queued, and `lrc16-engine2-v4` was filed at about
02:40 UTC. No output of either exists. The reasons are in `REVIEW_15.md` and
`REVIEW_16.md`.

## Correction: how X5 of addendum 9 is read

Old wording: the (1..15) probe of `lrc16-shift-v2` keeps 0 lifts at level 16
"exactly when" `pilot[].J16` = 0, and any disagreement is a bug.

**New reading.** Compare `pilot[].J16` with the `kept_by_level` value at level 16
of the **`cascadebb`** rows (no Lemma-S filter) of
`results/lrc16-shift-v2/orbits.jsonl`, one row per pilot prime. Each disagreement
in either direction is a bug in `lrc.c` or in `thresh.py`. The `scascadebb` rows
may keep fewer lifts. A `scascadebb` row with 0 at level 16 while J16 > 0 is a
bug only if its `shift_removed_by_level` is 0 at every level up to 16.

(For the record, before the job reports: at all ten pilot primes both modes keep
1, 2, 4, 0 lifts at levels 2, 4, 8, 16, and `shift_removed_by_level` is 0
everywhere. So the correction cannot change the outcome of X5. It only fixes a rule
that was wrong in one direction.)

## New measurement (no prediction, not a check)

**M1.** At each pilot prime, the sizes of J_p(L) for L = 2, 4, 8 in
`summary_uniform2.json` (`primes[].sizes`) next to the `cascadebb` `kept_by_level`
values (1, 2, 4). Equal sizes are expected only if `lrc.c` counts lift classes up
to odd units of Z_L, as `thresh.py` does. That convention has not been checked.
If the sizes differ while the level-16 zeros agree, check the counting convention
before calling it a bug.

## Reading N3 of addendum 11 (lrc-nb2), sharpened

N3 says U_inf(14) is empty for a13 and b13, as the paper's level-14 outcome
forces. If N3 fails, the bug hunt starts with one question: does the paper's
level-14 fibre search remove only lifts that fail Definition 2.1 and have no grid
witness, or does it also remove certified lifts (Lemma S with e > 1,
`THEORY.md` 5.3)? Only in the first case is a non-empty U_inf(14) a direct
contradiction (`REVIEW_16.md`, remark 1). Either way nothing is published until
it is resolved.

Nothing else changes: the predictions, checks and decision rules of addenda 9
and 11 stand as written.
