// pp_model.h — bit-exact C++ port of the ppfilter fault model
// (ecdsa-ppfilter-rl/src/bin/ppfilter.rs md5 f19ad08ddd00210942dd380d1fec81f2,
// ROUNDS_DIV=696, ROUNDS_MUL=696), retargeted to the E007 Q1272 stream at
// source commit ea93a131e2bc488bff6fa12010d1f3606c7771b0. The
// Rust circuit maps each walk round r to floor(r * 703 / 695) in the sampled
// 704-round width schedule for both divide and multiply traversals.
// Pure integer code; compiles under g++/clang++ (host CPU reference) and
// nvcc (host+device). No CUDA keywords live here.
//
// Provenance: every function is a line-level port of the Rust oracle.
// ROUNDS_MUL is fixed to 696 (hunt target; the Rust oracle's
// PPF_ROUNDS_MUL=696 env override selects the same value).
#pragma once

#include <cstdint>
#include <cstddef>
#include <cstring>

#ifdef __CUDACC__
#define PP_HD __host__ __device__ __forceinline__
#else
#define PP_HD inline
#endif

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef unsigned __int128 u128;

// ─── secp256k1 field arithmetic ─────────────────────────────────────────────

// PP_P4: secp256k1 prime initializer; materialize as a local const array at
// each use site (namespace-scope arrays are not addressable in device code).
#define PP_P4_INIT {0xFFFFFFFEFFFFFC2FULL, 0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL}
#define PP_P4(name) const u64 name[4] = PP_P4_INIT
#define PP_FC 0x1000003D1ULL // 2^32 + 977 = 2^256 - p
#define PP_MASK54 ((1ULL << 54) - 1)

PP_HD void pp_fadd(const u64 a[4], const u64 b[4], u64 s[4]) {
    PP_P4(P);
    u128 carry = 0;
    for (int i = 0; i < 4; i++) {
        u128 cur = (u128)a[i] + b[i] + carry;
        s[i] = (u64)cur;
        carry = cur >> 64;
    }
    if (carry == 1) {
        u128 c2 = (u128)PP_FC;
        for (int i = 0; i < 4; i++) {
            u128 cur = (u128)s[i] + c2;
            s[i] = (u64)cur;
            c2 = cur >> 64;
        }
    } else {
        // ge(&s, &P) -> subtract
        bool geq = true;
        for (int i = 3; i >= 0; i--) {
            if (s[i] != P[i]) { geq = s[i] > P[i]; break; }
        }
        if (geq) {
            u64 borrow = 0;
            for (int i = 0; i < 4; i++) {
                u128 cur = ((u128)1 << 64) + s[i] - P[i] - borrow;
                s[i] = (u64)cur;
                borrow = 1 - (u64)(cur >> 64);
            }
        }
    }
}

PP_HD void pp_sub_limbs(const u64 a[4], const u64 b[4], u64 d[4], u64* borrow_out) {
    u64 borrow = 0;
    for (int i = 0; i < 4; i++) {
        u128 cur = ((u128)1 << 64) + a[i] - b[i] - borrow;
        d[i] = (u64)cur;
        borrow = 1 - (u64)(cur >> 64);
    }
    *borrow_out = borrow;
}

PP_HD void pp_fsub(const u64 a[4], const u64 b[4], u64 out[4]) {
    PP_P4(P);
    u64 d[4], borrow;
    pp_sub_limbs(a, b, d, &borrow);
    if (borrow == 1) {
        u128 carry = 0;
        for (int i = 0; i < 4; i++) {
            u128 cur = (u128)d[i] + P[i] + carry;
            d[i] = (u64)cur;
            carry = cur >> 64;
        }
    }
    for (int i = 0; i < 4; i++) out[i] = d[i];
}

PP_HD bool pp_ge(const u64 a[4], const u64 b[4]) {
    for (int i = 3; i >= 0; i--) {
        if (a[i] != b[i]) return a[i] > b[i];
    }
    return true;
}

PP_HD bool pp_is_zero(const u64 a[4]) {
    return (a[0] | a[1] | a[2] | a[3]) == 0;
}

PP_HD bool pp_eq(const u64 a[4], const u64 b[4]) {
    return a[0] == b[0] && a[1] == b[1] && a[2] == b[2] && a[3] == b[3];
}

// Reduce a 512-bit product mod p via pseudo-Mersenne folding.
PP_HD void pp_reduce8(const u64 r[8], u64 out[4]) {
    u64 s[5];
    u128 carry = 0;
    for (int i = 0; i < 4; i++) {
        u128 cur = (u128)r[i] + (u128)r[4 + i] * PP_FC + carry;
        s[i] = (u64)cur;
        carry = cur >> 64;
    }
    s[4] = (u64)carry;
    u128 c2 = (u128)s[4] * PP_FC;
    for (int i = 0; i < 4; i++) {
        u128 cur = (u128)s[i] + c2;
        out[i] = (u64)cur;
        c2 = cur >> 64;
    }
    while (c2 > 0) {
        u128 c3 = (u128)PP_FC;
        for (int i = 0; i < 4; i++) {
            u128 cur = (u128)out[i] + c3;
            out[i] = (u64)cur;
            c3 = cur >> 64;
        }
        c2 = c2 - 1 + c3;
    }
    PP_P4(P);
    if (pp_ge(out, P)) {
        u64 b;
        pp_sub_limbs(out, P, out, &b);
    }
}

PP_HD void pp_fmul(const u64 a[4], const u64 b[4], u64 out[4]) {
    u64 r[8];
    for (int i = 0; i < 8; i++) r[i] = 0;
    for (int i = 0; i < 4; i++) {
        u128 carry = 0;
        for (int j = 0; j < 4; j++) {
            u128 cur = (u128)r[i + j] + (u128)a[i] * b[j] + carry;
            r[i + j] = (u64)cur;
            carry = cur >> 64;
        }
        r[i + 4] = (u64)carry;
    }
    pp_reduce8(r, out);
}

PP_HD void pp_fsq(const u64 a[4], u64 out[4]) { pp_fmul(a, a, out); }

PP_HD void pp_finv(const u64 a[4], u64 out[4]) {
    static const u64 PM2[4] = {
        0xFFFFFFFEFFFFFC2DULL,
        0xFFFFFFFFFFFFFFFFULL,
        0xFFFFFFFFFFFFFFFFULL,
        0xFFFFFFFFFFFFFFFFULL,
    };
    u64 r[4] = {1, 0, 0, 0};
    for (int i = 255; i >= 0; i--) {
        pp_fsq(r, r);
        if ((PM2[i / 64] >> (i % 64)) & 1) {
            u64 t[4];
            pp_fmul(r, a, t);
            for (int k = 0; k < 4; k++) r[k] = t[k];
        }
    }
    for (int i = 0; i < 4; i++) out[i] = r[i];
}

// ─── Jacobian point arithmetic (a = 0) ──────────────────────────────────────

struct PP_Jac {
    u64 x[4], y[4], z[4]; // zero z = infinity
};

static const u64 PP_GX[4] = {
    0x59F2815B16F81798ULL, 0x029BFCDB2DCE28D9ULL,
    0x55A06295CE870B07ULL, 0x79BE667EF9DCBBACULL,
};
static const u64 PP_GY[4] = {
    0x9C47D08FFB10D4B8ULL, 0xFD17B448A6855419ULL,
    0x5DA4FBFC0E1108A8ULL, 0x483ADA7726A3C465ULL,
};

PP_HD void pp_jac_inf(PP_Jac* p) {
    memset(p, 0, sizeof(*p));
}

PP_HD bool pp_jac_is_inf(const PP_Jac* p) { return pp_is_zero(p->z); }

PP_HD void pp_jdbl(const PP_Jac* p, PP_Jac* r) {
    if (pp_jac_is_inf(p) || pp_is_zero(p->y)) {
        pp_jac_inf(r);
        return;
    }
    u64 xx[4], yy[4], yyyy[4], t[4], s[4], m[4], s2[4], x3[4], y3[4], zz[4], z3[4], t2[4], t3[4];
    pp_fsq(p->x, xx);
    pp_fsq(p->y, yy);
    pp_fsq(yy, yyyy);
    pp_fadd(p->x, yy, t);
    pp_fsq(t, t);
    pp_fsub(t, xx, s);
    pp_fsub(s, yyyy, s);
    pp_fadd(s, s, s);
    pp_fadd(xx, xx, m);
    pp_fadd(m, xx, m);
    pp_fadd(s, s, s2);
    pp_fsq(m, x3);
    pp_fsub(x3, s2, x3);
    pp_fsub(s, x3, t2);
    pp_fmul(m, t2, t2);
    static const u64 EIGHT[4] = {8, 0, 0, 0};
    pp_fmul(yyyy, EIGHT, t3);
    pp_fsub(t2, t3, y3);
    pp_fsq(p->z, zz);
    pp_fadd(p->y, p->z, t);
    pp_fsq(t, t);
    pp_fsub(t, yy, t);
    pp_fsub(t, zz, z3);
    for (int i = 0; i < 4; i++) { r->x[i] = x3[i]; r->y[i] = y3[i]; r->z[i] = z3[i]; }
}

