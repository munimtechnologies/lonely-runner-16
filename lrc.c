/*
 * lrc.c -- independent level-one cover enumeration and lifting cascade for the
 * finite-checking framework of the Lonely Runner Conjecture (LRC) introduced by
 * Rosenfeld (arXiv:2509.14111), Trakulthongchai (arXiv:2511.22427),
 * Sungkawichai & Trakulthongchai (arXiv:2604.23906) and refined by Allikvere
 * (arXiv:2609.02604).  This is a from-scratch reimplementation written from the
 * published definitions only; it does not reuse any of their code.
 *
 * Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
 * SPDX-License-Identifier: Apache-2.0
 * Licensed under the Apache License, Version 2.0 (see LICENSE).
 * Made with AI agents working in MV2's name; not yet checked by a human expert.
 *
 * Conventions (Allikvere 2609.02604, Sec. 2 and 4):
 *   k speeds (k+1 runners), p prime, n = (p-1)/2 folded classes {1..n}.
 *   Speed class v covers folded time a  iff  (k+1) * d_p(a v) < p,
 *   where d_p(x) = distance of x to the nearest multiple of p.
 *   A level-1 vector (k-multiset of classes) is improper iff the union of the
 *   sets it covers is all of {1..n}.
 *   Level l: w in Z_{lp}^k with no coordinate divisible by p.  w is proper iff
 *     (a) for some i, gcd(l, w_1..w_k without w_i) > 1, or
 *     (b) some t = b/(lp) has  (k+1) d_{lp}(b w_i) >= lp  for every i.
 *
 * Two independent ways of doing each step are built in, so that they can be
 * cross-checked against each other on every gate:
 *   cover normalisation  norm=0: some class of the cover is moved to 1 by a
 *                                unit; canonical = lexicographic minimum over
 *                                all such images.
 *                        norm=1: Lemma 4.1 of 2609.02604: a class with the
 *                                MOST private times is moved to 1 (it has at
 *                                least q_s = ceil((2n - s m)/s) of them, which
 *                                prunes the search); canonical = minimum over
 *                                the classes tied for most private times.
 *                                The stored cover is then converted to the
 *                                norm=0 canonical form, so outputs compare.
 *   lifting              bb=0:   all c^k lifts tested by a full scan of times.
 *                        bb=1:   branch and bound over coordinates: a lift of
 *                                an improper vector is improper iff its
 *                                coordinates cover every NEW time b (b not
 *                                divisible by c; the others are level-l times,
 *                                already covered), and the gcd clause fails.
 *
 * Engine 3 (2026-11-22): two optional pruning rules for the cover search,
 * switched on by the environment variable LRC_PRUNE (a bit mask; default 0,
 * which is exactly the engine-2 search).  Both only remove search nodes below
 * which no reportable cover exists, so every mode prints the same covers, tau
 * and gate results with any LRC_PRUNE value (THEORY_13.md; test_prune.py):
 *   bit 1  fractional set-cover bound.  With g(v) = number of uncovered times
 *          class v covers and G(a) = max g(v) over allowed classes v covering
 *          the uncovered time a, any completion needs at least
 *          sum_a 1/G(a) more classes (LP duality: y_a = 1/G(a) is feasible
 *          for the dual of the covering LP).  Prune when this exceeds the
 *          number of classes still allowed.
 *   bit 2  forbidden classes.  A class that covers every private time of an
 *          already chosen class can never be added (private sets only
 *          shrink, so the cover could not be irredundant); with norm=1, nor
 *          can a class that would leave class 1 with fewer than q_s private
 *          times.  Such classes are removed from the allowed set of the
 *          subtree.
 *
 * Optional shift filter (shift=1; THEORY.md Sec. 5, "Lemma S"): an improper
 * lift w at level l is also dropped when some d | l, d >= 2, has
 *   E = {i : d does not divide w_i} non-empty and
 *   sum_{i in E} g_i * ceil(2 (d/g_i) / (k+1)) < d,   g_i = gcd(w_i, d).
 * Then every integer vector congruent to w mod lp has the LR property (given
 * LRC(m) for m < k), so by the chained form of Lemma 2.2(ii) of 2609.02604 it
 * cannot be the reduction of a counterexample.  Gates that use the filter
 * prove "p divides the speed product" through Lemma 2.2(ii), not through
 * J(k,p) being empty; the JSON reports how many lifts the filter removed.
 *
 * Optional general completion (ext=1; THEORY.md Sec. 6): canonical irredundant
 * covers of size s <= k-2 are completed by every multiset of k-s extra classes
 * (non-decreasing), so primes with tau(p) <= k-2 give complete gates too.  With
 * ext=0 such covers are only counted ("small_orbits_unhandled") and the gate is
 * marked incomplete, exactly as before.
 *
 * Modes:
 *   lrc covers K P [maxsize] [timecap_s] [norm]
 *   lrc tau K P maxsize [timecap_s]
 *       exact tau(p) if it is <= maxsize, otherwise a certificate that no
 *       cover on <= maxsize classes exists (Lemma 4.1 pruning, stop at the
 *       first cover found); prints "T key=value ..." and "F classes" if found.
 *   lrc cascade K P L1,L2,.. v1 .. vK          (brute-force lifting)
 *   lrc cascadebb K P L1,L2,.. v1 .. vK        (branch-and-bound lifting)
 *   lrc scascade / scascadebb  (same, with the shift filter)
 *       print "L level count" per level, "X level shift_removed" per level,
 *       "R status", up to 50 "W w1..wK".
 *   lrc gate K P L1,L2,.. timecap_s liftcap [norm] [bb] [shift] [ext]
 *       covers + cascade for every canonical cover of size K and, for covers of
 *       size K-1, for every extra class x (with ext=1: for covers of any size
 *       s, every multiset of K-s extra classes); prints one JSON object.
 *   lrc tuples K P [ext] [norm]
 *       prints "T v1..vK" for every level-1 tuple the gate would lift.
 *   lrc shiftok K P l w1 .. wK
 *       prints the smallest d certified by the shift filter at level l (or 0).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 1024
#define MAXW (MAXN / 64)
#define MAXK 32
#define MAXLEV 16

typedef struct { uint64_t w[MAXW]; } bset;

static int P, K, N, M, NW, MAXSIZE, NORM, QS;
static bset *cov;      /* cov[v]: folded times covered by speed class v */
static bset *who;      /* who[a]: speed classes covering time a */
static int *covlist;   /* covlist[v*M + j] */

