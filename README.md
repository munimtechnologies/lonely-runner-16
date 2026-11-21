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

## The bound for 16 runners (worked out in `THEORY.md`)

We carried the paper's shape lemma (its Lemma 3.7, proved there for 14 and 15
runners) to 16 runners. It gives **R_15 < 49/100**, so a primitive counterexample
with 15 speeds has `log(v_1...v_15) < 496.727`. After the forced divisor
720720 = lcm(2..16), **prime gates with log-sum above 483.239** prove the 16-runner
case: roughly 80 primes, against 71 used for 15 runners. Every inequality in the
note is re-checked in exact rational arithmetic by `test_bounds.py`.

For 16 runners, `k+1 = 16 = 2^4` is a prime power, so the binary lifting levels
already reach the natural level 16.

## Two engines

`lrc.c` has two independent ways of doing each step, so every gate can be checked
both ways:

| step | engine 1 | engine 2 |
|---|---|---|
| orbit normalisation of covers | any class moved to 1; lexicographic minimum | Lemma 4.1: the class with the most private times moved to 1 (prunes the search) |
| lifting to the next level | all c^k lifts, each tested by a full scan of times | branch and bound over coordinates on the new times only |

## What is here

| file | what it does |
|---|---|
| `lrc.c` | from-scratch C engine: canonical cover enumeration up to units, tau(p), lifting cascade (both engines) |
| `lrc_ref.py` | brute-force reference used to test the engine on small cases |
| `bounds.py` | exact flag bound (rational arithmetic), shape bound sweep, exact n = 15 shape checks, gate-set planning |
| `job.py` | `repro` (k = 13, 14 re-check), `pilot` (k = 15 survey), `engine2` (cross-check, then both with engine 2) |
| `test_*.py` | tests: the paper's constants, the n = 15 constants, C against Python, engine 1 against engine 2 |
| `THEORY.md` | the 16-runner bound, derived step by step |
| `PLAN.md` | the pre-registered plan and what counts as success |

Build and test:

```
cc -O3 -o lrc lrc.c
python -m unittest -v
python bounds.py 13 14 15
./lrc gate 15 401 2,2,2,2,2 1500 1000000 1 1
```

## Credit

All the mathematics this builds on belongs to the authors cited above. This
repository only reimplements their published definitions so the computation can
be checked by an independent route and, if it holds, pushed one runner further.
