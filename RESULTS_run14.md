# Results: jobs lrc16-engine2-v1 and lrc16-tau-v2 (graded 2026-11-22, run 14)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; not yet checked by a
human expert. CC BY 4.0. Raw outputs are in `results/lrc16-engine2-v1/` and
`results/lrc16-tau-v2/`, copied unchanged from the job outputs.

## lrc16-engine2-v1 (Blade, finished 15:07Z, 80 min, peak 0.09 GB)

Graded against `PLAN.md`, addendum 1 (engine 2).

**Cross-check: holds where tested.** Both engines finished 8 of the 12 small
gates (k = 8 to 11, p = 61 to 163). On all 8 they agree on tau, orbit counts by
size, tuples, killed, survived, overflow, completeness and per-level improper
counts. Each of these gates left exactly one surviving tuple after five binary
levels, as expected for the tight orbit. Engine 2's cover search plus lifting was
1.8 to 11.3 times faster (median about 6.6). The other 4 gates (k = 12 to 14)
hit the 240 s cap in both engines, so they test nothing.

| k | p | engine 1 s | engine 2 s | tuples | survived |
|---|---|---|---|---|---|
| 8 | 61 | 0.101 | 0.011 | 1,043 | 1 |
| 8 | 73 | 0.294 | 0.053 | 4,261 | 1 |
| 9 | 83 | 1.982 | 0.212 | 14,866 | 1 |
| 9 | 101 | 3.433 | 0.479 | 22,983 | 1 |
| 10 | 103 | 12.479 | 1.105 | 46,232 | 1 |
| 10 | 131 | 2.039 | 1.108 | 2,941 | 1 |
| 11 | 137 | 71.190 | 11.625 | 110,134 | 1 |
| 11 | 163 | 63.358 | 27.213 | 54,247 | 1 |

**Repro and pilot gates with engine 2: none finished.** All 20 gates (k = 13 at
401, 479; k = 14 at 239 to 569; k = 15 at 251 to 809) stopped in the level-one
cover search at the 800 s cap, before any lifting. Orbits found before the cap:
for k = 15, 263,565 at p = 251 but only 1 at p = 503, 601 and 809 and none at
p = 701. The level-one output at large p is tiny and the cost is pure search, as
`COST.md` inferred from the published logs. **This is a negative measurement:
our independent engine, as it stood, cannot do a single 16-runner gate in 800 s.**
That is why this run adds engine 3 (`THEORY_13.md`).

## lrc16-tau-v2 (Dell, finished 16:15Z, 255 min, peak 0.08 GB)

Graded against `PLAN.md`, addendum 3. Unit tests: all passed (the test fix from
v1 worked).

**R1 (re-check of Table 2 of arXiv:2609.02604 v2): agrees at 24 of 71 primes, no
disagreement, 47 untested.**

- At all 19 primes where the paper reports a cover of the folded times by at most
  12 classes (89, 131, ..., 241), we find one too: tau_14 = 11 at p = 131 and 12
  at the other 18. Each cover found is listed in `results/lrc16-tau-v2/tau_k14.jsonl`.
- At 5 of the paper's 52 "tau >= 13" primes (239, 251, 263, 269, 283) we certify
  that no cover on <= 12 classes exists (exhaustive search, 74 to 292 s each).
- The other 47 primes (257 to 569) hit the 300 s cap: untested.

**P3 (every prime in [400, 1000] has tau_15(p) >= 14): untested.** All 90 primes
in the range hit the 400 s cap. (The job's own summary prints "holds where
tested" because it only looked for counterexamples; with no prime tested, the
correct reading is untested.)

**Measurements for 16 runners (k = 15, covers on <= 13 classes).**

- 48 primes have tau_15(p) <= 13: **every prime from 17 to 277 except 29, 31 and
  239**, with 269 and 271 undecided. Histogram of tau: 8 (one prime), 9 (2),
  10 (5), 11 (8), 12 (22), 13 (10). tau_15 = 13 at 181, 191, 211, 223, 233, 241,
  251, 257, 263 and 277.
- Only **p = 239** (above the trivial 29 and 31) is certified tau_15 >= 14 in this
  range (114,684,186 nodes, 250 s).
- So small covers persist for 16 runners at least up to 277, beyond the paper's
  last small-cover prime for 15 runners (241). The PLAN's heuristic put the
  k = 15 threshold near 275; the data so far are consistent with that, but the
  primes above 277 are undecided.
- Consequence for the gate plan: the primes with tau_15 >= 14 known so far have a
  log-sum of 12.28, far from the 483.239 target. Gates at primes with tau <= 13
  need the general completion (`THEORY.md` 6.2), at a cost of up to
  C(n + 1, 2) extra tuples per 13-class cover.

## Still queued (not graded)

`lrc-repro-k14-v1`, `lrc16-pilot-v1`, `lrc16-shift-v2`, `lrc16-uniform-v1` and
`lrc16-allik-probe-v1` are waiting for memory on the shared machines. The probe,
which builds Allikvere's own generator for 15 speeds and times it, remains the
deciding measurement for the cost of 16 runners.
