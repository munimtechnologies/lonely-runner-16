# REVIEW 9: adversarial read of the grid-point witnesses (Lemma G, Lemma G2)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name;
not yet checked by a human expert. Text CC BY 4.0. Written 2026-11-24.

Scope: `THEORY_9.md` (Sections 9.1 to 9.4) against `grid.py` and `test_grid.py`
as committed with `THEORY_9.md`. The reviewer was told to break them: find a lift
that `grid_killed` kills although no component of any G_beta is longer than 1/P (an
unsound kill would put a wrong lift outside U_P and could hide a real
counterexample). Or find a vector that Lemma G2 misclassifies, or a step in a proof
that does not follow.

**Verdict: Lemma G (i) and (ii), Lemma G2 (closed form and both counts), the
Section 9.3 worked example and the sub-level fact of Section 9.4 are correct as
written. `grid.py` implements them faithfully. No error was found.** Three scope
remarks (R1-R3) belong in any write-up. They change no number in the repository.
`test_review9.py` re-derives Lemma G2 and the worked example by a second route that
imports nothing from this repository.

## 1. Lemma G (i): the one-sided reach from a grid point

- The good-side conditions are re-derived. Position a_i/N with s_i > 0. Moving
  right, the open strict range (B/N, (N-B)/N) is entered or kept for all small
  e > 0 iff B <= a_i < N - B. Moving left, iff B < a_i <= N - B. Correct, including
  the two boundary cases a_i = B (good to the right only) and a_i = N - B (good to
  the left only).
- Reach: coordinate i hits (N - B)/N at e = (N - B - a_i)/(N s_i). It cannot leave
  the strict range through B/N first, because it moves up. So dR is the min over i.
  N - B - a_i is a positive integer, which gives dR >= 1/(N max s). Correct.
  Mirror argument for dL.
- Good on both sides is equivalent to B < a_i < N - B for every i, i.e. x is strict,
  so the component is exactly (x - dL, x + dR). Good on one side only forces some
  a_i = B (or N - B): x is not strict, and the coordinate enters its bad arc on the
  other side, so x is an endpoint and the length is dR (or dL). Both sides bad: x is
  neither in a component nor an endpoint of one. All three cases match
  `component_at`.
- Soundness at any D (the property that matters most): `component_at` only ever
  returns the exact length of a real component. So `grid_killed(..., D, P)` can
  never kill a lift that the exact test keeps, for any grid D, coarse or fine.
  `test_grid.SmallGridIsSufficient` checks this on random cases. The proof above
  covers all cases.

## 2. Lemma G (ii): D = 2Q is exact

- Endpoints satisfy beta z_i/L + t s_i = j +- 1/(k+1), so t has denominator
  dividing lcm(L, k+1) s_i, which divides Q = lcm(L, k+1) lcm(s). Correct.
- A component is (a/Q, b/Q) with integers b >= a + 1 (it cannot be the whole circle
  minus finitely many points: each coordinate sweeps the circle, so its bad set in
  t has positive length). (2a+1)/(2Q) < (a+1)/Q <= b/Q, so the grid point is
  interior, hence strict. By (i) the length measured there is exact. A component
  that wraps past t = 0 is handled because c runs over all of Z_D. Correct.
- Code: `exact_D` returns 2 lcm(L, k+1) lcm(s), the same product as
  `uniform.qunit` (asserted in `test_grid.py`). With D = 2Q, N = lcm(L, D, k+1) = D.
  `grid_killed` uses `ln * P > 1`, i.e. length > 1/P, and with P = None any
  component kills. Strict ">" is the right direction for Lemma U: an open interval
  longer than 1/p contains a point of (1/p)Z, and one of length exactly 1/p may
  not. Lengths are positive whenever a side is good, so P = None behaves as stated.

## 3. Sections 9.2 and 9.3: the coarse grid and Lemma G2

- 9.2: for L | 16, k = 15, s = (1..15), D = 16: N = 16, B = 1, a_i = y_i, the bad
  values are {0, 15} (right) and {0, 1} (left), and dR, dL >= 1/240 > 1/251.
  Correct.
- beta = 0: c odd is blocked by i = -c^{-1} (y = 15) and i = c^{-1} (y = 1). c even
  is blocked by y_8 = 8c = 0. Correct.
- beta = 1, c odd. Even i other than 8 give y = 2 mod 4 or 4 mod 8, never 0 or +-1.
  y_8 = 8(z_8 + 1). For z_8 = 0 the right side needs c = -i^{-1} + 8 z_i. The
  inverses mod 16 (1, 11, 13, 7, 9, 3, 5, 15 for i = 1, 3, ..., 15) give the
  permutation 1->15, 3->5, 5->3, 7->9, 9->7, 11->13, 13->11, 15->1 stated in the
  proof. The pairing argument then forces z_1 = z_9, z_3 = z_11, z_5 = z_13 and
  z_7 = z_15. The left side, c = i^{-1} + 8 z_i, sends each pair {x, x+8} to
  coordinates x and x + 8 and gives the same four equalities. Correct.
