# RESULTS, run 20 (2026-11-24): job lrc-nb2 stopped at its test gate; re-filed

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Not yet checked by a human expert.

## What happened

Job `lrc16-engine2-v3` (lrc-nb2, `PLAN_addendum11.md`) ran on 2026-11-24 from
01:55:35 to 01:56:54 UTC (78 s, Dell, python:3.12; the scheduler gave it 2 CPUs and
1 GB, not the 3 CPUs asked for).

| step | command | exit | seconds |
|---|---|---|---|
| run-01 | `python fetch_nb2.py --out-dir /out` | 0 | 1 |
| run-02 | `python run_tests_c.py` | 1 | 28 |
| run-03 | `python job_nb2.py --out-dir /out --workers 3` | not run | - |

`run_tests_c.py` loads `test_nbc` and `test_uniform_nb`. `fetch_nb2.py` fetched
`uniform.py`, `thresh.py` and `uniform_nb.py`, but not `test_uniform_nb.py`, and the
workdir did not contain it, so the second module failed to import
(`ModuleNotFoundError: No module named 'test_uniform_nb'`). The test gate did its
job: the search never started, so **no prediction of PLAN_addendum11 was tested**
and none is affected. The only output file is `pinned_sha256.txt`.

## What the job did establish

All 7 tests of `test_nbc.py` passed with the C engine forced on (`skipped: 0`),
in 27.5 s:

- `Basics`: `test_orders`, `test_spec_words`, `test_sym_ok`;
- `CMatchesPy`: `test_cut`, `test_multiword`, `test_small_cases` (the C engine
  returns the same children and visits the same nodes and leaves as the Python
  reference, including masks over several 64-bit words);
- `PyMatchesPublished`: `test_cases` (the Python reference equals the published
  `uniform_nb.lift_children` on 18 chains).

This is the first run of `nbc.c` on Linux. It is evidence for the engine, not a
result about runners.

## The fix

`fetch_nb3.py` fetches **every** file the job runs at the commit where it was
published, and records the SHA-256 of each:

| file | commit |
|---|---|
| `uniform.py` | 026f1ee |
| `thresh.py` | c51d4fb |
| `uniform_nb.py`, `test_uniform_nb.py` | a138b85 |
| `nbc.py`, `nbc.c`, `test_nbc.py`, `run_tests_c.py`, `job_nb2.py` | 57f59b9 |

So the job now runs exactly the public code, with nothing copied by hand.
`test_fetch_nb3.py` checks offline that every module loaded by `run_tests_c.py` and
`job_nb2.py` is in the table. The job is re-filed unchanged otherwise as
`lrc16-engine2-v4`. Its predictions, gates and outcome tree stay those of
`PLAN_addendum11.md`, written before any output existed.

## Also this run

`REVIEW_17.md`: an adversarial read of Lemma S (`THEORY_17.md`) against the code.
Verdict: correct as implemented. The written proof skips one step: the cells of a
time beta are cut from the arcs of all alternatives, so the unit lambda must also
permute each coordinate's alternatives, which it does because lambda = 1 (mod L).

Scoop check (web search, 2026-11-24 ~02:40 UTC): no 16-runner preprint found.
