# THEORY, Section 19: the orbit (1..13, 15, 28) dies at level 16 at every prime p >= 251

MV2 of Munim, Inc. Made with AI agents working in MV2's name; text CC BY 4.0.
Written 2026-11-24 (run 28). **No human expert has checked this yet.** Every
window and every inequality below is checked in exact rational arithmetic by
`test_level16_gw.py` (standard library only, imports no repository code). That test
also finds every maximal good window by an exact sweep, checks each lift against
the actual integer vectors at every prime from 251 to 1,500, and runs a plain
brute-force search over all times at the first five primes.

## 19.0 What this section does

`THEORY_18.md` settled, for every prime p >= 251, the level-16 classes that the
prime-free cascade U_251 keeps for the tight orbit s = (1, ..., 15). The same job
(`lrc16-uniform-v1`) keeps **5** level-16 classes for the second orbit that a
16-runner computation has to lift, gw15 = (1, ..., 13, 15, 28) (the 16-runner
analogue of the 14-runner survivor (1..11, 13, 24); `THEORY.md` 7.3).
THEORY_18 18.6 left them open. Here they are settled by the same "odd-time union"
idea, and the one class that is not of the "i or i + 8" shape is settled by a
parity step that is shorter than the one of THEORY_18 18.3 (step 2 instead of 4).

**Theorem 19.** Let p >= 251 be prime. Then no lift of the orbit of
(1, ..., 13, 15, 28) to level 16 is improper at p: J_p(16) is empty for this orbit.

Conditional, exactly as Theorem 18, on (i) Lemma U (`THEORY.md` 8.2) and (ii) the
list U_251(16) for gw15 computed by `uniform.py` in job `lrc16-uniform-v1` (raw
output `results/lrc16-uniform-v1/summary_uniform.json`, base "gw15", P = 251).
Input (ii) is re-tested from scratch by the queued brute-force job
`lrc16-indep-v1` (prediction I2 of `PLAN_addendum15.md`), and Theorem 19 itself
becomes prediction I6 of `PLAN_addendum16.md`, written before that job reports.

Remark. By `THEORY.md` 7.3, gw15 has a strict level-1 witness interval of length
1/1344, so for p > 1344 the orbit is already proper at level 1 and the statement is
empty there. The content of Theorem 19 is therefore the primes from 251 to
1,327, settled here by one argument instead of one search per prime. **It is not a proof of
any case of the Lonely Runner Conjecture.**

## 19.1 The five classes

Speeds s = (1, 2, ..., 13, 15, 28); s mod 16 = (1, ..., 13, 15, 12). A level-16
lift is w in (Z_{16p})^15 with w_j = s_j (mod p); z = w mod 16. Proper means the gcd
clause holds or some b has ||b w_j / (16p)|| >= 1/16 for every j (non-strict, as in
arXiv:2609.02604). Units lambda (mod 16) odd, 1 (mod p) preserve properness.

| class | z (mod 16), in the order of s | D = { s : z = s + 8 (mod 16) } |
|---|---|---|
| g1 | (1,2,3,4,5,6,7,8,9,10,11,12,13,15,**0**) | none; z for speed 28 is 0 = 12 + 4 |
| g2 | (1,2,3,4,5,14,15,0,1,2,3,4,5,7,12) | {6, 7, 8, 9, 10, 11, 12, 13, 15} |
| g3 | (1,2,3,4,13,14,15,0,1,2,3,4,5,15,12) | {5, 6, 7, 8, 9, 10, 11, 12, 13} |
| g4 | (1,2,11,4,5,14,7,0,9,2,11,4,13,7,12) | {3, 6, 8, 10, 12, 15} |
| g5 | (1,2,11,4,13,14,7,0,9,2,11,4,13,15,12) | {3, 5, 6, 8, 10, 12} |

(copied from the job output; the test compares them with the committed file when it
is present). In g2-g5 the speed 28 keeps its linear residue 12, every D contains 8
and 12, and none contains 4.

## 19.2 Classes g2-g5: a fixed window for odd b

Lemma 18.1 holds word for word with i replaced by the speed s_j: for
w_j = s_j + 8p [s_j in D] (mod 16p), which is the lift with residue z because p is
odd, and an odd time b = m, put x = m/(16p); then
b w_j / (16p) = s_j x + [s_j in D]/2 (mod 1). So m is a witness as soon as x lies in

  W_D = { x : ||s x|| >= 1/16 for s not in D, ||s x - 1/2|| >= 1/16 for s in D },

which does not depend on p, and a closed interval of length >= 1/(8p) inside W_D
contains such an x.

**A rule for the windows next to x = j/8 (j odd).** Write x = j/8 + e with e > 0 and
r_s = (j s - 4 [s in D]) mod 8, so the position of coordinate s is r_s/8 + s e
(mod 1). For r_s = 0 the condition is 1/16 <= s e <= 15/16; for r_s in 1..7 it is
s e <= (15 - 2 r_s)/16 (the position must not pass 15/16). Hence the window to the
right of j/8 is

  16 e in [ max over r_s = 0 of 1/s , min over all s of (15 - 2 r_s)/s ],

