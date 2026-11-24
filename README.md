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

## Latest (2026-11-24, `REVIEW_9.md`)

- **REVIEW_9.md:** an adversarial read of the grid-point witnesses (`THEORY_9.md`,
  Lemmas G and G2) against `grid.py`. No error was found. Lemma G is exact with
  D = 2Q, and at any coarser grid it can only kill a lift that the exact test also
  kills. Lemma G2's closed form and its counts (1,024 and 12,030 blocked level-2
  lifts of (1..15)) are re-derived by hand. The worked example (dR = 1/320,
  dL = 3/1040) is recomputed. Three scope remarks: speeds must be positive (true
  for every vector used); "> 1/P" versus ">= 1/P" can never matter at the
  thresholds used; the 1/240 coarse-grid shortcut holds only for levels dividing
  16. `test_review9.py` repeats the 2^15 scan through a second route that imports
  no repository code.
- Still waiting for compute: `lrc16-engine2-v4` (lrc-nb2), `lrc16-uniform-v2`,
  `lrc16-engine3-v1`, `lrc16-orbit-v1`, `lrc16-allik-probe-v1`. No 16-runner
  preprint has appeared (checked 2026-11-24).
- Earlier: `RESULTS_run22.md` (`lrc-repro-k14-v1`'s cover search was capped at all
  ten gates, so step 1 is untested; tau_14(239) = 13). `REVIEW_13_14.md` (Lemmas F,
  P and M are correct; the C half of `test_prune.py` and `test_orbit.py` has never
  run, so `LRC_PRUNE != 0` stays unused until `lrc16-engine3-v1` or
  `lrc16-orbit-v1` passes on Linux). `REVIEW_15.md` and `REVIEW_16.md` (Lemmas A,
  E, T, R and N1-N4 are correct). `PLAN_addendum12.md` (how X5 is read).
  `RESULTS_run20.md` (lrc-nb2's first try stopped at its test gate and was
  re-filed). `RESULTS_run19.md` (U_inf(15) is empty for (1..14); N1 held).
  `RESULTS_run17.md` (the tight orbit (1..15) dies by level 16 at all ten pilot
  primes; P1 held). `RESULTS_run16.md` (P5b held, P5 **failed**).
  `RESULTS_run14.md` (our tau search agrees with Table 2 of arXiv:2609.02604 v2 at
  24 of its 71 primes, with no disagreement).

## A faster non-binary lift (`THEORY_17.md`, `REVIEW_17.md`)

- **Lemma S:** when c is an odd prime coprime to L, the units of Z_{cL} that are
  1 mod L permute the children of a class, keep their canonical form, and keep
  the kill test. So only children whose first nonzero residue mod c is 1 need to
  be searched. The output is unchanged.
- **C engine:** `nbc.c` is the Python reference search `nbc.dfs_py` written in C,
  node for node. Python builds all the geometry (cells, arcs, masks), so the C
  program only does bit operations.
- `test_nbc.py` checks the reference against the published
  `uniform_nb.lift_children` (with and without Lemma S, in three search orders),
  and checks the C engine against the reference: same children, same node and
  leaf counts.

## Non-binary levels: re-checking the 14- and 15-runner fibre searches (`THEORY_16.md`, `REVIEW_16.md`)