- beta = 1, c even, z_8 = 1 (only y = 0 blocks):
  - c = 0 blocks iff some z_i = 0 (iii).
  - c = 8 blocks iff z_i = i mod 2 for some i (iv; i = 8 is excluded by z_8 = 1).
  - c = 4 and c = 12 block iff i = 2 z_i mod 4 for some even i (ii).
  - c = 2m with m odd blocks iff m i = 4 z_i mod 8, i.e. i = 4 mod 8 with z_i = 1 (i).
  
  All four are re-derived and correct.
- Counts: (A) 2^10 = 1,024. (B) 2^14 - 2^12 = 12,288 satisfy (i). Of these, 2^8 fail
  (ii), 1 fails (iii) and 1 fails (iv). The three failure sets are pairwise disjoint
  (the (ii) failures have z_2 = 0, the (iv) failure has z_2 = 1, and the all-ones
  vector has odd ones), which leaves 12,030. Correct.
- The worked example (all ones except z_2 = 0, beta = 1, t = 1/5) was recomputed by
  hand. Every distance is at least 1/10. dR = 1/320 is set by coordinate 12 (at
  9/10, moving at speed 12) and dL = 3/1040 by coordinate 13 (at 1/10). The total
  is 0.00601, above 1/251 = 0.00398. Correct.
- `test_grid.LemmaG2` builds its brute force from `grid.blocked_masks`, which shares
  `positions` with `component_at`. `test_review9.py` repeats the 2^15 scan from the
  reduced formula y_i = 8 beta z_i + c i (mod 16), with a closed form typed afresh
  from the text. This also checks the 9.2 reduction itself.

## 4. Section 9.4: any level

- Sub-levels: for L = L1 L2 with gcd(L1, L2) = 1, the times beta = L2 b of level L
  give exactly the positions b (z_i mod L1)/L1 + t s_i of level L1. Every kill of
  z mod L1 at L1 (gcd clause, t = 0 witness, long component) is therefore a kill of
  z at L. The gcd clause transfers because q | L1 divides L and z_i = z_i mod L1
  (mod q). Correct (`test_review9.Remarks.test_sublevel_transfer` checks the
  identities).
- The general-L Lemma U claimed here was later written out in full in
  `THEORY_16.md` and reviewed in `REVIEW_16.md` (correct). This review does not
  repeat that.

## 5. Scope remarks (for any write-up)

- **R1 (positive speeds).** Lemma G and `component_at` assume every s_i >= 1;
  `grid.py` does not assert it. Nothing in the project passes a non-positive speed
  (the vectors are (1..15), (1..13,15,28), (1..14), (1..13), (1..11,13,24)). A
  negative speed can be made positive by replacing (z_i, s_i) with (-z_i, -s_i),
  since ||-x|| = ||x||. A speed 0 would divide by zero and is excluded by the
  problem.
- **R2 (ties at the threshold).** Lengths dL + dR have denominators dividing
  N lcm(s) = 2Q lcm(s). So a component of length exactly 1/P is possible only when
  P divides 2Q lcm(s). For every vector above, every level used (powers of 2 up to
  128, 3, 5, 7, 14, 15, 16) and every prime P from 199 to 3,000, that never happens
  (`test_R2_no_ties_at_used_thresholds`). The choice between > and >= can therefore
  not change any reported U_P. `test_grid.py`'s thresholds never test a tie. The
  proof above covers it instead.
- **R3 (coarse grid only for L | 16).** The 1/240 guarantee of 9.2, "unblocked at
  D = 16 implies killed in U_251", needs N = 16, i.e. L | 16. At L = 32, N = 32 and
  the bound drops to 1/480 < 1/251. `grid_killed` with D = 16 stays sound there
  (Section 1), but it is no longer the shortcut 9.2 describes. Nothing in the
  repository uses the shortcut above level 16. If grid.py's coarse masks are ever
  used as a prefilter inside `uniform.lift_parent` (an idea parked in the plan),
  they must be used only to kill, with the exact length check, never to keep.

## 6. What this review does not cover

`uniform.py`'s cell machinery is checked here only through `test_grid.py`'s
agreement tests (small s, and (1..7) at levels 4 and 8). Its line-by-line review is
`REVIEW_15.md` (Lemma A; Lemma D is the CRT step checked there). The bounds and
gates of `THEORY.md` Sections 2-7 (Lemmas L, S, C, N) have still had no
adversarial review. They are next. Every section needs one, ideally by a human,
before any 16-runner claim.