// Jacobian += affine. Matches the reference affine group law on all inputs.
PP_HD void pp_jadd_mixed(const PP_Jac* p, const u64 qx[4], const u64 qy[4], PP_Jac* r) {
    if (pp_jac_is_inf(p)) {
        for (int i = 0; i < 4; i++) { r->x[i] = qx[i]; r->y[i] = qy[i]; r->z[i] = (i == 0); }
        return;
    }
    u64 z1z1[4], u2[4], s2[4], h[4], rr[4];
    pp_fsq(p->z, z1z1);
    pp_fmul(qx, z1z1, u2);
    u64 t[4];
    pp_fmul(p->z, z1z1, t);
    pp_fmul(qy, t, s2);
    pp_fsub(u2, p->x, h);
    pp_fsub(s2, p->y, rr);
    if (pp_is_zero(h)) {
        if (pp_is_zero(rr)) {
            PP_Jac q;
            for (int i = 0; i < 4; i++) { q.x[i] = qx[i]; q.y[i] = qy[i]; q.z[i] = (i == 0); }
            pp_jdbl(&q, r);
            return;
        }
        pp_jac_inf(r);
        return;
    }
    u64 hh[4], hhh[4], v[4], v2[4], x3[4], y3[4], z3[4], t2[4];
    pp_fsq(h, hh);
    pp_fmul(h, hh, hhh);
    pp_fmul(p->x, hh, v);
    pp_fadd(v, v, v2);
    pp_fsq(rr, x3);
    pp_fsub(x3, hhh, x3);
    pp_fsub(x3, v2, x3);
    pp_fsub(v, x3, t2);
    pp_fmul(rr, t2, y3);
    pp_fmul(p->y, hhh, t2);
    pp_fsub(y3, t2, y3);
    pp_fmul(p->z, h, z3);
    for (int i = 0; i < 4; i++) { r->x[i] = x3[i]; r->y[i] = y3[i]; r->z[i] = z3[i]; }
}

// ─── fixed-base comb ────────────────────────────────────────────────────────
// table[j][d] = d * 2^(8j) * G affine, d in 1..=255 stored at index
// (j*255 + d-1)*8 (x[4] then y[4]).

#define PP_COMB_W 8
#define PP_COMB_WINDOWS 32

PP_HD void pp_comb_mul(const u64* table, const u8 k[32], PP_Jac* acc) {
    pp_jac_inf(acc);
    for (int j = 0; j < PP_COMB_WINDOWS; j++) {
        u32 d = k[j];
        if (d != 0) {
            const u64* e = table + (size_t)(j * 255 + (int)d - 1) * 8;
            PP_Jac r;
            pp_jadd_mixed(acc, e, e + 4, &r);
            *acc = r;
        }
    }
}

// ─── SHAKE256 with checkpointable state ─────────────────────────────────────

#define PP_RATE 136

#ifdef PP_TABLES_UNUSED
static const u64 PP_RC[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808AULL,
    0x8000000080008000ULL, 0x000000000000808BULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008AULL,
    0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000AULL,
    0x000000008000808BULL, 0x800000000000008BULL, 0x8000000000008089ULL,
    0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800AULL, 0x800000008000000AULL, 0x8000000080008081ULL,
    0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL,
};
static const u32 PP_ROTC[24] = {
    1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14, 27, 41, 56, 8, 25, 43, 62, 18,
    39, 61, 20, 44,
};
static const int PP_PILN[24] = {
    10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4, 15, 23, 19, 13, 12, 2, 20, 14,
    22, 9, 6, 1,
};
#endif // PP_TABLES_UNUSED

PP_HD u64 pp_rotl64(u64 x, int n) { return (x << n) | (x >> (64 - n)); }

PP_HD void pp_keccak_f(u64 st[25]) {
    const u64 RC[24] = {
        0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808AULL,
        0x8000000080008000ULL, 0x000000000000808BULL, 0x0000000080000001ULL,
        0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008AULL,
        0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000AULL,
        0x000000008000808BULL, 0x800000000000008BULL, 0x8000000000008089ULL,
        0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
        0x000000000000800AULL, 0x800000008000000AULL, 0x8000000080008081ULL,
        0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL,
    };
    const u32 ROTC[24] = {
        1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14, 27, 41, 56, 8, 25, 43, 62,
        18, 39, 61, 20, 44,
    };
    const int PILN[24] = {
        10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4, 15, 23, 19, 13, 12, 2, 20,
        14, 22, 9, 6, 1,
    };
#pragma unroll
    for (int round = 0; round < 24; round++) {
        u64 bc[5];
        for (int i = 0; i < 5; i++)
            bc[i] = st[i] ^ st[i + 5] ^ st[i + 10] ^ st[i + 15] ^ st[i + 20];
        for (int i = 0; i < 5; i++) {
            u64 t = bc[(i + 4) % 5] ^ pp_rotl64(bc[(i + 1) % 5], 1);
            for (int j = 0; j < 25; j += 5) st[j + i] ^= t;
        }
        u64 t = st[1];
#pragma unroll
        for (int i = 0; i < 24; i++) {
            int j = PILN[i];
            u64 tmp = st[j];
            st[j] = pp_rotl64(t, (int)ROTC[i]);
            t = tmp;
        }
        for (int j = 0; j < 25; j += 5) {
            u64 row[5];
            for (int i = 0; i < 5; i++) row[i] = st[j + i];
            for (int i = 0; i < 5; i++)
                st[j + i] = row[i] ^ ((~row[(i + 1) % 5]) & row[(i + 2) % 5]);
        }
        st[0] ^= RC[round];
    }
}

struct PP_Shake {
    u64 st[25];
    int n;         // absorbed bytes in the current block
    bool squeezing;
    int pos;       // squeeze position within the current block
};

PP_HD void pp_shake_new(PP_Shake* s) {
    for (int i = 0; i < 25; i++) s->st[i] = 0;
    s->n = 0;
    s->squeezing = false;
    s->pos = 0;
}

PP_HD void pp_shake_xor_byte(PP_Shake* s, int i, u8 b) {
    s->st[i / 8] ^= ((u64)b) << (8 * (i % 8));
}

PP_HD u8 pp_shake_get_byte(const PP_Shake* s, int i) {
    return (u8)(s->st[i / 8] >> (8 * (i % 8)));
}

PP_HD void pp_shake_absorb(PP_Shake* s, const u8* data, size_t len) {
    if (s->n > 0) {
        size_t take = (size_t)(PP_RATE - s->n) < len ? (size_t)(PP_RATE - s->n) : len;
        for (size_t k = 0; k < take; k++) pp_shake_xor_byte(s, s->n + (int)k, data[k]);
        s->n += (int)take;
        data += take;
        len -= take;
        if (s->n == PP_RATE) {
            pp_keccak_f(s->st);
            s->n = 0;
        }
    }
    while (len >= PP_RATE) {
        for (int i = 0; i < PP_RATE / 8; i++) {
            u64 b;
            memcpy(&b, data + i * 8, 8);
            s->st[i] ^= b;
        }
        pp_keccak_f(s->st);
        data += PP_RATE;
        len -= PP_RATE;
    }
    for (size_t k = 0; k < len; k++) {
        pp_shake_xor_byte(s, s->n, data[k]);
        s->n += 1;
    }
}

PP_HD void pp_shake_finalize(PP_Shake* s) {
    pp_shake_xor_byte(s, s->n, 0x1F);
    pp_shake_xor_byte(s, PP_RATE - 1, 0x80);
    pp_keccak_f(s->st);
    s->squeezing = true;
    s->pos = 0;
}

