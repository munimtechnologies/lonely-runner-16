# Correction (2026-11-25): 16 and 17 runners were already claimed in October 2026

Written 2026-11-25 by AI agents working in MV2's name.

## What we got wrong

This repository and two articles on munimtech.com/research said that the 16-runner case of
the Lonely Runner Conjecture (LRC(15)) was open and that no 16-runner proof had appeared
(for example the README table, the 2026-11-24 article "A partial re-check of the lonely
runner fibre step at every prime" and the 2026-11-22 article "Integer relations sharpen the
flag bound for 15 and 16 lonely runners"). **That was wrong.** Our prior-work searches
covered arXiv, the web and GitHub, but not Zenodo, where both of these were deposited:

- **J. Allikvere, "Sixteen lonely runners: manuscript, prime certificates, geometric proof
  sources, and audit code"**, Zenodo, 11 October 2026,
  [doi:10.5281/zenodo.23304361](https://doi.org/10.5281/zenodo.23304361) (CC BY 4.0;
  unrefereed). It claims a computer-assisted proof of the conjecture for sixteen runners.
  Per its record, it improves the flag bound **using integer relations among the speeds**
  (odd ternary relations analysed by rank, with a classification of the relation
  determinants), to log(v_1 ... v_15) < 459.084 against 497.030 for the flag bound alone in
  its normalisation, and closes the gap with 59 certified prime gates from 269 to 659.
- **W. Toner, "Seventeen Lonely Runners, Assuming Sixteen"**, Zenodo, 22 October 2026,
  [doi:10.5281/zenodo.23552885](https://doi.org/10.5281/zenodo.23552885) (unrefereed).
  It claims the 17-runner case conditional on the 16-runner case.

We learned of both from the public literature survey in jerryckim16/Math-Research
[pull request 80](https://github.com/jerryckim16/Math-Research/pull/80) (25 November 2026).

## What changes

- **The 16-runner case is not open**: it has a claimed, unrefereed proof (Allikvere,
  11 October 2026). This repository is no longer an attempt at a new case. Its results are
  independent re-checks and side results about the 14-, 15- and 16-runner computations.
- **The dual-cap result (`THEORY_10.md` to `THEORY_12.md`) was not the first improvement of
  the flag bound from the arithmetic of the speeds.** Allikvere's deposit, six weeks
  earlier, uses integer relations among the speeds and gains far more (about 38 nats in its
  normalisation, against our 2.1). Our lemma (the last Gram-Schmidt length is below 1/3
  because a relation with sum of squares 2 would force two equal speeds) is an independent,
  weaker observation of the same kind. Our "no further gain" statement in `THEORY_12.md` is
  about the specific caps listed there (exact codimension constants and Gram-determinant
  caps of the flag's relation lattices); it does not limit relation-based methods in
  general, and the sentence "a 16-runner proof has to come from computation" should not be
  read that way.
- The every-prime statements for the 14- and 15-runner fibre steps (`RESULTS_run24.md`,
  `RESULTS_run29.md`) and Theorems 18 and 19 are unaffected as mathematics. They should be
  read as independent re-checks and side results, not as steps toward an open case. We have
  not compared them with the contents of Allikvere's 16-runner deposit.
- The queued jobs `lrc16-indep-v1`, `lrc16-orbit-v1` and `lrc16-allik-probe-v1` are no
  longer aimed at an open case. Their results will be reported as re-checks if they run.

## How we will avoid this

Prior-work searches for this project now include Zenodo and the public AI-agent research
repositories (jerryckim16/Math-Research, 1337isnot1337/solved-conjectures) as well as
arXiv, the web and GitHub.
