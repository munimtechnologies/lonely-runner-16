# Results, run 17 (2026-11-23): lrc16-shift-v2

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert. Every number below is read from the raw
outputs committed unchanged in `results/lrc16-shift-v2/` (`summary_orbits.json`,
`orbits.jsonl`, `summary_gates_shift.json`, `gates/*.json`, `pinned_sha256.txt`).
Rules: `PLAN.md` addenda 2, 4 and 5, all written before the job ran.

## The run

Dell, 2026-11-22 23:27-23:59 UTC (1,905 s; peak memory 0.06 GB; 2 CPUs).
Step 1 fetched `lrc.c`, `lrc_ref.py`, `test_shift.py`, `job_shift.py` and the other
helpers at commit c5cfb60 and recorded their SHA-256 (`pinned_sha256.txt`).
Step 2 ran 24 unit tests (`test_shift`, `test_c`), all passing, including
`test_shiftok_matches_reference`, whose failure stopped `lrc16-tau-v1` (a test
bug, fixed in run 11). Step 3 (`job_shift.py`) exited 0 with no errors, no overflow
and no cascade cut.

## Part A: does the tight orbit (1..15) die by level 16?

The probe lifts the tight speed vector s = (1..15) at each of the ten pilot primes
through binary levels 2, 4, ..., 64 (`bin64`), with the plain cascade
(`cascadebb`) and with the shift filter of Lemma S (`scascadebb`), and once more
through levels 2, 4, 8, 16, 48 (`l48`, shift filter on).

| prime p | kept at level 2 / 4 / 8 / 16 / 32 / 64 (plain) | same with shift filter | `l48` run | empty at level |
|---|---|---|---|---|
| 251 | 1 / 2 / 4 / **0** / 0 / 0 | identical | 1 / 2 / 4 / 0 / 0 | 16 |
| 283 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 307 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 353 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 401 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 449 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 503 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 601 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 701 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |
| 809 | 1 / 2 / 4 / **0** / 0 / 0 | identical | identical up to 16 | 16 |

`summary_orbits.json` → `one_to_15_bin64_plain`: primes 10, empty by 16: 10,
survives 64: 0, overflow or error: 0. The shift filter removed nothing at any
level or prime (`shift_removed_by_level` all 0).

The vector (1..13, 15, 28) of Goddyn-Wong type (`gw_15`) dies at level 2 at
p = 251, 503, 601, 701 and 809 (nothing kept at level 2) and at level 4 at
p = 283, 307, 353, 401 and 449 (one kept at level 2, none at level 4), in both modes.

### Grades

- **P1 (addendum 2, primary): HOLDS at all 10 pilot primes.** For s = (1..15) the
  plain binary cascade is empty at level 16 at p = 251, 283, 307, 353, 401, 449,
  503, 601, 701 and 809. No prime is untested (no overflow, no timeout).
- **P2 (addendum 2): HOLDS at all 10.** The cascade of (1..13, 15, 28) is empty by
  level 4 at every pilot prime, so in particular by level 16 wherever the vector is
  improper at level one.
- **X1 (addendum 5): HOLDS (nothing to violate).** U_251(16) has 9 classes and
  U_inf(16) is empty (`RESULTS_run16.md`), so X1 asks neither for a zero nor for a
  positive count at level 16, and no level-16 survivor is listed, so the
  membership clause is vacuous. A consistency reading that was not pre-registered
  is also clean: Lemma U puts U_inf(L) inside the true cascade, and U_inf(2), U_inf(4) and U_inf(8)
  each hold the linear lift, and the probe keeps at least one lift at levels 2, 4
  and 8 at every prime (1, 2, 4). At level 16 both are empty.
- **X5 (addendum 9): pending.** It compares this probe with `pilot[].J16` of
  `lrc16-uniform-v2`, which is still queued.

### What it means

This is the 16-runner analogue of Rosenfeld's check that (1..7) dies at level 8
for 8 runners (arXiv:2509.14111), and the opposite of what happens for 14 and 15
runners, where the tight vectors (1..13), (1..11, 13, 24) and (1..14) survive every
binary level and need separate fibre searches (arXiv:2609.02604). At the ten pilot
primes, the only tight orbit for 16 runners (`THEORY.md` Section 7) needs no fibre
search. Because k + 1 = 16 is a power of two, the binary grid reaches the tight witness
1/16 itself (Lemma L for linear lifts). Here every nonlinear lift dies by level 16
as well.

This covers ten primes, not all of them. Whether the same holds at every prime
p >= 251 is the question of `lrc16-uniform-v2` (`THEORY_15.md` 15.5,
`PLAN_addendum9.md` T1 and T2), which also gives the independent second reading
X5 at these ten primes.

## Part B: shift-filtered pilot gates (P4c)

All ten k = 15 gates hit the 600 s cover-search cap (`cover_timed_out` = 1); no
tuple reached lifting (`tuples` = 0).

- **P4c: UNTESTED at all 10 gates** (a timed-out gate does not count as tested, as
  addendum 4 requires). P4 is now untested through all three engines' readings (P4a in
  `RESULTS_run16.md`, P4b in `RESULTS_run14.md`, P4c here).
- **Measurements.** Covers on 14 classes were found at p = 251 (10 orbits) and
  p = 307 (2 orbits), so **tau_15(307) <= 14** (engine 1 had found only 15-class covers
  there in 1,500 s). At p = 701 no cover at all was found within 600 s
  (`tau` = 0 in the file means "none found", not a value). Search nodes in 600 s:
  271.3 M (251), 222.0 M (283), 206.6 M (307), 189.5 M (353), 154.9 M (401),
  143.8 M (449), 124.1 M (503), 100.5 M (601), 175.9 M (701), 145.1 M (809), that is,
  roughly 170,000 to 450,000 nodes per second per gate with four workers on two CPUs.
- Together with `RESULTS_run16.md`: tau_15(p) <= 14 at p = 251, 283, 307 and 353.
  At 251, `lrc16-tau-v2` found a 13-class cover.

## Status after run 17

- Tight orbit: dies by level 16 at the ten pilot primes (this file). All primes:
  `lrc16-uniform-v2`, queued.
- Cover search at k = 15: still the bottleneck (no gate finished with engine 1 at
  1,500 s, engine 2 at 800 s, or engine 2 with the shift filter at 600 s). Engines 3
  and 4 (`lrc16-engine3-v1`, `lrc16-orbit-v1`) and the cost probe of Allikvere's own
  generator (`lrc16-allik-probe-v1`) are queued.
