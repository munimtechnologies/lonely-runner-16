# lonely-runner-16

An open, independent attempt at the next case of the **Lonely Runner Conjecture**:
**16 runners** (15 moving speeds, `LRC(15)`), plus an independent re-check of the
computer-assisted proofs for 14 and 15 runners.

By MV2 of Munim, Inc. (mv2@munimtech.com). Code: Apache-2.0. Text and data: CC BY 4.0.
The code and text were made with AI agents working in MV2's name. No human expert
has checked them yet. Nothing here claims a proof until the full pipeline has run,
been audited and been re-implemented a second time.

## The problem

Give k runners distinct constant integer speeds on a circular track of length 1,
plus one runner standing still. The conjecture (Wills 1967, Cusick 1973) says that
at some moment every moving runner is at distance at least 1/(k+1) from the
standing runner. Equivalently, for every v in (Z \ {0})^k there is a real t with
||t v_i|| >= 1/(k+1) for all i.

The status, as of November 2026:

| runners | k | reference |
|---|---|---|
| up to 7 | <= 6 | Barajas & Serra 2008 and earlier work |
| 8 | 7 | Rosenfeld, arXiv:2509.14111 (Math. Comp. 2026) |
| 9, 10 | 8, 9 | Trakulthongchai, arXiv:2511.22427 (EJC 2026); Rosenfeld, arXiv:2512.01912 |
| 11, 12, 13 | 10-12 | Sungkawichai & Trakulthongchai, arXiv:2604.23906 |
| 14, 15 | 13, 14 | Allikvere, arXiv:2609.02604 (about 2,140 CPU-hours for 15 runners) |
| **16** | **15** | **open: the target of this repository** |

## The method being followed

This is the finite-checking framework from those papers:

1. **Bound the speed product.** Malikiosis, Santos and Schymura (Forum Math. Sigma
   2025) showed a primitive counterexample has bounded speeds. Allikvere's "flag
   bound" (Korkine-Zolotarev prefix inequalities) sharpens it to
   `log(v_1...v_n) < n log(A_n r_n / n)`. Rosenfeld showed `lcm(2..n+1)` divides
   the product.
2. **Prime gates.** If no residue vector mod p is "not eventually proper"
   (`J(k,p)` is empty), then p divides the speed product of any counterexample
   (Sungkawichai & Trakulthongchai). Enough such primes push the product past the
   bound, so no counterexample can exist.
3. **Per prime:** enumerate the level-one improper family (covers of the folded
   times by multiplicative translates of an interval), then lift through levels
   2, 4, 8, 16, 32 until every lift is proper.

## Latest (2026-11-24, run 32)

### `RESULTS_run32.md`: a second, computational route to Theorems 18 and 19

Job `lrc16-uniform-v2` graded against `PLAN_addendum9.md` and `PLAN_addendum14.md`
(both written before it ran). Raw output in `results/lrc16-uniform-v2/`.

- **T1, T4, T5 hold; S2-S6, R1, X5, X6 all clean.** At each of the 377 primes from
  251 to 2,999 the exact per-prime test (`thresh.py`) finds no improper lift of
  (1..15) at level 16, agreeing with the hand proof of `THEORY_18.md`; the re-run
  lists the same 9 level-16 classes; at the ten pilot primes it agrees with the
  separate C engine (`lrc16-shift-v2`).
- **(1..15): the death level is exactly 16 at every prime p >= 251** (P*_16 = 288
  above the scan; the linear lift keeps level 8 non-empty at every prime).
- **(1..13, 15, 28): gone by level 8 at every prime p >= 251** (latest at
  p = 257, 269, 281, 293; for p > 1,344 already at level 1). This sharpens
  Theorem 19 from level 16 to level 8.
- **One defect, reported:** the job's `statement.holds` flag (prediction T2) read
  false because of an off-by-one in its own condition (it required the last prime
  scanned to be at least 3,000; the last prime below 3,000 is 2,999). T2's stated
  condition holds in the raw numbers; we do not count it as a clean pass.
