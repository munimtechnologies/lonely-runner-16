# RESULTS, run 28 (2026-11-24): job lrc16-engine3-v1 graded against PLAN_addendum7

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
No human expert has checked this yet.

Job `lrc16-engine3-v1` (filed run 14, 2026-11-22, predictions in
`PLAN_addendum7.md` written before any output existed) ran on the Blade from
2026-11-24 08:51 to 13:32 UTC (278 minutes, peak memory 0.09 GB). Raw output is in
`results/lrc16-engine3-v1/` (`summary_engine3.json`, `xcheck3.jsonl`,
`tau3_k14.jsonl`, `tau3_k15.jsonl`, `speed3.jsonl`, `sha256.txt`, the job's
stdout/stderr), copied unchanged.

## The gate: unit tests

`python -m unittest -v test_prune test_c` ran first: **19 tests, all OK, none
skipped** (`run-01` stderr). This is the first time the C halves of `test_prune.py`
(engine 3 against the reference, the forbidden-class rule and the fractional bound
against brute force) and `test_c.py` actually ran; REVIEW_13_14 had flagged that
they never had.

## Grades

| reading | statement (addendum 7) | outcome |
|---|---|---|
| A1 (decisive) | LRC_PRUNE = 0 and 3 give identical tau, orbit counts, tuples, kills, survivors, completeness and per-level counts on every Part X gate where both finish | **holds**: 8 of 12 gates finished both ways (k = 8..11, p = 61..163), 0 disagreements; 4 gates (k = 12..14) hit the 300 s cap in both modes and are untested |
| A2 | engine 3 gives the same answer as `lrc16-tau-v2` at its 24 slow (k, p), and every cover passes an independent Python check | **holds**: 24 rows, 0 disagreements, 0 failing certificates |
| S1 (speed) | median (seconds with prune 0)/(seconds with prune 3) >= 3 | **falsified**: median 0.98 (range 0.69 to 1.37 over 24 rows) |
| P3 | every prime 400..1000 has tau_15(p) >= 14 | **untested**: 0 of 90 primes decided within the 400 s cap |
| R1 | the 47 open primes of arXiv:2609.02604 Table 2 | 13 more decided, all **agree** with the paper (37 of 71 agree in total), 0 disagree, 34 still unknown |

## What it shows

- **Engine 3 is correct where it could be checked** (A1, A2, all certificates), so
  the pruning Lemmas F, P and M of `THEORY_13.md` now have both a hand review
  (REVIEW_13_14) and an executed test. LRC_PRUNE = 3 is safe to use.
- **It is not faster.** In the Part X rows the pruning cuts the number of search
  nodes by a factor of about 1.4 to 2.3 (for example k = 11, p = 163: 54.9 M nodes to
  30.0 M), but each node costs more, so wall time is unchanged or worse (33.5 s to
  43.1 s there). The prediction that it would be 3x faster was wrong.
- **Measurements for 16 runners (k = 15):** tau_15(269) >= 14 and tau_15(271) >= 14
  (no cover on 13 or fewer classes; 286 s and 243 s). Every other prime from 281 to
  997 hit the cap. Together with earlier runs, the primes from 100 with
  tau_15 >= 14 known to us are 239, 269, 271 (log-sum 16.67, far below the 483.24
  a 16-runner gate plan needs). This only confirms, for these primes, that they are
  usable gates; the public per-prime work (jerryckim16/Math-Research #5) already
  lists candidate gates from 251 to 743.

## Decision (addendum 7, "A1 and A2 hold, S1 fails")

Engine 3 is kept only where it is faster, which is nowhere measured: later cover
searches stay on LRC_PRUNE = 0 for speed, and LRC_PRUNE = 3 may be used as a
cross-check. The 16-runner cost question rests on Allikvere's generator
(`lrc16-allik-probe-v1`, queued). The level-one cover search remains the real cost
of a 16-runner proof; nothing here reduces it.
