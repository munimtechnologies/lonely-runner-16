# THEORY 13: two safe prunings for the level-one cover search (engine 3)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name;
not yet checked by a human expert. Text CC BY 4.0, code Apache-2.0.

## 13.1 Why the cover search is the bottleneck

Two jobs finished on 2026-11-22 (graded in `RESULTS_run14.md`):

- `lrc16-engine2-v1`: our engine finished none of the 20 gates for 14, 15 and 16
  runners at primes 239 to 809 within 800 s per gate. Every one of them stopped in
  the **level-one cover search**, before any lifting started.
- `lrc16-tau-v2`: deciding whether a cover on at most k - 2 classes exists took
  250 s at p = 239 for 16 runners (114,684,186 search nodes, about 460,000 nodes
  per second), and the 300 to 400 s cap stopped it at every prime from 257 (k = 14)
  and 269 (k = 15) upwards, apart from 263, 269, 283 (k = 14) and 277 (k = 15).

So for 16 runners the cover search, not the lifting, decides whether our own
engine can do anything at the gate primes (about 80 primes from 251 to about
800). The same is true of the published 15-runner proof, whose level-one cost
grows roughly as p^6 (arXiv:2609.02604).

## 13.2 The search (engine 2), in brief

State at a node: the chosen classes C (class 1 is always chosen first, to fix
the unit orbit), the set `allowed` of classes that may still be added (earlier
siblings are excluded, so each cover is reached once), the uncovered times U and,
for each chosen class v, its private times Priv_C(v) (times that only v covers).
A node is cut when some chosen class has no private time (`npriv0`), when with
norm = 1 class 1 has fewer than q_s private times (Lemma 4.1 of 2609.02604), or
when the b = maxsize - |C| largest gains cannot reach |U|. Otherwise it branches
on the uncovered time with the fewest allowed classes.

A cover is *reportable* if it is irredundant, has at most maxsize classes, and
(with norm = 1) class 1 has at least q_s private times. Every mode of `lrc.c`
(covers, tau, gate, tuples) reads only reportable covers.

## 13.3 Lemma F (fractional set-cover bound)

At a node, let g(v) = |cov(v) ∩ U| for v in `allowed` and, for a in U,
G(a) = max { g(v) : v in allowed, v covers a }. If F ⊆ allowed covers U then

    |F| >= sum_{a in U} 1/G(a).

*Proof.* Every a in U is covered by some v in F, and G(a) >= g(v) for each such
v, so

    sum_a 1/G(a) <= sum_a sum_{v in F, v covers a} 1/G(a)
                 <= sum_{v in F} sum_{a in cov(v) ∩ U} 1/g(v) = |F|. []

(This is weak LP duality: y_a = 1/G(a) is feasible for the dual of the covering
LP.) So a node with sum_a 1/G(a) > b has no reportable cover below it. The
engine compares in double precision with a margin of 1e-9 in the safe direction
(it cuts only when the sum exceeds b + 1e-9; the sum has at most 500 terms, so
rounding error is below 1e-12). If some a in U has G(a) = 0 the node is cut too
(no allowed class covers a). The bound is not implied by the old one: the old
bound sums the b largest gains over all classes, Lemma F charges each uncovered
time to its own best class, which is much stronger when a few times are reachable
only through classes with small gains.

## 13.4 Lemma P (forbidden classes)

Let u be in `allowed`.

(i) If cov(u) ⊇ Priv_C(v) for some chosen v, no reportable cover through the node
contains u.

(ii) With norm = 1, if |cov(u) ∩ Priv_C(1)| > |Priv_C(1)| - q_s, no reportable
cover through the node contains u.

*Proof.* Private sets only shrink as classes are added: for C ⊆ S,
Priv_S(v) ⊆ Priv_C(v) \ cov(u) for every u in S \ C. In (i) this is empty, so
v is redundant in S. In (ii), |Priv_S(1)| <= |Priv_C(1)| - |cov(u) ∩ Priv_C(1)|
< q_s, so S fails the q_s test. []

The engine removes all such u from `allowed` for the subtree of the node, and
restores `allowed` on return. Removing classes from `allowed` never makes the
search reach a cover twice or miss one that contains only non-removed classes:
the branching rule (every completion must contain an allowed class covering the
chosen time a) stays exhaustive over the remaining classes. Computing the
removed set uses that "u covers a" is symmetric in u and a (both say
(k+1) d_p(au) < p), so the classes covering a are the bit set of a's own cover;
the cost is one AND of bit sets per private time of each chosen class, which is
small next to the gain computation the node already does.

**Why (i) should help.** Deep in the search most chosen classes keep only one to
three private times, and each time is covered by exactly m = floor((p-1)/(k+1))
classes. So each chosen class with one private time forbids up to m - 1 classes,
and with ten or more chosen classes a large part of all n = (p-1)/2 classes is
gone. That shrinks the branching factor and makes both bounds sharper.

## 13.5 Consequence and how it is tested

Since both rules cut only nodes below which no reportable cover exists, every
output of `lrc.c` is the same for LRC_PRUNE = 0, 1, 2, 3: the set of canonical
covers, their counts by size, tau, the tau certificate's existence, and every
gate result (the order in which covers are found may change, so the tests
compare sorted lists). `test_prune.py` checks:

- Lemma F by brute force at random search states (k = 3 to 7, p <= 37);
- Lemma P by brute force: for every irredundant cover S of 9 small (k, p) and
  every C ⊂ S containing 1, no class of S is forbidden (both rules);
- the symmetry used by the engine;
- the C engine: identical canonical covers for all four LRC_PRUNE values (both
  normalisations, 9 gates up to k = 10, also with maxsize < k), agreement with
  the brute-force reference, identical tau answers at 11 (k, p) including three
  "no cover" certificates, tau covers that are verified irredundant covers by an
  independent Python check, and identical gate JSON.

Job `lrc16-engine3-v1` then measures what the rules buy and spends the time on
the tau scans that engine 2 could not finish (`PLAN_addendum7.md`).

## 13.6 What this is not

It is an engineering improvement of our own independent engine, not new
mathematics about runners. Allikvere's published pipeline has its own (and
probably much faster) generator; job `lrc16-allik-probe-v1` measures that one.
Lemma F and Lemma P are standard ideas from exact set-cover search (LP bounds,
dominance by private elements); we found no prior use of them for the
lonely-runner level-one search, but we have not seen the source of every
implementation.