static int cnt[MAXN + 1], own[MAXN + 1], pc[MAXN + 1];
static int npriv0;
static int chosen[MAXK + 1], nch;
static bset uncov, allowed;
static long long nodes;
static double tstart, timecap;
static int timed_out;

/* engine 3 pruning (LRC_PRUNE bit mask, see the header) */
static int PRUNE = 0;
static int gainv[MAXN + 1];

/* stop-at-first-cover mode (tau) */
static int STOPFIRST = 0, stopnow = 0;
static int firstcov[MAXK + 1], nfirst = 0;

/* canonical covers found */
static int *found;      /* flattened, each entry MAXK+1 ints: size then classes */
static long nfound, capfound;
static long count_by_size[MAXK + 2];
static long raw_by_size[MAXK + 2];

/* shift filter */
static int SHIFT = 0;
static long cur_shift[MAXLEV];  /* lifts removed by the shift filter, per level */

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int fold(long long x) {
    x %= P;
    if (x < 0) x += P;
    if (x > N) x = P - x;
    return (int)x;
}

static long long powmod(long long b, long long e, long long m) {
    long long r = 1 % m;
    b %= m;
    if (b < 0) b += m;
    while (e) {
        if (e & 1) r = r * b % m;
        b = b * b % m;
        e >>= 1;
    }
    return r;
}

static inline void bs_set(bset *s, int i) { s->w[(i - 1) >> 6] |= 1ULL << ((i - 1) & 63); }
static inline void bs_clr(bset *s, int i) { s->w[(i - 1) >> 6] &= ~(1ULL << ((i - 1) & 63)); }
static inline int bs_get(const bset *s, int i) { return (s->w[(i - 1) >> 6] >> ((i - 1) & 63)) & 1; }
static inline int bs_pop(const bset *s) {
    int c = 0;
    for (int j = 0; j < NW; j++) c += __builtin_popcountll(s->w[j]);
    return c;
}
static inline int bs_pop_and(const bset *a, const bset *b) {
    int c = 0;
    for (int j = 0; j < NW; j++) c += __builtin_popcountll(a->w[j] & b->w[j]);
    return c;
}

static void setup(int k, int p) {
    K = k;
    P = p;
    N = (p - 1) / 2;
    M = (p - 1) / (k + 1);
    NW = (N + 63) / 64;
    if (N > MAXN || k > MAXK || M < 1) {
        fprintf(stderr, "parameters out of range\n");
        exit(2);
    }
    cov = calloc(N + 1, sizeof(bset));
    who = calloc(N + 1, sizeof(bset));
    covlist = calloc((size_t)(N + 1) * M, sizeof(int));
    for (int v = 1; v <= N; v++) {
        int j = 0;
        for (int a = 1; a <= N; a++) {
            long long x = (long long)a * v % p;
            long long d = x < p - x ? x : p - x;
            if ((long long)(k + 1) * d < p) {
                bs_set(&cov[v], a);
                bs_set(&who[a], v);
                if (j >= M) { fprintf(stderr, "cover size mismatch\n"); exit(3); }
                covlist[v * M + j++] = a;
            }
        }
        if (j != M) { fprintf(stderr, "cover size mismatch %d %d\n", j, M); exit(3); }
    }
}

static void add_class(int v) {
    for (int j = 0; j < M; j++) {
        int a = covlist[v * M + j];
        if (cnt[a] == 1) {
            if (--pc[own[a]] == 0) npriv0++;
        } else if (cnt[a] == 0) {
            bs_clr(&uncov, a);
        }
        cnt[a]++;
        own[a] ^= v;
        if (cnt[a] == 1) pc[v]++;
    }
    if (pc[v] == 0) npriv0++;
}

static void remove_class(int v) {
    if (pc[v] == 0) npriv0--;
    for (int j = 0; j < M; j++) {
        int a = covlist[v * M + j];
        cnt[a]--;
        own[a] ^= v;
        if (cnt[a] == 0) {
            bs_set(&uncov, a);
            pc[v]--;
        } else if (cnt[a] == 1) {
            if (pc[own[a]]++ == 0) npriv0--;
        }
    }
}

static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