and the window to the left is its mirror (x -> -x maps W_D to itself). At every odd
j the only r_s = 0 coordinate is s = 12 (12 is in every D; even s other than 12
never give 0, odd s never do), so every window starts at |e| = 1/192, and it is
guaranteed long enough for every p >= 251 when its upper end for 16e is at least
1/12 + 2/251. Since (15 - 2 r)/s < 1/12 + 2/251 only for r = 7 and s >= 11, that
fails exactly when one of the speeds 11, 13, 15 has r_s = 7, which picks the
centre j:

| class | centre | window in W_D | length | binding at the ends | proper at every p >= |
|---|---|---|---|---|---|
| g2 | 3/8, right | [3/8 + 1/192, 3/8 + 1/144] | 1/576 | s = 12, s = 9 | 72 |
| g3 | 3/8, right | [3/8 + 1/192, 3/8 + 1/144] | 1/576 | s = 12, s = 9 | 72 |
| g4 | 1/8, right | [1/8 + 1/192, 1/8 + 1/112] | 5/1344 | s = 12, s = 7 | 34 |
| g5 | 1/8, left | [1/8 - 1/144, 1/8 - 1/192] | 1/576 | s = 9, s = 12 | 72 |

For example g2 at j = 3: r_9 = 27 - 4 = 23 = 7 (mod 8) gives the upper end 1/9 for
16e, r_5 = 7 gives 1/5, r_28 = 84 = 4 gives 7/28, every other speed allows more, and
r_11 = 5, r_13 = 3, r_15 = 1 are all different from 7. At j = 1 the same class fails
because r_11 = 3 - 4 = 7 (upper end 1/11 < 1/12 + 2/251; that window is
[1/8 + 1/192, 1/8 + 1/176], long enough only from p = 264). Each table row was then
re-checked coordinate by coordinate, and `test_level16_gw.py` re-checks it exactly
and also confirms, by the sweep, that each window is one whole maximal component of
W_D.

## 19.3 Class g1: a parity step of 2

In g1 every coordinate is linear except speed 28: w_j = s_j for s_j != 28, and
w_15 = 28 + 4 t' p with t' = p^{-1} (mod 4), which is odd (then 4 t' p = 4 (mod 16)
and 28 + 4 = 0 (mod 16)).

**Lemma 19.1.** For every prime p >= 147 this lift is proper.

*Proof.* The other 14 speeds are S' = {1, ..., 13, 15}, the same set as in
Lemma 18.2, so the interval I = [1/14 - 1/1680, 1/14 + 1/1456] (length 1/780) has
||s x|| >= 1/16 for every s in S' and x in I (Lemma 18.2's proof, unchanged). For
the speed-28 coordinate, going from b to b + 2 adds 2 w_15/(16p) =
7/(2p) + t'/2 = 1/2 + 7/(2p) (mod 1), whose norm 1/2 - 7/(2p) is at least 1/8 for
p >= 10. Two points of the open arc (-1/16, 1/16) are less than 1/8 apart, so of b and
b + 2 at least one has ||b w_15/(16p)|| >= 1/16. If b/(16p) and (b + 2)/(16p) both lie
in I, that one is a witness, and such a b exists when 16p/780 >= 3, i.e.
p >= 146.25. []

## 19.4 Proof of Theorem 19

For p >= 251, J_p(16) for gw15 is contained in the 5 classes of U_251(16) (Lemma
U(i) and input (ii)). Classes g2-g5 are proper at p by 19.2 (p >= 72), class g1 by
Lemma 19.1 (p >= 147), and properness does not depend on the representative of a
class. So J_p(16) is empty. []

## 19.5 What it means

- Together with Theorem 18: **for 16 runners, the two level-one orbits singled
  out by the tight-set analysis, (1..15) and (1..13, 15, 28), are removed by binary lifting alone by level 16 at every prime
  p >= 251.** A 16-runner computation that uses gate primes from 251 up needs no
  fibre search for either. (For 14 and 15 runners the analogous orbits survive every
  binary level and cost a fibre search at each gate prime; arXiv:2609.02604,
  Section 4.)
- Both theorems rest on the same two inputs; the brute-force job `lrc16-indep-v1`
  tests input (ii) for both bases and, with this section, now also predicts the
  gw15 death level: J_p(16) empty for gw15 at every prime it scans (I6).
- It says nothing about the level-one cover search, which is where almost all of
  the 16-runner cost lies (about 1.75e5 CPU-hours by a public estimate), nor about
  primes below 251, nor about any orbit other than these two.

## 19.6 Not covered

- Primes below 251 (U_251 does not apply there).
- Whether other level-one orbits of a 16-runner computation reach level 16; the two
  treated here are the ones the 14/15-runner proofs single out, chosen by Zhang's
  and Goddyn and Wong's analysis of tight sets.
