# REVIEW 13-14: adversarial read of the cover-search prunings (Lemmas F, P, M)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name;
not yet checked by a human expert. Text CC BY 4.0.

Scope: `THEORY_13.md` (Lemma F, Lemma P), `THEORY_14.md` (Lemma M), against `lrc.c`
as committed with `THEORY_14.md` (functions `run_covers`, `search`, `search_body`,
`forbid_classes`, `report`, `add_class`, `remove_class`), `test_prune.py` and
`test_orbit.py`. The reviewer's brief was to break them: find a cover that the engine
reports with `LRC_PRUNE=0` but misses with `LRC_PRUNE` = 1 to 7, or a tau answer
that changes.

**Verdict: the three lemmas are correct as written and as implemented. One process
finding: the C-side equality tests have never run.** Until job `lrc16-engine3-v1`
or `lrc16-orbit-v1` passes its first step on Linux, no job may use `LRC_PRUNE != 0`.
No current job does (`job_nb2.py` and `nbc.c` do not use `lrc.c`).

## 1. The threshold q_s (used by Lemma P(ii), Lemma M(iii) and the old cut)

`run_covers` sets QS = ceil((2n - s m)/s) with s = `maxsize`, once per search.

- Derivation, re-done: every class covers exactly m folded times (`setup` exits
  otherwise). For a cover S of size s, sum_v |cov(v)| = s m = sum_a c(a), where c(a)
  is the number of classes covering a. Times with c(a) = 1 are exactly the private
  times, and the others have c(a) >= 2, so s m >= P + 2(n - P), with P the total
  number of private times. Hence P >= 2n - s m, and the class with the most private
  times has at least P/s of them. Correct.
- Using s = maxsize for covers of size s' < maxsize is safe: (2n - s m)/s =
  2n/s - m decreases in s, so q_{s'} >= q_maxsize. The engine only ever uses a
  weaker threshold than the true one. This holds in tau mode too (maxsize = k - 2
  or 12 there, and the covers it looks for have at most maxsize classes).
- When 2n - s m <= 0 the engine sets QS = 0 and every QS-based rule is off
  (`T > 0` guard in `forbid_classes`). Correct.

## 2. Lemma F (bit 1)

- Proof (weak LP duality with y_a = 1/G(a)): checked; correct.
- Code: `gainv[v]` = |cov(v) ∩ U| for allowed v and 0 otherwise, computed in the same
  call just before use; G(a) is the max of `gainv` over `covlist[a]`, which lists the
  classes covering a by the symmetry "v covers a iff a covers v" (both say
  (k+1) d_p(av) < p; `test_symmetry_used_by_the_engine` checks it at (15, 101)).
  `b = MAXSIZE - nch` is the number of classes the completion may still add. The cut
  `need > b + 1e-9` is in the safe direction; at most n <= 1024 terms, each 1/g with
  g <= m, so the float error is far below 1e-9. `mg == 0` means no allowed class
  covers a; the cut is correct (it is also implied by the branching rule).
- The completion S \ C lies in the node's `allowed` set (after the bit-2/4
  removals, which only remove classes that no reportable cover through the node
  contains). So the bound is applied to the right family.

## 3. Lemma P (bit 2)

- (i): a class u that covers every private time of a chosen v makes v redundant in
  any S containing C and u, because Priv_S(v) ⊆ Priv_C(v) \ cov(u) = empty.
  Correct; the code intersects `who[a]` over the private times a of v (those with
  `cnt[a] == 1` among v's times) and removes the result from `allowed`.
- (ii) (norm = 1, also active with bit 4 alone): u is removed when
  |cov(u) ∩ Priv_C(1)| > pc[1] - T with T = QS. Then |Priv_S(1)| < QS, and S fails
  the cut `NORM && pc[1] < QS`, which `search()` applies at every node including the
  leaf, before `report()`. Correct.
- The variable `lim = pc[1] - T` is never negative: the node survived
  `pc[1] < QS`, and with bit 4 the node is already pruned when max L > pc[1].
- Removals are undone: `search()` saves `allowed` before `forbid_classes()` and
  restores it after `search_body()`; `search_body()` restores its own sibling
  exclusions first. Checked on both the normal path and the `timed_out`/`stopnow`
  break.

## 4. Lemma M (bit 4, norm = 1 only)

- Monotonicity of `allowed` along a path, needed for "locked times stay private":
  a child's `allowed` is the parent's (after its removals) minus the candidates
  tried so far, including the child's own class. So every class added below a node
  was in that node's `allowed`. Correct.
- (i) to (iii): checked. The cut in (ii) and the removal threshold in (iii) are
  strict, so a cover in which class 1 is only tied for the most private times is
  never cut; `report()` keeps the canonical member among the tied classes.
- L(v) is computed after the bit-2 removals at the same node. This is still sound:
  the removed classes are in no reportable cover through the node, so a reportable
  S \ C lies in the shrunken set and L(v) is still a lower bound for |Priv_S(v)|.
- tau mode (`STOPFIRST`): `report()` accepts any irredundant cover, but the cuts
  only remove orbit members in which class 1 is not the largest or has fewer than
  QS private times. For any cover of size <= maxsize, multiplying by the inverse of
  its largest class gives a member that survives every rule (Section 1 shows it has
  at least QS private times), and the branching is exhaustive over covers
  containing class 1. So "a cover on at most maxsize classes exists" gets the same
  answer. Correct.

## 5. The tests

- `test_prune.py` Part 1 and `test_orbit.py` (`LemmaMByBruteForce`, `PythonSearch`)
  are pure Python and ran in the publish test gate on Windows (commits f18317e and
  a4cf807 passed `test_first`). They check the right conditions: Lemma P(ii) is
  checked only against covers in which class 1 has at least q_s private times (the
  reportable ones), and Lemma M with the smallest possible allowed set S \ C,
  which is the strongest form, since L(v) and T can only grow as `allowed` shrinks.
- **Finding:** Part 2 of both files (the C engine: identical canonical covers,
  tau answers, tau certificates and gate JSON for every LRC_PRUNE value) is
  `skipUnless(CC)`. The Windows test gate has no C compiler, and no finished
  compete job has run either file. `lrc16-shift-v2` ran `test_shift test_c`,
  `lrc16-engine2-v2` ran `test_uniform_nb`, and `lrc-repro-k14-v1` ran an older
  `lrc.c`. So the claim "every output of `lrc.c` is the same for every LRC_PRUNE
  value" has a correct proof and passing Python tests, but **no machine check of the
  C code yet**. The first step of `lrc16-engine3-v1` (`python -m unittest -v
  test_prune test_c`) and of `lrc16-orbit-v1` (`python -m unittest -v test_orbit`)
  will run it. A skip there would look like a pass, so when grading those jobs,
  read stderr and confirm that `EngineThree` and `EngineFour` ran (not "skipped").

## 6. Rule for later runs

- `LRC_PRUNE=7` may be used in a gate job only after both C test classes have run
  and passed on Linux, and only for orbit-level outputs that are also re-derived
  with `LRC_PRUNE=0` at a sample of primes (PLAN_addendum7 A1/A2 and
  PLAN_addendum8 M1 already pre-register this comparison).
- Still unreviewed before any 16-runner claim: `THEORY.md` Sections 2-7 (bounds,
  gates, Lemmas L, S, C, N) and `THEORY_9.md` (`grid.py`, Lemma G).
