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
 * Modes:
 *   lrc covers K P [maxsize] [timecap_s] [norm]
 *   lrc cascade K P L1,L2,.. v1 .. vK          (brute-force lifting)
 *   lrc cascadebb K P L1,L2,.. v1 .. vK        (branch-and-bound lifting)
 *       print "L level count" per level, "R status", up to 50 "W w1..wK".
 *   lrc gate K P L1,L2,.. timecap_s liftcap [norm] [bb]
 *       covers + cascade for every canonical cover of size K and, for covers of
 *       size K-1, for every extra class x; prints one JSON object.
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

/* canonical covers found */
static int *found;      /* flattened, each entry MAXK+1 ints: size then classes */
static long nfound, capfound;
static long count_by_size[MAXK + 2];
static long raw_by_size[MAXK + 2];

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

static void search(void) {
    nodes++;
    if ((nodes & 0xFFFF) == 0 && timecap > 0 && now() - tstart > timecap) timed_out = 1;
    if (timed_out) return;
    if (npriv0) return;
    if (NORM && pc[1] < QS) return; /* private counts only fall as classes are added */
    int U = bs_pop(&uncov);
    if (U == 0) { report(); return; }
    int b = MAXSIZE - nch;
    if (b <= 0) return;
    if ((long long)b * M < U) return;
    /* bound: sum of the b largest gains among allowed classes must reach U */
    int top[MAXK + 1];
    int nt = 0;
    for (int v = 1; v <= N; v++) {
        if (!bs_get(&allowed, v)) continue;
        int g = bs_pop_and(&cov[v], &uncov);
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
        if (timed_out) break;
    }
    for (int i = 0; i < nc; i++) bs_set(&allowed, cands[i]);
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
 * -1 on overflow; counts[i] receives the number of improper lifts at level i. */
static int cascade(const int *v, const int *mult, int nlev, long liftcap,
                   long *counts, vecset *final_out) {
    vecset cur = {0}, nxt = {0};
    long long w[MAXK], w2[MAXK];
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
                    vs_push(&nxt, w2);
                    if (nxt.n > liftcap) { status = -1; break; }
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

static int bb_c, bb_nw, bb_nfac, bb_over;
static long long bb_L;
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

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: lrc covers K P [maxsize] [timecap] [norm] | cascade|cascadebb K P levels v.. | gate K P levels timecap liftcap [norm] [bb]\n");
        return 1;
    }
    const char *mode = argv[1];
    int k = atoi(argv[2]);
    int p = atoi(argv[3]);
    setup(k, p);
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
        printf("S k=%d p=%d n=%d m=%d norm=%d qs=%d nodes=%lld timed_out=%d tau=%d orbits=%ld seconds=%.3f\n",
               K, P, N, M, NORM, QS, nodes, timed_out, tau, nfound, now() - tstart);
        return 0;
    }
    if (!strcmp(mode, "cascade") || !strcmp(mode, "cascadebb")) {
        int bb = !strcmp(mode, "cascadebb");
        int mult[MAXLEV];
        int nlev = parse_levels(argv[4], mult);
        if (argc < 5 + k) { fprintf(stderr, "need K classes\n"); return 1; }
        int v[MAXK];
        for (int i = 0; i < k; i++) v[i] = atoi(argv[5 + i]);
        long counts[MAXLEV] = {0};
        vecset fin = {0};
        int st = bb ? cascade_bb(v, mult, nlev, 50000000L, counts, &fin)
                    : cascade(v, mult, nlev, 50000000L, counts, &fin);
        long long l = 1;
        for (int i = 0; i < nlev; i++) {
            l *= mult[i];
            printf("L %lld %ld\n", l, counts[i]);
        }
        printf("R %d\n", st);
        for (long s = 0; s < fin.n && s < 50; s++) {
            printf("W");
            for (int i = 0; i < K; i++) printf(" %lld", fin.data[(size_t)s * K + i]);
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(mode, "gate")) {
        int mult[MAXLEV];
        int nlev = parse_levels(argv[4], mult);
        double cap = argc > 5 ? atof(argv[5]) : 0;
        long liftcap = argc > 6 ? atol(argv[6]) : 2000000L;
        int norm = argc > 7 ? atoi(argv[7]) : 0;
        int bb = argc > 8 ? atoi(argv[8]) : 0;
        double t0 = now();
        run_covers(k, cap, norm);
        double tcov = now() - t0;
        int tau = 0;
        for (int s = 1; s <= k; s++) if (count_by_size[s]) { tau = s; break; }
        printf("{\"k\":%d,\"p\":%d,\"n\":%d,\"m\":%d,\"norm\":%d,\"bb\":%d,\"qs\":%d,"
               "\"cover_nodes\":%lld,\"cover_timed_out\":%d,"
               "\"cover_seconds\":%.3f,\"tau\":%d,\"orbits_by_size\":{",
               K, P, N, M, NORM, bb, QS, nodes, timed_out, tcov, tau);
        int first = 1;
        for (int s = 1; s <= k; s++) if (count_by_size[s]) {
            printf("%s\"%d\":%ld", first ? "" : ",", s, count_by_size[s]);
            first = 0;
        }
        printf("},\"levels\":[");
        for (int i = 0; i < nlev; i++) printf("%s%d", i ? "," : "", mult[i]);
        printf("],");
        int complete = !timed_out;
        long small_orbits = 0;
        for (int s = 1; s <= k - 2; s++) small_orbits += count_by_size[s];
        if (small_orbits) complete = 0;
        long tuples = 0, killed = 0, survived = 0, overflow = 0;
        long maxcount[MAXLEV] = {0};
        long sumcount[MAXLEV] = {0};
        printf("\"survivors\":[");
        int firsts = 1;
        int printed = 0;
        int cut = 0;
        if (!timed_out) {
            for (long i = 0; i < nfound && !cut; i++) {
                int *c = found + (size_t)i * (MAXK + 1);
                int s = c[0];
                if (s < k - 1) continue;
                int xlo = 1, xhi = N;
                if (s == k) { xlo = 0; xhi = 0; }
                for (int x = xlo; x <= xhi; x++) {
                    int v[MAXK];
                    memcpy(v, c + 1, s * sizeof(int));
                    if (s == k - 1) v[k - 1] = x;
                    long counts[MAXLEV] = {0};
                    int st = bb ? cascade_bb(v, mult, nlev, liftcap, counts, NULL)
                                : cascade(v, mult, nlev, liftcap, counts, NULL);
                    tuples++;
                    for (int j = 0; j < nlev; j++) {
                        if (counts[j] > maxcount[j]) maxcount[j] = counts[j];
                        sumcount[j] += counts[j];
                    }
                    if (st == 0) killed++;
                    else {
                        if (st == 1) survived++; else overflow++;
                        if (printed < 200) {
                            printf("%s{\"tuple\":", firsts ? "" : ",");
                            print_tuple_json(v, k);
                            printf(",\"status\":%d,\"counts\":[", st);
                            for (int j = 0; j < nlev; j++) printf("%s%ld", j ? "," : "", counts[j]);
                            printf("]}");
                            firsts = 0;
                            printed++;
                        }
                    }
                    if (timecap > 0 && now() - t0 > 3 * timecap) { complete = 0; cut = 1; break; }
                }
            }
        }
        printf("],\"tuples\":%ld,\"killed\":%ld,\"survived\":%ld,\"overflow\":%ld,\"cascade_cut\":%d,"
               "\"max_improper_by_level\":[", tuples, killed, survived, overflow, cut);
        for (int j = 0; j < nlev; j++) printf("%s%ld", j ? "," : "", maxcount[j]);
        printf("],\"sum_improper_by_level\":[");
        for (int j = 0; j < nlev; j++) printf("%s%ld", j ? "," : "", sumcount[j]);
        printf("],\"small_orbits_unhandled\":%ld,\"complete\":%d,\"total_seconds\":%.3f}\n",
               small_orbits, complete && overflow == 0, now() - t0);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 1;
}