PP_HD void pp_shake_read(PP_Shake* s, u8* out, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (s->pos == PP_RATE) {
            pp_keccak_f(s->st);
            s->pos = 0;
        }
        out[i] = pp_shake_get_byte(s, s->pos);
        s->pos += 1;
    }
}

// ─── 320-bit signed walk arithmetic ─────────────────────────────────────────

#define PP_LIMBS 5

struct PP_S320 {
    u64 v[PP_LIMBS];
};

PP_HD PP_S320 pp_s320_from_u256(const u64 l[4]) {
    PP_S320 r;
    for (int i = 0; i < 4; i++) r.v[i] = l[i];
    r.v[4] = 0;
    return r;
}

PP_HD void pp_s320_add(PP_S320* a, const PP_S320* o) {
    bool carry = false;
    for (int i = 0; i < PP_LIMBS; i++) {
        u64 r1 = a->v[i] + o->v[i];
        bool c1 = r1 < a->v[i];
        u64 r2 = r1 + (carry ? 1 : 0);
        bool c2 = r2 < r1;
        a->v[i] = r2;
        carry = c1 || c2;
    }
}

PP_HD void pp_s320_sub(PP_S320* a, const PP_S320* o) {
    bool borrow = false;
    for (int i = 0; i < PP_LIMBS; i++) {
        u64 r1 = a->v[i] - o->v[i];
        bool b1 = r1 > a->v[i];
        u64 r2 = r1 - (borrow ? 1 : 0);
        bool b2 = r2 > r1;
        a->v[i] = r2;
        borrow = b1 || b2;
    }
}

PP_HD void pp_s320_shr1(PP_S320* a) {
    for (int i = 0; i < PP_LIMBS - 1; i++)
        a->v[i] = (a->v[i] >> 1) | (a->v[i + 1] << 63);
    a->v[PP_LIMBS - 1] = (u64)(((int64_t)a->v[PP_LIMBS - 1]) >> 1);
}

PP_HD void pp_s320_shl1(PP_S320* a) {
    for (int i = PP_LIMBS - 1; i >= 1; i--)
        a->v[i] = (a->v[i] << 1) | (a->v[i - 1] >> 63);
    a->v[0] <<= 1;
}

PP_HD u64 pp_s320_bit1(const PP_S320* a) { return (a->v[0] >> 1) & 1; }

PP_HD u32 pp_clzll(u64 x) {
#ifdef __CUDA_ARCH__
    return (u32)__clzll((unsigned long long)x);
#else
    return (u32)__builtin_clzll(x);
#endif
}

// Minimal signed two's-complement width holding this value.
PP_HD u32 pp_s320_swidth(const PP_S320* a) {
    u64 sign = a->v[PP_LIMBS - 1] >> 63;
    for (int i = PP_LIMBS - 1; i >= 0; i--) {
        u64 diff = sign == 1 ? ~a->v[i] : a->v[i];
        if (diff != 0) {
            u32 pos = 63 - pp_clzll(diff);
            return (u32)i * 64 + pos + 2;
        }
    }
    return 1;
}

PP_HD bool pp_s320_is_neg(const PP_S320* a) { return (a->v[PP_LIMBS - 1] >> 63) == 1; }

PP_HD bool pp_s320_is_pm1(const PP_S320* a) {
    if (a->v[0] == 1 && a->v[1] == 0 && a->v[2] == 0 && a->v[3] == 0 && a->v[4] == 0)
        return true;
    return a->v[0] == ~0ULL && a->v[1] == ~0ULL && a->v[2] == ~0ULL &&
           a->v[3] == ~0ULL && a->v[4] == ~0ULL;
}

// ─── pingpong walk model ────────────────────────────────────────────────────

#define PP_N 256
#define PP_VALUE_WIDTH (PP_N + 3) // 259
#define PP_ROUNDS_DIV 696 // exact E007 Q1272 divide depth @ea93a131
#define PP_ROUNDS_MUL 696 // exact E007 Q1272 multiply depth @ea93a131

// WIDTH_SCHEDULE @7ca0559 — sampled value_width table, copied verbatim from
// ecdsa-ppfilter-rl/src/bin/ppfilter.rs (md5 f19ad08ddd00210942dd380d1fec81f2).
static const u16 PP_WIDTH_SCHEDULE[700] = {
    258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 258, 257, 257, 257, 257, 257, 257, 257,
    256, 256, 255, 255, 255, 255, 255, 254, 254, 254, 253, 253, 253, 252, 252, 252, 252, 251, 251, 250, 250, 250, 250, 250, 250,
    249, 249, 248, 248, 247, 247, 247, 246, 246, 246, 246, 245, 245, 245, 245, 244, 244, 243, 243, 243, 242, 242, 242, 241, 241,
    241, 240, 240, 240, 240, 239, 239, 239, 239, 238, 238, 238, 238, 237, 237, 236, 236, 236, 236, 235, 235, 234, 234, 233, 233,
    233, 232, 232, 232, 232, 231, 231, 231, 231, 230, 230, 229, 229, 229, 228, 228, 228, 227, 227, 226, 226, 225, 225, 224, 224,
    224, 224, 223, 223, 222, 222, 222, 222, 221, 221, 221, 220, 220, 220, 220, 219, 219, 219, 218, 218, 217, 217, 217, 216, 216,
    216, 215, 215, 215, 214, 214, 214, 214, 213, 213, 212, 212, 211, 211, 210, 210, 209, 209, 209, 209, 209, 209, 208, 208, 207,
    207, 207, 206, 206, 205, 205, 205, 204, 204, 203, 203, 203, 203, 202, 202, 202, 201, 201, 200, 200, 200, 200, 200, 199, 199,
    198, 198, 197, 197, 197, 196, 196, 195, 195, 194, 194, 194, 194, 193, 193, 193, 193, 192, 192, 191, 191, 191, 190, 190, 190,
    189, 189, 188, 188, 188, 187, 187, 186, 186, 186, 185, 185, 184, 184, 184, 183, 183, 183, 183, 182, 182, 181, 181, 180, 180,
    180, 180, 180, 179, 179, 178, 178, 177, 177, 176, 176, 175, 175, 174, 174, 174, 174, 173, 173, 172, 172, 172, 171, 171, 171,
    171, 170, 170, 169, 169, 168, 168, 168, 168, 167, 167, 167, 166, 166, 166, 165, 165, 164, 164, 164, 163, 163, 162, 162, 161,
    160, 160, 160, 159, 159, 159, 159, 159, 158, 158, 157, 157, 156, 156, 156, 155, 155, 155, 155, 154, 154, 153, 153, 152, 152,
    151, 151, 150, 150, 150, 150, 150, 149, 149, 148, 148, 147, 147, 146, 146, 146, 146, 145, 145, 145, 145, 144, 144, 144, 143,
    143, 142, 142, 142, 141, 141, 140, 140, 140, 139, 139, 138, 138, 137, 137, 137, 136, 136, 135, 135, 135, 135, 134, 134, 134,
    133, 133, 132, 132, 132, 132, 131, 131, 130, 130, 130, 129, 129, 128, 128, 128, 128, 127, 127, 127, 126, 126, 125, 125, 124,
    123, 123, 122, 122, 122, 122, 121, 121, 121, 121, 120, 120, 119, 119, 119, 119, 119, 118, 118, 117, 117, 117, 116, 116, 115,
    115, 115, 114, 114, 114, 114, 113, 113, 112, 112, 111, 111, 111, 111, 111, 110, 110, 109, 109, 108, 108, 107, 107, 106, 106,
    105, 105, 105, 105, 105, 104, 104, 103, 103, 102, 102, 101, 101, 100, 100, 100, 100, 99, 99, 98, 98, 97, 97, 96, 96,
    95, 95, 95, 95, 94, 94, 94, 93, 93, 92, 92, 92, 91, 91, 90, 90, 90, 90, 89, 89, 89, 88, 88, 87, 87,
    86, 86, 86, 86, 85, 85, 84, 83, 83, 83, 83, 82, 82, 81, 81, 80, 79, 79, 79, 79, 78, 78, 77, 77, 76,
    76, 75, 75, 74, 74, 73, 73, 73, 72, 72, 72, 71, 71, 70, 70, 70, 69, 69, 69, 69, 68, 68, 68, 67, 67,
    67, 66, 66, 65, 65, 65, 64, 64, 64, 64, 63, 63, 62, 61, 61, 61, 61, 60, 60, 59, 59, 58, 58, 57, 57,
    56, 56, 55, 55, 55, 54, 54, 54, 53, 53, 52, 52, 52, 51, 51, 50, 50, 50, 49, 49, 48, 48, 48, 47, 47,
    46, 46, 45, 45, 45, 45, 44, 44, 43, 43, 43, 42, 42, 41, 41, 40, 40, 40, 40, 39, 39, 38, 38, 37, 37,
    36, 36, 36, 35, 35, 35, 34, 34, 34, 34, 33, 33, 32, 32, 31, 31, 30, 30, 29, 29, 28, 28, 27, 27, 26,
    26, 25, 25, 25, 25, 24, 24, 23, 23, 22, 22, 21, 21, 20, 20, 20, 19, 19, 18, 18, 18, 17, 17, 17, 16,
    16, 15, 15, 14, 14, 13, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8,
};

