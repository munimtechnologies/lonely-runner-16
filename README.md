# lonely-runner-16

Independent re-checks and side results for the computer-assisted proofs of the **Lonely
Runner Conjecture** for 14, 15 and 16 runners.

> **Correction (2026-11-25).** This repository started as an attempt at the 16-runner case
> (`LRC(15)`), which we believed was open. It was not: J. Allikvere deposited a claimed
> computer-assisted proof for sixteen runners on Zenodo on 11 October 2026
> ([doi:10.5281/zenodo.23304361](https://doi.org/10.5281/zenodo.23304361), unrefereed), and
> W. Toner one for seventeen runners assuming sixteen on 22 October 2026
> ([doi:10.5281/zenodo.23552885](https://doi.org/10.5281/zenodo.23552885), unrefereed).
> Our searches missed Zenodo. Allikvere's deposit also improves the flag bound with integer
> relations among the speeds, so our dual-cap result was not the first such improvement.
> Details and what changes: [`CORRECTION.md`](CORRECTION.md).

By MV2 of Munim, Inc. (mv2@munimtech.com). Code: Apache-2.0. Text and data: CC BY 4.0.
The code and text were made with AI agents working in MV2's name. No human expert
has checked them yet.

## The problem

Give k runners distinct constant integer speeds on a circular track of length 1,
plus one runner standing still. The conjecture (Wills 1967, Cusick 1973) says that
at some moment every moving runner is at distance at least 1/(k+1) from the
standing runner. Equivalently, for every v in (Z \ {0})^k there is a real t with
||t v_i|| >= 1/(k+1) for all i.

The status, as of 25 November 2026:

| runners | k | reference |
|---|---|---|
| up to 7 | <= 6 | Barajas & Serra 2008 and earlier work |
| 8 | 7 | Rosenfeld, arXiv:2509.14111 (Math. Comp. 2026) |
| 9, 10 | 8, 9 | Trakulthongchai, arXiv:2511.22427 (EJC 2026); Rosenfeld, arXiv:2512.01912 |
| 11, 12, 13 | 10-12 | Sungkawichai & Trakulthongchai, arXiv:2604.23906 |
| 14, 15 | 13, 14 | Allikvere, arXiv:2609.02604 (about 2,140 CPU-hours for 15 runners) |
| 16 | 15 | claimed: Allikvere, Zenodo 10.5281/zenodo.23304361 (11 Oct 2026, unrefereed) |
| 17 | 16 | claimed, assuming 16: Toner, Zenodo 10.5281/zenodo.23552885 (22 Oct 2026, unrefereed) |
| 18 | 17 | no claim located (checked 2026-11-25) |

## The method being followed

This is the finite-checking framework from those papers:

1. **Bound the speed product.** Malikiosis, Santos and Schymura (Forum Math. Sigma
   2025) showed a primitive counterexample has bounded speeds. Allikvere's "flag
   bound" (Korkine-Zolotarev prefix inequalities) sharpens it to
   `log(v_1...v_n) < n log(A_n r_n / n)`; his 16-runner deposit sharpens it further with
   integer relations among the speeds. Rosenfeld showed `lcm(2..n+1)` divides the product.
2. **Prime gates.** If no residue vector mod p is "not eventually proper"
   (`J(k,p)` is empty), then p divides the speed product of any counterexample
   (Sungkawichai & Trakulthongchai). Enough such primes push the product past the
   bound, so no counterexample can exist.
3. **Per prime:** enumerate the level-one improper family (covers of the folded
   times by multiplicative translates of an interval), then lift through levels
   2, 4, 8, 16, 32 until every lift is proper.

## Results (all are re-checks or side results, not new cases)

- **`RESULTS_run24.md`, `RESULTS_run29.md`:** all three tight orbits that
  arXiv:2609.02604 searches separately at each gate prime reduce to one prime-free
  computation each: (1..14) at level 15 from p = 239, (1..13) and (1..11, 13, 24) at
  level 14 from p = 199, in agreement at every gate prime of the published proof in range.
- **`THEORY_18.md`, `THEORY_19.md`, `RESULTS_run32.md`:** at every prime p >= 251, no lift
  of the orbit of (1..15) or of (1..13, 15, 28) to level 16 is improper (hand proofs,
  adversarial AI reviews `REVIEW_18.md`, `REVIEW_19.md`, and an exact scan of the 377
  primes from 251 to 2,999). We have not compared this with Allikvere's 16-runner
  deposit, which reports that at each of its gate primes the retained families vanish by
  binary level 16.
- **`THEORY_10.md` to `THEORY_12.md`:** the dual cap (the last Gram-Schmidt length of the
  flag bound is below 1/3) lowers our 16-runner gate target from 483.239 to 481.123. See
  `CORRECTION.md`: Allikvere's relation-rank bound came first and is much stronger.
- `RESULTS_run28.md`: engine 3 is correct but not faster; 37 of 71 primes of Table 2 of
  arXiv:2609.02604 agree with the paper, none disagrees.
- Queued, now as re-checks only: `lrc16-indep-v1` (brute-force cascade from the bare
  definition), `lrc16-orbit-v1`, `lrc16-allik-probe-v1`.

Every THEORY section has had an adversarial pass by a second AI agent
(`REVIEW_THEORY_2_7.md`, `REVIEW_9.md`, `REVIEW_13_14.md`, `REVIEW_15.md` to `REVIEW_19.md`,
`REVIEW_indep_desk.md`). These are AI reviews, not human ones. Graded results:
`RESULTS_run14.md`, 16 (P5 **failed**), 17, 19, 20, 22, 24, 28, 29, 32 (T2 flag defective,
reported).

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
| `test_*.py` | tests against brute force and between independent implementations |
| `THEORY.md`, `THEORY_9.md` ... `THEORY_19.md` | the mathematics, written before each job ran |
| `REVIEW_*.md` | adversarial reviews: a second agent told to break each section |
| `PLAN.md`, `PLAN_addendum6.md` ... `PLAN_addendum16.md` | the pre-registered plan and what counts as success |
| `RESULTS_run*.md` | graded results and job reports |
| `CORRECTION.md` | the 2026-11-25 correction about the 16- and 17-runner claims |

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

All the mathematics this builds on belongs to the authors cited above. The 16-runner
proof and the relation-rank bound are Jaan Allikvere's (Zenodo 10.5281/zenodo.23304361);
the conditional 17-runner proof is William Toner's (Zenodo 10.5281/zenodo.23552885). The
level-14 and level-15 fibre searches, the gcd condition (Definition 2.1(a)), the 3 x 5
split (Lemma 4.5), the normalisation of Lemma 4.1, the flag bound and the tau table are
Jaan Allikvere's (arXiv:2609.02604). The lifting framework is Sungkawichai and
Trakulthongchai's (arXiv:2604.23906). The tight-set classification is Yuhan Zhang's
(arXiv:2608.13599) and Goddyn and Wong's. The relation theorem discussed in
`COST_addendum1.md` is Beck and Everett's (arXiv:2609.06259). The 8-runner check X2
uses Matthieu Rosenfeld's Lemma 6 (arXiv:2509.14111). The pipeline that `probe.py`
measures is Jaan Allikvere's (Zenodo 10.5281/zenodo.22667683 and
10.5281/zenodo.22066772, CC BY 4.0); it is downloaded, not copied into this
repository. The correction follows the literature survey in jerryckim16/Math-Research
pull request 80.
