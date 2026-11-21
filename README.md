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

## The bound for 16 runners (worked out in `THEORY.md`, Sections 1-3)

We carried the paper's shape lemma (its Lemma 3.7, proved there for 14 and 15
runners) to 16 runners. It gives **R_15 < 49/100**, so a primitive counterexample
with 15 speeds has `log(v_1...v_15) < 496.727`. After the forced divisor
720720 = lcm(2..16), **prime gates with log-sum above 483.239** prove the 16-runner
case: roughly 80 primes, against 71 used for 15 runners. Every inequality in the
note is re-checked in exact rational arithmetic by `test_bounds.py`. A second,
independent pass over the derivation (run 3) agreed, apart from one rounded
constant that nothing depends on (erratum in `THEORY.md`).

## What it would cost (`COST.md`)

The 15-runner proof's own audit file (Zenodo 10.5281/zenodo.22667683, CC BY 4.0)
shows where its roughly 2,140 CPU-hours went. 19 small primes (89 to 233, and 241)
left thousands to millions of orbits to lift and kill; p = 181 alone left
8,235,157 orbits, and its kill stage took about 140 CPU-hours. The other 52 gates
(every prime from 239 to 569 except 241) left only the tight orbit. Level-one
generation grows roughly as p^6 (arXiv:2609.02604). For 16 runners the gates sit
higher (about 80 primes from 251 up to about 800), so the deciding number is the
level-one generation cost at k = 15 for those primes. Nobody has published it.
Job `lrc16-allik-probe-v1` (`probe.py`) measures it with Allikvere's own
generator built for 15 speeds. It also first checks that the build reproduces his
published regression, and extracts the stage-by-stage costs from his logs. The
decision rule for what to do with the number is pre-registered in `COST.md`,
Section 4.

## Surviving orbits (`THEORY.md`, Section 5)

For 14 and 15 runners, the tight vectors (1..13), (1..11,13,24) and (1..14) survive
every binary lifting level, and the paper needs separate level-14 and level-15
searches. For 16 runners, k+1 = 16 = 2^4, so the binary levels reach the tight
witness 1/16 directly:

- **Lemma L:** every *linear* lift lambda (1..15) mod 16p is proper at level 16.
- **Lemma S:** a shift lemma for composite d (4, 8, 16, 32, ...), the 16-runner
  substitute for the paper's Lemma 4.6, which is useless at d = 2.
- **Lemma C:** the lifting cascade may drop every lift that Lemma S certifies.

`PLAN.md` (addendum 2) pre-registers the prediction that the orbit of (1..15) is
empty at level 16 at all ten pilot primes; job `lrc16-shift-v1` tests it. A third
reading of Section 5, written to find errors, found none (`THEORY.md` 5.5).

## Tight sets for 16 runners (`THEORY.md`, Section 7)

The orbits that survived binary lifting for 14 and 15 runners are exactly the
tight sets near [k]. Which tight sets exist for 16 runners?

- By Zhang's classification of tight one-entry modifications of [n-1]
  (arXiv:2608.13599, building on Goddyn and Wong), a short argument (**Lemma N**)
  shows there are none when n + 1 is prime. For 16 runners n + 1 = 17, so
  **(1..15) is the only tight set among [15] and its one-entry modifications**.
  The same criterion gives exactly the published survivors for 14 runners
  ((1..11,13,24)) and 15 runners (none besides (1..14)).
- Zhang's census finds no tight two-entry modification for 16 runners with
  inserted speeds up to 128.
- **Erratum:** run 3 called (1..13,15,28) tight. It is not: t = 993/2800 is a
  strict witness, and so is every t in an open interval of length 1/1344.

`PLAN.md` (addendum 4) pre-registers the consequence: binary lifting to level 32
should leave **no survivors at all** at the 16-runner pilot gates (prediction P4),
which would make 16 runners simpler than 14 and 15 at this step. `test_tight.py`
checks all of this in exact arithmetic.

## One computation for every prime (`THEORY.md`, Section 8)

Lifting an orbit is usually done one prime at a time. Section 8 separates the
prime from the problem. By the Chinese remainder theorem a time at level L is a
pair (beta, t) with beta in Z_L and t in (1/p)Z, and a lift is proper iff some
pair has ||beta z_i / L + t s_i|| >= 1/(k+1) for all i (or the gcd clause holds).
The prime only fixes the grid of t. **Lemma U** then gives two prime-free cascades
that sandwich the true one: U_inf(L) <= J_p(L) <= U_P(L) for every prime p >= P
(not dividing a fixed Q). For s = (1..15):

- if U_251(16) is empty, the orbit of (1..15) dies by level 16 at **every** prime
  p >= 251, which covers every planned gate in one computation;
- if U_inf(16) is not empty, its lifts survive level 16 at **every** prime p >= 17.

The same section gives a two-line, prime-free proof that the tight orbit (1..k)
can never be killed by binary lifting when k + 1 is not a power of 2: the
reason the 14- and 15-runner proofs needed separate fibre searches.
`uniform.py` computes the two cascades in exact integer arithmetic (branch and
bound over cell bitmasks), and `test_uniform.py` checks the sandwich level by level
against the brute-force definition at small primes. Job `lrc16-uniform-v1`
runs it; the readings are pre-registered in `PLAN.md` (addendum 5).