#ifdef __CUDACC__
__device__ __constant__ u16 PP_WIDTH_SCHEDULE_D[700];
#endif

// Q1272 rescaled value_width(): round 0 stays VALUE_WIDTH. Other rounds map
// through the exact Rust width_round_index calculation r * (704-1)/(696-1),
// then read the sampled table and clamp [8, 259]. Indices >=700 use the floor
// width 8. The _t variant reads a caller-supplied table (the kernels stage it
// in shared memory; constant memory serializes under divergent per-lane
// rounds).
PP_HD int pp_value_width_t(int round, const u16* tab) {
    if (round == 0) return PP_VALUE_WIDTH;
    int schedule_round = round * 703 / 695;
    if (schedule_round < 700) {
        int w = (int)tab[schedule_round];
        if (w < 8) w = 8;
        if (w > PP_VALUE_WIDTH) w = PP_VALUE_WIDTH;
        return w;
    }
    return 8;
}
PP_HD int pp_value_width(int round) {
#ifdef __CUDA_ARCH__
    return pp_value_width_t(round, PP_WIDTH_SCHEDULE_D);
#else
    return pp_value_width_t(round, PP_WIDTH_SCHEDULE);
#endif
}

struct PP_WalkOut {
    bool fault;
    bool term_ok;
    bool u_neg;
    bool v_neg;
    // tape bits 0..703, 11 u64 words. On device this struct is never
    // materialized whole: signs live in shared memory (see pp_walk_sh).
    u64 signs[11];
};

// Exact value-level walk, signs written to caller-provided storage (11 u64).
// wtab: width schedule table (700 entries).
PP_HD void pp_walk_sig(const u64 a[4], int rounds, bool* fault_out, bool* term_ok_out,
                       bool* u_neg_out, bool* v_neg_out, u64 signs[11],
                       const u16* wtab) {
    PP_P4(Pv);
    PP_S320 p320 = pp_s320_from_u256(Pv);
    PP_S320 h = pp_s320_from_u256(Pv);
    {
        u64 onev[4] = {1, 0, 0, 0};
        PP_S320 one = pp_s320_from_u256(onev);
        pp_s320_add(&h, &one);
    }
    pp_s320_shr1(&h); // (p+1)/2

    u64 a0 = a[0] & 1;
    u64 a1 = (a[0] >> 1) & 1;
    PP_S320 u = p320;
    PP_S320 v = pp_s320_from_u256(a);
    for (int i = 0; i < 11; i++) signs[i] = 0;
    bool fault = false;

    for (int r = 0; r < rounds; r++) {
        int w = pp_value_width_t(r, wtab);
        if ((int)pp_s320_swidth(&u) > w || (int)pp_s320_swidth(&v) > w) {
            fault = true;
            break;
        }
        if (r == 0) {
            // fused_lift_round0_forward: v = q - p + a1*p + a0*(p+1)/2
            PP_S320 nv = v;
            pp_s320_shr1(&nv);
            pp_s320_sub(&nv, &p320);
            if (a1 == 1) pp_s320_add(&nv, &p320);
            if (a0 == 1) pp_s320_add(&nv, &h);
            v = nv;
            if (a0 == 1) signs[0] |= 1;
            continue;
        }
        if (r % 2 == 0) {
            u64 sign = pp_s320_bit1(&v) ^ pp_s320_bit1(&u);
            if (sign == 0) {
                pp_s320_add(&v, &u);
            } else {
                pp_s320_sub(&v, &u);
            }
            if ((int)pp_s320_swidth(&v) > w) {
                fault = true;
                break;
            }
            pp_s320_shr1(&v);
            if (sign == 1) signs[r / 64] |= 1ULL << (r % 64);
        } else {
            u64 sign = pp_s320_bit1(&u) ^ pp_s320_bit1(&v);
            if (sign == 0) {
                pp_s320_add(&u, &v);
            } else {
                pp_s320_sub(&u, &v);
            }
            if ((int)pp_s320_swidth(&u) > w) {
                fault = true;
                break;
            }
            pp_s320_shr1(&u);
            if (sign == 1) signs[r / 64] |= 1ULL << (r % 64);
        }
    }
    *fault_out = fault;
    *term_ok_out = !fault && pp_s320_is_pm1(&u) && pp_s320_is_pm1(&v);
    *u_neg_out = pp_s320_is_neg(&u);
    *v_neg_out = pp_s320_is_neg(&v);
}

// Signed truncation performed by shrink_to: keep the scheduled low bits and
// interpret the retained top bit as the sign. This is only needed on the rare
// schedule-overflow fallback path; the fast path above exits at first overflow.
PP_HD void pp_s320_truncate_signed(PP_S320* a, int width) {
    bool sign = ((a->v[(width - 1) / 64] >> ((width - 1) % 64)) & 1) != 0;
    int limb = width / 64;
    int off = width % 64;
    if (off == 0) {
        for (int i = limb; i < PP_LIMBS; i++) a->v[i] = sign ? ~0ULL : 0;
    } else {
        u64 low_mask = (1ULL << off) - 1;
        a->v[limb] = (a->v[limb] & low_mask) | (sign ? ~low_mask : 0);
        for (int i = limb + 1; i < PP_LIMBS; i++) a->v[i] = sign ? ~0ULL : 0;
    }
}

// Classical fallback for a scheduled-width overflow. Unlike pp_walk_sig,
// this follows the circuit's actual wrapping registers through every round.
// It lets the final value check distinguish a real wrong answer from a rare
// overflow that wraps back onto the correct quotient/product.
PP_HD bool pp_walk_sig_wrapped(const u64 a[4], int rounds, bool* u_neg_out,
                               bool* v_neg_out, u64 signs[11], const u16* wtab) {
    PP_P4(Pv);
    PP_S320 p320 = pp_s320_from_u256(Pv);
    PP_S320 h = p320;
    {
        u64 onev[4] = {1, 0, 0, 0};
        PP_S320 one = pp_s320_from_u256(onev);
        pp_s320_add(&h, &one);
    }
    pp_s320_shr1(&h);

    u64 a0 = a[0] & 1;
    u64 a1 = (a[0] >> 1) & 1;
    PP_S320 u = p320;
    PP_S320 v = pp_s320_from_u256(a);
    for (int i = 0; i < 11; i++) signs[i] = 0;
    bool lossless = true;

    for (int r = 0; r < rounds; r++) {
        int w = pp_value_width_t(r, wtab);
        // shrink_to XOR-clears and frees the scheduled-away sign-copy wire.
        // A non-sign-extension bit here is irrecoverably lost; replay may
        // still land on the right numerator by chance, but walkback cannot
        // be assumed to restore the denominator.
        if ((int)pp_s320_swidth(&u) > w || (int)pp_s320_swidth(&v) > w) {
            lossless = false;
        }
        pp_s320_truncate_signed(&u, w);
        pp_s320_truncate_signed(&v, w);
        if (r == 0) {
            PP_S320 nv = v;
            pp_s320_shr1(&nv);
            pp_s320_sub(&nv, &p320);
            if (a1 == 1) pp_s320_add(&nv, &p320);
            if (a0 == 1) pp_s320_add(&nv, &h);
            pp_s320_truncate_signed(&nv, w);
            v = nv;
            if (a0 == 1) signs[0] |= 1;
            continue;
        }
        if (r % 2 == 0) {
            u64 sign = pp_s320_bit1(&v) ^ pp_s320_bit1(&u);
            if (sign == 0) pp_s320_add(&v, &u); else pp_s320_sub(&v, &u);
            pp_s320_truncate_signed(&v, w);
            pp_s320_shr1(&v);
            if (sign == 1) signs[r / 64] |= 1ULL << (r % 64);
        } else {
            u64 sign = pp_s320_bit1(&u) ^ pp_s320_bit1(&v);
            if (sign == 0) pp_s320_add(&u, &v); else pp_s320_sub(&u, &v);
            pp_s320_truncate_signed(&u, w);
            pp_s320_shr1(&u);
            if (sign == 1) signs[r / 64] |= 1ULL << (r % 64);
        }
    }
    *u_neg_out = pp_s320_is_neg(&u);
    *v_neg_out = pp_s320_is_neg(&v);
    return lossless;
}

