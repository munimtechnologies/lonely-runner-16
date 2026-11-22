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

## Latest results (2026-11-22, `RESULTS_run14.md`)

- **Engine cross-check:** our two independent engines agree on all 8 small gates
  that both finished (k = 8 to 11).
- **Re-check of the 15-runner proof's tau table:** at 24 of the 71 primes of
  Table 2 of arXiv:2609.02604 v2 our search agrees with the paper (all 19
  small-cover primes, and 5 of the "no small cover" primes); no disagreement; 47
  primes hit the time cap.
- **16 runners, small covers:** every prime from 17 to 277 except 29, 31 and 239
  has a cover of the folded times by at most 13 speed classes (269 and 271
  undecided). Small covers therefore persist beyond the 15-runner case's last one
  (241), and the gates at those primes need the general completion.
- **Negative:** with engine 2, none of the 20 gates for 14 to 16 runners at
  primes 239 to 809 got through the level-one cover search in 800 s. The cover
  search, not the lifting, is our bottleneck.

## Engine 3: two safe prunings of the cover search (`THEORY_13.md`)

- **Lemma F (fractional bound):** any completion needs at least
  sum over uncovered times a of 1/G(a) more classes, where G(a) is the largest
  number of uncovered times covered by one allowed class that covers a.
- **Lemma P (forbidden classes):** a class that covers every private time of an
  already chosen class can never be added, since the cover could not be
  irredundant; with Lemma 4.1's normalisation, neither can a class that would leave
  class 1 with fewer than q_s private times.

Both cut only search nodes with no reportable cover below them, so every output is
unchanged. `test_prune.py` checks both rules by brute force and the C engine with
all four settings. Set `LRC_PRUNE=3` to use them. Job `lrc16-engine3-v1` measures
the speed-up and spends it on the undecided tau primes. Its readings (including a
speed prediction that may fail) are pre-registered in `PLAN_addendum7.md`.

## Engine 4: early orbit pruning (`THEORY_14.md`)

The search fixes class 1 and keeps only the member of each orbit in which class 1
has the most private times, but it used to check that only at the leaf. **Lemma M:**
a private time of a chosen class v that no allowed class covers stays private to v
in every completion, so if v already has more such "locked" times than class 1 has
private times, nothing below the node can be reported, and every class that would
push class 1 below that count can be dropped. The rule never cuts the member in
which class 1 is the largest, so covers, tau and gate results are unchanged.
`test_orbit.py` checks it by brute force, with a second implementation of the whole
search in Python, and (with a compiler) the C engine with `LRC_PRUNE=4` and `7`.
Job `lrc16-orbit-v1` measures what it saves on top of engine 3; its readings
(two predictions that may fail) are pre-registered in `PLAN_addendum8.md`.

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
`THEORY_11.md` (an attempt to break Section 10) found no error, and
`THEORY_12.md` shows that exact constants at every codimension plus dual caps of
every rank give exactly the Section 10 bound and nothing more. Not yet checked by
a human. The 481.123 target is used for planning only, conditional on Section 10.

## What it would cost (`COST.md`, `COST_addendum1.md`, `SHARD_PLAN.md`)

The 15-runner proof's own audit file (Zenodo 10.5281/zenodo.22667683, CC BY 4.0)
shows where its roughly 2,140 CPU-hours went. 19 small primes (89 to 233, and 241)
left thousands to millions of orbits to lift and kill; p = 181 alone left
8,235,157 orbits, and its kill stage took about 140 CPU-hours. The other 52 gates
(every prime from 239 to 569 except 241) left only the tight orbit. Level-one
generation grows roughly as p^6 (arXiv:2609.02604). For 16 runners the gates sit
higher (about 80 primes from 251 up to about 800), so the deciding number is the
level-one generation cost at k = 15 for those primes. Nobody has published it.
Job `lrc16-allik-probe-v1` (`probe.py`) measures it with Allikvere's own
generator built for 15 speeds. The decision rule for what to do with the number
is pre-registered in `COST.md`, Section 4. `COST_addendum1.md` closes two ideas
that might have lowered the cost without new computation (Beck-Everett relations;
stronger Korkine-Zolotarev facts).

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
empty at level 16 at all ten pilot primes. Job `lrc16-shift-v2` tests it.

## Tight sets for 16 runners (`THEORY.md`, Section 7)

By Zhang's classification of tight one-entry modifications of [n-1]
(arXiv:2608.13599, building on Goddyn and Wong), **(1..15) is the only tight set
among [15] and its one-entry modifications** (Lemma N). `PLAN.md` (addendum 4)
pre-registers the consequence: binary lifting to level 32 should leave no
survivors at all at the 16-runner pilot gates (prediction P4).

## One computation for every prime (`THEORY.md` Section 8, `THEORY_9.md`)

**Lemma U** separates the prime from the lifting problem: two prime-free cascades
sandwich the true one, U_inf(L) <= J_p(L) <= U_P(L) for every prime p >= P. If
U_251(16) is empty for s = (1..15), the orbit of (1..15) dies by level 16 at every
planned gate in one computation. `uniform.py` and the independent `grid.py`
(Lemma G) compute it; job `lrc16-uniform-v1` runs it (`PLAN.md` addendum 5,
`PLAN_addendum6.md`).