The published 14- and 15-runner proofs run two extra searches at **every** gate
prime. They lift the tight orbits (1..13) and (1..11,13,24) to level 14, and
(1..14) to level 15, because those orbits survive every binary level (THEORY.md
8.5 proves they must when k + 1 is not a power of 2). `uniform_nb.py` carries the
prime-free cascade (Lemma U, and Lemmas E, T, R of `THEORY_15.md`) to any level.
It uses the general gcd clause over the primes dividing the level, and it computes
each level two ways: as a chain of divisors, and by a CRT combination of coprime
levels (the uniform form of the paper's Lemma 4.5). Jobs `lrc-nb` and `lrc-nb2`
ask whether one computation can replace those per-prime searches at every prime
from 239 (k = 14) or 199 (k = 13) upward. They also re-check the paper's outcome
at its gate primes.

## From the uniform cascade to every prime (`THEORY_15.md`, `REVIEW_15.md`)

Every lift that U_251 keeps does have strict witness intervals, only shorter than
1/251. `thresh.py` lists those intervals exactly, which gives:

- **Lemma E:** an exact test of one lift at one prime p (does some point j/p fall
  in a witness interval?), one integer comparison per interval;
- **Lemma T:** a kill threshold P*(z) = 1/(longest interval): the lift is proper
  at every prime above it;
- **Lemma R:** at every prime p >= 251 the true cascade is exactly the part of
  U_251 that is improper at p.

Job `lrc16-uniform-v2` (queued) applies them to (1..15) and (1..13,15,28): U_251 to
level 128, P*_L per level, and the exact cascade at every prime from 251 to at
least 3,000. Its predictions are pre-registered in `PLAN_addendum9.md` (X5 read as
in `PLAN_addendum12.md`).

## Engines 3 and 4: safe prunings of the cover search (`THEORY_13.md`, `THEORY_14.md`, `REVIEW_13_14.md`)

- **Lemma F (fractional bound)** and **Lemma P (forbidden classes)** cut only
  search nodes with no reportable cover below them (`LRC_PRUNE=3`).
- **Lemma M (early orbit pruning)** stops a branch once class 1 can no longer end
  up with the most private times (`LRC_PRUNE=4`).

`test_prune.py` and `test_orbit.py` check them by brute force. Jobs
`lrc16-engine3-v1` and `lrc16-orbit-v1` (queued) run the C half of those tests
first, then measure the speed-up; see `PLAN_addendum7.md` and `PLAN_addendum8.md`.

## The bound for 16 runners (worked out in `THEORY.md`, Sections 1-3)

We carried the paper's shape lemma (its Lemma 3.7, proved there for 14 and 15
runners) to 16 runners. It gives **R_15 < 49/100**, so a primitive counterexample
with 15 speeds has `log(v_1...v_15) < 496.727`. After the forced divisor
720720 = lcm(2..16), **prime gates with log-sum above 483.239** prove the 16-runner
case: roughly 80 primes, against 71 used for 15 runners. Every inequality in the
note is re-checked in exact rational arithmetic by `test_bounds.py`.

## A sharper flag bound: the dual cap (`THEORY_10.md` to `THEORY_12.md`)

Every integer relation h of a counterexample's speeds has sum h_k^2 >= 3, so the
last Gram-Schmidt length of the flag-bound lattice is below 1/3. Solving the
capped problem exactly (`capped.py`) lowers the 16-runner gate target from 483.239
to 481.123 (2.1162 nats; 1.9985 nats for 15 runners). The numbers are in
`dual_cap_results.json` and are recomputed by `test_theory11.py`. Not yet checked
by a human. The 481.123 target is used for planning only.

## What it would cost (`COST.md`, `COST_addendum1.md`, `SHARD_PLAN.md`)

The 15-runner proof's own audit file (Zenodo 10.5281/zenodo.22667683, CC BY 4.0)
shows where its roughly 2,140 CPU-hours went. 19 small primes (89 to 233, and 241)
left thousands to millions of orbits to lift and kill. The other 52 gates (every
prime from 239 to 569 except 241) left only the tight orbit. For 16 runners the
gates sit higher (about 80 primes from 251 up to about 800), so the deciding
number is the level-one generation cost at k = 15 for those primes. Job
`lrc16-allik-probe-v1` (`probe.py`, queued) measures it with Allikvere's own
generator built for 15 speeds; the decision rule is pre-registered in `COST.md`,
Section 4.

## Surviving orbits and tight sets (`THEORY.md`, Sections 5 and 7)

For 14 and 15 runners, the tight vectors (1..13), (1..11,13,24) and (1..14) survive
every binary lifting level. For 16 runners, k+1 = 16 = 2^4, so the binary levels
reach the tight witness 1/16 directly (Lemmas L, S, C). By Zhang's classification
(arXiv:2608.13599, building on Goddyn and Wong), (1..15) is the only tight set
among [15] and its one-entry modifications (Lemma N).

## One computation for every prime (`THEORY.md` Section 8, `THEORY_9.md`, `REVIEW_9.md`)

