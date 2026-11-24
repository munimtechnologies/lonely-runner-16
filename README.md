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

## Latest (2026-11-24, run 28)

### `THEORY_19.md`: the second 16-runner orbit, (1..13, 15, 28), also dies at level 16 at every prime p >= 251

- **Theorem 19.** At every prime p >= 251, no lift of the orbit of
  (1, ..., 13, 15, 28) to level 16 is improper. With Theorem 18, **both level-one
  orbits singled out by the tight-set analysis, (1..15) and (1..13, 15, 28), are
  removed by binary lifting alone by level 16 at every prime from 251**, so a
  16-runner computation needs no fibre search for either.
- How: the prime-free cascade keeps 5 classes. Four have every coordinate s or
  s + 8 mod 16; for odd times their witness condition does not depend on the prime,
  and one explicit window per class (length 1/576 or 5/1344, next to 1/8 or 3/8)
  catches a point of the grid of spacing 1/(8p). A simple residue rule (19.2) picks
  the window. The fifth class is off by 4 in the speed-28 coordinate only; moving
  the time b by 2 moves that coordinate by 1/2 + 7/(2p), so of b and b + 2 one works
  inside the 1/780-long interval of Lemma 18.2.
- `test_level16_gw.py` (standard library, no repository code) checks the residue
  rule, confirms by an exact sweep that each window is a whole component of the good
  set, re-checks the witness against the actual integer lifts at every prime from 251
  to 1,500, and runs a plain search over all times at the first five primes.
- Conditional, like Theorem 18, on Lemma U and the `lrc16-uniform-v1` class list.
  `PLAN_addendum16.md` adds prediction I6 to the queued brute-force job
  `lrc16-indep-v1` (written before it reports): gw15 must have no improper level-16
  lift at any prime it scans. For p > 1344 the orbit is already proper at level 1
  (`THEORY.md` 7.3), so the theorem's content is the primes 251 to 1,327. It proves
  no case of the conjecture: the level-one cover search is untouched.

### `RESULTS_run28.md`: engine 3 is correct but not faster

Job `lrc16-engine3-v1` graded against `PLAN_addendum7.md`. The C halves of
`test_prune.py` and `test_c.py` ran for the first time (19 tests, all OK). A1 and
A2 **hold** (0 disagreements at 8 gates and 24 slow rows; every cover certificate
passes an independent check), so the pruning lemmas F, P and M are safe. The speed
prediction S1 is **falsified**: the median speed-up was 0.98, not 3 (the pruning
cuts nodes by 1.4-2.3x, but each node costs more). New 16-runner measurements:
tau_15(269) >= 14 and tau_15(271) >= 14; all primes 281-997 hit the 400 s cap. 13
more primes of Table 2 of arXiv:2609.02604 agree with the paper (37 of 71 in all),
none disagrees.

Still waiting for compute: `lrc16-indep-v1`, `lrc16-uniform-v2`,
`lrc16-engine2-v5`, `lrc16-orbit-v1`, `lrc16-allik-probe-v1`. No 16-runner preprint
has appeared (checked 2026-11-24, about 15:00 UTC).

## Earlier (2026-11-24, `REVIEW_18.md`): THEORY_18 survives an adversarial pass; a brute-force check of its input is queued

- An agent told to break `THEORY_18.md` re-derived every window coordinate by
  coordinate, the lift form w_i = i + 8p[i in D], the class-1 parity step
  (4 w_14 = 56 + 8p mod 16p) and the assembly of the proof. **No error found.**
  `test_review18.py` (standard library, no repository code, no data file) starts from
  the 9 residue vectors alone, finds every component of the good set by an exact
  sweep over the bad arcs, and confirms that each hand window is a whole component,
  long enough at every prime from 251; it also re-checks a witness against the
  actual lifts at every prime from 251 to 1,500.
- The weakest premise is THEORY_18's input (ii), the computer list U_251(16): a
  wrong kill in `uniform.py` would hide a class. `indep.py` and `indep_brute.c`
  compute the cascade J_p(L) for (1..15) and (1..13,15,28) from the bare definition
  (every lift, every time, no shortcuts) and compare it with U_251 level by level, at
  every prime from 251 up. Job `lrc16-indep-v1` is queued; its predictions (I0-I5,
  and I6 from addendum 16) are fixed before it runs.