## Small covers and the gate primes (`THEORY.md`, Section 6)

At primes where the folded times can be covered by at most k - 2 speed classes
(tau(p) <= k - 2), the usual shortcut enumeration misses some level-one orbits.
`lrc.c` has a general completion (`ext`) for those primes and a `tau` mode that
decides whether such a cover exists. Results: see "Latest results" above.

## What is here

| file | what it does |
|---|---|
| `lrc.c` | from-scratch C engine: canonical cover enumeration up to units, tau(p), lifting cascade (both engines), shift filter, general completion, engine-3 and engine-4 pruning (`LRC_PRUNE` bits 1, 2, 4) |
| `lrc_ref.py` | brute-force reference used to test the engine on small cases; exact loneliness; Lemma S |
| `uniform.py` | prime-free lifting of one orbit (Lemma U): U_inf and U_P cascades in exact arithmetic |
| `grid.py` | grid-point witnesses (Lemma G): a second, independent kill test |
| `bounds.py` | exact flag bound (rational arithmetic), shape bound sweep, exact n = 15 shape checks, gate-set planning |
| `capped.py` | the flag bound with the dual cap t_d <= 1/3 (Proposition 10.2), solved exactly |
| `dual_cap_results.json` | the dual-cap numbers for 15 and 16 runners, recomputed by `test_theory11.py` |
| `job.py` | `repro` (k = 13, 14 re-check), `pilot` (k = 15 survey), `engine2` (cross-check, then both with engine 2) |
| `job_shift.py` | k = 15 orbit probe (prediction P1) and shift-filtered pilot gates |
| `job_tau.py` | tau(p) scans: the paper's k = 14 table (R1) and k = 15 up to p = 1000 (P3) |
| `job_engine3.py` | engine-3 cross-check (A1), consistency (A2), speed (S1), the undecided tau primes (P3, R1) |
| `job_orbit.py` | engine-4 checks: same answers (M1), work (M2), speed over engine 3 (S2) |
| `job_uniform.py` | Lemma U cascades for (1..15), (1..13,15,28) and the 14/15-runner sanity orbits |
| `fetch_pinned.py` | fetches the engine files at a pinned commit for a compete job and records their SHA-256 |
| `probe.py` | cost probe: downloads Allikvere's public pipeline from Zenodo, checks hashes, extracts his per-gate costs, builds his generator for K = 14 and 15, times it (`COST.md`) |
| `results/` | raw outputs of finished jobs, copied unchanged |
| `test_*.py` | tests: the paper's constants, C against Python, engine 1 against engine 2, engine 3 against engine 2 and its two lemmas by brute force (`test_prune.py`), engine 4 and Lemma M by brute force and a second Python search (`test_orbit.py`), Lemmas S, L, U, G, tight sets, the probe's parsers, the dual cap and its re-checks |
| `THEORY.md`, `THEORY_9.md` ... `THEORY_14.md` | the 16-runner bound, surviving-orbit lemmas, small covers, tight sets, lifting uniformly in p, the dual cap and its limits, engine-3 prunings, engine-4 orbit pruning |
| `COST.md`, `COST_addendum1.md`, `SHARD_PLAN.md` | the cost of the 15-runner proof, what it implies for 16, and how the gates would be sharded |
| `PLAN.md`, `PLAN_addendum6.md` ... `PLAN_addendum8.md` | the pre-registered plan and what counts as success |
| `RESULTS_run14.md` | graded results of `lrc16-engine2-v1` and `lrc16-tau-v2` |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python bounds.py 13 14 15
LRC_PRUNE=7 ./lrc tau 15 401 13 600
LRC_PRUNE=7 ./lrc gate 15 401 2,2,2,2,2 1500 1000000 1 1 1 1
./lrc scascadebb 15 401 2,2,2,2,2,2 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
```

## Credit

All the mathematics this builds on belongs to the authors cited above. This
repository only reimplements their published definitions so the computation can
be checked by an independent route and, if it holds, pushed one runner further.
The normalisation that engines 3 and 4 prune against is Lemma 4.1 of Jaan
Allikvere's paper (arXiv:2609.02604).
The flag bound that Sections 10 to 12 sharpen, re-check and bound is Jaan
Allikvere's (arXiv:2609.02604), including the Lemma 3.3 and Proposition 3.4 that
Section 12 examines, and the tau table that `job_tau.py` re-checks. The
tight-set classification used in `THEORY.md` Section 7 is Yuhan Zhang's
(arXiv:2608.13599) and Goddyn and Wong's. The relation theorem discussed in
`COST_addendum1.md` is Beck and Everett's (arXiv:2609.06259). The pipeline that
`probe.py` measures is Jaan Allikvere's (Zenodo 10.5281/zenodo.22667683 and
10.5281/zenodo.22066772, CC BY 4.0); it is downloaded, not copied into this
repository.
