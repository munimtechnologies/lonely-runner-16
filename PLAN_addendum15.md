# PLAN, addendum 15 (2026-11-24, run 27, before job lrc16-indep-v1 runs)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` and addenda 6-14 (unchanged and still in force, except the
wording point of `REVIEW_18.md` R5d: T5 of addendum 14 tests THEORY_18's hand
argument, not the U_251 list).

Written 2026-11-24 at about 14:30 UTC. No output of `lrc16-indep-v1` exists.

## The job

`lrc16-indep-v1` runs `indep_job.py`: for s = e15 = (1..15) and s = gw15 =
(1..13, 15, 28), at every prime p from 251 upward (to 5,000 or a 330-minute cap),
it computes the cascade J_p(L), L = 1, 2, 4, ..., 32, **by brute force from the
definition** (`indep.py` docstring): every lift, every time b, no Lemma D, no arcs,
no unit reduction, no pruning, nothing imported from the rest of the repository.
It first runs `run_tests_indep.py` (C engine against the Python reference, plus the
hand-proved facts of `REVIEW_18.md` R6); if any test fails or the C tests skip, the
job stops. The U lists it compares with are fetched from the committed
`results/lrc16-uniform-v1/summary_uniform.json` at commit 162a7b9 and their SHA-256
is recorded (`fetch_indep.py`).

## Predictions (graded from `summary_indep.json`)

- **I0 (sanity, proved):** e15 is improper at level 1 at every scanned prime.
- **I5 (sanity, proved):** every J_p(L) list is closed under the units lambda (mod L),
  1 (mod p).
- **I3 (Lemma U(ii), proved by hand too):** for e15, the linear classes of U_inf(2),
  U_inf(4), U_inf(8) are in J_p(2), J_p(4), J_p(8) at every scanned prime.
  A failure of I0, I3 or I5 means a bug in `indep`; nothing else is graded until it
  is found.
- **I1 (Theorem 18):** for e15, J_p(16) is empty at every scanned prime. A single
  prime with an improper level-16 lift **refutes THEORY_18** (or its input): the
  article and README are withdrawn the same run and the cause is found.
- **I2 (Lemma U(i) and the `uniform.py` lists):** for e15 and gw15, every unit class
  of J_p(L) is in U_251(L), at every level L = 2..32 and every scanned prime. A
  failure means `uniform.py` over-kills (or Lemma U is wrong); THEORY_18 is withdrawn
  until re-derived from the brute-force lists, and every result that used U_251 is
  re-examined.
- **Untested** at a prime where the stored list hit its cap (5,000) before the level.

If I0, I3, I5, I1 and I2 all hold, Theorem 18's input (ii) is confirmed by an
independent brute force at every scanned prime, and THEORY_18 then rests only on
Lemma U(i) (proved by hand) for primes above the scanned range.

## Data for THEORY_19 (no prediction)

For gw15 the job records, per prime, whether the base is improper at level 1 (the
level-1 witness interval of `THEORY.md` 7.3 has length 1/1344, so it must be proper
at every prime above 1,344), the counts and unit classes at each level, and the
death level. These are the per-prime facts an every-prime argument for gw15
(`THEORY_19`, planned) has to match.