/* t = sorted fold(c_j^{-1} * c) */
static void unit_image(const int *c, int s, int j, int *t) {
    long long inv = powmod(c[j], P - 2, P);
    for (int i = 0; i < s; i++) t[i] = fold(inv * c[i]);
    qsort(t, s, sizeof(int), cmp_int);
}

static int lexcmp(const int *a, const int *b, int s) {
    for (int i = 0; i < s; i++)
        if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1;
    return 0;
}

/* is the sorted cover c[0..s-1] the lexicographic minimum of {c_j^{-1} c}? */
static int is_canonical(const int *c, int s) {
    int t[MAXK + 1];
    for (int j = 1; j < s; j++) {
        unit_image(c, s, j, t);
        if (lexcmp(t, c, s) < 0) return 0;
    }
    return 1;
}

/* replace the sorted cover c by the lexicographic minimum of {c_j^{-1} c} */
static void to_global_canonical(int *c, int s) {
    int best[MAXK + 1], t[MAXK + 1];
    memcpy(best, c, s * sizeof(int));
    for (int j = 0; j < s; j++) {
        unit_image(c, s, j, t);
        if (lexcmp(t, best, s) < 0) memcpy(best, t, s * sizeof(int));
    }
    memcpy(c, best, s * sizeof(int));
}

static void report(void) {
    if (STOPFIRST) {
        /* tau mode: any irredundant cover settles existence at this size */
        if (!stopnow) {
            stopnow = 1;
            nfirst = nch;
            memcpy(firstcov, chosen, nch * sizeof(int));
            qsort(firstcov, nfirst, sizeof(int), cmp_int);
        }
        return;
    }
    int c[MAXK + 1];
    int s = nch;
    memcpy(c, chosen, s * sizeof(int));
    qsort(c, s, sizeof(int), cmp_int);
    raw_by_size[s]++;
    if (NORM) {
        /* class 1 must have the most private times; private counts are
         * invariant under multiplication by units */
        int mx = 0;
        for (int i = 0; i < s; i++) if (pc[c[i]] > mx) mx = pc[c[i]];
        if (pc[1] < mx) return;
        int t[MAXK + 1];
        for (int j = 1; j < s; j++) {
            if (pc[c[j]] != mx) continue;
            unit_image(c, s, j, t);
            if (lexcmp(t, c, s) < 0) return;
        }
        to_global_canonical(c, s);
    } else if (!is_canonical(c, s)) {
        return;
    }
    count_by_size[s]++;
    if (nfound == capfound) {
        capfound = capfound ? capfound * 2 : 1024;
        found = realloc(found, (size_t)capfound * (MAXK + 1) * sizeof(int));
        if (!found) { fprintf(stderr, "out of memory\n"); exit(4); }
    }
    int *dst = found + (size_t)nfound * (MAXK + 1);
    dst[0] = s;
    memcpy(dst + 1, c, s * sizeof(int));
    nfound++;
}

/* LRC_PRUNE bit 2: remove from `allowed` every class u whose addition would
 * leave some chosen class v without a private time (u covers every private
 * time of v), and, with NORM, every class u that would leave class 1 with
 * fewer than QS private times.  Private sets only shrink as classes are
 * added, so no cover through this node that contains u can be reported
 * (search() rejects it through npriv0 or the QS test before or at the leaf).
 * Uses the symmetry "u covers a iff a covers u", i.e. who[a] == cov[a]. */
static void forbid_classes(void) {
    bset x, p1;
    int have_p1 = 0;
    memset(&p1, 0, sizeof p1);
    for (int i = 0; i < nch; i++) {
        int v = chosen[i];
        int any = 0;
        x = allowed;
        for (int j = 0; j < M; j++) {
            int a = covlist[v * M + j];
            if (cnt[a] != 1) continue; /* a is private to v */
            any = 1;
            if (NORM && v == 1) bs_set(&p1, a);
            for (int w = 0; w < NW; w++) x.w[w] &= who[a].w[w];
        }
        if (!any) continue; /* cannot happen when npriv0 == 0 */
        for (int w = 0; w < NW; w++) allowed.w[w] &= ~x.w[w];
        if (NORM && v == 1) have_p1 = 1;
    }
    if (have_p1 && QS > 0) {
        int lim = pc[1] - QS; /* u may stay only if |cov[u] & P1| <= lim */
        if (lim < M) {
            for (int u = 1; u <= N; u++) {
                if (!bs_get(&allowed, u)) continue;
                if (bs_pop_and(&cov[u], &p1) > lim) bs_clr(&allowed, u);
            }
        }
    }
}

static void search(void);

/* bounds and branching at a node with U > 0 uncovered times and b > 0 free
 * slots; `allowed` is already final for this node */