PP_HD PP_WalkOut pp_walk(const u64 a[4], int rounds) {
    PP_WalkOut w;
#ifdef __CUDA_ARCH__
    const u16* tab = PP_WIDTH_SCHEDULE_D;
#else
    const u16* tab = PP_WIDTH_SCHEDULE;
#endif
    pp_walk_sig(a, rounds, &w.fault, &w.term_ok, &w.u_neg, &w.v_neg, w.signs, tab);
    return w;
}

// Walk-back round-0 sparse fold: fault iff the low-53 carry propagates out of
// bit 52. Pure function of a.
PP_HD bool pp_walkback_fold_fault(const u64 a[4]) {
    u64 a0 = a[0] & 1;
    u64 a1 = (a[0] >> 1) & 1;
    PP_P4(Pv);
    PP_S320 p320 = pp_s320_from_u256(Pv);
    PP_S320 h = pp_s320_from_u256(Pv);
    {
        u64 onev[4] = {1, 0, 0, 0};
        PP_S320 one = pp_s320_from_u256(onev);
        pp_s320_add(&h, &one);
    }
    pp_s320_shr1(&h);
    PP_S320 v1 = pp_s320_from_u256(a);
    pp_s320_shr1(&v1);
    pp_s320_sub(&v1, &p320);
    if (a1 == 1) pp_s320_add(&v1, &p320);
    if (a0 == 1) pp_s320_add(&v1, &h);
    bool not_a1 = pp_s320_is_neg(&v1);
    PP_S320 w2 = v1;
    pp_s320_shl1(&w2);
    u64 acc0 = w2.v[0];
    u64 acc1 = not_a1 ? ~acc0 : acc0;
    u64 addend = a0 * PP_FC + ((not_a1 && a0 == 0) ? 2 * PP_FC : 0);
    u64 low = acc1 & PP_MASK54;
    return (u128)low + addend >= ((u128)1 << 54);
}

// ─── replay coefficient-pass model ──────────────────────────────────────────

PP_HD void pp_not256(u64 a[4]) {
    for (int i = 0; i < 4; i++) a[i] = ~a[i];
}

PP_HD bool pp_add256(const u64 a[4], const u64 b[4], u64 s[4]) {
    bool carry = false;
    for (int i = 0; i < 4; i++) {
        u64 r1 = a[i] + b[i];
        bool c1 = r1 < a[i];
        u64 r2 = r1 + (carry ? 1 : 0);
        bool c2 = r2 < r1;
        s[i] = r2;
        carry = c1 || c2;
    }
    return carry;
}

PP_HD void pp_shr1_256(u64 a[4]) {
    for (int i = 0; i < 3; i++) a[i] = (a[i] >> 1) | (a[i + 1] << 63);
    a[3] >>= 1;
}

PP_HD u64 pp_shl1_256(u64 a[4]) {
    u64 out = a[3] >> 63;
    for (int i = 3; i >= 1; i--) a[i] = (a[i] << 1) | (a[i - 1] >> 63);
    a[0] <<= 1;
    return out;
}

// Truncated const subtract: borrows applied to positions <= last+1; a borrow
// into position last+2 is dropped. k = last + 2 in {54, 65, 66}.
PP_HD bool pp_trunc_sub(u64 acc[4], u64 c, int k) {
    if (k == 54) {
        u64 low = acc[0] & ((1ULL << 54) - 1);
        bool fault = low < c;
        u64 nl = (low - c) & ((1ULL << 54) - 1);
        acc[0] = (acc[0] & ~((1ULL << 54) - 1)) | nl;
        return fault;
    } else {
        int extra = k - 64;
        u64 emask = (1ULL << extra) - 1;
        u128 low = (u128)acc[0] | (((u128)(acc[1] & emask)) << 64);
        bool fault = low < (u128)c;
        u128 nl = (low + ((u128)1 << k) - c) & (((u128)1 << k) - 1);
        acc[0] = (u64)nl;
        acc[1] = (acc[1] & ~emask) | (((u64)(nl >> 64)) & emask);
        return fault;
    }
}

// Truncated const add. Same window rule.
PP_HD bool pp_trunc_add(u64 acc[4], u64 c, int k) {
    if (k == 54) {
        u64 low = acc[0] & ((1ULL << 54) - 1);
        u128 s = (u128)low + c;
        acc[0] = (acc[0] & ~((1ULL << 54) - 1)) | ((u64)s & ((1ULL << 54) - 1));
        return s >= ((u128)1 << 54);
    } else {
        int extra = k - 64;
        u64 emask = (1ULL << extra) - 1;
        u128 low = (u128)acc[0] | (((u128)(acc[1] & emask)) << 64);
        u128 s = low + c;
        acc[0] = (u64)s;
        acc[1] = (acc[1] & ~emask) | (((u64)(s >> 64)) & emask);
        return s >= ((u128)1 << k);
    }
}

// Candidate fused_fold_maskfree on the low 55 bits: add k*f, carry out of
// bit 54 dropped. The returned fault flag is unused by the verdict.
PP_HD bool pp_fold55(u64 acc[4], int k) {
    if (k == 0) return false;
    const u64 mask55 = (1ULL << 55) - 1;
    u64 low = acc[0] & mask55;
    u64 nl;
    bool fault;
    if (k == 1) {
        u128 s = (u128)low + PP_FC;
        nl = (u64)s & mask55;
        fault = s >= ((u128)1 << 55);
    } else if (k == 2) {
        u128 s = (u128)low + 2 * PP_FC;
        nl = (u64)s & mask55;
        fault = s >= ((u128)1 << 55);
    } else { // k == -1
        fault = low < PP_FC;
        nl = (low - PP_FC) & mask55;
    }
    acc[0] = (acc[0] & ~mask55) | nl;
    return fault;
}

// conditional_mod_negate: complement then csub(f-1, window=20 -> last=52).
PP_HD bool pp_cneg(u64 acc[4]) {
    pp_not256(acc);
    return pp_trunc_sub(acc, PP_FC - 1, 54);
}

// mod_halve_pm: csub(f, parity, window 20) then rotate-halve.
PP_HD bool pp_mod_halve_pm(u64 t[4]) {
    u64 parity = t[0] & 1;
    bool fault = false;
    if (parity == 1) fault = pp_trunc_sub(t, PP_FC, 54);
    u64 old0 = t[0] & 1;
    pp_shr1_256(t);
    t[3] |= (old0 ^ parity) << 63;
    return fault;
}

// mod_double_pm: shift left, then cadd(f, overflow, window 20).
PP_HD bool pp_mod_double_pm(u64 t[4]) {
    u64 o = pp_shl1_256(t);
    if (o == 1) return pp_trunc_add(t, PP_FC, 54);
    return false;
}

// signed_mod_add_pm_halve_fused (divide replay, round >= 2).
PP_HD bool pp_halve_fused(bool sign, const u64 s[4], u64 t[4]) {
    if (sign) pp_not256(t);
    u64 sum[4];
    bool o = pp_add256(t, s, sum);
    for (int i = 0; i < 4; i++) t[i] = sum[i];
    bool parity = (t[0] & 1) == 1;
    bool nsap = !sign && parity;
    bool sap = sign && parity;
    bool minus_f = !o && nsap;
    bool plus_2f = o && sap;
    bool plus_f = minus_f ^ sign ^ parity;
    int k = (int)plus_f + 2 * (int)plus_2f - (int)minus_f;
    bool fault = pp_fold55(t, k);
    if (sign) pp_not256(t);
    u64 old0 = t[0] & 1;
    pp_shr1_256(t);
    t[3] |= (old0 ^ (u64)parity ^ (u64)o ^ (u64)sign) << 63;
    return fault;
}