## Earlier (2026-11-24, `THEORY_18.md`): the 16-runner tight orbit dies at level 16 at every prime p >= 251

- **Theorem 18.** At every prime p >= 251, no lift of the orbit of (1..15) to
  level 16 is improper. So the 16-runner computation needs **no fibre search for
  the tight orbit at any prime from 251 on.**
- How: the prime-free cascade (`lrc16-uniform-v1`) leaves 9 classes at level 16.
  For 8 of them every coordinate is i or i + 8 mod 16, so for odd b the witness
  condition no longer depends on the prime; one explicit window of times per class
  (length 1/576 to 5/1344) then catches a point of the grid of spacing 1/(8p). The
  ninth class falls to a parity step: moving b by 4 moves its one odd coordinate
  by 1/2 + 7/(2p).
- `test_level16.py` checks every window in exact arithmetic and the predicted
  witness of each class against the actual integer vectors at every prime from
  251 to 3,000 (data in `level16_certificate.json`).
- Conditional on Lemma U (`THEORY.md` 8.2) and the `lrc16-uniform-v1` computation.
  A public per-prime check (jerryckim16/Math-Research pull request 5) reported the
  same at the 79 candidate gates 251..743, one prime at a time; this covers every
  prime from 251 on.

## Earlier (2026-11-24, `RESULTS_run24.md`): two per-prime searches become one computation each

Job lrc-nb2 (`lrc16-engine2-v4`) was graded against its pre-registered plan
(`PLAN_addendum11.md`). Every sanity check passed.

- **(1..14), level 15 (the 15-runner proof):** every lift is proper at **every
  prime p >= 239** (kill threshold 1980/7; no improper lift at any of the 379 primes
  from 239 to 2,999).
- **(1..13), level 14 (the 14-runner proof):** every lift is proper at **every
  prime p >= 199** (largest threshold 1848/5; no improper lift at any of the 385
  primes from 199 to 2,999).
- **(1..11,13,24), level 14:** the level-7 search at P = 199 hit its one-hour cap;
  `PLAN_addendum13.md` re-runs it alone (job `lrc16-engine2-v5`).
- At all 52 + 56 gate primes of the 15- and 14-runner proofs that are at least 199,
  the result agrees with the published outcome. This re-checks one step of a
  published proof. **It proves no new case** (`REVIEW_16.md` for scope).

## Every THEORY section has had an adversarial pass

`REVIEW_THEORY_2_7.md` re-derives THEORY.md Sections 1-3 and 5-8 by hand (no error
that changes a claim; `test_review_theory.py`). `REVIEW_18.md` does the same for
`THEORY_18.md`. Earlier: `REVIEW_9.md`, `REVIEW_13_14.md`, `REVIEW_15.md`,
`REVIEW_16.md`, `REVIEW_17.md`. These are AI reviews, not human ones. `THEORY_19.md`
has not had its own adversarial pass yet. Graded results: `RESULTS_run14.md`, 16
(P5 **failed**), 17, 19, 20, 22, 24, 28.

## Other parts

- **Non-binary levels** (`THEORY_16.md`, `THEORY_17.md`, `uniform_nb.py`, `nbc.py`,
  `nbc.c`): the prime-free cascade at levels 14 and 15, used for the 14/15-runner
  re-check above.
- **From the uniform cascade to every prime** (`THEORY_15.md`, `thresh.py`): exact
  per-prime test, kill thresholds, exact cascade inside U_P (Lemmas E, T, R). Job
  `lrc16-uniform-v2` (queued; `PLAN_addendum9.md`, 12, 14).
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
| `test_*.py` | tests against brute force and between independent implementations (`test_review9.py`, `test_review_theory.py`, `test_level16.py`, `test_review18.py` and `test_level16_gw.py` import no repository code) |
| `THEORY.md`, `THEORY_9.md` ... `THEORY_19.md` | the mathematics, written before each job ran |
| `REVIEW_*.md` | adversarial reviews: a second agent told to break each section |
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