static void search_body(int U, int b) {
    /* bound: sum of the b largest gains among allowed classes must reach U */
    int top[MAXK + 1];
    int nt = 0;
    for (int v = 1; v <= N; v++) {
        if (!bs_get(&allowed, v)) { gainv[v] = 0; continue; }
        int g = bs_pop_and(&cov[v], &uncov);
        gainv[v] = g;
        if (g == 0) continue;
        if (nt < b) {
            int i = nt++;
            while (i > 0 && top[i - 1] < g) { top[i] = top[i - 1]; i--; }
            top[i] = g;
        } else if (g > top[b - 1]) {
            int i = b - 1;
            while (i > 0 && top[i - 1] < g) { top[i] = top[i - 1]; i--; }
            top[i] = g;
        }
    }
    int sum = 0;
    for (int i = 0; i < nt; i++) sum += top[i];
    if (sum < U) return;
    if (PRUNE & 1) {
        /* fractional set-cover bound: need >= sum over uncovered a of 1/G(a) */
        double need = 0.0;
        for (int a = 1; a <= N; a++) {
            if (!bs_get(&uncov, a)) continue;
            const int *cl = covlist + (size_t)a * M; /* classes covering a */
            int mg = 0;
            for (int j = 0; j < M; j++) if (gainv[cl[j]] > mg) mg = gainv[cl[j]];
            if (mg == 0) return;
            need += 1.0 / mg;
        }
        if (need > (double)b + 1e-9) return;
    }
    /* branch on the uncovered time with the fewest allowed candidates */
    int best = -1, bestc = 1 << 30;
    for (int a = 1; a <= N; a++) {
        if (!bs_get(&uncov, a)) continue;
        int c = bs_pop_and(&who[a], &allowed);
        if (c < bestc) { bestc = c; best = a; if (c == 0) return; }
    }
    int cands[MAXN];
    int nc = 0;
    for (int v = 1; v <= N; v++)
        if (bs_get(&who[best], v) && bs_get(&allowed, v)) cands[nc++] = v;
    for (int i = 0; i < nc; i++) {
        int v = cands[i];
        bs_clr(&allowed, v);
        add_class(v);
        chosen[nch++] = v;
        search();
        nch--;
        remove_class(v);
        if (timed_out || stopnow) break;
    }
    for (int i = 0; i < nc; i++) bs_set(&allowed, cands[i]);
}

static void search(void) {
    nodes++;
    if ((nodes & 0xFFFF) == 0 && timecap > 0 && now() - tstart > timecap) timed_out = 1;
    if (timed_out || stopnow) return;
    if (npriv0) return;
    if (NORM && pc[1] < QS) return; /* private counts only fall as classes are added */
    int U = bs_pop(&uncov);
    if (U == 0) { report(); return; }
    int b = MAXSIZE - nch;
    if (b <= 0) return;
    if ((long long)b * M < U) return;
    if (PRUNE & 2) {
        bset saved = allowed;
        forbid_classes();
        search_body(U, b);
        allowed = saved;
    } else {
        search_body(U, b);
    }
}

static void run_covers(int maxsize, double cap, int norm) {
    MAXSIZE = maxsize;
    NORM = norm;
    {
        int slack = 2 * N - maxsize * M;
        QS = slack > 0 ? (slack + maxsize - 1) / maxsize : 0;
    }
    memset(cnt, 0, sizeof cnt);
    memset(own, 0, sizeof own);
    memset(pc, 0, sizeof pc);
    memset(count_by_size, 0, sizeof count_by_size);
    memset(raw_by_size, 0, sizeof raw_by_size);
    nfound = 0;
    npriv0 = 0;
    nch = 0;
    stopnow = 0;
    memset(&uncov, 0, sizeof uncov);
    memset(&allowed, 0, sizeof allowed);
    for (int a = 1; a <= N; a++) { bs_set(&uncov, a); bs_set(&allowed, a); }
    nodes = 0;
    timed_out = 0;
    timecap = cap;
    tstart = now();
    /* orbit normalisation: every orbit has a member containing class 1 (for
     * norm=1: a member in which class 1 has the most private times) */
    bs_clr(&allowed, 1);
    add_class(1);
    chosen[nch++] = 1;
    search();
}

/* ---------------- lifting cascade ---------------- */

static int prime_factors(long long l, long long *f) {
    int nf = 0;
    for (long long d = 2; d * d <= l; d++) {
        if (l % d == 0) {
            f[nf++] = d;
            while (l % d == 0) l /= d;
        }
    }
    if (l > 1) f[nf++] = l;
    return nf;
}

static int gcd_proper(const long long *w, const long long *fac, int nfac) {
    for (int j = 0; j < nfac; j++) {
        int bad = 0;
        for (int i = 0; i < K; i++)
            if (w[i] % fac[j] != 0) bad++;
        if (bad <= 1) return 1; /* gcd clause (a) */
    }
    return 0;
}

static long long gcdll(long long a, long long b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { long long t = a % b; a = b; b = t; }
    return a;
}

/* Lemma S (THEORY.md Sec. 5): smallest d | l, d >= 2, such that
 * E = {i : d does not divide w_i} is non-empty and
 * sum_{i in E} g_i * ceil(2 (d/g_i) / (K+1)) < d  (g_i = gcd(w_i, d));
 * 0 if there is none. */
static int shift_ok(const long long *w, long long l) {
    for (long long d = 2; d <= l; d++) {
        if (l % d) continue;
        long long tot = 0;
        int e = 0;
        for (int i = 0; i < K && tot < d; i++) {
            long long g = gcdll(w[i], d);
            if (g == d) continue;
            long long n = d / g;
            tot += g * ((2 * n + K) / (K + 1));
            e++;
        }
        if (e >= 1 && tot < d) return (int)d;
    }
    return 0;
}