// signed_mod_double_add_pm_fused (multiply replay, round >= 2).
PP_HD bool pp_double_add_fused(bool sign, const u64 s[4], u64 t[4]) {
    bool d = pp_shl1_256(t) == 1;
    if (sign) pp_not256(t);
    u64 sum[4];
    bool o = pp_add256(t, s, sum);
    for (int i = 0; i < 4; i++) t[i] = sum[i];
    bool sxa = sign ^ o;
    bool routed = d && sxa;
    bool minus_f = routed && sign;
    bool plus_2f = routed && !sign;
    bool plus_f = d ^ o ^ minus_f;
    int k = (int)plus_f + 2 * (int)plus_2f - (int)minus_f;
    bool fault = pp_fold55(t, k);
    if (sign) pp_not256(t);
    return fault;
}

// seed_round_one (divide replay round 1).
PP_HD bool pp_seed_round_one(bool sign, const u64 s[4], u64 t[4]) {
    for (int i = 0; i < 4; i++) t[i] ^= s[i];
    if (sign) {
        pp_not256(t);
        return pp_trunc_sub(t, PP_FC - 1, 66);
    }
    return false;
}

// seed_round_one_inverse (multiply replay round 1).
PP_HD bool pp_seed_round_one_inverse(bool sign, const u64 s[4], u64 t[4]) {
    bool fault = false;
    if (sign) {
        fault = pp_trunc_add(t, PP_FC - 1, 66);
        pp_not256(t);
    }
    for (int i = 0; i < 4; i++) t[i] ^= s[i];
    return fault;
}

PP_HD bool pp_sign_at(const u64 signs[11], int r) {
    return (signs[r / 64] >> (r % 64)) & 1;
}

// Divide replay. Returns x, y after conditional negates; clean iff x == y.
PP_HD void pp_divide_replay(const u64 dy[4], const u64 signs[11], bool su, bool sv,
                            u64 x_out[4], u64 y_out[4]) {
    u64 x[4] = {0, 0, 0, 0};
    u64 y[4];
    for (int i = 0; i < 4; i++) y[i] = dy[i];
    pp_mod_halve_pm(&y[0]); // round 0 (target = y)
    // round 1 is odd: (source, target) = (y, x)
    pp_seed_round_one(pp_sign_at(signs, 1), y, x);
    pp_mod_halve_pm(x);
    for (int r = 2; r < PP_ROUNDS_DIV; r++) {
        bool sign = pp_sign_at(signs, r);
        if (r % 2 == 0) {
            pp_halve_fused(sign, x, y);
        } else {
            pp_halve_fused(sign, y, x);
        }
    }
    if (su) pp_cneg(x);
    if (sv) pp_cneg(y);
    for (int i = 0; i < 4; i++) { x_out[i] = x[i]; y_out[i] = y[i]; }
}

// Multiply replay: replays rounds 695..0 in reverse. x must end at 0.
PP_HD void pp_multiply_replay(const u64 lam[4], const u64 signs[11], bool su, bool sv,
                              u64 x_out[4], u64 y_out[4]) {
    u64 x[4], y[4];
    for (int i = 0; i < 4; i++) { x[i] = lam[i]; y[i] = lam[i]; }
    if (su) pp_cneg(x);
    if (sv) pp_cneg(y);
    for (int r = PP_ROUNDS_MUL - 1; r >= 2; r--) {
        // replay_doubling_round toggles the tape qubit: effective sign !tape[r]
        bool sign = !pp_sign_at(signs, r);
        if (r % 2 == 0) {
            pp_double_add_fused(sign, x, y);
        } else {
            pp_double_add_fused(sign, y, x);
        }
    }
    // round 1: (source, target) = (y, x)
    pp_mod_double_pm(x);
    pp_seed_round_one_inverse(pp_sign_at(signs, 1), y, x);
    // round 0: (source, target) = (x, y)
    pp_mod_double_pm(y);
    for (int i = 0; i < 4; i++) { x_out[i] = x[i]; y_out[i] = y[i]; }
}

// ─── value-level shell model ────────────────────────────────────────────────

#define PP_ARITH_LSBS 53
#define PP_SQ_LSBS 56
#define PP_GUARD 24

// F_NAF: (shift, negate) — local copies at each use site (device addressing).
#define PP_F_NAF_TABLES \
    const int F_NAF_SHIFT[5] = {0, 4, 6, 10, 32}; \
    const bool F_NAF_NEG[5] = {false, false, true, false, false}

typedef u64 PP_Wide[6]; // 384 bits, little-endian limbs

PP_HD void pp_wide_from4(const u64 a[4], PP_Wide w) {
    for (int i = 0; i < 4; i++) w[i] = a[i];
    w[4] = 0;
    w[5] = 0;
}

// Extract bits [lo, lo+w) as a Wide.
PP_HD void pp_wide_get(const PP_Wide v, int lo, int w, PP_Wide out) {
    for (int i = 0; i < 6; i++) out[i] = 0;
    if (w == 0) return;
    int limb = lo / 64;
    int off = lo % 64;
    int nlimbs = (w + 63) / 64;
    for (int i = 0; i < nlimbs; i++) {
        u64 x = (limb + i < 6) ? v[limb + i] : 0;
        if (off != 0) {
            x = (x >> off) | ((limb + i + 1 < 6) ? (v[limb + i + 1] << (64 - off)) : 0);
        }
        out[i] = x;
    }
    if (w % 64 != 0) out[w / 64] &= (1ULL << (w % 64)) - 1;
    for (int i = w / 64 + 1; i < 6; i++) out[i] = 0;
}

// Splice val's low w bits into v at [lo, lo+w).
PP_HD void pp_wide_set(PP_Wide v, int lo, int w, const PP_Wide val) {
    if (w == 0) return;
    int limb = lo / 64;
    int off = lo % 64;
    int nlimbs = (w + 63) / 64;
    for (int i = 0; i < nlimbs; i++) {
        u64 x = val[i];
        if (w % 64 != 0 && i == w / 64) x &= (1ULL << (w % 64)) - 1;
        if (off == 0) {
            u64 m = (w % 64 != 0 && i == w / 64) ? ((1ULL << (w % 64)) - 1) : ~0ULL;
            if (limb + i < 6) v[limb + i] = (v[limb + i] & ~m) | (x & m);
        } else {
            u64 lo_part = x << off;
            u64 hi_part = x >> (64 - off);
            u64 m = (w % 64 != 0 && i == w / 64) ? (((1ULL << (w % 64)) - 1) << off)
                                                 : (~0ULL << off);
            if (limb + i < 6) v[limb + i] = (v[limb + i] & ~m) | (lo_part & m);
            if (limb + i + 1 < 6) {
                u64 m2 = (w % 64 != 0 && i == w / 64) ? (((1ULL << (w % 64)) - 1) >> (64 - off))
                                                      : (~0ULL >> (64 - off));
                v[limb + i + 1] = (v[limb + i + 1] & ~m2) | (hi_part & m2);
            }
        }
    }
}

PP_HD bool pp_wide_add(const PP_Wide a, const PP_Wide b, PP_Wide s) {
    bool carry = false;
    for (int i = 0; i < 6; i++) {
        u64 r1 = a[i] + b[i];
        bool c1 = r1 < a[i];
        u64 r2 = r1 + (carry ? 1 : 0);
        bool c2 = r2 < r1;
        s[i] = r2;
        carry = c1 || c2;
    }
    return carry;
}

PP_HD void pp_wide_mul(const PP_Wide a, const PP_Wide b, PP_Wide r) {
    for (int i = 0; i < 6; i++) r[i] = 0;
    for (int i = 0; i < 6; i++) {
        u128 carry = 0;
        for (int j = 0; j < 6 - i; j++) {
            u128 cur = (u128)r[i + j] + (u128)a[i] * b[j] + carry;
            r[i + j] = (u64)cur;
            carry = cur >> 64;
        }
    }
}

PP_HD void pp_wide_mask(int w, PP_Wide m) {
    for (int i = 0; i < 6; i++) m[i] = 0;
    for (int i = 0; i < w; i++) m[i / 64] |= 1ULL << (i % 64);
}

PP_HD void pp_wide_xor(const PP_Wide a, const PP_Wide b, PP_Wide o) {
    for (int i = 0; i < 6; i++) o[i] = a[i] ^ b[i];
}

PP_HD bool pp_wide_bit(const PP_Wide v, int i) { return (v[i / 64] >> (i % 64)) & 1; }

