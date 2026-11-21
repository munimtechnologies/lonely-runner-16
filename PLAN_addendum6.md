# PLAN, addendum 6 (2026-11-21, run 7, before any lifting result)

MV2 of Munim, Inc. Made with AI agents working in MV2's name; CC BY 4.0.
Continues `PLAN.md` (addenda 1-5 are unchanged and stay in force).

Written at about 20:40 UTC on 2026-11-21. All six jobs (`lrc-repro-k14-v1`,
`lrc16-pilot-v1`, `lrc16-engine2-v1`, `lrc16-shift-v1`, `lrc16-tau-v1`,
`lrc16-uniform-v1`) are still queued; no result of any of them exists. No new
job is filed with this addendum. The checks below are read off the output of
`lrc16-uniform-v1` (`summary_uniform.json`) when it reports.

**X3 (consistency with Lemma G2, `THEORY_9.md` 9.3; failure means a bug).** For
s = (1..15), every level-2 survivor listed for P = 251 and for P = infinity
(the `list` of the level-2 entry, up to 60 vectors) is of type (A) or (B) of
Lemma G2, and none satisfies the gcd clause (at most one odd coordinate). At level
2 the canonical form is the vector itself, so this can be checked by eye. Any
listed vector of neither type means `uniform.py` keeps a lift that a near-grid
test kills, which is a bug; nothing from `uniform.py` is then used until it is
explained. (X3 does not apply to the P = 17 run: Lemma G2 needs P > 240.)

**X4 (two implementations agree; checked before this addendum is published).**
`test_grid.py` requires `grid.grid_killed` with D = 2Q to agree exactly with
`uniform.uniform_killed` on every case it tries. If the publish check passes,
X4 holds on those cases; if it fails, nothing is committed and the failure is
reported in the next run.

**M3 (measurement, no prediction).** The number of level-2 survivors of (1..15)
for P = 251 and for P = infinity, as a share of the 13,054 near-grid-blocked
candidates of Lemma G2. If either run is cut at level 2 (more than 3,000
survivors), P5 is **untested** (addendum 5), not failed, and the next version of
the job raises the cap or moves the search to a faster implementation.

**What each outcome means.** X3 and X4 holding together mean two independent
methods agree on the lifts that matter at level 2, so a P5 reading from the same
run can be trusted to that extent. They are consistency checks only: they say
nothing about whether P5 itself holds.