/* proper at modulus L = l*P ? */
static int is_proper(const long long *w, long long l, const long long *fac, int nfac) {
    if (gcd_proper(w, fac, nfac)) return 1;
    long long L = l * P;
    long long lo = (L + K) / (K + 1); /* smallest d with (K+1) d >= L */
    long long hi = L - lo;
    for (long long b = 1; b <= L / 2; b++) {
        int ok = 1;
        for (int i = 0; i < K; i++) {
            long long r = (b * w[i]) % L;
            if (r < lo || r > hi) { ok = 0; break; }
        }
        if (ok) return 1;
    }
    return 0;
}

typedef struct {
    long long *data; /* K per vector */
    long n, cap;
} vecset;

static void vs_push(vecset *s, const long long *w) {
    if (s->n == s->cap) {
        s->cap = s->cap ? s->cap * 2 : 64;
        s->data = realloc(s->data, (size_t)s->cap * K * sizeof(long long));
        if (!s->data) { fprintf(stderr, "out of memory\n"); exit(4); }
    }
    memcpy(s->data + (size_t)s->n * K, w, K * sizeof(long long));
    s->n++;
}

/* returns 0 if eventually proper within the given levels, 1 if survivors remain,
 * -1 on overflow; counts[i] receives the number of improper lifts at level i
 * that are kept (with the shift filter on: not removed by it; the removed ones
 * are counted in cur_shift[i]). */
static int cascade(const int *v, const int *mult, int nlev, long liftcap,
                   long *counts, vecset *final_out) {
    vecset cur = {0}, nxt = {0};
    long long w[MAXK], w2[MAXK];
    memset(cur_shift, 0, sizeof cur_shift);
    for (int i = 0; i < K; i++) w[i] = v[i];
    long long nofac[1];
    if (is_proper(w, 1, nofac, 0)) { free(cur.data); return 0; }
    vs_push(&cur, w);
    long long l = 1;
    int status = 1;
    for (int li = 0; li < nlev; li++) {
        long long c = mult[li];
        long long L = l * P;
        long long nl = l * c;
        long long fac[16];
        int nfac = prime_factors(nl, fac);
        nxt.n = 0;
        for (long s = 0; s < cur.n; s++) {
            long long *base = cur.data + (size_t)s * K;
            int a[MAXK];
            memset(a, 0, sizeof a);
            for (;;) {
                for (int i = 0; i < K; i++) w2[i] = base[i] + a[i] * L;
                if (!is_proper(w2, nl, fac, nfac)) {
                    if (SHIFT && shift_ok(w2, nl)) {
                        cur_shift[li]++;
                    } else {
                        vs_push(&nxt, w2);
                        if (nxt.n > liftcap) { status = -1; break; }
                    }
                }
                int i = 0;
                while (i < K && ++a[i] == c) { a[i] = 0; i++; }
                if (i == K) break;
            }
            if (status == -1) break;
        }
        counts[li] = nxt.n;
        vecset t = cur; cur = nxt; nxt = t;
        l = nl;
        if (status == -1) break;
        if (cur.n == 0) { status = 0; break; }
    }
    if (final_out && status == 1) {
        for (long s = 0; s < cur.n; s++) vs_push(final_out, cur.data + (size_t)s * K);
    }
    free(cur.data);
    free(nxt.data);
    return status;
}

/* ---- branch-and-bound lifting (same answers as cascade(), much faster) ---- */

static int bb_c, bb_nw, bb_nfac, bb_over, bb_li;
static long long bb_L, bb_l;
static long long bb_fac[16];
static const long long *bb_base;
static uint64_t *bb_cv;  /* (i*c + a) * nw : new times covered by w_i + a L */
static uint64_t *bb_U;   /* (depth) * nw   : uncovered new times */
static int bb_a[MAXK];
static vecset *bb_out;
static long bb_liftcap;

static inline int pop_words(const uint64_t *x, int nw) {
    int c = 0;
    for (int j = 0; j < nw; j++) c += __builtin_popcountll(x[j]);
    return c;
}
static inline int pop_and_words(const uint64_t *x, const uint64_t *y, int nw) {
    int c = 0;
    for (int j = 0; j < nw; j++) c += __builtin_popcountll(x[j] & y[j]);
    return c;
}

static void bb_emit(void) {
    long long w2[MAXK];
    for (int i = 0; i < K; i++) w2[i] = bb_base[i] + bb_a[i] * bb_L;
    if (gcd_proper(w2, bb_fac, bb_nfac)) return;
    if (SHIFT && shift_ok(w2, bb_l)) { cur_shift[bb_li]++; return; }
    vs_push(bb_out, w2);
    if (bb_out->n > bb_liftcap) bb_over = 1;
}

static void bb_fill(int i) { /* every new time is covered: all completions */
    if (bb_over) return;
    if (i == K) { bb_emit(); return; }
    for (int a = 0; a < bb_c; a++) { bb_a[i] = a; bb_fill(i + 1); }
}

static void bb_dfs(int i) {
    if (bb_over) return;
    const uint64_t *Ui = bb_U + (size_t)i * bb_nw;
    int need = pop_words(Ui, bb_nw);
    if (need == 0) { bb_fill(i); return; }
    if (i == K) return; /* an uncovered new time is a witness: proper */
    int sum = 0;
    for (int j = i; j < K && sum < need; j++) {
        int best = 0;
        for (int a = 0; a < bb_c; a++) {
            int g = pop_and_words(bb_cv + (size_t)(j * bb_c + a) * bb_nw, Ui, bb_nw);
            if (g > best) best = g;
        }
        sum += best;
    }
    if (sum < need) return;
    uint64_t *Un = bb_U + (size_t)(i + 1) * bb_nw;
    for (int a = 0; a < bb_c; a++) {
        const uint64_t *cv = bb_cv + (size_t)(i * bb_c + a) * bb_nw;
        for (int x = 0; x < bb_nw; x++) Un[x] = Ui[x] & ~cv[x];
        bb_a[i] = a;
        bb_dfs(i + 1);
        if (bb_over) return;
    }
}