// add_f_window: if ctrl, add f to reg[..lsbs]; carry into bit lsbs dropped.
PP_HD void pp_f_window(PP_Wide reg, bool ctrl, int lsbs) {
    if (!ctrl) return;
    PP_Wide low, fcw, sum;
    pp_wide_get(reg, 0, lsbs, low);
    {
        u64 fcv[4] = {PP_FC, 0, 0, 0};
        pp_wide_from4(fcv, fcw);
    }
    pp_wide_add(low, fcw, sum);
    pp_wide_set(reg, 0, lsbs, sum); // truncates to lsbs bits: drop
}

// mod_add_top: out' = out + (-1)^sign * (value << shift) with f-window
// overflow correction. value has 256-shift bits.
PP_HD void pp_mod_add_top_model(PP_Wide out, const PP_Wide value, int shift, bool sign) {
    PP_Wide m256;
    pp_wide_mask(256, m256);
    if (sign) pp_wide_xor(out, m256, out);
    PP_Wide acc, sum;
    pp_wide_get(out, shift, 256 - shift, acc);
    pp_wide_add(acc, value, sum);
    bool ovf = pp_wide_bit(sum, 256 - shift);
    pp_wide_set(out, shift, 256 - shift, sum);
    pp_f_window(out, ovf, PP_SQ_LSBS);
    if (sign) pp_wide_xor(out, m256, out);
}

// window_add: acc = out[shift..shift+w+GUARD]; add value (w bits), dropping
// the carry past the window top; complement sandwich if sign.
PP_HD void pp_window_add_model(PP_Wide out, const PP_Wide value, int w, int shift, bool sign) {
    int wtot = w + PP_GUARD;
    PP_Wide acc, mw, sum;
    pp_wide_get(out, shift, wtot, acc);
    pp_wide_mask(wtot, mw);
    if (sign) pp_wide_xor(acc, mw, acc);
    pp_wide_add(acc, value, sum);
    if (sign) {
        pp_wide_xor(sum, mw, acc);
    } else {
        for (int i = 0; i < 6; i++) acc[i] = sum[i];
    }
    pp_wide_set(out, shift, wtot, acc); // truncated splice: carry dropped
}

// apply_f: add value*f (mod p fold of the product tail), NAF form.
PP_HD void pp_apply_f_model(PP_Wide out, const PP_Wide value, int vbits, bool sign) {
    PP_F_NAF_TABLES;
    bool s = sign;
#pragma unroll
    for (int i = 0; i < 5; i++) {
        if (F_NAF_NEG[i]) s = !s;
        pp_window_add_model(out, value, vbits, F_NAF_SHIFT[i], s);
        if (F_NAF_NEG[i]) s = !s;
    }
}

// apply_shift_half: mod_add_top(shift=128) then apply_f over product[128..].
PP_HD void pp_apply_shift_half_model(PP_Wide out, const PP_Wide product, int plen, bool sign) {
    PP_Wide lo;
    pp_wide_get(product, 0, 128, lo);
    pp_mod_add_top_model(out, lo, 128, sign);
    if (plen > 128) {
        PP_Wide hi;
        pp_wide_get(product, 128, plen - 128, hi);
        pp_apply_f_model(out, hi, plen - 128, sign);
    }
}

// apply_shift_full: subtract (sign=1) product*f mod p via NAF.
PP_HD void pp_apply_shift_full_model(PP_Wide out, const PP_Wide product, bool sign) {
    PP_F_NAF_TABLES;
    bool s = sign;
#pragma unroll
    for (int i = 0; i < 5; i++) {
        int shift = F_NAF_SHIFT[i];
        if (F_NAF_NEG[i]) s = !s;
        if (shift == 0) {
            pp_mod_add_top_model(out, product, 0, s);
        } else {
            PP_Wide main_, tail;
            pp_wide_get(product, 0, 256 - shift, main_);
            pp_mod_add_top_model(out, main_, shift, s);
            pp_wide_get(product, 256 - shift, shift, tail);
            pp_apply_f_model(out, tail, shift, s);
        }
        if (F_NAF_NEG[i]) s = !s;
    }
}

// product_register::square_sub: out -= y^2 mod p, circuit-exact.
PP_HD void pp_square_model(const u64 y[4], const u64 out0[4], u64 out[4]) {
    PP_Wide yw, ylo, yhi, sum, pa, pb, pc, o;
    pp_wide_from4(y, yw);
    pp_wide_get(yw, 0, 128, ylo);
    pp_wide_get(yw, 128, 128, yhi);
    pp_wide_add(ylo, yhi, sum); // 129 bits
    pp_wide_mul(ylo, ylo, pa);
    pp_wide_mul(yhi, yhi, pb);
    pp_wide_mul(sum, sum, pc); // 258 bits
    pp_wide_from4(out0, o);
    // step 1: out -= pa
    pp_mod_add_top_model(o, pa, 0, true);
    // step 2: out += pa << 128 (mod-reduced)
    pp_apply_shift_half_model(o, pa, 256, false);
    // step 3: out += pb << 128
    pp_apply_shift_half_model(o, pb, 256, false);
    // step 4: out -= pb << 256 == pb*f
    pp_apply_shift_full_model(o, pb, true);
    // step 5: out -= pc << 128
    pp_apply_shift_half_model(o, pc, 258, true);
    for (int i = 0; i < 4; i++) out[i] = o[i];
}

// mod_sub_vented: reg = (reg - coord) mod p, with the 53-bit f-window drop.
PP_HD void pp_coord_sub_model(const u64 reg[4], const u64 coord[4], u64 out[4]) {
    PP_Wide m256, rw, cw, nreg, s, w, o;
    pp_wide_mask(256, m256);
    pp_wide_from4(reg, rw);
    pp_wide_from4(coord, cw);
    pp_wide_xor(rw, m256, nreg);
    pp_wide_add(nreg, cw, s);
    bool anc = pp_wide_bit(s, 256); // carry out of bit 255 = borrow indicator
    pp_wide_xor(s, m256, w);        // uncomplement
    for (int i = 0; i < 6; i++) o[i] = w[i];
    if (anc) {
        PP_Wide m53, low, lc, fcw, s2, lu;
        u64 fcv[4] = {PP_FC, 0, 0, 0};
        pp_wide_mask(PP_ARITH_LSBS, m53);
        pp_wide_get(o, 0, PP_ARITH_LSBS, low);
        pp_wide_xor(low, m53, lc);
        pp_wide_from4(fcv, fcw);
        pp_wide_add(lc, fcw, s2);
        pp_wide_xor(s2, m53, lu);
        pp_wide_set(o, 0, PP_ARITH_LSBS, lu);
    }
    for (int i = 0; i < 4; i++) out[i] = o[i];
}

// E007 final-y-only correction. The circuit computes the missing low53 borrow
// from the unchanged post-low result, then decrements the complete high203
// suffix. Initial coordinate subtractions continue to use pp_coord_sub_model.
PP_HD void pp_coord_sub_final_model(const u64 reg[4], const u64 coord[4], u64 out[4]) {
    pp_coord_sub_model(reg, coord, out);
    const bool anc = !pp_ge(reg, coord); // carry(~reg + coord) iff coord > reg
    const u64 low53 = out[0] & ((1ULL << PP_ARITH_LSBS) - 1);
    const u64 threshold = (1ULL << PP_ARITH_LSBS) - PP_FC;
    if (anc && low53 >= threshold) {
        u64 step[4] = {1ULL << PP_ARITH_LSBS, 0, 0, 0};
        u64 ignored_borrow = 0;
        pp_sub_limbs(out, step, out, &ignored_borrow);
    }
}

// mod_add_exact (coord_add3x): reg = (x + y) mod p, 53-bit f-window drop.
PP_HD void pp_mod_add_exact_model(const u64 x[4], const u64 y[4], u64 out[4]) {
    u64 s[4];
    bool anc = pp_add256(x, y, s);
    PP_Wide o;
    pp_wide_from4(s, o);
    if (anc) {
        PP_Wide low, fcw, s2;
        u64 fcv[4] = {PP_FC, 0, 0, 0};
        pp_wide_get(o, 0, PP_ARITH_LSBS, low);
        pp_wide_from4(fcv, fcw);
        pp_wide_add(low, fcw, s2);
        pp_wide_set(o, 0, PP_ARITH_LSBS, s2);
    }
    for (int i = 0; i < 4; i++) out[i] = o[i];
}