## Grid-point witnesses: a second implementation (`THEORY_9.md`)

Section 9 answers the same question as `uniform.py` a different way: from each grid
point c/D it measures exactly how far the strict witnesses reach (**Lemma G**).
With D = 2Q the test is exact, and `test_grid.py` checks that `grid.py` and
`uniform.py`, which share no code, agree on every case tried. With the coarse
grid D = 16 the test is fast and, at level 2 for (1..15), solvable by hand:
**Lemma G2** names exactly which 13,054 of the 32,768 level-2 lifts survive the
near-grid tests, which gives a check of the uniform job's output that can be read
off by eye (`PLAN_addendum6.md`, X3). Section 9.4 notes that Lemma U holds at any
level, the route to a prime-free version of the 14- and 15-runner fibre searches.

## Small covers and the gate primes (`THEORY.md`, Section 6)

At primes where the folded times can be covered by at most k - 2 speed classes
(tau(p) <= k - 2), the usual shortcut enumeration misses some level-one orbits.
The paper handled 19 such primes for 15 runners with a general enumeration.
`lrc.c` now has:

- **`ext`**: a general completion (every small cover plus every multiset of extra
  classes), tested against a brute-force enumeration of all k-multisets at
  primes where tau(p) <= k - 2;
- **`tau`**: decides whether a cover on at most a given number of classes exists.

Job `lrc16-tau-v1` re-checks the paper's tau table for 15 runners (71 primes) and
maps tau_15(p) for every prime up to 1000, which fixes the gate primes for 16
runners. Its readings are pre-registered in `PLAN.md` (addendum 3).

## Two engines

`lrc.c` has two independent ways of doing each step, so every gate can be checked
both ways:

| step | engine 1 | engine 2 |
|---|---|---|
| orbit normalisation of covers | any class moved to 1; lexicographic minimum | Lemma 4.1: the class with the most private times moved to 1 (prunes the search) |
| lifting to the next level | all c^k lifts, each tested by a full scan of times | branch and bound over coordinates on the new times only |

Either engine can run with the optional shift filter (`scascade`, `scascadebb`,
or the `shift` argument of `gate`) and the general completion (`ext` argument).

## What is here

| file | what it does |
|---|---|
| `lrc.c` | from-scratch C engine: canonical cover enumeration up to units, tau(p), lifting cascade (both engines), shift filter, general completion |
| `lrc_ref.py` | brute-force reference used to test the engine on small cases; exact loneliness; Lemma S |
| `uniform.py` | prime-free lifting of one orbit (Lemma U): U_inf and U_P cascades in exact arithmetic |
| `grid.py` | grid-point witnesses (Lemma G): a second, independent kill test, exact at D = 2Q; near-grid masks for Lemma G2 |
| `bounds.py` | exact flag bound (rational arithmetic), shape bound sweep, exact n = 15 shape checks, gate-set planning |
| `job.py` | `repro` (k = 13, 14 re-check), `pilot` (k = 15 survey), `engine2` (cross-check, then both with engine 2) |
| `job_shift.py` | k = 15 orbit probe (prediction P1) and shift-filtered pilot gates |
| `job_tau.py` | tau(p) scans: the paper's k = 14 table (R1) and k = 15 up to p = 1000 (P3) |
| `job_uniform.py` | Lemma U cascades for (1..15), (1..13,15,28) and the 14/15-runner sanity orbits (P5, P6, S1) |
| `probe.py` | cost probe: downloads Allikvere's public pipeline from Zenodo, checks hashes, extracts his per-gate costs, builds his generator for K = 14 and 15, times it (`COST.md`) |
| `test_*.py` | tests: the paper's constants, the n = 15 constants, C against Python, engine 1 against engine 2, Lemmas S and L, tau and the general completion, tight sets (`test_tight.py`), the Lemma U sandwich (`test_uniform.py`), `grid.py` against `uniform.py` and Lemma G2 (`test_grid.py`), the probe's parsers (`test_probe.py`) |
| `THEORY.md` | the 16-runner bound, derived step by step, the surviving-orbit lemmas, small covers, tight sets, lifting uniformly in p |
| `THEORY_9.md` | Section 9: grid-point witnesses, Lemma G2, Lemma U at any level |
| `COST.md` | the published cost of the 15-runner proof, what it implies for 16 runners, and the pre-registered decision rule for the probe |
| `PLAN.md`, `PLAN_addendum6.md` | the pre-registered plan and what counts as success |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python bounds.py 13 14 15
python job_uniform.py --out-dir out --only e7
python -I probe.py --data-dir data --out-dir out --budget-min 60
./lrc tau 15 401 13 600
./lrc gate 15 401 2,2,2,2,2 1500 1000000 1 1 1 1
./lrc scascadebb 15 401 2,2,2,2,2,2 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
```

## Credit

All the mathematics this builds on belongs to the authors cited above. This
repository only reimplements their published definitions so the computation can
be checked by an independent route and, if it holds, pushed one runner further.
The tight-set classification used in `THEORY.md` Section 7 is Yuhan Zhang's
(arXiv:2608.13599) and Goddyn and Wong's. The pipeline that `probe.py` measures
is Jaan Allikvere's (Zenodo 10.5281/zenodo.22667683 and 10.5281/zenodo.22066772,
CC BY 4.0); it is downloaded, not copied into this repository.
