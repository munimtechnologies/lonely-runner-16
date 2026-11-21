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
3. **Bound for n = 15.** `bounds.py` gives the exact K_15 and A_15 and a numerical
   shape bound r_15. Before r_15 is used in a proof, the paper's Lemma 3.7
   reduction must be re-derived in writing for n = 15.
4. **Persistent orbits for k = 15.** Survivors at level 32, probably the orbit of
   (1..15) and tight Goddyn-Wong-type tuples, need an argument. Candidates are
   level 16 lifts plus the gcd clause, a shift lemma for d = 3, 5, 7, or
   Lemma 2.2(ii). This is written up before any gate is counted.
5. **Full gates.** Only after steps 1-4: run every gate prime, archive certificates,
   write an audit script, and ask a second, independent implementation to
   re-verify.

## Honesty rules

- No claim of a proof for 16 runners until steps 1-5 are complete and audited.
  Even then it is a computer-assisted special case of an open conjecture, not a
  resolution of it.
- Any discrepancy with the published 14- and 15-runner computation is reported
  first, and to its author, with Sheehan's approval.
- Negative outcomes, such as a cost too high or an argument that fails, are
  published as such.
