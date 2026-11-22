# PLAN addendum 8 (2026-11-22, run 15, before any engine-4 result)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.

Job `lrc16-orbit-v1` (`job_orbit.py`) runs engine 4 (`lrc.c` with LRC_PRUNE = 7,
`THEORY_14.md`). No result of engine 3 or engine 4 exists as this is written:
neither has been compiled (this run has no shell; the job compiles them). Job
`lrc16-engine3-v1` (`PLAN_addendum7.md`) is still waiting for memory and is graded
on its own terms. The unit tests (`test_orbit.py`) run first; if any fails,
nothing below is graded.

## Readings and what counts

**M1 (same answers, decisive).** On the 8 gates of Part X (k = 8 to 11, p = 61
to 163), wherever the cover search and cascade finish with both LRC_PRUNE = 0 and
7: identical tau, orbit counts by size, tuples, killed, survived, overflow,
completeness and per-level improper counts. On the 24 rows of Part T (the rows
that `lrc16-tau-v2` decided in 3.5 s or more): wherever LRC_PRUNE = 7 decides, the
same answer as tau-v2, and every certificate passes the independent Python
check. Any disagreement voids engine 4 until it is explained.

**M2 (prediction: work).** Among the Part T rows decided by both LRC_PRUNE = 3
and 7, at least 20 have nodes(7) <= nodes(3). Not guaranteed by the lemma: bit 4
changes the allowed sets and so the branching order, and rows answered "a cover
exists" stop at the first cover found. Untested if fewer than 20 rows are decided
by both.

**S2 (prediction: speed).** The median over Part T rows of
seconds(LRC_PRUNE = 3) / seconds(LRC_PRUNE = 7), same machine, 300 s cap (a run
that hits the cap counts as 300 s), is **at least 1.5**. Falsified if below.
Reason for the guess: in a cover of 13 classes several classes typically keep
q_s or more private times, so each orbit is approached through several members;
we have no measurement.

## What each outcome means

- M1 holds and S2 holds: engine 4 (LRC_PRUNE = 7) is used for every later cover
  search (the P3 and R1 tau scans and the 16-runner pilot gates).
- M1 holds and S2 fails: bit 4 stays off by default; the cover search needs a
  different idea (THEORY_13 Sec. 13.6 and the playbook's list).
- M1 fails: the bug is found and reported before any engine-4 number is used.
