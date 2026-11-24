# PLAN, addendum 14 (2026-11-24, run 26, before any result of lrc16-uniform-v2)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` and addenda 6-13 (all unchanged and still in force).

Written on 2026-11-24 at about 12:30 UTC. `lrc16-uniform-v2` is still queued
(place about 30 of 247); no output of it exists. `THEORY_18.md` (written this run)
proves by hand, conditional on Lemma U and the `lrc16-uniform-v1` list of
U_251(16), that the tight orbit (1..15) has no improper lift at level 16 at any
prime p >= 251. That gives the queued job a new, sharper check. It is added here
before the job reports; nothing in addendum 9 is changed.

## Prediction T5 (new)

For e15 = (1..15), at **every** prime 251 <= p <= `scanned_to`, the exact cascade
J_p is empty at level 16 (death level <= 16 at every scanned prime; at level 16
the per-prime count of improper lifts is 0). Read from the per-prime records of
`summary_uniform2.json`.

- **Holds:** an independent computation (exact per-prime test, `thresh.py`)
  agrees with Theorem 18 at every scanned prime.
- **Falsified** by any scanned prime with an improper lift at level 16. That would
  mean `THEORY_18.md`, `thresh.py` or `uniform.py` is wrong; the prime and the
  lift are reported and Theorem 18 is withdrawn until the cause is found.
- **Untested** if the job is cut before it reaches the per-prime scan.

T5 implies T4 (all ten pilot primes have `J16` = 0) and, with the U_251 cascade
of addendum 9, implies T1 at every scanned prime.

## Check X6 (new)

`test_level16.py` (run by the publish gate) re-checks Theorem 18's windows in exact
arithmetic and the predicted witness of each of the 9 classes at every prime from
251 to 3,000, against the actual integer vectors. If the job's R1 re-run of
U_251(16) does not reproduce the same 9 classes, Theorem 18's input has changed
and it is withdrawn until re-derived.