- Same inputs as before (Lemma U and `uniform.py`'s class list). The brute-force
  check of that list, `lrc16-indep-v1`, is still queued. No case of the conjecture
  is proved, and the level-one cover search (the real cost) is untouched.

## Earlier (2026-11-24, runs 30-31)

- **Wording made precise.** Of the two 16-runner orbits treated by `THEORY_18.md` and
  `THEORY_19.md`, only (1..15) is tight. (1..13, 15, 28) is near-tight: it is not tight
  by Goddyn and Wong's theorem (Zhang, arXiv:2608.13599, Thm 1.1 with n = 16, r = 14,
  m = 2, where b = 3 is coprime to 14), and it has a strict level-1 witness interval of
  length 1/1344 (`THEORY.md` 7.3). By Zhang's one-entry classification and Lemma N
  (`THEORY.md` 7.2), (1..15) is the only known tight set for 16 runners. Earlier
  summaries that called both orbits "singled out by the tight-set analysis" should be
  read this way. No mathematical claim changes.
- `REVIEW_indep_desk.md` (run 30): a line-by-line desk review of the never-run
  brute-force job `lrc16-indep-v1` found no defect before it runs.
- Still waiting for compute (memory on the shared machines): `lrc16-indep-v1`,
  `lrc16-orbit-v1`, `lrc16-allik-probe-v1`. No 16-runner preprint has appeared
  (checked 2026-11-24, about 21:50 UTC).

## Earlier (2026-11-24, run 29)

### `RESULTS_run29.md`: the third tight orbit of the 14-runner proof, at every prime from 199

Job `lrc16-engine2-v5` graded against `PLAN_addendum13.md`; every sanity check passed
(22 tests, 0 skipped; the earlier sets reproduced member by member; two independent
routes agree).

- **(1..11, 13, 24), level 14: every lift is proper at every prime p >= 199.**
  U_199(14) has 3 classes with kill thresholds 2352/11, 245 and 231; the exact test
  finds no improper lift at any of the 385 primes from 199 to 2,999, including all 56
  gate primes of the 14-runner proof in that range (prediction N4b and X1b hold).
- With `RESULTS_run24.md`, **all three tight orbits that arXiv:2609.02604 searches
  separately at each gate prime now reduce to one prime-free computation each**:
  (1..14) from 239, (1..13) and (1..11, 13, 24) from 199. This re-checks one step of a
  published proof; **it proves no new case**, and gates below 199 are not covered.
- The level-7 step needed 6,632 s at P = 199 (18,839,529,813 nodes); the one-hour cap
  of the first run was simply too short.

### `REVIEW_19.md`: THEORY_19 survives an adversarial pass

- An agent told to break `THEORY_19.md` re-derived the lift form by CRT, the odd-time
  reduction, the residue rule and all four windows coordinate by coordinate, and the
  step-of-2 lemma for class g1. **No error found that changes a claim.**
- It closed one gap: the commit that added THEORY_19 did not include the raw job
  output, so the class-list comparison in `test_level16_gw.py` was skipped. The 5
  classes were compared by hand with `results/lrc16-uniform-v1/summary_uniform.json`
  (identical), and that file now ships with `test_review19.py`, which checks it.
- `test_review19.py` (standard library, no shared code) checks every window as the
  image of a linear map, its tightness at both ends, and **every** odd time in each
  window against the actual integer lift at every prime from 251 to 1,500.
- Still conditional on Lemma U and the `lrc16-uniform-v1` list; the brute-force job
  `lrc16-indep-v1` (queued) tests both orbits from the bare definition.

## Earlier (2026-11-24, run 28)

### `THEORY_19.md`: the second 16-runner orbit, (1..13, 15, 28), also dies at level 16 at every prime p >= 251

- **Theorem 19.** At every prime p >= 251, no lift of the orbit of
  (1, ..., 13, 15, 28) to level 16 is improper. With Theorem 18, **both the tight
  orbit (1..15) and the near-tight orbit (1..13, 15, 28), the 16-runner analogue of
  the 14-runner survivor (1..11, 13, 24), are removed by binary lifting alone by
  level 16 at every prime from 251**, so a 16-runner computation needs no fibre
  search for either.
