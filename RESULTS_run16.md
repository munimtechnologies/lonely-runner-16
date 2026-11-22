# Results, run 16 (2026-11-22): lrc16-uniform-v1 and lrc16-pilot-v1

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Every number below is read from the raw
outputs committed unchanged in `results/lrc16-uniform-v1/summary_uniform.json`
and `results/lrc16-pilot-v1/summary_pilot.json`. Rules: `PLAN.md` addenda 2, 4 and 5,
and `PLAN_addendum6.md`, all written before the jobs ran.

## lrc16-uniform-v1 (Lemma U cascades; Dell, 2026-11-22 22:56-22:58 UTC)

Unit tests passed (step 1 exit 0); the job ran in about 3.4 minutes.

| base s | P | survivors at level 2 / 4 / 8 / 16 / 32 (unit classes) | linear among them | cut |
|---|---|---|---|---|
| (1..7) | inf | 1 / 1 / **0** | 1 / 1 / - | none |
| (1..7) | 29 | 49 / 331 / 364 / 415 (levels 2-16) | 1 / 1 / 0 / 0 | none |
| (1..15) | inf | 1 / 1 / 1 / **0** | 1 / 1 / 1 / - | none |
| (1..15) | 251 | 20 / 13 / 17 / **9** / **2** | 1 / 1 / 1 / 0 / 0 | none |
| (1..13,15,28) | inf | killed at level 1 | - | none |
| (1..13,15,28) | 251 | 10 / 8 / 12 / 5 / 2 | 1 / 1 / 1 / 0 / 0 | none |
| (1..14) | 239 | 2 / 4 / 8 / 16 | 1 / 1 / 1 / 1 | none |
| (1..14) | inf | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 | none |
| (1..13) | 89 | 537 / 8,937 | 1 / 1 | at level 4 (> 3,000) |
| (1..11,13,24) | 89 | 942 / 22,220 | 1 / 1 | at level 4 (> 3,000) |
| (1..15) | 17 | 32,751 | 1 | at level 2 (> 3,000) |

### Grades

- **X2 (external check against Rosenfeld's 8-runner Lemma 6): HOLDS.** U_inf(8)
  is empty for s = (1..7), as his proof at p = 31 requires.
- **X3 (consistency with Lemma G2): HOLDS.** All 20 level-2 survivors of (1..15)
  for P = 251 are of type (A) (4 vectors) or (B) (16 vectors) of `THEORY_9.md`
  Lemma G2, and none satisfies the gcd clause; the single P = infinity survivor
  is the linear lift, of type (A). Checked by eye against the closed form.
- **S1 (sanity): HOLDS.** (1..14) has one linear survivor at every level for
  P = 239 and P = infinity; (1..13) has one at levels 2 and 4 (P = 89); for
  (1..15) and P = 251, levels 2, 4 and 8 each have one linear survivor and level
  16 has none (Lemma L).
- **P5 (primary): FALSIFIED.** U_251(16) for (1..15) is not empty: 9 unit
  classes, all nonlinear, and 2 still remain at level 32,
  (1..13, 0, 15) and (1..13, 16, 15) mod 32. The prime-free bound alone therefore
  cannot show that the orbit of (1..15) dies by level 16 at every prime >= 251.
  (P5 was a prediction about the upper bound U_251, not about any true cascade:
  J_p(16) can still be empty at every prime. `THEORY_15.md` and job
  `lrc16-uniform-v2` decide that prime by prime.)
- **P5b: HOLDS.** U_inf(16) is empty for (1..15): no lift of (1..15) is improper
  at level 16 at every prime at once. Every lift kept by U_251(16) has strict
  witness intervals; they are just shorter than 1/251.
- **P6: first part HOLDS, second part FALSIFIED.** (1..13,15,28) is killed at
  level 1 in U_inf (it is not tight), but U_251 keeps 5 classes at level 16 and
  2 at level 32: (1..13, 15, 0) and (1..13, 15, 16) mod 32.
- **M3 (measurement).** Level-2 survivors of (1..15): 20 of the 13,054
  near-grid-blocked candidates of Lemma G2 (0.15%) for P = 251; 1 for P = infinity.
- **Measurements.** (1..7) at P = 29 does not empty through level 16 (415 classes),
  in line with Rosenfeld's remark that p = 29 does not work at level 8 for k = 7.
  (1..15) at P = 17 has 32,751 level-2 survivors (cut). Run times 0.0-69.1 s per
  configuration.

### What it means

The level-32 survivors of both 15-speed orbits have the same shape: every
coordinate is linear except one, which is 0 mod 16. Their witnesses are those of
S' = {1..13, 15} at gap 1/16, coupled to the free coordinate (`THEORY_15.md` 15.6).
This points the next step at an exact per-prime answer, now in `thresh.py` and
job `lrc16-uniform-v2` (`PLAN_addendum9.md`).

## lrc16-pilot-v1 (engine 1 pilot, k = 15; Dell, finished 2026-11-22 22:13 UTC)

Unit tests passed (step 1 exit 0). All ten pilot gates (p = 251, 283, 307, 353,
401, 449, 503, 601, 701, 809) hit the 1,500 s cover-search cap
(`cover_timed_out` = 1); no tuple reached lifting (`tuples` = 0 everywhere).

- **P4a: UNTESTED at all 10 gates.** No gate is tested (cover search timed out).
- **R1/P1-P3 of the pilot:** nothing to grade (no complete gate).
- **Measurement.** Within 1,500 s, engine 1 found covers on 14 classes at
  p = 251 (53 orbits), 283 (2) and 353 (5), so tau_15(p) <= 14 there; at the other
  seven primes it found only 15-class covers. The `tau` field of a timed-out gate
  is the smallest cover size found so far, not a certified tau: at p = 251,
  `lrc16-tau-v2` had already found a 13-class cover. Combined with `lrc16-tau-v2`
  (no cover on <= 12 classes at 283 and 353), tau_15(283) and tau_15(353) are 13
  or 14.
- **Negative, confirmed with a second engine and a longer cap:** like engine 2 at
  800 s (`RESULTS_run14.md`), engine 1 at 1,500 s finishes no k = 15 cover search
  at primes 251 to 809. The cover search remains the bottleneck; engines 3 and 4
  (`lrc16-engine3-v1`, `lrc16-orbit-v1`, queued) target it.