static int cascade_bb(const int *v, const int *mult, int nlev, long liftcap,
                      long *counts, vecset *final_out) {
    vecset cur = {0}, nxt = {0};
    long long w[MAXK];
    memset(cur_shift, 0, sizeof cur_shift);
    for (int i = 0; i < K; i++) w[i] = v[i];
    long long nofac[1];
    if (is_proper(w, 1, nofac, 0)) return 0;
    vs_push(&cur, w);
    long long l = 1;
    int status = 1;
    for (int li = 0; li < nlev; li++) {
        long long c = mult[li];
        long long L = l * P;
        long long nl = l * c;
        long long Lp = nl * P;
        long long half = Lp / 2;
        int T = 0;
        for (long long b = 1; b <= half; b++) if (b % c) T++;
        long long *tb = malloc((size_t)(T ? T : 1) * sizeof(long long));
        T = 0;
        for (long long b = 1; b <= half; b++) if (b % c) tb[T++] = b;
        int nw = (T + 63) / 64;
        if (nw == 0) nw = 1;
        uint64_t *cvb = calloc((size_t)K * c * nw, sizeof(uint64_t));
        uint64_t *Ub = calloc((size_t)(K + 1) * nw, sizeof(uint64_t));
        if (!tb || !cvb || !Ub) { fprintf(stderr, "out of memory\n"); exit(4); }
        bb_c = (int)c; bb_nw = nw; bb_L = L; bb_cv = cvb; bb_U = Ub;
        bb_l = nl; bb_li = li;
        bb_nfac = prime_factors(nl, bb_fac);
        bb_out = &nxt; bb_liftcap = liftcap; bb_over = 0;
        nxt.n = 0;
        for (long s = 0; s < cur.n; s++) {
            const long long *base = cur.data + (size_t)s * K;
            bb_base = base;
            memset(cvb, 0, (size_t)K * c * nw * sizeof(uint64_t));
            for (int i = 0; i < K; i++)
                for (long long a = 0; a < c; a++) {
                    long long x = (base[i] + a * L) % Lp;
                    uint64_t *dst = cvb + (size_t)(i * c + a) * nw;
                    for (int j = 0; j < T; j++) {
                        long long r = (tb[j] * x) % Lp;
                        long long d = r < Lp - r ? r : Lp - r;
                        if ((long long)(K + 1) * d < Lp) dst[j >> 6] |= 1ULL << (j & 63);
                    }
                }
            memset(Ub, 0, (size_t)nw * sizeof(uint64_t));
            for (int j = 0; j < T; j++) Ub[j >> 6] |= 1ULL << (j & 63);
            bb_dfs(0);
            if (bb_over) { status = -1; break; }
        }
        free(tb); free(cvb); free(Ub);
        counts[li] = nxt.n;
        vecset t = cur; cur = nxt; nxt = t;
        l = nl;
        if (status == -1) break;
        if (cur.n == 0) { status = 0; break; }
    }
    if (final_out && status == 1) {
        for (long s = 0; s < cur.n; s++) vs_push(final_out, cur.data + (size_t)s * K);
    }
    free(cur.data);
    free(nxt.data);
    return status;
}

static int parse_levels(const char *s, int *mult) {
    int n = 0;
    const char *q = s;
    while (*q && n < MAXLEV) {
        mult[n++] = atoi(q);
        while (*q && *q != ',') q++;
        if (*q == ',') q++;
    }
    return n;
}

static void print_tuple_json(const int *v, int s) {
    printf("[");
    for (int i = 0; i < s; i++) printf("%s%d", i ? "," : "", v[i]);
    printf("]");
}

/* ---------------- gate: one level-1 tuple at a time ---------------- */

static int g_list, g_bb, g_nlev, g_cut, g_printed, g_firsts, g_complete;
static int g_mult[MAXLEV];
static long g_liftcap, g_tuples, g_killed, g_survived, g_overflow, g_using;
static long g_maxcount[MAXLEV], g_sumcount[MAXLEV], g_sumshift[MAXLEV];
static double g_t0;

static void gate_tuple(const int *v) {
    if (g_list) {
        printf("T");
        for (int i = 0; i < K; i++) printf(" %d", v[i]);
        printf("\n");
        g_tuples++;
        return;
    }
    long counts[MAXLEV] = {0};
    int st = g_bb ? cascade_bb(v, g_mult, g_nlev, g_liftcap, counts, NULL)
                  : cascade(v, g_mult, g_nlev, g_liftcap, counts, NULL);
    g_tuples++;
    int used = 0;
    for (int j = 0; j < g_nlev; j++) {
        if (counts[j] > g_maxcount[j]) g_maxcount[j] = counts[j];
        g_sumcount[j] += counts[j];
        g_sumshift[j] += cur_shift[j];
        if (cur_shift[j]) used = 1;
    }
    if (used) g_using++;
    if (st == 0) g_killed++;
    else {
        if (st == 1) g_survived++; else g_overflow++;
        if (g_printed < 200) {
            printf("%s{\"tuple\":", g_firsts ? "" : ",");
            print_tuple_json(v, K);
            printf(",\"status\":%d,\"counts\":[", st);
            for (int j = 0; j < g_nlev; j++) printf("%s%ld", j ? "," : "", counts[j]);
            printf("]}");
            g_firsts = 0;
            g_printed++;
        }
    }
    if (timecap > 0 && now() - g_t0 > 3 * timecap) { g_complete = 0; g_cut = 1; }
}

