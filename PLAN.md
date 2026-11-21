# Pre-registered plan (fixed 2026-11-21, before any result)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.

## Question

Can the finite-checking method that proved the Lonely Runner Conjecture for 14 and
15 runners (Allikvere, arXiv:2609.02604) be carried to **16 runners** (LRC(15)) at a
cost an open project can afford? And does an independent reimplementation agree
with the published 14- and 15-runner computation?

## The "wow" if it works

The first proof of the Lonely Runner Conjecture for 16 runners: a new case of a
problem open since 1967, which Quanta covered in March 2026. Until then, an
independent check of the 15-runner proof, which its author says has not been
independently reimplemented.

## Steps and what counts as each result

1. **Repro (k = 13, 14).** `job.py repro`. Success means our level-one enumeration
   plus binary cascade leaves only the persistent orbits the paper reports:
   (1..14) for k = 14, and (1..13) and (1..11,13,24) for k = 13, at every prime
   tested. Any other surviving orbit, or a tau(p) contradicting the paper's
   blocks (tau >= 13 for k = 14 at every prime from 239 to 569 except 241), is a
   discrepancy. We would report it and investigate it before anything else.
2. **Pilot (k = 15).** `job.py pilot`. This measures tau(p), level-one orbit counts,
   cascade survivors and run time at ten primes from 251 to 809. It decides
   which primes can be gates, and the total cost.
3. **Bound for n = 15.** Done on paper 2026-11-21 (run 2): `THEORY.md` re-derives
   the paper's Lemma 3.7 for n = 15 and gets R_15 < 49/100, a product bound of
   496.727 and a required gate log-sum of 483.239. It still needs an independent
   check (second reader or formalisation) before a proof relies on it.
4. **Persistent orbits for k = 15.** Survivors at level 32, probably the orbit of
   (1..15) and tight Goddyn-Wong-type tuples, need an argument. Candidates are
   level 16 lifts plus the gcd clause, a shift lemma for d = 3, 5, 7, or
   Lemma 2.2(ii). This is written up before any gate is counted.
5. **Full gates.** Only after steps 1-4: run every gate prime, archive certificates,
   write an audit script, and ask a second, independent implementation to
   re-verify.

## Addendum (2026-11-21, run 2, before any result): engine 2

`job.py engine2` (job `lrc16-engine2-v1`) first runs 12 small gates (k = 8 to 14,
p = 61 to 241) with both engines. **Agreement** means: on every gate where both
finish, identical tau, orbit counts by size, number of tuples, killed, survived,
overflow, completeness, per-level maximum and total improper counts, and the
same survivor set. Any disagreement is a bug in at least one engine; it is
reported, and no gate result from either engine is used until it is explained.
It then reruns the repro and pilot gates with engine 2. Its results on gates
that `lrc-repro-k14-v1` and `lrc16-pilot-v1` also finish must match theirs in the
same way; the same rule applies.

## Addendum 2 (2026-11-21, run 3, before any k = 15 lifting result): step 4

Tools written up in `THEORY.md` Section 5: Lemma L (linear lifts of a tight vector
die once its witness denominator divides the level), Lemma S (shift lemma for
composite d) and Lemma C (the cascade may drop what Lemma S certifies).
Job `lrc16-shift-v1` (`job_shift.py`) tests them.

**Primary prediction (P1).** For the tight vector (1,...,15), the plain binary
cascade (engine 2 lifting, no shift filter) is **empty at level 16 at all ten
pilot primes** (251, 283, 307, 353, 401, 449, 503, 601, 701, 809).
Reason: Lemma L kills every linear lift at level 16, and for 14 runners the paper
found that every witness-free lift at the natural level 14 was a multiple of 7
(that is, linear with a non-unit multiplier). P1 is **falsified** at a prime if
the level-16 kept count is positive there; it is **untested** at a prime where the
probe overflows or times out. We report the number of primes in each class.

**Secondary (P2).** The same for (1,...,13,15,28) at every prime where it is
level-1 improper.

**What each outcome means.**
- P1 holds everywhere: 16 runners has no persistent tight orbit of the kind that
  needed separate fibre searches for 14 and 15 runners. The remaining work is
  the gates themselves (and any primes with small tau).
- P1 fails somewhere: the surviving nonlinear lifts are listed. If the shift
  filter (Lemma C) removes them by level 32 or 64, the filter is the argument; if
  not, a new argument is needed, and we say so.

**Part B** of the same job runs the ten pilot gates for k = 15 with engine 2 and the
shift filter. No prediction is made; it measures how many level-one tuples are
left after the filter, which decides the cost of the full 16-runner computation.
A gate result counts toward a proof only after the engine cross-check
(`lrc16-engine2-v1`) agrees and the repro matches the paper.

## Honesty rules

- No claim of a proof for 16 runners until steps 1-5 are complete and audited.
  Even then it is a computer-assisted special case of an open conjecture, not a
  resolution of it.
- Any discrepancy with the published 14- and 15-runner computation is reported
  first, and to its author, with Sheehan's approval.
- Negative outcomes, such as a cost too high or an argument that fails, are
  published as such.
