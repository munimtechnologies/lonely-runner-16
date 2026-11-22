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

## A sharper flag bound: the dual cap (`THEORY_10.md`, re-checked in `THEORY_11.md`)

The flag bound minimises the product of the Gram-Schmidt lengths t_1, ..., t_d of a
KZ basis of the lattice Lambda = P Z^n. `COST_addendum1.md` showed that no further
KZ fact can raise that minimum. Section 10 uses an arithmetic fact instead. The
dual of Lambda is the lattice of **integer relations** of the speeds, and the last
Gram-Schmidt length is exactly t_d = 1 / (sum_k q_k h_k^2) for an integer relation
h. Since a counterexample's speeds are distinct and positive, every relation has
sum h_k^2 >= 3, so **t_d < 1/3** (Lemma 10.1). The old minimiser has t_d = c_d =
17/36 for 16 runners, so the cap bites. Solving the capped problem exactly
(`capped.py`, a vertex enumeration cross-checked by brute force in small
dimensions):

| runners | min prod t_i, as a multiple of Allikvere's K_n | drop in the log speed-product bound | gate target |
|---|---|---|---|
| 15 | 1369/1029 = 1.3304 | 1.9985 nats | 401.9846 -> 399.986 |
| 16 | 12150/9163 = 1.3260 | 2.1162 nats | 483.239 -> 481.123 |

This is a small saving (about a third of one gate prime near p = 800). It costs no
computation, and as far as we know it is the first improvement of the flag bound
that uses the arithmetic of the speeds. The numbers are in `dual_cap_results.json`,
and `test_theory11.py` recomputes every one of them from `capped.py`.

**Re-check and limits (`THEORY_11.md`).** A deliberate attempt to break Section 10
found no error. It also checked the step from the covolume to the speed product
against Allikvere's Theorem 3.8. It then closed the two natural extensions:

- **The same relation runs both bounds.** The hyperplane in Allikvere's prefix
  bound at r = d-1 is exactly h^perp for the same relation h (Lemma 11.1). Using
  the exact hyperplane constant together with the cap gains nothing: the binding
  case is a 3-term sum relation v_c = v_a + v_b, where both constants stay at 1/3
  (Prop. 11.2).
- **A rank-2 cap does not bind.** t_{d-1} t_d < 1/8, since two independent
  relations have Gram determinant >= 8 (Lemma 11.4). At the minimiser the product
  is only 75/784.

The remaining obstruction is a counterexample whose last dual relation is a sum
relation among speeds below about a fifth of the fastest (Remark 11.3). Not yet
checked by a human. The 481.123 target is used for planning only, conditional on
Section 10.

## What it would cost (`COST.md`, `COST_addendum1.md`)

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

`COST_addendum1.md` closes two ideas that might have lowered the cost without any
new computation:

- **Beck-Everett relations** (arXiv:2609.06259) say a counterexample satisfies an
  integer relation with l1-norm at most 33. By Minkowski's theorem, every residue
  vector modulo any level up to 39,142 already satisfies a relation with l1-norm
  at most 13, so the condition prunes nothing inside the gates.
- **Stronger Korkine-Zolotarev facts** cannot sharpen the flag bound. An orthogonal
  lattice with the optimal profile is itself a KZ basis, so the minimum prod c_r
  stands. Only a stronger prefix inequality (Proposition 3.4) would help: scaling
  every B_r by f lowers the gate target by 105 ln f nats. (Section 10 above gets
  around this a different way: that orthogonal lattice is not the lattice of any
  vector with distinct speeds.)

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
empty at level 16 at all ten pilot primes. Job `lrc16-shift-v2` tests it (v1 was
withdrawn because of a test bug, see below). A third reading of Section 5,
written to find errors, found none (`THEORY.md` 5.5).

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

Job `lrc16-tau-v2` re-checks the paper's tau table for 15 runners (71 primes) and
maps tau_15(p) for every prime up to 1000, which fixes the gate primes for 16
runners. Its readings are pre-registered in `PLAN.md` (addendum 3).

