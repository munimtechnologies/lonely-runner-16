/* Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
 * SPDX-License-Identifier: Apache-2.0
 * Made with AI agents working in MV2's name; not yet checked by a human expert.
 *
 * nbc.c: the branch and bound of nbc.dfs_py (uniform_nb.lift_children with the
 * unit-symmetry reduction of THEORY_17), node for node, in C.
 *
 *   nbc SECONDS < spec        (SECONDS = 0: no time limit)
 *
 * spec (whitespace-separated integers, written by nbc.spec_text):
 *   K C L2 P Q USEGCD SYM NPR primes[NPR] W NB
 *   vals[K][C]                       (search order)
 *   NB times: M lengths[M] big[W] masks[K][C][W]
 * Output: one line "Z v_0 ... v_{K-1}" per surviving child (search order), then
 * "END DONE|CUT nodes leaves nout".
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef unsigned long long u64;

static int K, C, L2, NB, W, SYM, NPR, USEGCD;
static long long PV, QQ;
static int primes[64];
static int *vals;
static int *Mc;
static long long **lens;
static u64 *big, *masks, *suf, *cur;
static int choice[128];
static u64 nodes = 0, leaves = 0, nout = 0;
static double tlimit = 0.0, t0 = 0.0;
static int cut = 0;

#define MASK(j, d, a) (masks + ((((size_t)(j) * K + (d)) * C + (a)) * W))
#define SUF(j, d) (suf + (((size_t)(j) * (K + 1) + (d)) * W))
#define CUR(d, j) (cur + (((size_t)(d) * NB + (j)) * W))
#define BIG(j) (big + (size_t)(j) * W)

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static void die(const char *m) {
    fprintf(stderr, "nbc: %s\n", m);
    exit(2);
}
static int rd_i(void) {
    int x;
    if (scanf("%d", &x) != 1) die("bad input (int)");
    return x;
}
static long long rd_ll(void) {
    long long x;
    if (scanf("%lld", &x) != 1) die("bad input (long)");
    return x;
}
static u64 rd_u(void) {
    u64 x;
    if (scanf("%llu", &x) != 1) die("bad input (word)");
    return x;
}

static int bit(const u64 *v, int i) { return (int)((v[i >> 6] >> (i & 63)) & 1ULL); }

/* uniform.Cells.killed: does beta j give a witness for the covered set orv? */
static int killed_beta(int j, const u64 *orv) {
    int m = Mc[j], i, t, c0 = -1, anyunc = 0;
    long long run = 0;
    if (!bit(orv, m)) return 1; /* t = 0 is an exact witness */
    for (i = 0; i < m; i++) {
        if (bit(orv, i)) {
            if (c0 < 0) c0 = i;
        } else {
            anyunc = 1;
        }
    }
    if (!anyunc) return 0;
    if (PV == 0) return 1;
    if (c0 < 0) return 1; /* nothing covered */
    for (t = 1; t <= m; t++) {
        i = (c0 + t) % m;
        if (bit(orv, i)) {
            run = 0;
        } else {
            run += lens[j][i];
            if (run * PV > QQ) return 1;
        }
    }
    return 0;
}

static void leaf(void) {
    int q, d, j;
    leaves++;
    if (USEGCD) {
        for (q = 0; q < NPR; q++) {
            int cnt = 0;
            for (d = 0; d < K; d++)
                if (vals[d * C + choice[d]] % primes[q]) cnt++;
            if (cnt <= 1) return;
        }
    }
    for (j = 0; j < NB; j++)
        if (killed_beta(j, CUR(K, j))) return;
    printf("Z");
    for (d = 0; d < K; d++) printf(" %d", vals[d * C + choice[d]]);
    printf("\n");
    nout++;
}

static void dfs(int d, int nz) {
    int j, w, a;
    if (cut) return;
    nodes++;
    if ((nodes & 0xFFFFULL) == 0 && tlimit > 0 && now() - t0 > tlimit) {
        cut = 1;
        return;
    }
    for (j = 0; j < NB; j++) {
        const u64 *cu = CUR(d, j), *sf = SUF(j, d), *bg = BIG(j);
        for (w = 0; w < W; w++)
            if (((cu[w] | sf[w]) & bg[w]) != bg[w]) return;
    }
    if (d == K) {
        leaf();
        return;
    }
    for (a = 0; a < C; a++) {
        int nz2 = nz;
        if (SYM) {
            int y = vals[d * C + a] % C;
            if (!nz && y > 1) continue;
            if (y) nz2 = 1;
        }
        choice[d] = a;
        for (j = 0; j < NB; j++) {
            const u64 *cu = CUR(d, j), *mk = MASK(j, d, a);
            u64 *nx = CUR(d + 1, j);
            for (w = 0; w < W; w++) nx[w] = cu[w] | mk[w];
        }
        dfs(d + 1, nz2);
        if (cut) return;
    }
}

int main(int argc, char **argv) {
    int i, j, d, a, w;
    if (argc > 1) tlimit = atof(argv[1]);
    K = rd_i();
    C = rd_i();
    L2 = rd_i();
    PV = rd_ll();
    QQ = rd_ll();
    USEGCD = rd_i();
    SYM = rd_i();
    NPR = rd_i();
    if (K < 1 || K > 120 || C < 1 || NPR < 0 || NPR > 64) die("bad header");
    for (i = 0; i < NPR; i++) primes[i] = rd_i();
    W = rd_i();
    NB = rd_i();
    if (W < 1 || NB < 0) die("bad sizes");
    vals = malloc(sizeof(int) * (size_t)K * C);
    for (i = 0; i < K * C; i++) vals[i] = rd_i();
    Mc = malloc(sizeof(int) * (size_t)(NB + 1));
    lens = malloc(sizeof(long long *) * (size_t)(NB + 1));
    big = calloc((size_t)(NB + 1) * W, sizeof(u64));
    masks = calloc((size_t)(NB + 1) * K * C * W, sizeof(u64));
    suf = calloc((size_t)(NB + 1) * (K + 1) * W, sizeof(u64));
    cur = calloc((size_t)(K + 1) * (NB + 1) * W, sizeof(u64));
    if (!vals || !Mc || !lens || !big || !masks || !suf || !cur) die("out of memory");
    for (j = 0; j < NB; j++) {
        Mc[j] = rd_i();
        if (Mc[j] < 2 || Mc[j] + 1 > 64 * W) die("bad M");
        lens[j] = malloc(sizeof(long long) * (size_t)Mc[j]);
        for (i = 0; i < Mc[j]; i++) lens[j][i] = rd_ll();
        for (w = 0; w < W; w++) BIG(j)[w] = rd_u();
        for (d = 0; d < K; d++)
            for (a = 0; a < C; a++)
                for (w = 0; w < W; w++) MASK(j, d, a)[w] = rd_u();
        for (d = K - 1; d >= 0; d--)
            for (w = 0; w < W; w++) {
                u64 u = SUF(j, d + 1)[w];
                for (a = 0; a < C; a++) u |= MASK(j, d, a)[w];
                SUF(j, d)[w] = u;
            }
    }
    t0 = now();
    dfs(0, 0);
    printf("END %s %llu %llu %llu\n", cut ? "CUT" : "DONE", nodes, leaves, nout);
    return 0;
}