**Lemma U** separates the prime from the lifting problem: two prime-free cascades
sandwich the true one, U_inf(L) <= J_p(L) <= U_P(L) for every prime p >= P.
`uniform.py` and the independent `grid.py` (Lemma G) compute it.

## What is here

| file | what it does |
|---|---|
| `lrc.c` | from-scratch C engine: canonical cover enumeration up to units, tau(p), lifting cascade, shift filter, general completion, engine-3 and engine-4 pruning (`LRC_PRUNE` bits 1, 2, 4) |
| `lrc_ref.py` | brute-force reference used to test the engine on small cases; exact loneliness; Lemma S of `THEORY.md` |
| `uniform.py` | prime-free lifting of one orbit (Lemma U): U_inf and U_P cascades in exact arithmetic |
| `thresh.py` | exact per-prime test, kill thresholds and the exact cascade inside U_P (Lemmas E, T, R) |
| `uniform_nb.py` | the same at any level (14 = 2*7, 15 = 3*5, ...): general gcd clause, divisor chains, CRT combination (`THEORY_16.md`) |
| `nbc.py`, `nbc.c` | fast non-binary lifting: unit-symmetry reduction, search order, C engine (`THEORY_17.md`) |
| `grid.py` | grid-point witnesses (Lemma G): a second, independent kill test |
| `bounds.py`, `capped.py` | exact flag bound, shape bound, gate planning; the dual-capped flag bound |
| `job*.py` | compete jobs: `job.py`, `job_shift.py`, `job_tau.py`, `job_engine3.py`, `job_orbit.py`, `job_uniform.py`, `job_uniform2.py`, `job_nb.py`, `job_nb2.py` |
| `fetch_*.py` | fetch published files at a pinned commit for a compete job and record their SHA-256 (`fetch_nb3.py` fetches every file of job lrc-nb2) |
| `run_tests_c.py` | runs `test_nbc` and `test_uniform_nb` with the C tests required (no skips) |
| `probe.py` | cost probe of Allikvere's public pipeline (`COST.md`) |
| `results/` | raw outputs of finished jobs, copied unchanged |
| `test_*.py` | tests against brute force and between independent implementations (`test_review9.py` imports no repository code) |
| `THEORY.md`, `THEORY_9.md` ... `THEORY_17.md` | the mathematics, written before each job ran |
| `REVIEW_9.md`, `REVIEW_13_14.md`, `REVIEW_15.md`, `REVIEW_16.md`, `REVIEW_17.md` | adversarial reviews: a second agent told to break Sections 9 and 13 to 17 against the code |
| `PLAN.md`, `PLAN_addendum6.md` ... `PLAN_addendum12.md` | the pre-registered plan and what counts as success |
| `RESULTS_run14.md`, `RESULTS_run16.md`, `RESULTS_run17.md`, `RESULTS_run19.md`, `RESULTS_run20.md`, `RESULTS_run22.md` | graded results and job reports |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python run_tests_c.py            # Linux/macOS with cc: the C tests may not skip
python job_nb2.py --out-dir out --only a14 --workers 1
```

## Credit

All the mathematics this builds on belongs to the authors cited above. This
repository only reimplements their published definitions so the computation can
be checked by an independent route and, if it holds, pushed one runner further.
The level-14 and level-15 fibre searches that `THEORY_16.md` and `THEORY_17.md`
recast, the gcd condition (Definition 2.1(a)), the 3 x 5 split (Lemma 4.5), the
normalisation of Lemma 4.1, the flag bound and the tau table are Jaan Allikvere's
(arXiv:2609.02604). The tight-set classification is Yuhan Zhang's
(arXiv:2608.13599) and Goddyn and Wong's. The relation theorem discussed in
`COST_addendum1.md` is Beck and Everett's (arXiv:2609.06259). The 8-runner check
X2 uses Matthieu Rosenfeld's Lemma 6 (arXiv:2509.14111). The pipeline that
`probe.py` measures is Jaan Allikvere's (Zenodo 10.5281/zenodo.22667683 and
10.5281/zenodo.22066772, CC BY 4.0); it is downloaded, not copied into this
repository.
