# THEORY, Section 9: grid-point witnesses (run 7)

MV2 of Munim, Inc. Text CC BY 4.0. Written 2026-11-21 by AI agents working in
MV2's name. **No human expert has checked this yet.** It continues `THEORY.md`
(Sections 1-8) and uses its notation: k speeds, a level-one vector s, a level L,
a lift z (values mod L), times beta in Z_L and t real, positions
beta z_i / L + t s_i (mod 1), G_beta(z) the open set of strict witnesses, and the
prime-free cascades U_inf and U_P of Lemma U (Section 8.2). Checked by
`test_grid.py`; implemented in `grid.py`.

Section 8 decides "is some component of G_beta longer than 1/P?" by cutting the
circle at every arc endpoint (`uniform.py`). This section gives a second way to
answer the same question: look only at grid points c/D and measure, from each,
how far the strict witnesses reach. With a fine grid it is exact. With a coarse
grid it is a fast sufficient test, and at level 2 for s = (1..15) it can be
solved by hand (Lemma G2), which gives a check of the uniform job's output that
can be read off by eye.

## 9.1 Lemma G

Fix beta and a grid point x = c/D. Put N = lcm(L, D, k+1), B = N/(k+1) and

  a_i = beta z_i (N/L) + c s_i (N/D)  (mod N),

so the position of coordinate i at time x is a_i/N. Coordinate i is at distance
> 1/(k+1) for all small t - x > 0 iff B <= a_i < N - B ("good to the right"),
and for all small x - t > 0 iff B < a_i <= N - B ("good to the left").

**Lemma G.** (i) If every coordinate is good to the right of x, then the open
interval (x, x + dR) with dR = min_i (N - B - a_i)/(N s_i) lies in G_beta, and
dR >= 1/(N max s). Symmetrically to the left with dL = min_i (a_i - B)/(N s_i).
The component of G_beta that contains x (if x is strict, i.e. good on both
sides) has length exactly dL + dR; if x is good on one side only, x is an
endpoint of a component whose length is exactly dR (or dL).
(ii) Let Q = lcm(L, k+1) lcm(s) (`uniform.qunit`). Every component of every
G_beta(z) contains a strict point of (1/(2Q))Z. So "some grid point c/(2Q) gives
a component longer than 1/P" holds iff z is killed by condition (c) of Lemma U,
for every P (P = infinity: any component).

*Proof.* (i) Moving right by e, position i goes from a_i/N, which lies in
[1/(k+1), 1 - 1/(k+1)), up to a_i/N + e s_i. For 0 < e < (N - B - a_i)/(N s_i)
it stays strictly inside (1/(k+1), 1 - 1/(k+1)), so the distance to the nearest
integer is > 1/(k+1); at e = (N - B - a_i)/(N s_i) it reaches 1 - 1/(k+1), the
edge of the bad arc. So the strict witnesses to the right of x end exactly at
x + dR. N - B - a_i is a positive integer, so dR >= 1/(N max s). The left side is
the mirror image. If x is good on one side only, some coordinate sits exactly at
distance 1/(k+1) at x and enters its bad arc on the other side, so x is an
endpoint. (ii) The endpoints of the components of G_beta are points where some
coordinate is at distance exactly 1/(k+1): t = (j +- 1/(k+1) - beta z_i/L)/s_i,
whose denominators divide lcm(k+1, L) s_i, which divides Q. So a component is
(a/Q, b/Q) with b > a (or the whole circle minus such points, which cannot
happen because every bad arc has positive length), and the grid point
(2a+1)/(2Q) lies strictly inside it, so it is strict. By (i) the length computed there is the component's exact
length. []

`grid.grid_killed(s, k, z, L, D, P)` applies the gcd clause, the exact witness at
t = 0, and Lemma G at every grid point; `grid.exact_D` returns D = 2Q.
**`test_grid.py` checks that grid_killed with D = 2Q equals
`uniform.uniform_killed` exactly**: for every lift of (1,2,3) at levels 1, 2, 4 and
six thresholds P, for 40 random small cases (levels up to 8), and for lifts of
(1..7) at levels 4 and 8. The two implementations share no code (one cuts the
circle into cells and merges runs of uncovered cells, the other measures from
grid points), so this is a check of the machinery behind job `lrc16-uniform-v1`.

## 9.2 The coarse grid D = k + 1

With D = k + 1 = 16, L | 16 and s = (1..15), N = 16 and B = 1, so a grid point is
good to the right iff no a_i is 0 or 15 (mod 16), and then dR >= 1/(16 * 15) =
1/240. So, **for every P > 240** (in particular P = 251): a lift z is killed in
U_P if some beta in Z_L and c in Z_16 make

  y_i = beta z_i (16/L) + c i  (mod 16)

avoid {0, 15} for every i (or avoid {0, 1}: the left side). In other words: a
survivor in U_251(L) must be **blocked** at every one of the 2 * 16 * L near-grid
tests (some coordinate lands on 0 or -1, resp. 0 or +1). This is a purely
combinatorial condition on z.

## 9.3 Lemma G2: the blocked level-2 lifts of (1..15)

At level 2, z is a 0/1 vector. Beta = 0 gives y = c s, which is always blocked
(for c odd, i = -c^{-1} gives y_i = -1 and i = c^{-1} gives y_i = +1; for c even,
y_8 = 8c = 0). For beta = 1, y_i = 8 z_i + c i (mod 16).

