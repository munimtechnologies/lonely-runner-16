# RESULTS, run 19: job lrc-nb (filed as lrc16-engine2-v2), graded

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Graded 2026-11-24 against `PLAN_addendum10.md`,
which was written before the job ran. Every number below is from
`results/lrc-nb/summary_nb.json` and `results/lrc-nb/stdout.txt`. Those are the raw
outputs, copied unchanged from the job: Blade, python:3.12, 1 CPU, started
2026-11-23 14:15 UTC, 4,878 s wall, peak memory 0.03 GB. The published helpers
were fetched at their pinned commits (`results/lrc-nb/pinned_sha256.txt`).

## Sanity gate

| check | result |
|---|---|
| G0: `test_uniform_nb` inside the job | passed (15 tests, 1.7 s) |
| S2, a14 = (1..14) | holds: the linear lift is in U_inf(3) and U_inf(5), is not in U_inf(15), and has status t0 at 15 |
| S2, a13 and b13 | partly checked: linear lift in U_inf(2), status t0 at 14; U_inf(7) and U_inf(14) were not reached |
| S3 (U_inf inside U_P0) | no violation where both were computed: level 3 (a14), level 2 (a13, b13) |
| S4, S5 | not reached (no U_P0(L) was completed) |
| C1 (chain = CRT combination) | holds wherever both finished: a14 at P = inf, with the gcd clause (both empty) and without it (both the same 3 classes) |
| S7 | holds for a14 at P = inf: the gcd-free U_inf(15) has 3 classes and all 3 meet the gcd clause |

No sanity check failed.

## Predictions

| prediction | outcome |
|---|---|
| **N1: U_inf(15) is empty for (1..14)** | **holds.** Chain 1 -> 3 -> 15 and the CRT combination of U_inf(3) and U_inf(5) (4 candidates tested) agree. |
| N2: the (1..14) statement at P0 = 239 | untested. U_239(3) has 3 classes, but the level-5 lift at P = 239 (576 s) and the chain to 15 (864 s) hit their deadlines. |
| N3: U_inf(14) empty for a13 and b13 | untested. The level-7 lift from level 1 (189 s) and the chain 2 -> 14 (283.5 s) hit their deadlines, even at P = inf. |
| N4: the a13 and b13 statements at P0 = 199 | untested (same reason) |
| X1: J_p(L) empty at the paper's gate primes | untested (no U_P0(L)) |
| I1, I2 (recorded only) | not computed |

So the outcome is "a cut before U_P0(L) completes: no statement". The only graded
result is N1. N1 is a consistency check that the published 15-runner proof
forces (`THEORY_16.md` 16.3). It agrees with arXiv:2609.02604 Section 4.4, but
on its own it proves nothing new.

## What the computed sets look like

For (1..14) at P = inf: U_inf(3) = {(1,2,0) repeated} and U_inf(5) = {(1,2,3,4,0)
repeated}. These are just the linear lifts. Without the gcd clause, U_inf(15)
consists of the zero vector, 3(1..14) mod 15 and 5(1..14) mod 15. Each of them has
every coordinate divisible by 3 or by 5, so the gcd clause removes all three.
This matches the paper's report that every witness-free tuple at level 15 fails
the gcd condition, here for every prime at once.

At P = 239, U_239(3) has 3 classes. They are the linear lift and the two vectors
that differ from it only in the coordinate of speed 6 (residue 1 or 2 instead of
0). Without the gcd clause there are 5 classes. For a13 the sizes are
|U_inf(2)| = 1 and |U_199(2)| = 9, and without the gcd clause 2 and 12. For b13
they are 1 and 5, and without the gcd clause 2 and 8.

## Where the time went

All the lifting ran in pure Python branch and bound over f^k children per parent.

| step | P = inf | P = P0 |
|---|---|---|
| (1..14): 1 -> 5 (5^14 leaves) | 15.5 s | cut at 576 s |
| (1..14): 1 -> 3 -> 15 | 33.0 s | cut at 864 s |
| (1..13), b13: 1 -> 7 (7^13 leaves) | cut at 189 s | cut at 252 s |
| (1..13), b13: 1 -> 2 -> 14 | cut at 283.5 s | cut at 378 s |

The time budget was split across four modes, and most of it went to steps that
could not finish. The plan's next step for a cut ("a larger budget or a
faster lifting order, after reading where the time went") is taken in
`THEORY_17.md` and `PLAN_addendum11.md`. That means a C engine, the unit-symmetry
reduction (Lemma S), and the cheap order f2 -> L first (7 -> 14 is 2^13 leaves per
parent instead of 7^13).
