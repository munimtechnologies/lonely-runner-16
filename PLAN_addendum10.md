# PLAN, addendum 10: job lrc-nb (pre-registered 2026-11-23, run 18)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written before the job ran. The theory is in `THEORY_16.md`, the code in
`uniform_nb.py` and `job_nb.py`, and the tests in `test_uniform_nb.py`.

The compete job is filed under the name `lrc16-engine2-v2`. That reuses a
finished job name only so the shared scheduler plans its memory from that job's
history (0.09 GB peak). It runs `job_nb.py`, not engine 2. Its raw outputs will be
committed under `results/lrc-nb/`.

## What runs

For a14 = (1..14) (k = 14, L = 15 = 3*5, P0 = 239), and a13 = (1..13) and
b13 = (1..11,13,24) (k = 13, L = 14 = 2*7, P0 = 199):
U_inf and U_P0 at the factor levels and at L. Each is computed by the chain and by
the CRT combination, with and without the gcd clause. Then the thresholds P*(z) on
U_P0(L), and J_p(L) at every prime from P0 to B (B >= 3000; raised to cover P*_L,
at most 20,000). Budgets: a14 80 min, a13 and b13 35 min each, plus up to 15 min
of prime scan each. Anything cut by a deadline is reported as cut. Nothing is
inferred past a cut.

## Sanity gate (any failure means a bug; then nothing below is used)

- G0: `test_uniform_nb` passes inside the job.
- S2: each linear lift is in U_inf at both factor levels, is not in U_inf(L), and
  has status t0 at L.
- S3: U_inf is contained in U_P0 at f1, f2 and L. S4: every member of U_P0(L) is
  open and not P0-killed.
- S5: every lift improper at p has improper reductions at p (0 violations).
- C1: chain and combination agree wherever both finish.
- S7: the set with the gcd clause equals the gcd-free set minus the lifts that
  meet the gcd clause.

## Predictions

- **N1 (primary): U_inf(15) is empty for a14.** THEORY_16 16.3 says the paper's
  result forces this. If it fails, that means a bug hunt, not a claim.
- **N2: the a14 statement holds at P0 = 239.** J_p(15) is empty at every scanned
  prime and P*_15 <= B, so every lift of the orbit of (1..14) to level 15 is proper
  at every prime p >= 239.
- **N3: U_inf(14) is empty for a13 and for b13.**
- **N4: the a13 and b13 statements hold at P0 = 199.**
- **X1 (re-check of the paper):** J_p(L) is empty at each of the paper's gate
  primes in the scanned range: 52 for k = 14, and for k = 13 the P_13 primes
  >= 199. The paper's Section 4.3 reports its level-14 search at its archived
  primes; at a P_13 prime it did not search, X1 is only our own result. If X1 disagrees with arXiv:2609.02604, that means a bug hunt first. An
  author is contacted only after a second independent check and with Sheehan's OK.

## Recorded, not graded

- I1: at each paper gate prime, the number of gcd-free witness-free classes at L
  (up to units mod L) and how many of them fail the gcd clause (S7 implies 0
  when N2/N4 hold). The paper reports "seven candidates" for a14, and its
  counting convention may differ (tuples or orbits, per prime or total), so this
  is not compared formally.
- I2: whether every member of the gcd-free U_inf(14) for a13 and b13 has all
  coordinates divisible by 7. The paper reports this pattern at its primes.
- Sizes of U_inf and U_P0 at every level, P*_L, run times.

## What each outcome leads to

- N1-N4 all hold: commit the results and RESULTS_run{n}.md. An article ("the
  per-prime fibre searches of the 14- and 15-runner proofs collapse to one
  prime-free computation") only if the website's two-per-day limit allows it.
  Say plainly that it re-checks one step of a published proof and proves no new
  case.
- N2 or N4 fails only because P*_L > 20,000 or the scan ran out of time: report the
  scanned range. That is a partial result, and the statement holds for the
  scanned primes only.
- N2 or N4 fails because some J_p(L) is non-empty at a scanned prime: list the
  primes. If one of them is a paper gate prime, it disagrees with the paper (bug
  hunt first, as for X1).
- A cut before U_P0(L) completes: no statement. File a version with a larger budget
  or a faster lifting order (for example 1 -> 5 -> 15) only after reading where
  the time went.