**The v1 failure (2026-11-22).** `lrc16-tau-v1` ran, and 14 of its 15 engine
tests passed: the C engine agreed with the reference on covers, cascades, both
lifting methods, gates and the shift cascade. The one failure was a bug in the
test, not the engine. `test_shiftok_matches_reference` drew up to 8 exceptional
coordinates, so for k = 7 it built an 8-entry vector. The C engine reads exactly
K = 7 values, and on those it was right (d = 2). The Python reference read all 8
(answer 0). The test now builds vectors of length k and asserts it.
`fetch_pinned.py` lets the v2 jobs run the engine exactly as published at commit
c5cfb60, together with the fixed test.

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
| `capped.py` | the flag bound with the dual cap t_d <= 1/3 (Proposition 10.2), solved exactly by vertex enumeration, with a brute-force cross-check; the Lemma 10.1 identity on explicit lattices; Lemma 10.4 |
| `dual_cap_results.json` | the dual-cap numbers for 15 and 16 runners and the THEORY_11 negative results, each recomputed by `test_theory11.py` |
| `job.py` | `repro` (k = 13, 14 re-check), `pilot` (k = 15 survey), `engine2` (cross-check, then both with engine 2) |
| `job_shift.py` | k = 15 orbit probe (prediction P1) and shift-filtered pilot gates |
| `job_tau.py` | tau(p) scans: the paper's k = 14 table (R1) and k = 15 up to p = 1000 (P3) |
| `job_uniform.py` | Lemma U cascades for (1..15), (1..13,15,28) and the 14/15-runner sanity orbits (P5, P6, S1) |
| `fetch_pinned.py` | fetches the engine files at a pinned commit for a compete job and records their SHA-256 |
| `probe.py` | cost probe: downloads Allikvere's public pipeline from Zenodo, checks hashes, extracts his per-gate costs, builds his generator for K = 14 and 15, times it (`COST.md`) |
| `test_*.py` | tests: the paper's constants, the n = 15 constants, C against Python, engine 1 against engine 2, Lemmas S and L, tau and the general completion, tight sets (`test_tight.py`), the Lemma U sandwich (`test_uniform.py`), `grid.py` against `uniform.py` and Lemma G2 (`test_grid.py`), the probe's parsers (`test_probe.py`), the Minkowski and flag-sensitivity facts (`test_cost_addendum1.py`), the dual cap (`test_capped.py`), its re-check and limits (`test_theory11.py`) |
| `THEORY.md` | the 16-runner bound, derived step by step, the surviving-orbit lemmas, small covers, tight sets, lifting uniformly in p |
| `THEORY_9.md` | Section 9: grid-point witnesses, Lemma G2, Lemma U at any level |
| `THEORY_10.md` | Section 10: the dual cap t_d < 1/3 and the sharper flag bound for 15 and 16 runners; exact hyperplane loneliness |
| `THEORY_11.md` | Section 11: adversarial re-check of Section 10; the prefix bound at r = d-1 and the cap share one relation; why coupling them and rank-2 caps gain nothing |
| `COST.md` | the published cost of the 15-runner proof, what it implies for 16 runners, and the pre-registered decision rule for the probe |
| `COST_addendum1.md` | two cost-reduction ideas checked and closed (Beck-Everett relations; KZ constraints in the flag bound) |
| `PLAN.md`, `PLAN_addendum6.md` | the pre-registered plan and what counts as success |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python bounds.py 13 14 15
python capped.py
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
The flag bound that Sections 10 and 11 sharpen and re-check is Jaan Allikvere's
(arXiv:2609.02604). The tight-set classification used in `THEORY.md` Section 7 is
Yuhan Zhang's (arXiv:2608.13599) and Goddyn and Wong's. The relation theorem
discussed in `COST_addendum1.md` is Beck and Everett's (arXiv:2609.06259). The
pipeline that `probe.py` measures is Jaan Allikvere's (Zenodo
10.5281/zenodo.22667683 and 10.5281/zenodo.22066772, CC BY 4.0); it is downloaded,
not copied into this repository.
