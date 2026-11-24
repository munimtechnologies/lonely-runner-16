# REVIEW of THEORY_15 (Lemmas A, E, T, R) against thresh.py and job_uniform2.py

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Written 2026-11-24 (run 21), before any output of job `lrc16-uniform-v2` exists.
This is a second agent's attempt to **break** Section 15 and the code that applies
it. No human expert has checked it yet.

Files read: `THEORY_15.md`, `thresh.py`, `test_thresh.py`, `job_uniform2.py` and
`PLAN_addendum9.md` (commit c51d4fb), `uniform.py` (commit 026f1ee), and
`THEORY.md` Sections 5 and 8.

## Verdict

**Lemmas A, E, T and R are correct as written and as implemented.** The uniform
statement that `job_uniform2.py` prints (15.5) follows from them. One pre-registered
cross-check, **X5 of `PLAN_addendum9.md`, was worded too strongly**: a disagreement
is a bug in only one direction, unless X5 is read against the unfiltered lrc.c rows.
`PLAN_addendum12.md` fixes the reading before the job reports. No code change is
needed.

## Lemma A (cells are components)

The cut points of `uniform.Cells` are exactly the arc end points, and every arc has
positive length 2/((k+1)s_i) < 1. If the common end point E of two cells starts an
arc, the next cut point after E is at most that arc's end, so the cell to the right
of E is inside the arc; symmetrically for an arc that ends at E. So two adjacent
cells are never both uncovered, and every uncovered open cell is one whole component
of the strict-witness set. **Holds.** `Cells.mask` marks cell m covered while
`E2[m+1] <= start + length`, starting from the arc's own start point, which is a
cut point. This is the closed arc's cell set, wrapping correctly through the
doubled array `E2`.

## Lemma E (exact test at one prime)

- **CRT:** with 1 = A L + B p, b w_i/(Lp) = (bA mod p) s_i/p + (bB mod L) z_i/L
  (mod 1), since w_i = s_i (mod p) and w_i = z_i (mod L). It is a bijection
  Z_{Lp} -> Z_L x Z_p. **Holds** (this is `THEORY.md` Lemma D).
- **No grid point is an end point:** an arc end point t satisfies
  s_i t = m - beta z_i/L -/+ 1/(k+1), so its denominator divides
  s_i lcm(L, k+1), which divides Q. If j/p = x/Q with p not dividing j, then p
  divides jQ, so p divides Q. That is excluded. **Holds.**
- **Witness iff inside an uncovered cell:** a point that is not an end point is at
  distance exactly 1/(k+1) from no bad centre. So it is a witness (non-strict
  inequality) iff it lies in no closed arc, iff its open cell is uncovered. **Holds.**
- **t = 0 for beta != 0** may be an end point. It is handled separately by the
  exact bit (`exact_bad`: (k+1) min(x, L-x) < L means distance < 1/(k+1)).
  Equality counts as lonely, so it is correctly not bad. **Holds.**
- **The integer test in `proper_at`:** for a cell (a/Q, b/Q), the least j with
  j/p > a/Q is floor(ap/Q) + 1 in both cases (ap/Q an integer or not), and j/p
  lies in the cell iff jQ < bp. Cells that wrap past Q give j >= p. That is fine
  modulo 1. The only grid point that is 0 mod 1 is excluded: when the status is
  "open", every beta fails t = 0, so 0 lies in a closed bad arc and in no
  uncovered cell. **Holds.**

## Lemma T (kill threshold)

- An open interval longer than 1/p contains a point j/p, and by the remark above
  j is not 0 mod p. So z is proper at every admissible prime p > P*(z). **Holds.**
- p = P*(z) cannot occur: Q/(b - a) = p would make p divide Q.
- `killed_uniform` returns (b - a) P > Q for the longest cell, which is the
  `Cells.killed` run test because runs are single cells (Lemma A). This equality
  is tested (`test_matches_uniform`). **Holds.**
- **Monotonicity** (P*(child) <= P*(parent)): for a child z' of z at level 2L,
  beta = 2b gives positions 2b z'_i/(2L) = b z_i/L (mod 1), which are the parent's
  arcs at b. So the child's uncovered cells contain the parent's. P* is also
  invariant under z -> lambda z (beta -> beta lambda permutes Z_L). **Holds.**
  The job does not use this claim; it is stated for orientation only.

## Lemma R (the exact cascade inside the uniform one)

- **Parent property:** a witness b of the parent w' (level L/2) gives the witness
  2b of every lift w, because w - w' is a multiple of (L/2)p. The gcd clause of
  `THEORY.md` 5 is gcd(l, w_j : j != i) > 1. At L = 2^a with a >= 1 it reads
  "at most one coordinate is odd". That depends only on parities, which a lift
  keeps. At L = 1 there is no gcd clause. **Holds.**