**Lemma G2.** For s = (1..15) at level 2, z is blocked at every near-grid test
with D = 16 iff

- **(A)** z_8 = 0 and z_1 = z_9, z_3 = z_11, z_5 = z_13, z_7 = z_15; or
- **(B)** z_8 = 1 and all of:
  (i) z_4 = 1 or z_12 = 1;
  (ii) some of z_2, z_6, z_10, z_14 is 1, or some of z_4, z_12 is 0;
  (iii) some z_i is 0;
  (iv) some odd i has z_i = 1, or some even i other than 8 has z_i = 0.

There are exactly 1,024 vectors of type (A) and 12,030 of type (B).

*Proof.* Take beta = 1.
*c odd.* For odd i, y_i is odd, so only y_i = -1 (right side) or +1 (left side)
can block; for even i other than 8, c i is 2 mod 4 or 4 mod 8, so y_i is never
0 or +-1; and y_8 = 8(z_8 + 1) is 0 iff z_8 = 1. So if z_8 = 1 every odd c is
blocked. If z_8 = 0, odd i blocks (right side) exactly the c with
c = -i^{-1} + 8 z_i (mod 16) (using 8 z_i i^{-1} = 8 z_i for odd i). The map
i -> -i^{-1} permutes the odd residues: 1->15, 3->5, 5->3, 7->9, 9->7, 11->13,
13->11, 15->1. Adding 8 z_i moves a value inside its pair {x, x+8}. Eight odd
coordinates must block eight odd c, so the values must be distinct, which happens
iff the two coordinates landing in each pair are shifted alike: pair {1,9} gets
i = 15 and 7, {3,11} gets 5 and 13, {5,13} gets 3 and 11, {7,15} gets 9 and 1.
That is z_7 = z_15, z_5 = z_13, z_3 = z_11, z_1 = z_9. The left side
(c = i^{-1} + 8 z_i) gives the same four pairs.
*c even.* y_i is even, so only y_i = 0 blocks, on both sides. If z_8 = 0, y_8 = 8c
= 0 blocks every even c. If z_8 = 1: c = 0 is blocked iff some z_i = 0 (iii);
c = 8 iff some i has z_i = i (mod 2) (iv); c = 4, 12 iff some even i has
i = 2 z_i (mod 4), i.e. z_i = 1 for i = 2 mod 4 or z_i = 0 for i in {4, 12} (ii)
(i = 8 would need z_8 = 0); c = 2, 6, 10, 14 iff some i has 8 z_i + c i = 0,
which forces i = 2j with j = 2 z_i (mod 4), i.e. i in {4, 12} with z_i = 1 (i).
*Counting.* (A): 14 free coordinates, 4 equalities, 2^10. (B): 2^14 - 2^12 =
12,288 satisfy (i); of these, 256 fail (ii) (z_2 = z_6 = z_10 = z_14 = 0,
z_4 = z_12 = 1, odd coordinates free), one fails (iii) (all ones) and one fails
(iv) (odd coordinates 0, even ones 1); no vector fails two of them. []

`test_grid.LemmaG2` checks the closed form and both counts against a brute-force
scan of all 2^15 vectors, and checks on random unblocked vectors that the
component found is at least 1/240 long, so they are killed in U_251.

**Consequences.**
- U_P(2) for s = (1..15) and P > 240 is contained in (A) union (B), minus the
  gcd clause. The linear lift (1..15) mod 2 is of type (A), as Section 8.5
  requires. This gives a check that can be done by eye: **every level-2 survivor
  that `lrc16-uniform-v1` lists for (1..15) with P = 251 or P = infinity must be
  of type (A) or (B)** (PLAN addendum 6, X3).
- The near-grid tests alone leave 13,054 candidates at level 2. Interior
  witnesses must do the rest. Example: z = all ones except z_2 = 0 is of type (B),
  but t = 1/5 is a strict witness (every distance is 1/10 or more), inside a
  component of length 1/320 + 3/1040 > 1/251. How many survive both is exactly
  what the uniform job measures. If more than 3,000 survive at level 2, that run
  stops (`cut`) and P5 is untested, not failed (`job_uniform.py`, max_parents).

## 9.4 Lemma U at any level

Nothing in Lemmas D and U (Section 8) needs L to be a power of 2. For any level L
coprime to p, with the gcd clause read as "some prime q | L divides every z_i but
at most one" and the units of Z_L in place of the odd residues, the same proofs
give U_inf(L) <= J_p(L) <= U_P(L) for every prime p >= P, p > max s, p not dividing
Q = lcm(L, k+1) lcm(s). Two more facts make non-binary levels usable:

- **Sub-levels.** If L = L1 L2 with gcd(L1, L2) = 1 and z is not P-killed at
  level L, then z mod L1 is not P-killed at level L1. (The times beta = L2 b of
  level L give the positions b z_i / L1 + t s_i of level L1; the gcd clause at L1
  implies it at L.) So U_P(L) is inside the CRT merge of U_P(L1) and U_P(L2),
  which is how Allikvere's level-15 search merges levels 3 and 5.
- **`grid.py` already handles any L** (its gcd clause uses the prime factors of
  L), so it can serve as the reference implementation for a non-binary uniform
  cascade.

This is the route to a prime-free version of the level-14 and level-15 fibre
searches in the 14- and 15-runner proofs (arXiv:2609.02604, Sec. 4), which that
paper states only for the primes it ran ("it is not an assertion about all
primes"). It is planned, not computed.
