# Desk review of the queued brute-force job `lrc16-indep-v1` (run 30)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written 2026-11-24 (~18:30 UTC), **before** the job has run (it is queued for memory on
the compute machines). No output of `lrc16-indep-v1` exists. No human expert has
checked this yet.

Why: each compete job runs once, and the C half of this check (`indep_brute.c`) has
never been executed. A defect found now saves one queue cycle. This pass read
`indep_brute.c`, `indep.py`, `indep_job.py`, `fetch_indep.py`, `run_tests_indep.py`,
`test_indep.py` and the job spec line by line against `PLAN_addendum15.md` and
`PLAN_addendum16.md` (I6).

## Findings: no defect that changes a grade

| # | item | verdict |
|---|---|---|
| D1 | `fetch_indep.py` pins `results/lrc16-uniform-v1/summary_uniform.json` at commit 162a7b9 | the file **exists at that commit** (fetched 2026-11-24 via raw.githubusercontent.com; contains both "e15" and "gw15" runs), so step 1 will not 404 |
| D2 | `u_classes(data, base, P)` needs exactly one run per (base, P) | the committed file has one run each for (e15, null), (e15, 251), (gw15, null), (gw15, 251) (other e15 run is P = 17); no ValueError |
| D3 | I3 loops over every level of U_inf(e15), not only 2, 4, 8 as the plan words it | U_inf(e15) has survivors 1, 1, 1, 0 at levels 2, 4, 8, 16, and empty levels are skipped, so the loop tests exactly levels 2, 4, 8; no false alarm possible from level 16 |
| D4 | the cap of 5,000 stored lifts | U_251 for e15 has 20, 13, 17, 9, 2 classes at levels 2..32 (at most 1, 2, 4, 8, 16 lifts per class), for gw15 10, 8, 12, 5, 2; J_p(L) is a subset (Lemma U(i)) if the theory is right, so the cap cannot be reached unless I2 fails, in which case the true count is still reported |
| D5 | C and Python agree on output format, child order, level-1 handling, cap and stop rule | yes, line by line (`LEVEL 1 0` / `END` when proper at level 1; zeros printed for z mod 1; stop when the count is 0 or `2L > lmax`) |
| D6 | integer overflow | b <= n/2 <= 16 * 5000 = 80,000 and w < 32 * 5000, so b * w < 1.3e10, far inside 64 bits |
| D7 | the gcd clause (at most one odd w_i mod L is proper) is shared with `uniform.py` | as intended: the job is independent of Lemma D, arcs, unit reduction and pruning, not of the definition of properness, which is the paper's |
| D8 | runtime | per prime the cascade handles at most ~70 parents x 32,768 masks; improper lifts scan all n/2 times, proper ones stop at their first witness. The 330-minute cap is checked between primes, so the job always writes `summary_indep.json`. A long tail at large p only shortens the scanned range ("time cap" is recorded, not a failure) |

## Residual risks (not defects)

- `test_k7_capped` and `test_k3` (p = 101, lmax 16) run in pure Python inside the job;
  estimated well under the 400-minute timeout.
- The grading treats a capped level as untested (correct), and I1 is "untested" only if
  every scanned prime stopped before level 16.

Decision: leave `lrc16-indep-v1` queued unchanged (re-filing would lose its place).
