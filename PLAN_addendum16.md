# PLAN, addendum 16 (2026-11-24, run 28, before job lrc16-indep-v1 reports)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` and addenda 6-15, all unchanged and still in force.

Written 2026-11-24 at about 15:30 UTC. Job `lrc16-indep-v1` is queued and has
produced no output (no result folder exists). Addendum 15 recorded its gw15 data
"with no prediction"; `THEORY_19.md` (this run) now gives one.

## New prediction

- **I6 (Theorem 19):** for gw15 = (1, ..., 13, 15, 28), J_p(16) is empty at every
  prime p the job scans (all of them are >= 251). Equivalently, gw15 dies at level
  16 or earlier at every scanned prime (at level 1 for every p > 1344, by
  `THEORY.md` 7.3). A single scanned prime with an improper level-16 lift of gw15
  **refutes THEORY_19** (or its input): THEORY_19 is withdrawn in the README the
  same run and the cause is found.
- **Untested** at a prime where the job's stored list hit its cap (5,000) before
  level 16, as in addendum 15.

## Grading order

Unchanged from addendum 15: I0, I3, I5 first (a failure means a bug in `indep`,
nothing else is graded); then I1, I2 and I6. I6 is read from
`bases.gw15.death_levels` and `J32_nonempty_primes` / the per-level counts in
`summary_indep.json`.