- **Containment in U_P:** an improper lift at p >= P is not gcd-killed and not
  t0-killed. Since 1/P >= 1/p, a strict-witness interval longer than 1/P would be
  longer than 1/p and so contain a grid witness. So an improper lift is never
  P-killed. By induction on the level (parent property),
  every improper lift lies in the cascade U_P. **Holds.**
- **Fine cells in `lift_parent`:** the child's cells are cut at the end points of
  *both* alternatives of each coordinate, so an uncovered region can span several
  fine cells. `Cells.killed` merges runs (rotating so that no run wraps), and the
  internal prune tests only single big fine cells, which can only prune less. So
  the cascade still kills exactly by Lemma T's rule. The interior cut points of a
  run are not in any chosen arc: a chosen closed arc of positive length that
  contained such a point would cover a neighbouring fine cell. **Holds.**
- **Canonical forms:** the unit Lambda (lambda mod L, 1 mod p) maps lifts of s to
  lifts of s and permutes times. So properness, P-killing and P* are class
  invariants. Every child class of a non-canonical parent lambda z is lambda
  times a child of z, because odd units of Z_{2L} reduce onto the odd units of
  Z_L. **Holds.**

## job_uniform2.py

- **Statement logic** (15.5): L_uniform is the first level with finite
  P*_L <= `scanned_to`. Primes above `scanned_to` are above P*_L (Lemma T, strict).
  Primes from 251 to `scanned_to` are decided one by one. An empty J_p stays empty
  at higher levels (parent property, also checked as S6). The printed level
  max(L_uniform, max_death_level) is therefore right. The statement is refused
  when the U cascade was cut, when any scanned prime persists to level 128, or
  when the scan stopped below 3,000. **Correct.**
- **Admissibility:** every prime factor of Q and of the speeds is at most 13 for
  e15 and gw15 (28 = 4 * 7), so no prime >= 251 is skipped. The code also skips
  and reports any prime that divides Q or a speed. **Correct.**
- **Sanity checks:** S2 (improper above threshold), S4, S5 and S6 test exactly the
  lemmas above. **Correct.**
- **Deadline:** the U cascade gets min(30, minutes/3) = 15 minutes per orbit by
  default. U_251(32) has 2 classes, so levels 64 and 128 cost at most a few
  thousand 15-bit branch-and-bound leaves. This is not expected to bind.

## The one real finding: X5 must be read against the unfiltered rows

`PLAN_addendum9.md` X5 says that the (1..15) probe of `lrc16-shift-v2` keeps 0
lifts at level 16 "exactly when" `pilot[].J16` = 0, and that any disagreement is a
bug. `thresh.py` computes J_p with **only** the gcd clause (Lemma S of
`THEORY.md` 5 with e = 1). The `scascadebb` mode of `lrc.c` also drops lifts that
are *certified* by Lemma S with e > 1 and d | L (`THEORY.md` 5.3, Lemma C). So with
the filter on:

- J16 = 0 implies the filtered probe keeps 0 (it removes a superset);
- the filtered probe keeping 0 while J16 > 0 is **not** a bug if
  `shift_removed_by_level` is positive at some level <= 16.

The job already recorded both modes. `cascadebb` (no filter) is the exact
analogue of J_p, and for it "exactly when" is right. At all ten pilot primes,
`results/lrc16-shift-v2/orbits.jsonl` has `shift_removed_by_level` = 0 at every
level and identical `kept_by_level` in both modes ([2,1], [4,2], [8,4], [16,0]).
So the outcome of X5 cannot change, but the rule as written was wrong in one
direction. `PLAN_addendum12.md` fixes the reading (against `cascadebb`) before
`lrc16-uniform-v2` reports.

## Consistency already visible in existing outputs

Lemma U predicts U_inf(L) <= J_p(L) <= U_251(L) at every pilot prime. If `lrc.c`
counts classes up to odd units, as `thresh.py` does, the published sizes agree:
U_inf = 1, 1, 1, 0 (`RESULTS_run16.md`) <= lrc.c's J_p = 1, 2, 4, 0
(`RESULTS_run17.md`) <= U_251 = 20, 13, 17, 9 at levels 2, 4, 8, 16. This is
consistent, not a proof: the counting convention of `lrc.c` has not been checked
against `canon`. `PLAN_addendum12.md` records it as measurement M1, not as a check.

## Test coverage (gaps, none blocking)

`test_thresh.py` checks `proper_at` against a brute force over all of Z_{Lp}, with
k = 3 and 4, L <= 8 and primes up to 13, and `prime_levels` against a brute-force
cascade. The k = 15 run uses the same code paths with larger integers (Q =
lcm(128, 16) * 360360 for e15). Python integers are exact, so size alone is no
risk. Not covered by any test: a cell that wraps past Q being the one that
contains the grid point. The wrap logic is shared with `Cells.killed`, which
`uniform.py`'s own tests cover.