/* complete v[0..s-1] by every non-decreasing sequence of classes >= from */
static void gate_extend(int *v, int s, int from) {
    if (g_cut) return;
    if (s == K) { gate_tuple(v); return; }
    for (int x = from; x <= N; x++) {
        v[s] = x;
        gate_extend(v, s + 1, x);
        if (g_cut) return;
    }
}

/* every stored canonical cover of size K (as is), of size K-1 (with every extra
 * class), and with ext also every smaller cover (with every multiset of extras) */
static void gate_all_tuples(int ext) {
    for (long i = 0; i < nfound && !g_cut; i++) {
        int *c = found + (size_t)i * (MAXK + 1);
        int s = c[0];
        if (s < K - 1 && !ext) continue;
        int v[MAXK];
        memcpy(v, c + 1, s * sizeof(int));
        gate_extend(v, s, 1);
    }
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: lrc covers K P [maxsize] [timecap] [norm] | "
                        "tau K P maxsize [timecap] | "
                        "cascade|cascadebb|scascade|scascadebb K P levels v.. | "
                        "gate K P levels timecap liftcap [norm] [bb] [shift] [ext] | "
                        "tuples K P [ext] [norm] | "
                        "shiftok K P l w..   (environment: LRC_PRUNE=0..3)\n");
        return 1;
    }
    {
        const char *pe = getenv("LRC_PRUNE");
        PRUNE = pe ? atoi(pe) : 0;
    }
    const char *mode = argv[1];
    int k = atoi(argv[2]);
    int p = atoi(argv[3]);
    setup(k, p);
    if (!strcmp(mode, "shiftok")) {
        if (argc < 5 + k) { fprintf(stderr, "need l and K values\n"); return 1; }
        long long l = atoll(argv[4]);
        long long w[MAXK];
        for (int i = 0; i < k; i++) w[i] = atoll(argv[5 + i]);
        printf("D %d\n", shift_ok(w, l));
        return 0;
    }
    if (!strcmp(mode, "covers")) {
        int maxsize = argc > 4 ? atoi(argv[4]) : k;
        double cap = argc > 5 ? atof(argv[5]) : 0;
        int norm = argc > 6 ? atoi(argv[6]) : 0;
        run_covers(maxsize, cap, norm);
        for (long i = 0; i < nfound; i++) {
            int *c = found + (size_t)i * (MAXK + 1);
            printf("C %d", c[0]);
            for (int j = 1; j <= c[0]; j++) printf(" %d", c[j]);
            printf("\n");
        }
        int tau = 0;
        for (int s = 1; s <= maxsize; s++) if (count_by_size[s]) { tau = s; break; }
        long raw = 0;
        for (int s = 1; s <= maxsize; s++) raw += raw_by_size[s];
        printf("S k=%d p=%d n=%d m=%d norm=%d qs=%d nodes=%lld timed_out=%d tau=%d orbits=%ld seconds=%.3f prune=%d raw=%ld\n",
               K, P, N, M, NORM, QS, nodes, timed_out, tau, nfound, now() - tstart, PRUNE, raw);
        return 0;
    }
    if (!strcmp(mode, "tau")) {
        int maxsize = argc > 4 ? atoi(argv[4]) : k;
        double cap = argc > 5 ? atof(argv[5]) : 0;
        if (maxsize > MAXK) maxsize = MAXK;
        double t0 = now();
        long long totnodes = 0;
        int tau = 0, unknown = 0, none_upto = 0;
        int lb = (N + M - 1) / M; /* s classes cover at most s*M times */
        STOPFIRST = 1;
        for (int s = 1; s <= maxsize; s++) {
            if (s < lb) { none_upto = s; continue; }
            double rem = 0;
            if (cap > 0) {
                rem = cap - (now() - t0);
                if (rem <= 0) { unknown = 1; break; }
            }
            run_covers(s, rem, 1);
            totnodes += nodes;
            if (stopnow) { tau = s; break; }
            if (timed_out) { unknown = 1; break; }
            none_upto = s;
        }
        STOPFIRST = 0;
        printf("T k=%d p=%d n=%d m=%d maxsize=%d tau=%d none_upto=%d unknown=%d nodes=%lld seconds=%.3f prune=%d\n",
               K, P, N, M, maxsize, tau, none_upto, unknown, totnodes, now() - t0, PRUNE);
        if (tau) {
            printf("F");
            for (int i = 0; i < nfirst; i++) printf(" %d", firstcov[i]);
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(mode, "cascade") || !strcmp(mode, "cascadebb") ||
        !strcmp(mode, "scascade") || !strcmp(mode, "scascadebb")) {
        int bb = !strcmp(mode, "cascadebb") || !strcmp(mode, "scascadebb");
        SHIFT = mode[0] == 's';
        int mult[MAXLEV];
        int nlev = parse_levels(argv[4], mult);
        if (argc < 5 + k) { fprintf(stderr, "need K classes\n"); return 1; }
        int v[MAXK];
        for (int i = 0; i < k; i++) v[i] = atoi(argv[5 + i]);
        long counts[MAXLEV] = {0};
        vecset fin = {0};
        const char *lcs = getenv("LRC_LIFTCAP");
        long lc = lcs ? atol(lcs) : 50000000L;
        int st = bb ? cascade_bb(v, mult, nlev, lc, counts, &fin)
                    : cascade(v, mult, nlev, lc, counts, &fin);
        long long l = 1;
        for (int i = 0; i < nlev; i++) {
            l *= mult[i];
            printf("L %lld %ld\n", l, counts[i]);
        }
        l = 1;
        for (int i = 0; i < nlev; i++) {
            l *= mult[i];
            printf("X %lld %ld\n", l, cur_shift[i]);
        }
        printf("R %d\n", st);
        for (long s = 0; s < fin.n && s < 50; s++) {
            printf("W");
            for (int i = 0; i < K; i++) printf(" %lld", fin.data[(size_t)s * K + i]);
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(mode, "tuples")) {
        int ext = argc > 4 ? atoi(argv[4]) : 0;
        int norm = argc > 5 ? atoi(argv[5]) : 0;
        run_covers(k, 0, norm);
        g_list = 1;
        g_cut = 0;
        g_tuples = 0;
        g_t0 = now();
        gate_all_tuples(ext);
        long small_orbits = 0;
        for (int s = 1; s <= k - 2; s++) small_orbits += count_by_size[s];
        printf("S k=%d p=%d ext=%d norm=%d tuples=%ld small_orbits=%ld\n",
               K, P, ext, norm, g_tuples, small_orbits);
        return 0;
    }
    if (!strcmp(mode, "gate")) {
        if (argc < 5) { fprintf(stderr, "need levels\n"); return 1; }
        g_nlev = parse_levels(argv[4], g_mult);
        double cap = argc > 5 ? atof(argv[5]) : 0;
        g_liftcap = argc > 6 ? atol(argv[6]) : 2000000L;
        int norm = argc > 7 ? atoi(argv[7]) : 0;
        g_bb = argc > 8 ? atoi(argv[8]) : 0;
        SHIFT = argc > 9 ? atoi(argv[9]) : 0;
        int ext = argc > 10 ? atoi(argv[10]) : 0;
        g_t0 = now();
        run_covers(k, cap, norm);
        double tcov = now() - g_t0;
        int tau = 0;
        for (int s = 1; s <= k; s++) if (count_by_size[s]) { tau = s; break; }
        printf("{\"k\":%d,\"p\":%d,\"n\":%d,\"m\":%d,\"norm\":%d,\"bb\":%d,\"shift\":%d,\"ext\":%d,\"qs\":%d,"
               "\"prune\":%d,\"cover_nodes\":%lld,\"cover_timed_out\":%d,"
               "\"cover_seconds\":%.3f,\"tau\":%d,\"orbits_by_size\":{",
               K, P, N, M, NORM, g_bb, SHIFT, ext, QS, PRUNE, nodes, timed_out, tcov, tau);
        int first = 1;
        for (int s = 1; s <= k; s++) if (count_by_size[s]) {
            printf("%s\"%d\":%ld", first ? "" : ",", s, count_by_size[s]);
            first = 0;
        }
        printf("},\"levels\":[");
        for (int i = 0; i < g_nlev; i++) printf("%s%d", i ? "," : "", g_mult[i]);
        printf("],");
        g_complete = !timed_out;
        long small_orbits = 0;
        for (int s = 1; s <= k - 2; s++) small_orbits += count_by_size[s];
        if (small_orbits && !ext) g_complete = 0;
        g_list = 0;
        g_tuples = g_killed = g_survived = g_overflow = g_using = 0;
        memset(g_maxcount, 0, sizeof g_maxcount);
        memset(g_sumcount, 0, sizeof g_sumcount);
        memset(g_sumshift, 0, sizeof g_sumshift);
        g_firsts = 1;
        g_printed = 0;
        g_cut = 0;
        printf("\"survivors\":[");
        if (!timed_out) gate_all_tuples(ext);
        printf("],\"tuples\":%ld,\"killed\":%ld,\"survived\":%ld,\"overflow\":%ld,\"cascade_cut\":%d,"
               "\"max_improper_by_level\":[", g_tuples, g_killed, g_survived, g_overflow, g_cut);
        for (int j = 0; j < g_nlev; j++) printf("%s%ld", j ? "," : "", g_maxcount[j]);
        printf("],\"sum_improper_by_level\":[");
        for (int j = 0; j < g_nlev; j++) printf("%s%ld", j ? "," : "", g_sumcount[j]);
        printf("],\"shift_removed_by_level\":[");
        for (int j = 0; j < g_nlev; j++) printf("%s%ld", j ? "," : "", g_sumshift[j]);
        printf("],\"tuples_using_shift\":%ld", g_using);
        printf(",\"small_orbits\":%ld,\"small_orbits_unhandled\":%ld,\"complete\":%d,\"total_seconds\":%.3f}\n",
               small_orbits, ext ? 0L : small_orbits, g_complete && g_overflow == 0, now() - g_t0);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 1;
}
