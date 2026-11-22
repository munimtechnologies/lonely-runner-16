# Sharding plan for the 16-runner gates (run 13, 2026-11-22)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
**No human expert has checked this yet.** This is a plan, not a result. It is
written now so that the gate jobs can be filed the moment `lrc16-allik-probe-v1`
reports, without improvising under time pressure. Nothing here is a proof step.

## 1. What is fixed by the public record (Allikvere, CC BY 4.0)

Sources: Zenodo 10.5281/zenodo.22667683 (README.md, 15 runners) and
10.5281/zenodo.22066772 (CODE_GUIDE.md, 14 runners).

- The 15-runner generator is `bgk14`, built from `basegen_k_campaign.cpp` and
  `bgk_incremental_gain.h` with
  `g++ -O3 -march=native -std=c++20 -DK=14 -DNW=8 -DMAXN=512 -DBGK_INCREMENTAL_GAIN -DBGK_DEFERRED_PROBES -DBGK_THRESHOLD_WITNESS`.
  The cascade `cascade_k14` (`cascade_filter_k.cpp`, `-std=c++17 -DK=14`) has a
  `--selftest`. The level-15 kill is `tight_lift_15` (`tight_lift_L.cpp`).
- K is a compile-time constant. For 16 runners we build with `-DK=15`.
  `MAXN=512` and `NW=8` (8 x 64 = 512 bits of folded times) cover
  n = (p-1)/2 <= 511, that is every planned gate p <= 809.
- The generator works on n = (p-1)/2 folded time classes. Class v covers time t
  when (K+1) dist_p(v t) < p, and a level-one row is a K-multiset of classes
  covering every time. It has two branches: an irredundant branch (K distinct
  classes) and a reducible branch (at most K-1 distinct classes), the second
  being complete only when tau(p) >= K-1 (the `km1low` precondition).
- The 14-runner generator documents its sharding modes: `irroots` and
  `irsubroots` list the two-class prefixes (r, s); `irsubrootrawc r s` runs one
  irredundant shard and writes only orbit-canonical rows; `12root r` runs one
  root of the reducible branch. The campaign generator's exact mode names
  (`km1root`, `km1all`, `km1low` and the irredundant ones) are read from
  `out/allik_code/` and the probe's `usage` output before any job is filed.
- Every 15-runner gate ran unsharded on one 16-vCPU machine. The shard merge
  script `gate_merge_k14.py` exists but was never used, so **our sharded runs
  are the first use of that path** and need their own check (Section 3, S2).

## 2. Job layout (to be filed only if the probe's C3 reading gives E <= 1,000 CPU-h)

- One job per (prime, block of subroots): `lrc16-g<p>-b<j>-v1`, memory_gb 1,
  cpu 2, timeout 180 minutes, no network in run steps after the pinned download.
  Blocks are sized from the probe's mean time per subroot so that each job is
  expected to take about 90 minutes, which leaves a factor-2 margin.
- Each job: fetch the pinned Zenodo zip by SHA-256, build `bgk15`, run the
  listed subroots with canonical output, and write
  `out/rows_<p>_<j>.hex`, `out/log_<p>_<j>.txt` with node and leaf counters,
  and `out/sha256.txt`.
- One merge job per prime: concatenate the shard rows, check that the union of
  shard indices equals the `irsubroots` list exactly, run the reducible branch
  (`km1all`, or `km1root` shards), run the cascade at levels 2, 4, 8, 16 and 32
  with `cascade_k15 --selftest` first, and report the persistent orbits.
- Gate order: from the smallest prime up (251, 257, 263, ...), because under a
  p^a cost the small gates are cheapest and they also test the prediction that
  only the orbit of (1, ..., 15) survives at large primes.

## 3. Pre-registered checks for the sharded path

- **S1 (shard completeness).** The subroot list a gate's shards cover equals
  `irsubroots` for that prime, with no index missing or repeated.
- **S2 (shard = unsharded).** At one small prime where an unsharded run fits in
  one job (chosen from the probe timings, at K = 15), the merged canonical rows
  of a sharded run equal the unsharded run's rows byte for byte after sorting.
  The same is checked at K = 14 against one archived 15-runner gate's rows
  (`evidence_<p>_s0.tgz`, `rows_ir/`), for the smallest Empty gate the probe
  can afford.
- **S3 (survivors).** At every gate p >= 251, the cascade leaves only the orbit
  of (1, ..., 15). Any other persistent orbit is reported, not hidden, and stops
  the gate list until it is understood.
- **S4 (no proof claim).** A closed gate is recorded as "J(15,p) empty, pending
  the level-16 kill and an independent audit". The 16-runner case is claimed
  only after every gate, an audit script, a second independent check of the
  bound (THEORY sections 2 and 5-12) and a human review, and only through
  Sheehan.

## 4. If E is larger

- 1,000 < E <= 30,000 CPU-h: no jobs. A per-gate table of measured costs goes to
  Sheehan as a request for rented compute.
- E > 30,000 CPU-h: no request. The main deliverable becomes the first
  independent re-check of the 15-runner proof (`lrc-repro-k14-v1` and its
  successors), and the work turns to cheaper level-one generation.
