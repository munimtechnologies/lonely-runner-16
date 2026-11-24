/* Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
 * SPDX-License-Identifier: Apache-2.0
 * Made with AI agents working in MV2's name; not yet checked by a human expert.
 *
 * indep_brute.c: the brute-force binary cascade J_p(L) of indep.py (cascade()),
 * written in C, same algorithm and same output order. No pruning, no unit
 * reduction: every lift is tested against every time b in 1..n/2 directly.
 *
 * usage: indep_brute p lmax cap s1 ... sk
 * output: "LEVEL L count [CAP]" then one "Z z1 ... zk" line per stored improper
 *         lift (z = w mod L), for L = 1, 2, 4, ...; finally "END".
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef long long i64;

static int K;
static i64 K1;

static int is_witness(i64 b, const i64 *w, i64 n) {
    for (int i = 0; i < K; i++) {
        i64 r = (b * w[i]) % n;
        i64 d = r < n - r ? r : n - r;
        if (K1 * d < n) return 0;
    }
    return 1;
}

static int proper(const i64 *w, i64 n, i64 L) {
    if (L >= 2) {
        int odd = 0;
        for (int i = 0; i < K; i++)
            if ((w[i] % L) % 2) odd++;
        if (odd <= 1) return 1;
    }
    for (i64 b = 1; b <= n / 2; b++)
        if (is_witness(b, w, n)) return 1;
    return 0;
}

static void print_z(const i64 *w, i64 L) {
    fputs("Z", stdout);
    for (int i = 0; i < K; i++) printf(" %lld", w[i] % L);
    fputs("\n", stdout);
}

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s p lmax cap s1 ... sk\n", argv[0]);
        return 2;
    }
    i64 p = atoll(argv[1]);
    i64 lmax = atoll(argv[2]);
    long long cap = atoll(argv[3]);
    K = argc - 4;
    if (K < 1 || K > 30 || cap < 1 || p < 2 || lmax < 1) {
        fprintf(stderr, "bad arguments\n");
        return 2;
    }
    K1 = K + 1;
    i64 *cur = malloc(sizeof(i64) * (size_t)K * (size_t)cap);
    i64 *nxt = malloc(sizeof(i64) * (size_t)K * (size_t)cap);
    if (!cur || !nxt) {
        fprintf(stderr, "out of memory\n");
        return 3;
    }
    for (int i = 0; i < K; i++) {
        i64 x = atoll(argv[4 + i]) % p;
        if (x < 0) x += p;
        cur[i] = x;
    }
    if (proper(cur, p, 1)) {
        printf("LEVEL 1 0\nEND\n");
        return 0;
    }
    printf("LEVEL 1 1\n");
    print_z(cur, 1);
    long long ncur = 1;
    i64 L = 1;
    i64 w[32];
    while (2 * L <= lmax && ncur > 0) {
        i64 n = 2 * L * p, step = L * p;
        long long count = 0, nstore = 0;
        for (long long a = 0; a < ncur; a++) {
            const i64 *par = cur + (size_t)a * K;
            for (long long mask = 0; mask < (1LL << K); mask++) {
                for (int i = 0; i < K; i++)
                    w[i] = ((mask >> i) & 1) ? (par[i] + step) % n : par[i];
                if (!proper(w, n, 2 * L)) {
                    if (nstore < cap) {
                        memcpy(nxt + (size_t)nstore * K, w, sizeof(i64) * K);
                        nstore++;
                    }
                    count++;
                }
            }
        }
        L *= 2;
        printf("LEVEL %lld %lld%s\n", L, count, count > nstore ? " CAP" : "");
        for (long long a = 0; a < nstore; a++) print_z(nxt + (size_t)a * K, L);
        if (count > nstore) break;
        i64 *t = cur;
        cur = nxt;
        nxt = t;
        ncur = nstore;
    }
    printf("END\n");
    fflush(stdout);
    free(cur);
    free(nxt);
    return 0;
}