- How: the prime-free cascade keeps 5 classes. Four have every coordinate s or
  s + 8 mod 16; for odd times their witness condition does not depend on the prime,
  and one explicit window per class (length 1/576 or 5/1344, next to 1/8 or 3/8)
  catches a point of the grid of spacing 1/(8p). The fifth class is off by 4 in the
  speed-28 coordinate only; moving the time b by 2 moves that coordinate by
  1/2 + 7/(2p), so of b and b + 2 one works inside the 1/780-long interval of
  Lemma 18.2.
- For p > 1344 the orbit is already proper at level 1 (`THEORY.md` 7.3), so the
  theorem's content is the primes 251 to 1,327. It proves no case of the conjecture:
  the level-one cover search is untouched.

### `RESULTS_run28.md`: engine 3 is correct but not faster

Job `lrc16-engine3-v1` graded against `PLAN_addendum7.md`. The C halves of
`test_prune.py` and `test_c.py` ran for the first time (19 tests, all OK). A1 and
A2 **hold**, so the pruning lemmas F, P and M are safe. The speed prediction S1 is
**falsified**: the median speed-up was 0.98, not 3. New 16-runner measurements:
tau_15(269) >= 14 and tau_15(271) >= 14. 13 more primes of Table 2 of
arXiv:2609.02604 agree with the paper (37 of 71 in all), none disagrees.

## Earlier (2026-11-24, `THEORY_18.md` and `REVIEW_18.md`): the 16-runner tight orbit dies at level 16 at every prime p >= 251

- **Theorem 18.** At every prime p >= 251, no lift of the orbit of (1..15) to
  level 16 is improper, so the 16-runner computation needs **no fibre search for
  the tight orbit at any prime from 251 on.** The prime-free cascade leaves 9
  classes; 8 fall to one explicit window of odd times each, the ninth to a parity
  step. `test_level16.py` checks it at every prime from 251 to 3,000.
- `REVIEW_18.md`: an adversarial pass found no error; `test_review18.py` re-checks it
  from the 9 residue vectors alone.
- A public per-prime check (jerryckim16/Math-Research pull request 5) reported the
  same at the 79 candidate gates 251..743, one prime at a time; this covers every
  prime from 251 on.

## Every THEORY section has had an adversarial pass

`REVIEW_THEORY_2_7.md` re-derives THEORY.md Sections 1-3 and 5-8 by hand (no error
that changes a claim; `test_review_theory.py`). Also: `REVIEW_9.md`, `REVIEW_13_14.md`,
`REVIEW_15.md`, `REVIEW_16.md`, `REVIEW_17.md`, `REVIEW_18.md`, `REVIEW_19.md`, and the
desk review of the brute-force job, `REVIEW_indep_desk.md`. These are AI reviews, not
human ones. Graded results: `RESULTS_run14.md`, 16 (P5 **failed**), 17, 19, 20, 22,
24, 28, 29, 32 (T2 flag defective, reported).

## Other parts

- **Non-binary levels** (`THEORY_16.md`, `THEORY_17.md`, `uniform_nb.py`, `nbc.py`,
  `nbc.c`): the prime-free cascade at levels 14 and 15, used for the 14/15-runner
  re-check above.
- **From the uniform cascade to every prime** (`THEORY_15.md`, `thresh.py`): exact
  per-prime test, kill thresholds, exact cascade inside U_P (Lemmas E, T, R). Job
  `lrc16-uniform-v2` graded in `RESULTS_run32.md` (`PLAN_addendum9.md`, 12, 14).
- **Engines 3 and 4** (`THEORY_13.md`, `THEORY_14.md`): safe prunings of the cover
  search. Engine 3 is correct and no faster (`RESULTS_run28.md`); engine 4 is tested
  by the queued `lrc16-orbit-v1`.
- **The bound for 16 runners** (`THEORY.md` 1-3): R_15 < 49/100, so prime gates with
  log-sum above 483.239 prove the 16-runner case (roughly 80 primes).
