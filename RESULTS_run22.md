# RESULTS, run 22 (2026-11-24): grading job `lrc-repro-k14-v1`

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name;
not yet checked by a human expert. Text CC BY 4.0.

## What the job was

`lrc-repro-k14-v1` is step 1 of the original pre-registered plan (`PLAN.md`, fixed
2026-11-21). It runs the run-1 engine (`lrc.c` at commit time of `PLAN.md`; plain
canonical covers up to units, no Lemma 4.1 normalisation, no pruning) in `gate` mode
at ten gate primes of the published 14- and 15-runner proof (Allikvere,
arXiv:2609.02604): k = 14 at p = 569, 503, 449, 401, 353, 307, 271, 239 and k = 13
at p = 479, 401. Levels 2,2,2,2,2 (up to 32), cover-search cap 1,500 s per gate,
lift cap 10^6. It was filed on 2026-11-21, waited in the queue, and ran on the Dell
on 2026-11-23 from 18:57 to 20:13 UTC (4,569 s, peak memory 0.07 GB). Raw outputs
are copied unchanged to `results/lrc-repro-k14-v1/`.

The test gate passed: 17 of 17 tests (`test_bounds`, `test_ref`, `test_c`) on Linux
with a C compiler.

## Grade

**Step 1 of PLAN.md: UNTESTED.** The level-one cover search hit its 1,500 s cap at
all ten gates (`cover_timed_out = 1` everywhere), so the engine lifted no tuple
(`tuples = 0`, `killed = 0`, `survived = 0` at every gate). The question "does our
cascade leave only the persistent orbits the paper reports?" got no answer. This is
the same bottleneck that `lrc16-pilot-v1` and `lrc16-engine2-v1` had already shown
for 16 runners (`RESULTS_run14.md`, `RESULTS_run16.md`): the cover search, not the
lifting, is what our own engine cannot finish at gate-size primes.

**tau check: no contradiction with the paper.** When the search is cut, `tau` in the
gate output is the size of the smallest cover found so far. Every reported cover is
a real irredundant cover, so it is an **upper** bound on tau(p).

| k | p | smallest cover found (upper bound) | lower bound from `lrc16-tau-v2` | our value | paper (PLAN.md) |
|---|---|---|---|---|---|
| 14 | 239 | 13 | > 12 (search complete, "gt") | **tau = 13** | >= 13 |
| 14 | 271 | 13 | > 11 (12 unknown) | 12 or 13 | >= 13 |
| 14 | 307 | 13 | > 11 (12 unknown) | 12 or 13 | >= 13 |
| 14 | 353 | 14 | > 11 (12 unknown) | 12 to 14 | >= 13 |
| 14 | 401 | 14 | > 11 (12 unknown) | 12 to 14 | >= 13 |
| 14 | 449 | 14 | > 11 (12 unknown) | 12 to 14 | >= 13 |
| 14 | 503 | 14 | > 11 (12 unknown) | 12 to 14 | >= 13 |
| 14 | 569 | 14 | > 11 (12 unknown) | 12 to 14 | >= 13 |
| 13 | 401 | 13 | not run | <= 13 | (not stated in PLAN.md) |
| 13 | 479 | 13 | not run | <= 13 | (not stated in PLAN.md) |

Lower bounds are from `results/lrc16-tau-v2/tau_k14.jsonl` (rows for these primes:
`none_upto` 12 at p = 239, 11 elsewhere). So:

- At **p = 239, k = 14**, our two jobs together determine **tau_14(239) = 13**
  exactly, using our code alone: the tau job proved that no cover on at most 12
  classes exists, and this job found covers on 13 classes (20 canonical orbits of
  size 13 among the covers found before the cap). This matches the paper's
  "tau >= 13 on every prime from 239 to 569 except 241".
- Everywhere else our bounds are consistent with the paper and decide nothing new.
- The orbit counts in `summary_repro.json` (for example 168 orbits of size 13 and
  179,903 of size 14 at p = 271) are counts of covers found **before the cap**.
  They are not complete counts and must not be compared with the paper's tables.

## What follows

- Nothing to publish as a finding. The only exact number (tau_14(239) = 13) agrees
  with the paper, and the step it was meant to test did not run.
- The repro question is not lost. Job `lrc-nb2` (`lrc16-engine2-v4`) re-checks the
  persistent-orbit step of the 14- and 15-runner proofs by a different, prime-free
  route (`THEORY_16.md`, `THEORY_17.md`). The level-one cover search at these primes
  waits for the pruned engines (`lrc16-engine3-v1`, `lrc16-orbit-v1`; see
  `REVIEW_13_14.md`) or for Allikvere's own generator (`lrc16-allik-probe-v1`).
- We will not re-run this job with a longer cap. A 1,500 s cap is already far below
  what the paper spent per gate, and the old engine has no pruning.
