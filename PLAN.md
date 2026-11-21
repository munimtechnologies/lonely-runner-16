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
   (Note, run 5: there are no tight Goddyn-Wong-type tuples for 16 runners;
   see addendum 4 and `THEORY.md` Section 7.)
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

## Addendum 3 (2026-11-21, run 4, before any tau result): small covers

`THEORY.md` Section 6 adds the general completion (engine option `ext`) for primes
where a cover on at most k - 2 classes exists, and a `tau` mode that decides this.
Job `lrc16-tau-v1` (`job_tau.py`) runs two scans. No result of either exists as
this is written; none of the four earlier jobs has started.

**R1 (re-check of a published table).** For k = 14, our `tau` mode agrees with
Table 2 of arXiv:2609.02604 v2 at every one of its 71 primes: a cover on <= 12
classes exists at the 19 primes 89, 131, 149, 157, 163, 167, 173, 179, 181, 191,
193, 197, 199, 211, 223, 227, 229, 233, 241, and none exists at the 52 primes
from 239 to 569 other than 241. Reported as the number of primes that agree,
disagree and are untested (300 s cap per prime). Any disagreement is a
discrepancy with the published proof's bookkeeping, or a bug of ours; it is
investigated before any further use of the engine, and the cover found (or the
certificate) is kept so the paper's author can check it.

**P3 (16 runners).** **Every prime p from 400 to 1000 has tau_15(p) >= 14**, so the
old enumeration is complete there and the general completion is needed only below
400. Reason: an independence heuristic (each of n = (p-1)/2 times is missed by a
random class with probability about 7/8, and there are about (p/2)^12/13! unit
orbits of 13-class sets) puts the last 13-class covers near p = 435 for k = 15,
but the same heuristic for k = 14 puts the last 12-class covers near p = 380,
while the paper found none above 241. Scaling by that ratio (0.63) puts the k = 15
threshold near 275. P3 is **falsified** by any prime in [400, 1000] with
tau_15(p) <= 13 (the cover found is the evidence), and **untested** at primes
that hit the 400 s cap.

**Measurements (no prediction).** The exact tau_15(p) where it is <= 13; the
largest prime with tau_15(p) <= 13; the smallest P0 above which every scanned
prime has tau_15(p) >= 14; and the smallest set of primes with tau_15(p) >= 14
whose log-sum passes 483.239. Together with the pilot's cost per gate, these
fix the prime list for the full 16-runner computation.

## Addendum 4 (2026-11-21, run 5, before any k = 15 lifting result): no survivors

Written at about 16:45 UTC on 2026-11-21. All five jobs (`lrc-repro-k14-v1`,
`lrc16-pilot-v1`, `lrc16-engine2-v1`, `lrc16-shift-v1`, `lrc16-tau-v1`) are still
queued; no k = 15 result of any kind exists.

**Background (`THEORY.md` Section 7).** The published binary-lifting survivors for
14 and 15 runners are exactly the tight sets near [k]. By Zhang's classification
(arXiv:2608.13599, Thm 1.2) and Lemma N (n + 1 = 17 is prime), 16 runners has no
tight one-entry modification of [15], and Zhang's census finds no tight
two-entry modification with inserted speeds up to 128. The only known tight
15-speed set is (1..15), whose witnesses a/16 are on the grid from level 16 on.
Also, (1..13,15,28) is not tight (strict witness 993/2800).

**P4 (primary, new).** At every k = 15 pilot gate that is *tested*, binary lifting
through level 32 leaves **no surviving level-one tuple** (`survived` = 0), even
without the shift filter. Read separately in three places, each with its own
count of primes that hold / falsify / are untested:

- P4a: `lrc16-pilot-v1`, `summary_pilot.json` (engine 1, no shift, levels to 32);
- P4b: `lrc16-engine2-v1`, the k = 15 entries of `summary_engine2.json` "gates"
  (engine 2, no shift, levels to 32);
- P4c: `lrc16-shift-v1`, `summary_gates_shift.json` (engine 2, shift filter on,
  levels to 32).

A gate is **tested** when it has no error, `cover_timed_out` = 0, `overflow` = 0
and the cascade was not cut (`cascade_cut` = 0 in its `gates/*.json` file). It
**holds** if `survived` = 0 and is **falsified** if `survived` > 0. A gate that
is not tested but already shows `survived` > 0 also counts as falsified (a
survivor is a survivor). Gates flagged incomplete only because of small covers
(`small_orbits_unhandled` > 0) are still tested for P4: the prediction is about
the tuples that were lifted.

**P4d (secondary).** If any survivor appears, it is not in the orbit of (1..15):
its tuple is not a unit multiple of (1..15) mod p, folded. (This is what would
happen if a tight set unknown to us, or a non-tight residue class with no grid
witness, persists.)

**What each outcome means.**
- P4 holds at every tested gate: at the pilot primes, 16 runners needs no
  fibre search at all. The full computation is "only" the gates, and the cost
  is the cover enumeration and lifting time the pilot measures.
- P4 fails: the survivors are listed and checked against (1..15) (P4d). A
  survivor outside the orbit of (1..15) would point to a tight 15-speed set
  not in the literature, or to a gap in the heuristic of `THEORY.md` 7.1, and we
  would look at it closely: an unknown tight set for 16 runners would be a
  finding in its own right.
- Untested everywhere (cover searches time out at 1500 s or 600 s): the pilot
  costs are too high at these caps, and P4 waits for longer gate runs.

## Honesty rules

- No claim of a proof for 16 runners until steps 1-5 are complete and audited.
  Even then it is a computer-assisted special case of an open conjecture, not a
  resolution of it.
- Any discrepancy with the published 14- and 15-runner computation is reported
  first, and to its author, with Sheehan's approval.
- Negative outcomes, such as a cost too high or an argument that fails, are
  published as such.