- **A sharper flag bound: the dual cap** (`THEORY_10.md` to `THEORY_12.md`): target
  481.123 (planning only; `dual_cap_results.json`).
- **Cost** (`COST.md`, `COST_addendum1.md`, `SHARD_PLAN.md`): a public estimate puts
  the 16-runner gates at about 1.75e5 CPU-hours, far beyond this project's hardware;
  `lrc16-allik-probe-v1` (queued) measures it with Allikvere's generator.
- **Lemma U** (`THEORY.md` 8, `THEORY_9.md`): two prime-free cascades sandwich the
  true one, U_inf(L) <= J_p(L) <= U_P(L) for every prime p >= P. `uniform.py` and
  `grid.py` compute it; `indep.py` is a third, brute-force route at single primes.

## What is here

| file | what it does |
|---|---|
| `lrc.c` | from-scratch C engine: canonical cover enumeration up to units, tau(p), lifting cascade, shift filter, general completion, engine-3 and engine-4 pruning (`LRC_PRUNE` bits 1, 2, 4) |
| `lrc_ref.py` | brute-force reference used to test the engine on small cases |
| `uniform.py`, `thresh.py`, `uniform_nb.py`, `nbc.py`, `nbc.c`, `grid.py` | prime-free cascades, exact per-prime tests, non-binary lifting, grid witnesses |
| `indep.py`, `indep_brute.c` | brute-force binary cascade J_p(L) from the bare definition (`indep_job.py` is job `lrc16-indep-v1`) |
| `bounds.py`, `capped.py` | exact flag bound, shape bound, gate planning; the dual-capped flag bound |
| `level16_certificate.json` | the windows and step data of `THEORY_18.md` |
| `job*.py`, `fetch_*.py`, `run_tests_c.py`, `run_tests_indep.py`, `probe.py` | compete jobs, pinned fetches, C-required test runners, cost probe |
| `results/` | raw outputs of finished jobs, copied unchanged |
| `test_*.py` | tests against brute force and between independent implementations (`test_review9.py`, `test_review_theory.py`, `test_level16.py`, `test_review18.py`, `test_level16_gw.py` and `test_review19.py` import no repository code) |
| `THEORY.md`, `THEORY_9.md` ... `THEORY_19.md` | the mathematics, written before each job ran |
| `REVIEW_*.md` | adversarial reviews: a second agent told to break each section (and `REVIEW_indep_desk.md`, a desk review of a job before it runs) |
| `PLAN.md`, `PLAN_addendum6.md` ... `PLAN_addendum16.md` | the pre-registered plan and what counts as success |
| `RESULTS_run*.md` | graded results and job reports |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python run_tests_c.py            # Linux/macOS with cc: the C tests may not skip
python run_tests_indep.py        # the brute-force cascade, C engine required
python test_level16.py           # THEORY_18, standard library only
python test_review18.py          # REVIEW_18, standard library only
python test_level16_gw.py        # THEORY_19, standard library only
python test_review19.py          # REVIEW_19, standard library only
```

## Credit

All the mathematics this builds on belongs to the authors cited above. This
repository only reimplements their published definitions so the computation can
be checked by an independent route and, if it holds, pushed one runner further.
The level-14 and level-15 fibre searches, the gcd condition (Definition 2.1(a)), the
3 x 5 split (Lemma 4.5), the normalisation of Lemma 4.1, the flag bound and the tau
table are Jaan Allikvere's (arXiv:2609.02604). The lifting framework is Sungkawichai
and Trakulthongchai's (arXiv:2604.23906). The tight-set classification is Yuhan
Zhang's (arXiv:2608.13599) and Goddyn and Wong's. The relation theorem discussed in
`COST_addendum1.md` is Beck and Everett's (arXiv:2609.06259). The 8-runner check X2
uses Matthieu Rosenfeld's Lemma 6 (arXiv:2509.14111). The pipeline that `probe.py`
measures is Jaan Allikvere's (Zenodo 10.5281/zenodo.22667683 and
10.5281/zenodo.22066772, CC BY 4.0); it is downloaded, not copied into this
repository.
