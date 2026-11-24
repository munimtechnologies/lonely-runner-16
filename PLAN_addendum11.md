# PLAN, addendum 11: job lrc-nb2 (pre-registered 2026-11-24, run 19)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written before the job ran. The theory is in `THEORY_17.md`, the code in
`nbc.py`, `nbc.c` and `job_nb2.py`, and the tests in `test_nbc.py`. This plan
repeats the questions of `PLAN_addendum10.md`, which job lrc-nb could not answer
(`RESULTS_run19.md`), with a faster engine.

The compete job is filed as `lrc16-engine2-v3`. It reuses a finished job name only
so the shared scheduler plans its memory from that job's history (0.03 GB
peak). It runs `fetch_nb2.py`, then `test_nbc.py` and `test_uniform_nb.py` with
`NBC_REQUIRE_C=1` (so the C tests cannot be skipped), then `job_nb2.py` with
3 workers (one per base). Its raw outputs will be committed under
`results/lrc-nb2/`.

## What runs

For a14 = (1..14) (L = 15, P0 = 239), a13 = (1..13) and b13 = (1..11,13,24)
(L = 14, P0 = 199), each in its own worker process:

- Phase 1, with the gcd clause, P = inf then P = P0: U(f1) and U(f2) from level 1,
  then route B (U(f2) lifted by f1). Then the thresholds on U_P0(L), and J_p(L) at
  every prime from P0 to B (B >= 3000, raised to cover P*_L, at most 20,000; at
  most 15 min).
- Phase 2, while time is left: route A (U(f1) lifted by f2), route C
  (`uniform_nb.combine`), then the gcd-free modes for S7, I1 and I2.

Caps per step: 900 s (f1), 1,800 s (f2 and B at P = inf), 3,600 s (f2 and B at
P0, route A), 900 s (route C), and a job deadline of 390 min. A step that hits
its cap is reported as cut. Nothing is inferred past a cut.

## Sanity gate (any failure means a bug; then nothing below is used)

- G0: `test_nbc` (with the C engine) and `test_uniform_nb` pass inside the job.
- R0: the job reproduces every set that lrc-nb finished. For a14: |U_inf(3)| = 1,
  |U_inf(5)| = 1, U_inf(15) empty, |U_239(3)| = 3, and without the gcd clause
  |U_inf(15)| = 3. For a13: |U_inf(2)| = 1 and |U_199(2)| = 9. For b13:
  |U_inf(2)| = 1 and |U_199(2)| = 5. The member lists must match too.
- S2, S3, S4, S5, S7 as in addendum 10.
- C1: routes A, B and C give the same U(L) wherever two or more finish.

## Predictions (the same as addendum 10)

- **N1:** U_inf(15) is empty for a14 (it held in lrc-nb; R0 repeats it).
- **N2:** the a14 statement holds at P0 = 239: J_p(15) is empty at every scanned
  prime and P*_15 is within the scan, so every lift of the orbit of (1..14) to
  level 15 is proper at every prime p >= 239.
- **N3:** U_inf(14) is empty for a13 and for b13. The paper's result forces this
  (THEORY_16 16.3), so a failure means a bug hunt, not a claim.
- **N4:** the a13 and b13 statements hold at P0 = 199.
- **X1:** J_p(L) is empty at each of the paper's gate primes in the scanned range.
  If X1 disagrees with arXiv:2609.02604, that means a bug hunt first. The author
  is contacted only after a second independent check and with Sheehan's OK.
- **S (speed, may fail):** with the C engine, Lemma S and the order f2 -> L,
  every phase-1 step at P = inf finishes within its cap for all three bases.

## Recorded, not graded

Nodes, leaves and seconds per step (where the time goes now). I1 and I2 as in
addendum 10. Sizes of every set.

## What each outcome leads to

- N2-N4 hold and the sanity gate passes: commit the results and RESULTS_run{n}.md,
  then write an article. Its claim: for the three tight orbits of the 14- and
  15-runner proofs, the per-prime level-14/15 fibre searches are replaced by one
  prime-free computation that is valid at every prime from 199 / 239, and that
  agrees with the published proof at its gate primes. It will say plainly that this
  re-checks one step of a published proof and proves no new case.
- Only some bases hold: report those, and say which steps were cut.
- N2 or N4 fails because P*_L is too large or the scan ran out of time: report
  the scanned range. The statement then holds for those primes only.
- Some J_p(L) is non-empty at a scanned prime: list the primes. At a paper gate
  prime, this is a disagreement with the paper and means a bug hunt first.
- Still cut at P0: read the node counts. The next step is a stronger prune for
  the P0 search (for example, the prune test applied to the run of uncovered
  cells and not just single big cells), or a sharded job.