// coord_rsub (fused default): x := (coord - reg) mod p.
PP_HD void pp_coord_rsub_model(const u64 reg[4], const u64 coord[4], u64 out[4]) {
    PP_Wide m256;
    pp_wide_mask(256, m256);
    u64 t1[4];
    {
        u64 onev[4] = {1, 0, 0, 0};
        pp_add256(coord, onev, t1); // wraps mod 2^256
    }
    PP_Wide nreg, s, o;
    PP_Wide rw, t1w;
    pp_wide_from4(reg, rw);
    pp_wide_xor(rw, m256, nreg);
    pp_wide_from4(t1, t1w);
    pp_wide_add(nreg, t1w, s);
    bool anc = pp_wide_bit(s, 256);
    for (int i = 0; i < 6; i++) o[i] = s[i]; // no full un-complement in rsub_loaded
    if (!anc) {
        PP_Wide m53, low, lc, fcw, s2, lu;
        u64 fcv[4] = {PP_FC, 0, 0, 0};
        pp_wide_mask(PP_ARITH_LSBS, m53);
        pp_wide_get(o, 0, PP_ARITH_LSBS, low);
        pp_wide_xor(low, m53, lc);
        pp_wide_from4(fcv, fcw);
        pp_wide_add(lc, fcw, s2);
        pp_wide_xor(s2, m53, lu);
        pp_wide_set(o, 0, PP_ARITH_LSBS, lu);
    }
    for (int i = 0; i < 4; i++) out[i] = o[i];
}

// ─── per-shot fault evaluation ──────────────────────────────────────────────

PP_HD void pp_mod_p(const u64 a[4], u64 out[4]) {
    PP_P4(P);
    if (pp_ge(a, P)) {
        u64 b;
        pp_sub_limbs(a, P, out, &b);
    } else {
        for (int i = 0; i < 4; i++) out[i] = a[i];
    }
}

// Fault-cause bitmask (same vocabulary as the Rust oracle).
#define PP_F_WALK_DIV 1u
#define PP_F_REPLAY_DIV 2u
#define PP_F_WALK_MUL 4u
#define PP_F_REPLAY_MUL 8u
#define PP_F_RESULT 16u

// Reference affine add (expected evaluator result).
PP_HD void pp_expected_add(const u64 tx[4], const u64 ty[4], const u64 ox[4],
                           const u64 oy[4], const u64 lam[4], u64 rx[4], u64 ry[4]) {
    u64 t[4];
    pp_fsq(lam, rx);
    pp_fsub(rx, tx, rx);
    pp_fsub(rx, ox, rx);
    pp_fsub(tx, rx, t);
    pp_fmul(lam, t, ry);
    pp_fsub(ry, ty, ry);
}

// Slow overflow fallback: propagate the circuit's wrapped walk values through
// the complete classical point-add shell and compare the actual output. The
// caller supplies sign storage so CUDA keeps the same shared-memory layout.
PP_HD bool pp_wrapped_output_correct(const u64 tx[4], const u64 ty[4],
                                     const u64 ox[4], const u64 oy[4],
                                     const u64 lam[4], u64 signs_d[11],
                                     u64 signs_m[11], const u16* wtab) {
    u64 rx[4], ry[4];
    pp_expected_add(tx, ty, ox, oy, lam, rx, ry);

    u64 x2[4], y2[4];
    pp_coord_sub_model(tx, ox, x2);
    pp_coord_sub_model(ty, oy, y2);

    bool du_neg, dv_neg;
    if (!pp_walk_sig_wrapped(x2, PP_ROUNDS_DIV, &du_neg, &dv_neg, signs_d, wtab)) {
        return false;
    }
    u64 xd[4], y2d[4];
    pp_divide_replay(y2, signs_d, du_neg, dv_neg, xd, y2d);

    u64 three[4], x2b[4], x2c[4];
    pp_fadd(ox, ox, three);
    pp_fadd(three, ox, three);
    pp_mod_add_exact_model(three, x2, x2b);
    pp_square_model(y2d, x2b, x2c);

    bool mu_neg, mv_neg;
    if (!pp_walk_sig_wrapped(x2c, PP_ROUNDS_MUL, &mu_neg, &mv_neg, signs_m, wtab)) {
        return false;
    }
    u64 xm[4], y2m[4];
    pp_multiply_replay(y2d, signs_m, mu_neg, mv_neg, xm, y2m);

    u64 y2f[4], x2f[4];
    pp_coord_sub_final_model(y2m, oy, y2f);
    pp_coord_rsub_model(x2c, ox, x2f);
    return pp_eq(x2f, rx) && pp_eq(y2f, ry);
}

// Full circuit-exact value simulation of one shot, with caller-provided signs
// storage (11 u64 each). On device these point into shared memory; on the
// host they are stack arrays. Same early-return order as the Rust oracle;
// identical mask vocabulary.
PP_HD u32 pp_shot_fault_mask_s(const u64 tx[4], const u64 ty[4], const u64 ox[4],
                               const u64 oy[4], const u64 lam[4], u64 signs_d[11],
                               u64 signs_m[11], const u16* wtab) {
    u64 rx[4], ry[4];
    pp_expected_add(tx, ty, ox, oy, lam, rx, ry);

    // tlm_coord_x_sub / tlm_coord_y_sub
    u64 x2[4], y2[4];
    pp_coord_sub_model(tx, ox, x2);
    pp_coord_sub_model(ty, oy, y2);

    // Divide traversal (denominator x2, numerator y2)
    bool wd_fault, wd_term_ok, wd_u_neg, wd_v_neg;
    pp_walk_sig(x2, PP_ROUNDS_DIV, &wd_fault, &wd_term_ok, &wd_u_neg, &wd_v_neg, signs_d, wtab);
    if (wd_fault) {
        return pp_wrapped_output_correct(tx, ty, ox, oy, lam, signs_d, signs_m, wtab)
                   ? 0 : PP_F_WALK_DIV;
    }
    if (!wd_term_ok || pp_walkback_fold_fault(x2)) {
        return PP_F_WALK_DIV;
    }
    u64 xd[4], y2d[4];
    pp_divide_replay(y2, signs_d, wd_u_neg, wd_v_neg, xd, y2d);
    if (!pp_eq(xd, y2d)) {
        return PP_F_REPLAY_DIV; // coefficient not cleared -> dirty free
    }

    // tlm_coord_add3x: x2 += 3*ox (classical 3x mod p is exact)
    u64 three[4], x2b[4], x2c[4];
    pp_fadd(ox, ox, three);
    pp_fadd(three, ox, three);
    pp_mod_add_exact_model(three, x2, x2b);

    // tlm_square: x2 -= lambda^2 (product-register square, windowed)
    pp_square_model(y2d, x2b, x2c);

    // Multiply traversal (denominator x2c, numerator y2d)
    if (pp_is_zero(x2c)) {
        return PP_F_WALK_MUL;
    }
    bool wm_fault, wm_term_ok, wm_u_neg, wm_v_neg;
    pp_walk_sig(x2c, PP_ROUNDS_MUL, &wm_fault, &wm_term_ok, &wm_u_neg, &wm_v_neg, signs_m, wtab);
    if (wm_fault) {
        return pp_wrapped_output_correct(tx, ty, ox, oy, lam, signs_d, signs_m, wtab)
                   ? 0 : PP_F_WALK_MUL;
    }
    if (!wm_term_ok || pp_walkback_fold_fault(x2c)) {
        return PP_F_WALK_MUL;
    }
    u64 xm[4], y2m[4];
    pp_multiply_replay(y2d, signs_m, wm_u_neg, wm_v_neg, xm, y2m);
    if (!pp_is_zero(xm)) {
        return PP_F_REPLAY_MUL; // coefficient not cleared -> dirty free
    }

    // tlm_coord_y_sub_final / tlm_coord_rsub_final
    u64 y2f[4], x2f[4];
    pp_coord_sub_final_model(y2m, oy, y2f);
    pp_coord_rsub_model(x2c, ox, x2f);

    if (!pp_eq(x2f, rx) || !pp_eq(y2f, ry)) {
        return PP_F_RESULT;
    }
    return 0;
}

PP_HD u32 pp_shot_fault_mask(const u64 tx[4], const u64 ty[4], const u64 ox[4],
                             const u64 oy[4], const u64 lam[4]) {
    u64 signs_d[11], signs_m[11];
#ifdef __CUDA_ARCH__
    const u16* tab = PP_WIDTH_SCHEDULE_D;
#else
    const u16* tab = PP_WIDTH_SCHEDULE;
#endif
    return pp_shot_fault_mask_s(tx, ty, ox, oy, lam, signs_d, signs_m, tab);
}
