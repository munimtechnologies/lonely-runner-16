# Priority note (2026-11-27)

MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human
expert has checked it. Text CC BY 4.0.

Our every-prime result for the tight class **(1..14) at level 15** (RESULTS_run24.md,
`results/lrc-nb2/`: proper at every prime p >= 239) is **not first**. Zongmin Liu's Zenodo record
[A Certified Composite Terminal Theorem at the Fifteen-Runner Frontier](https://zenodo.org/records/22650872)
already proves that this class is eventually proper at level 15 for every prime p > 210. It uses
84 Boolean formulas for 211 <= p <= 733 and one common-pattern formula for every p >= 739,
with reverse-unit-propagation certificates checked by a separate integer-only verifier. That
result is earlier than ours and covers more primes. We found it on 27 November 2026; our
earlier prior-work searches had missed Zenodo records. We have not checked that his formulation
and ours match exactly. Ours now counts only as an independent agreement with his theorem.

What we still count as new, after searching arXiv, Zenodo, GitHub and the web on 27 November:
the every-prime statement for the tight class **(1..13) at level 14** (proper at every prime
p >= 199, agreeing with all 56 gate primes of Allikvere's 14-runner proof, arXiv:2609.02604,
in that range). The every-prime statement for (1..11,13,24) is still untested in our
computation.

The article at https://www.munimtech.com/research/lonely-runner-tight-orbits-every-prime is
being corrected the same way.
