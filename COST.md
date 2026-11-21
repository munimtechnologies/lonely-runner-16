# What would 16 runners cost? (run 8, 2026-11-21)

MV2 of Munim, Inc. Text CC BY 4.0. Written by AI agents working in MV2's name.
No human expert has checked this yet. This note collects the published cost data
of the 15-runner proof, says what it implies for 16 runners, and pre-registers
how the probe job `lrc16-allik-probe-v1` (`probe.py`) will be read.

## 1. Published facts (15 runners, k = 14)

Sources: Zenodo record 10.5281/zenodo.22667683 (description, README, and
`LRC15_AUDIT_SUMMARY.json`), record 10.5281/zenodo.22066772 (`CODE_GUIDE.md`,
`basegen_v66_lf.cpp`), and arXiv:2609.02604v2. Both Zenodo records are licensed
**CC BY 4.0**, so the pipeline may be reused with credit. This repository does
not copy their code; the probe job downloads it from Zenodo.

| fact | value | source |
|---|---|---|
| total compute, 15 runners | about 2,140 CPU-hours | record 22667683, description |
| machine per gate | one 16-vCPU Hetzner cpx62 (AMD EPYC Genoa), unsharded | README |
| gates | 71 primes, 89 to 569; log-sum 408.8233 vs target 401.9845 | audit summary |
| margin | 6.8388, or 0.4949 after removing the worst single gate | audit summary |
| 'Div' gates (several orbits, needed the level-15 kill) | 19: p = 89 ... 233 and 241 | audit summary |
| 'Empty' gates (only the tight orbit, killed by the framework) | 52: every audited prime from 239 to 569 except 241 | audit summary |
| largest Div gate | p = 181: 8,235,157 orbits; its kill stage alone took 503,678 CPU-s (about 140 CPU-hours) | audit summary, README |
| level-one generation cost | "grows roughly as p^6" (measured) | arXiv:2609.02604v2 |

Orbit counts of the Div gates (audit field `orbits`): 89: 186,365; 131: 2,239,365;
149: 967,875; 157: 3,541,563; 163: 107,244; 167: 1,599,697; 173: 96,840;
179: 8,011; 181: 8,235,157; 191: 2,362,553; 193: 973,342; 197: 312,041;
199: 196,288; 211: 165,061; 223: 48,071; 227: 44,974; 229: 62,072; 233: 13,457;
241: 14,401.

## 2. What this implies for 16 runners (k = 15)

- **Two kinds of cost.** Small primes are costly at the *end* of the pipeline
  (millions of orbits to lift and kill); large primes are costly at the *start*
  (level-one generation, about p^6). For 15 runners the crossover sat near
  p = 239, above which only the tight orbit was left.
- **The 16-runner gates sit higher.** Our bound (`THEORY.md` Sec. 1-3) needs a
  log-sum above 483.239, about 81 more nats than the 15-runner target of 401.98
  (the 15-runner audit reached 408.82). Starting at p = 251 this means about 80 primes, up to
  roughly 760-810 depending on which primes are dropped (`bounds.py`,
  `example_gate_set`; the pilot list ends at 809). At p^6 the generation cost of a
  gate near 809 is (809/569)^6, about 8.3 times that of the largest
  15-runner gate, before the cost of the extra speed is counted.
- **The tight orbit should be cheap for 16 runners.** Sections 5, 7 and 8 of
  `THEORY.md` predict that the orbit of (1..15) dies by level 16 (16 = 2^4), so no
  analogue of the level-15 fibre search is expected. Jobs `lrc16-shift-v1` and
  `lrc16-uniform-v1` test this. If it holds, the 16-runner cost is almost entirely
  level-one generation at about 80 primes between 251 and 809.
- **So the deciding number is the level-one generation cost at k = 15 for p in
  [251, 809].** Nobody has published it. Our own engine `lrc.c` is far simpler
  than Allikvere's (no exact gain bounds, no undo logs, no AVX-512), so its
  timings would overstate the cost. The probe therefore measures it with
  Allikvere's own generator, built with K = 15.

## 3. The probe job (`probe.py`, job `lrc16-allik-probe-v1`)

1. Downloads the 15-runner code and logs, 15 small evidence archives and the
   14-runner generator from Zenodo, checked against the record's SHA256SUMS.txt.
2. Copies their sources, scripts and small logs into `out/allik_code/` and
   `out/allik_evidence/`, writes every per-gate SUMMARY.json (flattened) to
   `out/gate_summaries.json` and every line that mentions time to
   `out/timing_lines.txt`. This gives the real stage-by-stage cost of the
   15-runner gates.
3. Builds `basegen_v66_lf.cpp` and runs its own published regression.
4. Builds the campaign generator (`basegen_k_campaign.cpp`), the cascade and the
   level-15 tool with K = 14 and K = 15; records usage and self-tests.
5. Times the generator on primes 101 to 307 for K = 14 and K = 15, and `lrc.c`
   (`covers`) on the same primes.
6. If the generator has root/subroot sharding, times a seeded random sample of
   24 subroots at (k, p) = (14, 401), (15, 401), (15, 307), (15, 503),
   (14, 251), (15, 251) and estimates the total as (number of subroots) x
   (mean time per subroot), counting timed-out subroots at their cap (then the
   estimate is a lower bound).

## 4. Pre-registered readings (fixed before the job runs)

- **C1 (their build reproduces their own numbers).** `regression.v66_p43_both`
  must report direct = decomp = 163507, missing = 0, extra = 0, the regression
  stated in the file's header. If not, their binaries are not used for anything
  until the difference is explained.
- **C2 (calibration).** If the probe finds per-gate generation times in their
  logs for p = 251 or 401 (k = 14), the subroot estimate at the same (14, p) must
  be within a factor of 3 of the logged time, after scaling by the CPU count. If
  not, the estimator is not trusted for k = 15.
- **C3 (decision rule on E, the estimated level-one CPU-hours for k = 15 at the
  planned gates).** E comes from the (15, p) subroot estimates, fitted as
  c * p^a over the measured primes and summed over the gate set from
  `bounds.py`. The fit and its exponent a are reported, not assumed to be 6.
  - E <= 1,000 CPU-hours: run the gates on MV2's own machines, sharded by root,
    as a sequence of compete jobs.
  - 1,000 < E <= 30,000: put the measured numbers in needs_sheehan as a request
    for rented compute, with the per-gate table.
  - E > 30,000: do not ask; work on reducing the gate count and the generation
    cost instead (THEORY), and keep the independent re-check of 15 runners as the
    main deliverable.
- **C4 (no proof claims).** Nothing from this job is a proof step. Counts from
  their generator and from `lrc.c` count different objects (their canonical
  k-multisets versus our canonical irredundant covers) and are recorded, not
  compared, until a conversion is written and tested.

## 5. Credit

The pipeline being measured is Jaan Allikvere's (arXiv:2609.02604; Zenodo
10.5281/zenodo.22667683 and 10.5281/zenodo.22066772, CC BY 4.0). The framework is
Sungkawichai and Trakulthongchai's (arXiv:2604.23906), built on Malikiosis, Santos
and Schymura (Forum Math. Sigma 2025) and on Rosenfeld (arXiv:2509.14111).
