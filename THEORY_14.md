# THEORY 14: early orbit pruning for the level-one cover search (engine 4)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name;
not yet checked by a human expert. Text CC BY 4.0, code Apache-2.0.

## 14.1 Where the waste is

The level-one search (THEORY_13 Sec. 13.2) uses the normalisation of Lemma 4.1 of
arXiv:2609.02604: every orbit of covers under multiplication by units has a
member in which class 1 has the **most** private times, and that class has at
least q_s of them. The engine fixes class 1 first and prunes when class 1 drops
below q_s private times. But it only checks "class 1 has the most private
times" at the leaf (`report()`). A cover of size s has up to s members that
contain class 1 (one for each of its classes), and the search walks down to
every one of them in which class 1 keeps at least q_s private times, only to
throw away all but the ones in which class 1 is the largest. In tau mode
(proving that no cover on at most k - 2 classes exists) the same happens to
every dead-end subtree: the search explores partial covers that could only
complete to members of an orbit that the normalisation would reject.

## 14.2 Lemma M

Fix a search node: chosen classes C (with 1 in C), the set `allowed` of classes
that the subtree may still add, and private sets Priv_C(v). For a chosen class
v != 1 let

    L(v) = | { a in Priv_C(v) : no class in `allowed` covers a } |

(the private times of v that are **locked**).

**Lemma M.** Let S be a cover reached in the subtree (so C ⊆ S ⊆ C ∪ allowed).

(i) |Priv_S(v)| >= L(v) for every chosen v, and |Priv_S(1)| <= |Priv_C(1)|.

(ii) If L(v) > |Priv_C(1)| for some chosen v != 1, then class 1 does not have
the most private times in S, so S is not reported (norm = 1).

(iii) Let T = max(q_s, max_v L(v)). If an allowed class u has
|cov(u) ∩ Priv_C(1)| > |Priv_C(1)| - T, then no reportable cover through the
node contains u.

*Proof.* (i) A locked time a of v is covered by v and by no other chosen class,
and every class of S \ C is in `allowed`, so none covers a; hence a stays
private to v in S. Private sets only shrink when classes are added, so
|Priv_S(1)| <= |Priv_C(1)|. (ii) follows from (i): |Priv_S(v)| >= L(v) >
|Priv_C(1)| >= |Priv_S(1)|. (iii) If u is in S, Priv_S(1) ⊆ Priv_C(1) \ cov(u),
so |Priv_S(1)| < T. If T = q_s, S fails Lemma 4.1's test; if T = L(v), then
|Priv_S(1)| < L(v) <= |Priv_S(v)| and class 1 is not the largest. Either way S
is not reported. []

Two facts make it safe inside the engine:

- `allowed` only shrinks along a search path (earlier siblings are excluded,
  THEORY_13's forbidden classes are removed), so L(v) computed at a node is a
  valid lower bound for every node below it, and the classes removed by (iii)
  never come back in the subtree.
- In tau mode the engine stops at the first irredundant cover, of any shape.
  Lemma M can cut the members of an orbit in which class 1 is not the largest,
  but never the member in which it is (there |Priv_S(1)| >= |Priv_S(v)| >= L(v)
  for every v, and |Priv_S(1)| >= q_s by Lemma 4.1). So "a cover on at most s
  classes exists" gets the same answer with or without the rule.

The rule is strict: a cover in which class 1 is only **tied** for the most
private times is never cut, because `report()` keeps a tied member when it is
the canonical one.

## 14.3 In the engine

`LRC_PRUNE` bit 4 (`lrc.c`, `forbid_classes()`), norm = 1 only. After
THEORY_13's Lemma P (bit 2) has shrunk `allowed`, the engine computes L(v) for
every chosen v != 1 (one AND of two bit sets per private time), prunes the node
by (ii), and otherwise removes the classes of (iii) with T = max(q_s, max L).
Without bit 4 the removal uses T = q_s, exactly as engine 3 does. `LRC_PRUNE=7`
switches on all three rules.

Because it cuts only covers that `report()` would reject, the canonical covers,
their counts, tau, the existence of a tau certificate and every gate result are
unchanged. The `raw` count printed by `covers` mode (covers reached before the
normalisation filter) can only go down: that drop is exactly the waste of 14.1
that the rule removes before the leaf.

## 14.4 Tests (`test_orbit.py`)

The test file imports nothing else from this repository, so its brute force is
independent of `lrc_ref.py` and of `lrc.c`.

- Lemma M by brute force: at 10 small (k, p), for every irredundant cover S in
  which class 1 has the most private times, and every C ⊂ S containing 1, the
  rule neither prunes nor removes a class of S, with the smallest possible
  allowed set S \ C (the strongest form of the rule).
- The rule is not vacuous: it fires on covers where class 1 is not the largest.
- The whole search, written again in Python with all three bits, finds exactly
  the brute-force orbits with LRC_PRUNE = 0 and 7, reaches no more raw covers
  with 7, and gives the true tau with 0, 4 and 7.
- With a C compiler (in the compete job): the C engine gives the brute-force
  orbits with LRC_PRUNE = 4 and 7, the same covers and tau as LRC_PRUNE = 0 at
  nine larger (k, p), never more raw covers, the same orbits as the Python
  search at (7, 43) and (8, 53), identical tau answers and verified tau
  certificates at 11 (k, p) up to k = 15, and identical gate JSON.

## 14.5 What this is not

An engineering step for our own independent engine, not new mathematics about
runners. Detecting early that a partial solution cannot be the canonical member
of its orbit is a standard idea in isomorph-free search; the particular
invariant (locked private times against class 1's private count) is ours, but
we have not seen every implementation of the published pipelines. Its value is
measured, not assumed: job `lrc16-orbit-v1` (`PLAN_addendum8.md`).
