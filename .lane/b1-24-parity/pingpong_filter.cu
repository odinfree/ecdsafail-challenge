// ===========================================================================
// pingpong_gpu -- CUDA classical prefilter for the ping-pong divider circuit.
//
// A function-by-function transliteration of the VALIDATED CPU reference
//   src/bin/pingpong_filter.rs   (md5 f35c70fe1d0859c9124a568b97b0d269)
// against circuit commit cc82b18.  Every device function below names the Rust
// line it mirrors; when in doubt, the Rust file is the authority.
//
// SCOPE: CLASSICAL CHANNELS ONLY.  The chunk-boundary and flag comparators of
// the circuit fail through the PHASE channel and are invisible to any purely
// classical model.  A nonce this filter calls clean STILL needs a CPU
// eval_circuit phase-confirm.  See README.md.
//
// LIMB CHOICE: 64-bit limbs throughout, word-for-word with the Rust reference.
// This is deliberate for v1: the width-adaptive walk masks and truncates at
// 64*NL boundaries, and moving those boundaries is a documented FALSE-NEGATIVE
// hazard.  A 32-bit-limb rewrite is a measured-speedup follow-up, not a
// correctness prerequisite.
// ===========================================================================

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <chrono>
#include <vector>
#include <string>
#include <cuda_runtime.h>
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif

typedef unsigned long long u64;
typedef unsigned int       u32;
typedef unsigned char      u8;

#define CUCHK(x) do { cudaError_t _e = (x); if (_e != cudaSuccess) { \
    fprintf(stderr, "pingpong_gpu: CUDA error at %s:%d (%s): %s\n", __FILE__, __LINE__, #x, \
            cudaGetErrorString(_e)); exit(3);} } while (0)

// ---------------------------------------------------------------------------
// shape constants (mirror pingpong_filter.rs)
// ---------------------------------------------------------------------------
#define N_BITS       256
#define VALUE_WIDTH  259          // N + 3
#define NUM_TESTS    9024
#define RATE         136          // SHAKE256 rate
#define TAIL_OPS     96
#define ABSORB_BPO   49
#define CKP_SIZE     5064
#define MAX_ROUNDS   1024
#define MAX_BLK      64
#define FCV          0x1000003d1ULL
#define TAPE_WORDS   (MAX_ROUNDS / 32)
#define EXPECTED_OPS_B1_24 12822408ULL

// ===========================================================================
// Keccak-f[1600]                                     (pingpong_filter.rs:57)
// rho/pi is written out with literal lane indices so the 25-lane state stays
// in registers (a table-driven index would force it to local memory).
// ===========================================================================
static const u64 H_RC[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL, 0x8000000080008000ULL,
    0x000000000000808bULL, 0x0000000080000001ULL, 0x8000000080008081ULL, 0x8000000000008009ULL,
    0x000000000000008aULL, 0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL, 0x000000000000800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL };
__constant__ u64 c_RC[24];

__device__ __forceinline__ u64 rotl64(u64 x, int n) { return (x << n) | (x >> (64 - n)); }

#define RHOPI(J, R) do { tmp = a[J]; a[J] = rotl64(t, R); t = tmp; } while (0)

__device__ __forceinline__ void d_keccakf(u64 a[25]) {
    for (int r = 0; r < 24; ++r) {
        u64 bc0 = a[0]^a[5]^a[10]^a[15]^a[20];
        u64 bc1 = a[1]^a[6]^a[11]^a[16]^a[21];
        u64 bc2 = a[2]^a[7]^a[12]^a[17]^a[22];
        u64 bc3 = a[3]^a[8]^a[13]^a[18]^a[23];
        u64 bc4 = a[4]^a[9]^a[14]^a[19]^a[24];
        u64 d0 = bc4 ^ rotl64(bc1, 1);
        u64 d1 = bc0 ^ rotl64(bc2, 1);
        u64 d2 = bc1 ^ rotl64(bc3, 1);
        u64 d3 = bc2 ^ rotl64(bc4, 1);
        u64 d4 = bc3 ^ rotl64(bc0, 1);
#pragma unroll
        for (int j = 0; j < 25; j += 5) {
            a[j]^=d0; a[j+1]^=d1; a[j+2]^=d2; a[j+3]^=d3; a[j+4]^=d4;
        }
        u64 t = a[1], tmp;
        RHOPI(10, 1); RHOPI( 7, 3); RHOPI(11, 6); RHOPI(17,10); RHOPI(18,15); RHOPI( 3,21);
        RHOPI( 5,28); RHOPI(16,36); RHOPI( 8,45); RHOPI(21,55); RHOPI(24, 2); RHOPI( 4,14);
        RHOPI(15,27); RHOPI(23,41); RHOPI(19,56); RHOPI(13, 8); RHOPI(12,25); RHOPI( 2,43);
        RHOPI(20,62); RHOPI(14,18); RHOPI(22,39); RHOPI( 9,61); RHOPI( 6,20); RHOPI( 1,44);
#pragma unroll
        for (int j = 0; j < 25; j += 5) {
            u64 b0=a[j],b1=a[j+1],b2=a[j+2],b3=a[j+3],b4=a[j+4];
            a[j  ] = b0 ^ ((~b1) & b2);
            a[j+1] = b1 ^ ((~b2) & b3);
            a[j+2] = b2 ^ ((~b3) & b4);
            a[j+3] = b3 ^ ((~b4) & b0);
            a[j+4] = b4 ^ ((~b0) & b1);
        }
        a[0] ^= c_RC[r];
    }
}
#undef RHOPI

// ===========================================================================
// secp256k1 field arithmetic                        (pingpong_filter.rs:139)
// ===========================================================================
__constant__ u64 c_PMOD[4];
static const u64 H_PMOD[4] = {0xfffffffefffffc2fULL, ~0ULL, ~0ULL, ~0ULL};
static const u64 H_GX[4] = {0x59f2815b16f81798ULL,0x029bfcdb2dce28d9ULL,0x55a06295ce870b07ULL,0x79be667ef9dcbbacULL};
static const u64 H_GY[4] = {0x9c47d08ffb10d4b8ULL,0xfd17b448a6855419ULL,0x5da4fbfc0e1108a8ULL,0x483ada7726a3c465ULL};

#ifdef __CUDA_ARCH__
#define PMODP c_PMOD
#else
#define PMODP H_PMOD
#endif

__host__ __device__ __forceinline__ u64 mulhi64(u64 a, u64 b) {
#ifdef __CUDA_ARCH__
    return __umul64hi(a, b);
#else
    // MSVC has no __int128; 32x32 split (host only, used for the comb table).
    u64 a0 = a & 0xffffffffULL, a1 = a >> 32, b0 = b & 0xffffffffULL, b1 = b >> 32;
    u64 p00 = a0*b0, p01 = a0*b1, p10 = a1*b0, p11 = a1*b1;
    u64 mid = (p00 >> 32) + (p01 & 0xffffffffULL) + (p10 & 0xffffffffULL);
    return p11 + (p01 >> 32) + (p10 >> 32) + (mid >> 32);
#endif
}

__host__ __device__ __forceinline__ void u4_copy(u64 r[4], const u64 a[4]) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = a[i];
}
__host__ __device__ __forceinline__ bool u4_is_zero(const u64 a[4]) {
    return (a[0] | a[1] | a[2] | a[3]) == 0;
}
__host__ __device__ __forceinline__ bool u4_eq(const u64 a[4], const u64 b[4]) {
    return a[0]==b[0] && a[1]==b[1] && a[2]==b[2] && a[3]==b[3];
}
// pingpong_filter.rs:158
__host__ __device__ __forceinline__ bool u4_ge(const u64 a[4], const u64 b[4]) {
    if (a[3] != b[3]) return a[3] > b[3];
    if (a[2] != b[2]) return a[2] > b[2];
    if (a[1] != b[1]) return a[1] > b[1];
    if (a[0] != b[0]) return a[0] > b[0];
    return true;
}
// pingpong_filter.rs:169
__host__ __device__ __forceinline__ u64 u4_addc(u64 r[4], const u64 a[4], const u64 b[4]) {
#ifdef __CUDA_ARCH__
    u64 r0,r1,r2,r3,c;
    asm("add.cc.u64  %0, %5,  %9;\n\t"
        "addc.cc.u64 %1, %6, %10;\n\t"
        "addc.cc.u64 %2, %7, %11;\n\t"
        "addc.cc.u64 %3, %8, %12;\n\t"
        "addc.u64    %4,  0,   0;"
        : "=l"(r0),"=l"(r1),"=l"(r2),"=l"(r3),"=l"(c)
        : "l"(a[0]),"l"(a[1]),"l"(a[2]),"l"(a[3]),
          "l"(b[0]),"l"(b[1]),"l"(b[2]),"l"(b[3]));
    r[0]=r0; r[1]=r1; r[2]=r2; r[3]=r3;
    return c;
#else
    u64 c = 0;
    for (int i = 0; i < 4; ++i) {
        u64 s = a[i] + b[i];      u64 c1 = (s < a[i]);
        u64 s2 = s + c;           u64 c2 = (s2 < s);
        r[i] = s2;                c = c1 | c2;
    }
    return c;
#endif
}
// pingpong_filter.rs:180
__host__ __device__ __forceinline__ u64 u4_subb(u64 r[4], const u64 a[4], const u64 b[4]) {
    u64 brw = 0;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        u64 t  = a[i] - b[i];    u64 b1 = (a[i] < b[i]);
        u64 t2 = t - brw;        u64 b2 = (t < brw);
        r[i] = t2;               brw = b1 | b2;
    }
    return brw;
}
__host__ __device__ __forceinline__ void u4_not(u64 r[4], const u64 a[4]) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = ~a[i];
}
__host__ __device__ __forceinline__ void u4_xor(u64 r[4], const u64 a[4], const u64 b[4]) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = a[i] ^ b[i];
}
__host__ __device__ __forceinline__ void u4_shr1(u64 r[4], const u64 a[4]) {
    u64 t0 = (a[0]>>1)|(a[1]<<63), t1 = (a[1]>>1)|(a[2]<<63),
        t2 = (a[2]>>1)|(a[3]<<63), t3 = a[3]>>1;
    r[0]=t0; r[1]=t1; r[2]=t2; r[3]=t3;
}
__host__ __device__ __forceinline__ void u4_shl1(u64 r[4], const u64 a[4]) {
    u64 t3 = (a[3]<<1)|(a[2]>>63), t2 = (a[2]<<1)|(a[1]>>63),
        t1 = (a[1]<<1)|(a[0]>>63), t0 = a[0]<<1;
    r[0]=t0; r[1]=t1; r[2]=t2; r[3]=t3;
}
// pingpong_filter.rs:198
__host__ __device__ __forceinline__ void fe_norm(u64 r[4], const u64 a[4]) {
    if (u4_ge(a, PMODP)) u4_subb(r, a, PMODP); else u4_copy(r, a);
}
// pingpong_filter.rs:207
__host__ __device__ __forceinline__ void fe_add(u64 r[4], const u64 a[4], const u64 b[4]) {
    u64 t[4]; u64 c = u4_addc(t, a, b);
    if (c == 1 || u4_ge(t, PMODP)) u4_subb(r, t, PMODP); else u4_copy(r, t);
}
// pingpong_filter.rs:216
__host__ __device__ __forceinline__ void fe_sub(u64 r[4], const u64 a[4], const u64 b[4]) {
    u64 t[4]; u64 brw = u4_subb(t, a, b);
    if (brw == 1) u4_addc(r, t, PMODP); else u4_copy(r, t);
}
// pingpong_filter.rs:232
__host__ __device__ __forceinline__ void reduce512(u64 r[4], const u64 t[8]) {
    u64 m[5];
    u64 c = 0;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        u64 plo = t[4+i] * FCV;
        u64 phi = mulhi64(t[4+i], FCV);
        u64 s = plo + c;  u64 cc = (s < plo);
        m[i] = s;         c = phi + cc;
    }
    m[4] = c;
    u64 carry = 0;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        u64 s = m[i] + t[i];  u64 c1 = (s < m[i]);
        u64 s2 = s + carry;   u64 c2 = (s2 < s);
        m[i] = s2;            carry = c1 | c2;
    }
    m[4] = m[4] + carry;
    u64 rr[4] = { m[0], m[1], m[2], m[3] };
    u64 hi = m[4];
    while (hi != 0) {
        u64 addend[4] = { hi * FCV, mulhi64(hi, FCV), 0, 0 };
        hi = u4_addc(rr, rr, addend);
    }
    fe_norm(r, rr);
}
// pingpong_filter.rs:263
__host__ __device__ __forceinline__ void fe_mul(u64 r[4], const u64 a[4], const u64 b[4]) {
    u64 t[8];
#pragma unroll
    for (int i = 0; i < 8; ++i) t[i] = 0;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        u64 carry = 0;
#pragma unroll
        for (int j = 0; j < 4; ++j) {
            u64 lo = a[i] * b[j];
            u64 hi = mulhi64(a[i], b[j]);
            u64 s  = lo + t[i+j];  hi += (s < lo);
            u64 s2 = s + carry;    hi += (s2 < s);
            t[i+j] = s2;           carry = hi;
        }
        t[i+4] = carry;
    }
    reduce512(r, t);
}
__host__ __device__ __forceinline__ void fe_sqr(u64 r[4], const u64 a[4]) { fe_mul(r, a, a); }

// pingpong_filter.rs:280 -- a^(p-2); the exponent is the compile-time p-2.
__host__ __device__ void fe_inv(u64 r[4], const u64 a[4]) {
    const u64 e0 = 0xfffffffefffffc2dULL, e1 = ~0ULL, e2 = ~0ULL, e3 = ~0ULL;
    u64 acc[4] = {1,0,0,0};
    bool started = false;
    for (int i = 255; i >= 0; --i) {
        u64 ew = (i >= 192) ? e3 : ((i >= 128) ? e2 : ((i >= 64) ? e1 : e0));
        if (started) fe_sqr(acc, acc);
        if (((ew >> (i & 63)) & 1ULL) == 1ULL) {
            if (started) fe_mul(acc, acc, a); else u4_copy(acc, a);
            started = true;
        }
    }
    u4_copy(r, acc);
}

// ===========================================================================
// Jacobian EC                                       (pingpong_filter.rs:293)
// ===========================================================================
struct Jac { u64 x[4], y[4], z[4]; };

__host__ __device__ void jac_double(Jac *o, const Jac *p) {
    if (u4_is_zero(p->z)) {
        o->x[0]=1;o->x[1]=0;o->x[2]=0;o->x[3]=0;
        o->y[0]=1;o->y[1]=0;o->y[2]=0;o->y[3]=0;
        o->z[0]=0;o->z[1]=0;o->z[2]=0;o->z[3]=0; return;
    }
    u64 a[4],b[4],c[4],xb[4],d[4],e[4],f[4],x3[4],c8[4],y3[4],z3[4],t[4],t2[4];
    fe_sqr(a, p->x);
    fe_sqr(b, p->y);
    fe_sqr(c, b);
    fe_add(xb, p->x, b);
    fe_sqr(t, xb); fe_add(t2, a, c); fe_sub(d, t, t2);
    fe_add(d, d, d);
    fe_add(t, a, a); fe_add(e, t, a);
    fe_sqr(f, e);
    fe_add(t, d, d); fe_sub(x3, f, t);
    { u64 c2[4], c4[4]; fe_add(c2, c, c); fe_add(c4, c2, c2); fe_add(c8, c4, c4); }
    fe_sub(t, d, x3); fe_mul(t2, e, t); fe_sub(y3, t2, c8);
    fe_mul(t, p->y, p->z); fe_add(z3, t, t);
    u4_copy(o->x, x3); u4_copy(o->y, y3); u4_copy(o->z, z3);
}

// madd-2007-bl with the degenerate cases            (pingpong_filter.rs:325)
__host__ __device__ void jac_add_affine(Jac *o, const Jac *p, const u64 qx[4], const u64 qy[4]) {
    if (u4_is_zero(p->z)) {
        u4_copy(o->x, qx); u4_copy(o->y, qy);
        o->z[0]=1;o->z[1]=0;o->z[2]=0;o->z[3]=0; return;
    }
    u64 z1z1[4],u2[4],s2[4],h[4],rr[4],t[4],t2[4];
    fe_sqr(z1z1, p->z);
    fe_mul(u2, qx, z1z1);
    fe_mul(t, qy, p->z); fe_mul(s2, t, z1z1);
    fe_sub(h, u2, p->x);
    fe_sub(rr, s2, p->y);
    if (u4_is_zero(h)) {
        if (u4_is_zero(rr)) { jac_double(o, p); return; }
        o->x[0]=1;o->x[1]=0;o->x[2]=0;o->x[3]=0;
        o->y[0]=1;o->y[1]=0;o->y[2]=0;o->y[3]=0;
        o->z[0]=0;o->z[1]=0;o->z[2]=0;o->z[3]=0; return;
    }
    u64 hh[4],ii[4],j[4],rd[4],v[4],x3[4],y1j[4],y3[4],zh[4],z3[4];
    fe_sqr(hh, h);
    fe_add(t, hh, hh); fe_add(ii, t, t);
    fe_mul(j, h, ii);
    fe_add(rd, rr, rr);
    fe_mul(v, p->x, ii);
    fe_sqr(t, rd); fe_sub(t, t, j); fe_add(t2, v, v); fe_sub(x3, t, t2);
    fe_mul(y1j, p->y, j);
    fe_sub(t, v, x3); fe_mul(t, rd, t); fe_add(t2, y1j, y1j); fe_sub(y3, t, t2);
    fe_add(zh, p->z, h);
    fe_sqr(t, zh); fe_sub(t, t, z1z1); fe_sub(z3, t, hh);
    u4_copy(o->x, x3); u4_copy(o->y, y3); u4_copy(o->z, z3);
}

// ===========================================================================
// device constants uploaded by the host
// ===========================================================================
__constant__ u64 c_masks[VALUE_WIDTH + 1][5];
__constant__ unsigned short c_wid_div[MAX_ROUNDS];
__constant__ unsigned short c_wid_mul[MAX_ROUNDS];
__constant__ int c_rounds_div, c_rounds_mul, c_fold_w, c_endpoint_m, c_seed_m;
__constant__ u64 c_state0[25];
__constant__ u64 c_stream[MAX_BLK * 17];
__constant__ u32 c_patch[TAIL_OPS];   // blk:8 | lane:5 | shift:6 | noncebit:6
__constant__ int c_nblk;

// ===========================================================================
// W5 helpers                                        (pingpong_filter.rs:420)
// Every `_n<NL>` variant ZEROES words >= NL, exactly like the Rust original.
// Bit indexing uses select chains, not dynamic indexing, so the 5-limb values
// stay in registers.
// ===========================================================================
__device__ __forceinline__ void w_copy5(u64 r[5], const u64 a[5]) {
#pragma unroll
    for (int i = 0; i < 5; ++i) r[i] = a[i];
}
__device__ __forceinline__ u64 w_bit(const u64 a[5], int i) {
    int wd = i >> 6, sh = i & 63;
    u64 x = 0;
#pragma unroll
    for (int k = 0; k < 5; ++k) x = (k == wd) ? a[k] : x;
    return (x >> sh) & 1ULL;
}
__device__ __forceinline__ void w_set_bit(u64 a[5], int i, u64 v) {
    int wd = i >> 6, sh = i & 63;
    u64 m = 1ULL << sh, val = v << sh;
#pragma unroll
    for (int k = 0; k < 5; ++k) a[k] = (k == wd) ? ((a[k] & ~m) | val) : a[k];
}
__device__ __forceinline__ void w_xor_bit(u64 a[5], int i, u64 v) {
    int wd = i >> 6, sh = i & 63;
    u64 val = v << sh;
#pragma unroll
    for (int k = 0; k < 5; ++k) a[k] ^= (k == wd) ? val : 0ULL;
}
// Full 5-limb add.  Carry propagation is strictly upward, so doing the full
// width and then zeroing words >= NL is bit-identical to Rust's w_add_n::<NL>.
__device__ __forceinline__ void w_add5(u64 r[5], const u64 a[5], const u64 b[5]) {
    u64 r0,r1,r2,r3,r4;
    asm("add.cc.u64  %0, %5, %10;\n\t"
        "addc.cc.u64 %1, %6, %11;\n\t"
        "addc.cc.u64 %2, %7, %12;\n\t"
        "addc.cc.u64 %3, %8, %13;\n\t"
        "addc.u64    %4, %9, %14;"
        : "=l"(r0),"=l"(r1),"=l"(r2),"=l"(r3),"=l"(r4)
        : "l"(a[0]),"l"(a[1]),"l"(a[2]),"l"(a[3]),"l"(a[4]),
          "l"(b[0]),"l"(b[1]),"l"(b[2]),"l"(b[3]),"l"(b[4]));
    r[0]=r0; r[1]=r1; r[2]=r2; r[3]=r3; r[4]=r4;
}
template<int NL> __device__ __forceinline__ void w_add_n(u64 r[5], const u64 a[5], const u64 b[5]) {
    u64 t[5]; w_add5(t, a, b);
#pragma unroll
    for (int i = 0; i < 5; ++i) r[i] = (i < NL) ? t[i] : 0ULL;
}
template<int NL> __device__ __forceinline__ void w_and_n(u64 r[5], const u64 a[5], const u64 b[5]) {
#pragma unroll
    for (int i = 0; i < 5; ++i) r[i] = (i < NL) ? (a[i] & b[i]) : 0ULL;
}
template<int NL> __device__ __forceinline__ void w_xor_n(u64 r[5], const u64 a[5], const u64 b[5]) {
#pragma unroll
    for (int i = 0; i < 5; ++i) r[i] = (i < NL) ? (a[i] ^ b[i]) : 0ULL;
}
// pingpong_filter.rs:476   (s is always 1 or 2)
template<int NL> __device__ __forceinline__ void w_shr_n(u64 r[5], const u64 a[5], int s) {
    u64 t[5];
#pragma unroll
    for (int i = 0; i < 5; ++i)
        t[i] = (i < NL) ? ((a[i] >> s) | (((i+1) < NL) ? (a[i+1] << (64 - s)) : 0ULL)) : 0ULL;
    w_copy5(r, t);
}
// pingpong_filter.rs:489
template<int NL> __device__ __forceinline__ void w_shl_n(u64 r[5], const u64 a[5], int s) {
    u64 t[5];
#pragma unroll
    for (int i = 0; i < 5; ++i)
        t[i] = (i < NL) ? ((a[i] << s) | ((i > 0) ? (a[i-1] >> (64 - s)) : 0ULL)) : 0ULL;
    w_copy5(r, t);
}
// pingpong_filter.rs:533 (the Rust early `break` is a pure optimisation)
__device__ __forceinline__ void w_add_u64(u64 r[5], u64 v) {
    u64 c = v;
#pragma unroll
    for (int i = 0; i < 5; ++i) { u64 t = r[i] + c; c = (t < r[i]); r[i] = t; }
}

// ===========================================================================
// signed_add_wrapping_sigma                         (pingpong_filter.rs:677)
// ===========================================================================
template<int NL>
__device__ __forceinline__ void sigma_add_n(u64 res[5], u64 sign, const u64 src[5],
                                            const u64 tgt[5], int w, int t0_is_one) {
    const u64 *m = c_masks[w];
    u64 tp[5];
    if (sign == 1) { w_xor_n<NL>(tp, tgt, m); } else { w_copy5(tp, tgt); }
    u64 c0 = sign ^ (u64)t0_is_one;
    u64 b0 = (tp[0] ^ src[0]) & 1;
    u64 b1 = ((tp[0] >> 1) ^ (src[0] >> 1) ^ c0) & 1;
    u64 c1 = (src[0] >> 1) & 1;
    u64 sa[5], sb[5], high[5];
    w_shr_n<NL>(sa, tp, 2);
    w_shr_n<NL>(sb, src, 2);
    w_add_n<NL>(high, sa, sb);
    w_add_u64(high, c1);
    w_and_n<NL>(high, high, c_masks[w-2]);
    u64 t[5];
    w_shl_n<NL>(t, high, 2);
    t[0] |= (b1 << 1) | b0;
    if (sign == 1) w_xor_n<NL>(res, t, m); else w_copy5(res, t);
}

// ===========================================================================
// round-0 fused lift                                (pingpong_filter.rs:704)
// ===========================================================================
__device__ __forceinline__ u64 fused_lift_round0_forward(u64 v[5]) {
    u64 a0 = v[0] & 1;
    u64 t[5]; w_shr_n<5>(t, v, 1); w_copy5(v, t);
    u64 not_a1 = 1ULL ^ (v[0] & 1);
    const u64 f4[4] = { FCV, 0, 0, 0 };
    const u64 hcon = (FCV - 1) >> 1;
    u64 k[4] = {0,0,0,0};
    if (not_a1 == 1) u4_addc(k, k, f4);
    if (a0 == 1) {
        const u64 zero4[4] = {0,0,0,0};
        const u64 hv[4] = { hcon, 0, 0, 0 };
        u64 negh[4]; u4_subb(negh, zero4, hv);
        u4_addc(k, k, negh);
    }
    u64 lo[4] = { v[0], v[1], v[2], v[3] };
    u64 s[4]; u4_addc(s, lo, k);
    v[0]=s[0]; v[1]=s[1]; v[2]=s[2]; v[3]=s[3];
#pragma unroll
    for (int i = N_BITS; i < VALUE_WIDTH; ++i) w_xor_bit(v, i, not_a1);
    w_xor_bit(v, N_BITS - 1, a0);
    return a0;
}
// pingpong_filter.rs:734
__device__ __forceinline__ void fused_lift_round0_reverse(u64 v[5], u64 a0, int fold_w) {
    u64 not_a1 = w_bit(v, VALUE_WIDTH - 1);
    w_xor_bit(v, VALUE_WIDTH - 1, not_a1);
    u64 sh[5]; w_shl_n<5>(sh, v, 1);
#pragma unroll
    for (int i = 0; i < 5; ++i) v[i] = sh[i] & c_masks[VALUE_WIDTH][i];
    u64 k2 = (a0 == 1) ? FCV : ((not_a1 == 1) ? (2ULL * FCV) : 0ULL);
    u64 lo[4] = { v[0], v[1], v[2], v[3] };
    if (not_a1 == 1) u4_not(lo, lo);
    u64 fm = (fold_w >= 64) ? ~0ULL : ((1ULL << fold_w) - 1ULL);
    lo[0] = (lo[0] & ~fm) | ((lo[0] + k2) & fm);
    if (not_a1 == 1) u4_not(lo, lo);
    v[0]=lo[0]; v[1]=lo[1]; v[2]=lo[2]; v[3]=lo[3];
    w_xor_bit(v, N_BITS,     a0);
    w_xor_bit(v, N_BITS + 1, not_a1);
    w_xor_bit(v, N_BITS + 2, not_a1);
}

// ===========================================================================
// forward walk                                      (pingpong_filter.rs:766)
// ===========================================================================
template<int NL>
__device__ __forceinline__ u64 walk_core(u64 src[5], u64 tgt[5], int w) {
    u64 sign = ((tgt[0] >> 1) & 1) ^ ((src[0] >> 1) & 1);
    u64 t[5]; sigma_add_n<NL>(t, sign, src, tgt, w, 1);
    u64 a0 = t[0] & 1;
    u64 rot[5]; w_shr_n<NL>(rot, t, 1);
    w_set_bit(rot, w - 1, a0);
    u64 top = w_bit(rot, w - 1) ^ w_bit(rot, w - 2);
    u64 nt[5]; w_and_n<NL>(nt, rot, c_masks[w-1]);
    w_set_bit(nt, w - 1, top);
    w_copy5(tgt, nt);
    return sign;
}
template<int NL>
__device__ __forceinline__ u64 walk_round_n(u64 u[5], u64 v[5], int r, int w) {
    const u64 *mask = c_masks[w];
    w_and_n<NL>(u, u, mask);
    w_and_n<NL>(v, v, mask);
    if (r == 0) return fused_lift_round0_forward(v);
    if ((r & 1) == 0) return walk_core<NL>(u, v, w);   // even: src=u, tgt=v
    else              return walk_core<NL>(v, u, w);   // odd : src=v, tgt=u
}
__device__ __forceinline__ u64 walk_round(u64 u[5], u64 v[5], int r, int w) {
    switch ((w + 63) / 64) {
        case 1:  return walk_round_n<1>(u, v, r, w);
        case 2:  return walk_round_n<2>(u, v, r, w);
        case 3:  return walk_round_n<3>(u, v, r, w);
        case 4:  return walk_round_n<4>(u, v, r, w);
        default: return walk_round_n<5>(u, v, r, w);
    }
}
// pingpong_filter.rs:803
__device__ __forceinline__ void sign_extend(u64 v[5], int from_w, int to_w) {
    if (w_bit(v, from_w - 1) == 1) {
#pragma unroll
        for (int i = 0; i < 5; ++i) v[i] |= c_masks[to_w][i] & ~c_masks[from_w][i];
    }
}
// pingpong_filter.rs:811
template<int NL>
__device__ __forceinline__ void walk_back_core(u64 src[5], u64 tgt0[5], u64 sign, int w) {
    u64 b = w_bit(tgt0, w - 1) ^ w_bit(tgt0, w - 2);
    u64 tgt[5]; w_and_n<NL>(tgt, tgt0, c_masks[w-1]);
    w_set_bit(tgt, w - 1, b);
    u64 sh[5]; w_shl_n<NL>(sh, tgt, 1);
    w_and_n<NL>(sh, sh, c_masks[w]);
    sh[0] |= b;
    u64 t[5]; sigma_add_n<NL>(t, sign ^ 1ULL, src, sh, w, 0);
    w_copy5(tgt0, t);
}
template<int NL>
__device__ __forceinline__ void walk_back_round_n(u64 u[5], u64 v[5], int w_prev,
                                                  int r, u64 sign, int w, int fold_w) {
    if (w > w_prev) { sign_extend(u, w_prev, w); sign_extend(v, w_prev, w); }
    if (r == 0) { fused_lift_round0_reverse(v, sign, fold_w); return; }
    if ((r & 1) == 0) walk_back_core<NL>(u, v, sign, w);
    else              walk_back_core<NL>(v, u, sign, w);
}
__device__ __forceinline__ void walk_back_round(u64 u[5], u64 v[5], int w_prev,
                                                int r, u64 sign, int w, int fold_w) {
    switch ((w + 63) / 64) {
        case 1:  walk_back_round_n<1>(u, v, w_prev, r, sign, w, fold_w); break;
        case 2:  walk_back_round_n<2>(u, v, w_prev, r, sign, w, fold_w); break;
        case 3:  walk_back_round_n<3>(u, v, w_prev, r, sign, w, fold_w); break;
        case 4:  walk_back_round_n<4>(u, v, w_prev, r, sign, w, fold_w); break;
        default: walk_back_round_n<5>(u, v, w_prev, r, sign, w, fold_w); break;
    }
}

// ===========================================================================
// replay cells (256-bit)                            (pingpong_filter.rs:857)
// ===========================================================================
__device__ __forceinline__ void const_trunc(u64 out[4], const u64 acc[4], u64 c, int mbits, int sub) {
    int hkw = mbits >> 6, hkb = mbits & 63;
    u64 mask[4], low[4];
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        mask[i] = (i < hkw) ? ~0ULL : ((i == hkw && hkb > 0) ? ((1ULL << hkb) - 1ULL) : 0ULL);
        low[i]  = acc[i] & mask[i];
    }
    const u64 cv[4] = { c, 0, 0, 0 };
    u64 r[4];
    if (sub) u4_subb(r, low, cv); else u4_addc(r, low, cv);
#pragma unroll
    for (int i = 0; i < 4; ++i) out[i] = (acc[i] & ~mask[i]) | (r[i] & mask[i]);
}
// pingpong_filter.rs:891
__device__ __forceinline__ u64 fold_operand(u64 minus_f, u64 plus_2f, u64 plus_f, int fold_w) {
    if (minus_f == 1) return (fold_w >= 64) ? (0ULL - FCV) : ((1ULL << fold_w) - FCV);
    if (plus_2f == 1) return 2ULL * FCV;
    if (plus_f  == 1) return FCV;
    return 0ULL;
}
// pingpong_filter.rs:882 -- branchless: operand==0 leaves acc unchanged.
__device__ __forceinline__ void fold_apply(u64 acc[4], u64 operand, int fold_w) {
    u64 fm = (fold_w >= 64) ? ~0ULL : ((1ULL << fold_w) - 1ULL);
    acc[0] = (acc[0] & ~fm) | ((acc[0] + operand) & fm);
}
// pingpong_filter.rs:909
__device__ __forceinline__ void mod_halve_pm(u64 out[4], const u64 tin[4], int endpoint_m) {
    u64 parity = tin[0] & 1;
    u64 t[4]; u4_copy(t, tin);
    if (parity == 1) const_trunc(t, t, FCV, endpoint_m, 1);
    u64 d0 = t[0] & 1;
    u64 rot[4]; u4_shr1(rot, t);
    rot[3] |= (d0 ^ parity) << 63;
    u4_copy(out, rot);
}
// pingpong_filter.rs:919
__device__ __forceinline__ void mod_double_pm(u64 out[4], const u64 tin[4], int endpoint_m) {
    u64 o = (tin[3] >> 63) & 1;
    u64 t[4]; u4_shl1(t, tin);
    if (o == 1) const_trunc(t, t, FCV, endpoint_m, 0);
    u4_copy(out, t);
}
// pingpong_filter.rs:929
__device__ __forceinline__ void seed_round_one(u64 out[4], u64 sign, const u64 src[4],
                                               const u64 tgt[4], int seed_m) {
    u64 t[4]; u4_xor(t, tgt, src);
    if (sign == 1) { u4_not(t, t); const_trunc(t, t, FCV - 1, seed_m, 1); }
    u4_copy(out, t);
}
// pingpong_filter.rs:938
__device__ __forceinline__ void seed_round_one_inverse(u64 out[4], u64 sign, const u64 src[4],
                                                       const u64 tgt[4], int seed_m) {
    u64 t[4]; u4_copy(t, tgt);
    if (sign == 1) { const_trunc(t, t, FCV - 1, seed_m, 0); u4_not(t, t); }
    u4_xor(out, t, src);
}
// pingpong_filter.rs:948
__device__ __forceinline__ void smaph(u64 out[4], u64 sign, const u64 src[4],
                                      const u64 tgt[4], int fold_w) {
    u64 acc[4];
    if (sign == 1) u4_not(acc, tgt); else u4_copy(acc, tgt);
    u64 o = u4_addc(acc, acc, src);
    u64 par = acc[0] & 1;
    u64 minus_f = (1ULL - o) & (1ULL - sign) & par;
    u64 plus_2f = o & sign & par;
    u64 plus_f  = minus_f ^ sign ^ par;
    fold_apply(acc, fold_operand(minus_f, plus_2f, plus_f, fold_w), fold_w);
    u64 newtop = par ^ o ^ sign;
    u64 d[4];
    if (sign == 1) u4_not(d, acc); else u4_copy(d, acc);
    u64 d0 = d[0] & 1;
    u64 res[4]; u4_shr1(res, d);
    res[3] |= (d0 ^ newtop) << 63;
    u4_copy(out, res);
}
// pingpong_filter.rs:966
__device__ __forceinline__ void smdapf(u64 out[4], u64 sign, const u64 src[4],
                                       const u64 tgt[4], int fold_w) {
    u64 d = (tgt[3] >> 63) & 1;
    u64 acc[4]; u4_shl1(acc, tgt);
    if (sign == 1) u4_not(acc, acc);
    u64 o = u4_addc(acc, acc, src);
    u64 routed  = d & (sign ^ o);
    u64 minus_f = routed & sign;
    u64 plus_2f = routed ^ minus_f;
    u64 plus_f  = d ^ o ^ minus_f;
    fold_apply(acc, fold_operand(minus_f, plus_2f, plus_f, fold_w), fold_w);
    if (sign == 1) u4_not(out, acc); else u4_copy(out, acc);
}
// pingpong_filter.rs:989
__device__ __forceinline__ void conditional_mod_negate(u64 out[4], u64 ctrl, const u64 value[4],
                                                       int endpoint_m) {
    if (ctrl == 0) { u4_copy(out, value); return; }
    u64 t[4]; u4_not(t, value);
    const_trunc(out, t, FCV - 1, endpoint_m, 1);
}

// ===========================================================================
// pingpong_divide                                  (pingpong_filter.rs:1005)
// ===========================================================================
__device__ void pingpong_divide(u64 dxr[4], u64 lam[4], const u64 den[4], const u64 num[4],
                                u32 *tape) {
    const int rounds = c_rounds_div;
    const int fold_w = c_fold_w, endpoint_m = c_endpoint_m, seed_m = c_seed_m;
    u64 u[5] = { c_PMOD[0], c_PMOD[1], c_PMOD[2], c_PMOD[3], 0 };
    u64 v[5] = { den[0], den[1], den[2], den[3], 0 };
    for (int r = 0; r < rounds; ++r) {
        u64 sg = walk_round(u, v, r, (int)c_wid_div[r]);
        if ((r & 31) == 0) tape[r >> 5] = 0;
        tape[r >> 5] |= ((u32)sg) << (r & 31);
    }
    const int w = (int)c_wid_div[rounds - 1];
    u64 su = w_bit(u, w - 1), sv = w_bit(v, w - 1);
#pragma unroll
    for (int i = 0; i < 5; ++i) {
        u[i] = su ? c_masks[w][i] : ((i == 0) ? 1ULL : 0ULL);
        v[i] = sv ? c_masks[w][i] : ((i == 0) ? 1ULL : 0ULL);
    }
    u64 x[4] = {0,0,0,0};
    u64 y[4] = { num[0], num[1], num[2], num[3] };
    for (int r = 0; r < rounds; ++r) {
        u64 sign = (tape[r >> 5] >> (r & 31)) & 1u;
        u64 nt[4];
        if ((r & 1) == 0) {                 // even: src = x, tgt = y
            if (r == 0) mod_halve_pm(nt, y, endpoint_m);
            else        smaph(nt, sign, x, y, fold_w);
            u4_copy(y, nt);
        } else {                             // odd:  src = y, tgt = x
            if (r == 1) { u64 s[4]; seed_round_one(s, sign, y, x, seed_m);
                          mod_halve_pm(nt, s, endpoint_m); }
            else        smaph(nt, sign, y, x, fold_w);
            u4_copy(x, nt);
        }
    }
    conditional_mod_negate(y, sv, y, endpoint_m);
    int wp = w;
    for (int r = rounds - 1; r >= 0; --r) {
        int wr = (int)c_wid_div[r];
        u64 sign = (tape[r >> 5] >> (r & 31)) & 1u;
        walk_back_round(u, v, wp, r, sign, wr, fold_w);
        wp = wr;
    }
    if (wp < VALUE_WIDTH) sign_extend(v, wp, VALUE_WIDTH);
    dxr[0]=v[0]; dxr[1]=v[1]; dxr[2]=v[2]; dxr[3]=v[3];
    u4_copy(lam, y);
}

// pingpong_multiply                                (pingpong_filter.rs:1064)
__device__ void pingpong_multiply(u64 xout[4], u64 yout[4], const u64 den[4], const u64 num[4],
                                  u32 *tape) {
    const int rounds = c_rounds_mul;
    const int fold_w = c_fold_w, endpoint_m = c_endpoint_m, seed_m = c_seed_m;
    u64 u[5] = { c_PMOD[0], c_PMOD[1], c_PMOD[2], c_PMOD[3], 0 };
    u64 v[5] = { den[0], den[1], den[2], den[3], 0 };
    for (int r = 0; r < rounds; ++r) {
        u64 sg = walk_round(u, v, r, (int)c_wid_mul[r]);
        if ((r & 31) == 0) tape[r >> 5] = 0;
        tape[r >> 5] |= ((u32)sg) << (r & 31);
    }
    const int w = (int)c_wid_mul[rounds - 1];
    u64 su = w_bit(u, w - 1), sv = w_bit(v, w - 1);
#pragma unroll
    for (int i = 0; i < 5; ++i) {
        u[i] = su ? c_masks[w][i] : ((i == 0) ? 1ULL : 0ULL);
        v[i] = sv ? c_masks[w][i] : ((i == 0) ? 1ULL : 0ULL);
    }
    u64 x[4], y[4];
    conditional_mod_negate(x, su, num, endpoint_m);
    conditional_mod_negate(y, sv, num, endpoint_m);
    for (int r = rounds - 1; r >= 0; --r) {
        u64 sign = (tape[r >> 5] >> (r & 31)) & 1u;
        u64 nt[4];
        if ((r & 1) == 0) {                 // even: src = x, tgt = y
            if (r > 1) smdapf(nt, sign ^ 1ULL, x, y, fold_w);
            else       mod_double_pm(nt, y, endpoint_m);            // r == 0
            u4_copy(y, nt);
        } else {                             // odd:  src = y, tgt = x
            if (r > 1) smdapf(nt, sign ^ 1ULL, y, x, fold_w);
            else { u64 t[4]; mod_double_pm(t, x, endpoint_m);        // r == 1
                   seed_round_one_inverse(nt, sign, y, t, seed_m); }
            u4_copy(x, nt);
        }
    }
    int wp = w;
    for (int r = rounds - 1; r >= 0; --r) {
        int wr = (int)c_wid_mul[r];
        u64 sign = (tape[r >> 5] >> (r & 31)) & 1u;
        walk_back_round(u, v, wp, r, sign, wr, fold_w);
        wp = wr;
    }
    if (wp < VALUE_WIDTH) sign_extend(v, wp, VALUE_WIDTH);
    xout[0]=v[0]; xout[1]=v[1]; xout[2]=v[2]; xout[3]=v[3];
    u4_copy(yout, y);
}

// point_add_classical                              (pingpong_filter.rs:1158)
__device__ void point_add_classical(u64 gx[4], u64 gy[4], const u64 tx[4], const u64 ty[4],
                                    const u64 ox[4], const u64 oy[4], u32 *tape) {
    u64 dx[4], dy[4];
    fe_sub(dx, tx, ox);
    fe_sub(dy, ty, oy);
    u64 dxr[4], lam[4];
    pingpong_divide(dxr, lam, dx, dy, tape);
    u64 ox3[4], t[4];
    fe_add(t, ox, ox); fe_add(ox3, t, ox);
    u64 x[4], dn[4], lamn[4], ls[4];
    fe_norm(dn, dxr);
    fe_add(x, dn, ox3);
    fe_norm(lamn, lam);
    fe_sqr(ls, lamn);
    fe_sub(x, x, ls);
    u64 x2[4], y2[4], n2[4];
    pingpong_multiply(x2, y2, x, lam, tape);
    fe_norm(n2, y2); fe_sub(gy, n2, oy);
    fe_norm(n2, x2); fe_sub(gx, ox, n2);
}

// ===========================================================================
// per-shot verdict.  Cross-multiplication replaces the reference's batch
// inversion: with D = ox-tx invertible, gx*D2==E && gy*D3==T is identical to
// gx==ex && gy==ey.  (Design S6.3.)
// ===========================================================================
__device__ int shot_verdict(const u64 tx[4], const u64 ty[4], const u64 ox[4], const u64 oy[4],
                            int t_inf, int o_inf, u32 *tape) {
    // harness skip rules, pingpong_filter.rs:1348-1362
    if (u4_eq(tx, ox)) return 0;
    if (t_inf || o_inf) return 0;

    u64 D[4], Y[4], D2[4], D3[4], E[4], T[4], t1[4], t2[4];
    fe_sub(D, ox, tx);
    fe_sub(Y, oy, ty);
    fe_sqr(D2, D);
    fe_mul(D3, D2, D);
    fe_sqr(t1, Y);
    fe_add(t2, tx, ox);
    fe_mul(t2, t2, D2);
    fe_sub(E, t1, t2);                  // ex * D2
    fe_mul(t1, tx, D2);
    fe_sub(t1, t1, E);
    fe_mul(t1, Y, t1);
    fe_mul(t2, ty, D3);
    fe_sub(T, t1, t2);                  // ey * D3

    u64 gx[4], gy[4];
    point_add_classical(gx, gy, tx, ty, ox, oy, tape);
    fe_mul(t1, gx, D2);
    if (!u4_eq(t1, E)) return 1;
    fe_mul(t2, gy, D3);
    if (!u4_eq(t2, T)) return 1;
    return 0;
}

// ===========================================================================
// Fiat-Shamir producer kernels
// ===========================================================================
struct SqState { u64 st[25]; u32 lane; };

__global__ void fs_init_kernel(const u64 *__restrict__ nonces, int n, SqState *sq) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    u64 nonce = nonces[i];
    u64 st[25];
#pragma unroll
    for (int k = 0; k < 25; ++k) st[k] = c_state0[k];
    for (int b = 0; b < c_nblk; ++b) {
#pragma unroll
        for (int k = 0; k < 17; ++k) st[k] ^= c_stream[b * 17 + k];
        for (int p = 0; p < TAIL_OPS; ++p) {
            u32 e = c_patch[p];
            if ((int)(e & 0xffu) != b) continue;
            u32 ln = (e >> 8) & 0x1fu, sh = (e >> 13) & 0x3fu, nb = (e >> 19) & 0x3fu;
            u64 val = ((nonce >> nb) & 1ULL) << sh;
#pragma unroll
            for (int k = 0; k < 17; ++k) st[k] ^= (k == (int)ln) ? val : 0ULL;
        }
        d_keccakf(st);
    }
#pragma unroll
    for (int k = 0; k < 25; ++k) sq[i].st[k] = st[k];
    sq[i].lane = 0;
}

__global__ void fs_squeeze_kernel(SqState *sq, u64 *__restrict__ xof, int n,
                                  int nwords, int win_words, const int *__restrict__ dead) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    if (dead && dead[i]) return;
    u64 st[25];
#pragma unroll
    for (int k = 0; k < 25; ++k) st[k] = sq[i].st[k];
    u32 lane = sq[i].lane;
    u64 *out = xof + (size_t)i * (size_t)win_words;
    for (int w = 0; w < nwords; ++w) {
        if (lane == 17u) { d_keccakf(st); lane = 0; }
        u64 x = 0;
#pragma unroll
        for (int k = 0; k < 17; ++k) x = (k == (int)lane) ? st[k] : x;
        out[w] = x;
        ++lane;
    }
#pragma unroll
    for (int k = 0; k < 25; ++k) sq[i].st[k] = st[k];
    sq[i].lane = lane;
}

// ===========================================================================
// model kernel -- one warp per nonce, lane = shot within a 32-shot pass
// ===========================================================================
__device__ __forceinline__ void shfl_up_fe(u64 r[4], const u64 a[4], int d) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = __shfl_up_sync(0xffffffffu, a[i], d, 32);
}
__device__ __forceinline__ void shfl_down_fe(u64 r[4], const u64 a[4], int d) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = __shfl_down_sync(0xffffffffu, a[i], d, 32);
}
__device__ __forceinline__ void shfl_idx_fe(u64 r[4], const u64 a[4], int src) {
#pragma unroll
    for (int i = 0; i < 4; ++i) r[i] = __shfl_sync(0xffffffffu, a[i], src, 32);
}

__device__ __forceinline__ void comb_mul2(Jac *ja, Jac *jb, const u64 k1[4], const u64 k2[4],
                                          const u64 *__restrict__ comb) {
    Jac a; a.x[0]=1;a.x[1]=0;a.x[2]=0;a.x[3]=0;
           a.y[0]=1;a.y[1]=0;a.y[2]=0;a.y[3]=0;
           a.z[0]=0;a.z[1]=0;a.z[2]=0;a.z[3]=0;
    Jac b = a;
    for (int wi = 0; wi < 32; ++wi) {
        u64 kw1 = (wi < 8) ? k1[0] : ((wi < 16) ? k1[1] : ((wi < 24) ? k1[2] : k1[3]));
        u64 kw2 = (wi < 8) ? k2[0] : ((wi < 16) ? k2[1] : ((wi < 24) ? k2[2] : k2[3]));
        unsigned d1 = (unsigned)((kw1 >> ((wi & 7) * 8)) & 0xffULL);
        unsigned d2 = (unsigned)((kw2 >> ((wi & 7) * 8)) & 0xffULL);
        if (d1 != 0) { const u64 *p = comb + (size_t)(wi*255 + d1 - 1)*8;
                       Jac t; jac_add_affine(&t, &a, p, p + 4); a = t; }
        if (d2 != 0) { const u64 *p = comb + (size_t)(wi*255 + d2 - 1)*8;
                       Jac t; jac_add_affine(&t, &b, p, p + 4); b = t; }
    }
    *ja = a; *jb = b;
}

// Occupancy knob: minBlocksPerMultiprocessor.  2 -> 202 regs / 8 warps per SM
// (the ptxas default here, zero spills).  Raising it trades registers for
// warps; measured on the 4090, 2 wins.  -maxrregcount is IGNORED when
// __launch_bounds__ is present, so this is the only lever that works.
#ifndef MODEL_MINBLOCKS
#define MODEL_MINBLOCKS 2
#endif
__global__ __launch_bounds__(128, MODEL_MINBLOCKS)
void model_kernel(const u64 *__restrict__ xof, const u64 *__restrict__ comb,
                  int n, int shot_lo, int shot_hi, int win_words,
                  unsigned long long *counts, int *dead, int screen) {
    const int lane   = threadIdx.x & 31;
    const int wpb    = blockDim.x >> 5;
    const int nwarps = gridDim.x * wpb;
    const int warp0  = blockIdx.x * wpb + (threadIdx.x >> 5);

    u32 tape[TAPE_WORDS];

    for (int slot = warp0; slot < n; slot += nwarps) {
        if (dead && dead[slot]) continue;
        const u64 *base = xof + (size_t)slot * (size_t)win_words;
        unsigned long long acc = 0;
        int aborted = 0;
        for (int s0 = shot_lo; s0 < shot_hi; s0 += 32) {
            const u64 *w = base + (size_t)(s0 - shot_lo + lane) * 8;
            u64 k1[4] = { w[0], w[1], w[2], w[3] };
            u64 k2[4] = { w[4], w[5], w[6], w[7] };

            Jac j0, j1;
            comb_mul2(&j0, &j1, k1, k2, comb);

            int inf0 = u4_is_zero(j0.z), inf1 = u4_is_zero(j1.z);
            u64 z0[4], z1[4];
            u4_copy(z0, j0.z); u4_copy(z1, j1.z);
            if (inf0) { z0[0]=1;z0[1]=0;z0[2]=0;z0[3]=0; }
            if (inf1) { z1[0]=1;z1[1]=0;z1[2]=0;z1[3]=0; }

            // warp-wide Montgomery batch inversion of the 64 z values
            u64 prod[4]; fe_mul(prod, z0, z1);
            u64 inc[4];  u4_copy(inc, prod);
            for (int d = 1; d < 32; d <<= 1) {
                u64 o[4]; shfl_up_fe(o, inc, d);
                if (lane >= d) fe_mul(inc, inc, o);
            }
            u64 suf[4];  u4_copy(suf, prod);
            for (int d = 1; d < 32; d <<= 1) {
                u64 o[4]; shfl_down_fe(o, suf, d);
                if (lane + d < 32) fe_mul(suf, suf, o);
            }
            u64 total[4]; shfl_idx_fe(total, inc, 31);
            u64 tinv[4];  fe_inv(tinv, total);
            u64 preL[4];  shfl_up_fe(preL, inc, 1);
            if (lane == 0)  { preL[0]=1;preL[1]=0;preL[2]=0;preL[3]=0; }
            u64 sufR[4];  shfl_down_fe(sufR, suf, 1);
            if (lane == 31) { sufR[0]=1;sufR[1]=0;sufR[2]=0;sufR[3]=0; }
            u64 pinv[4]; fe_mul(pinv, tinv, preL); fe_mul(pinv, pinv, sufR);
            u64 z0i[4], z1i[4];
            fe_mul(z0i, pinv, z1);
            fe_mul(z1i, pinv, z0);

            u64 tx[4], ty[4], ox[4], oy[4], zz[4], zzz[4];
            fe_sqr(zz, z0i); fe_mul(zzz, zz, z0i);
            fe_mul(tx, j0.x, zz); fe_mul(ty, j0.y, zzz);
            fe_sqr(zz, z1i); fe_mul(zzz, zz, z1i);
            fe_mul(ox, j1.x, zz); fe_mul(oy, j1.y, zzz);
            if (inf0) { tx[0]=0;tx[1]=0;tx[2]=0;tx[3]=0; ty[0]=0;ty[1]=0;ty[2]=0;ty[3]=0; }
            if (inf1) { ox[0]=0;ox[1]=0;ox[2]=0;ox[3]=0; oy[0]=0;oy[1]=0;oy[2]=0;oy[3]=0; }

            int t_inf = u4_is_zero(tx) && u4_is_zero(ty);
            int o_inf = u4_is_zero(ox) && u4_is_zero(oy);

            int mm = shot_verdict(tx, ty, ox, oy, t_inf, o_inf, tape);
            unsigned ball = __ballot_sync(0xffffffffu, mm);
            acc += (unsigned long long)__popc(ball);
            if (screen && ball) { aborted = 1; break; }
        }
        if (lane == 0) {
            if (screen && aborted) { counts[slot] = 1; if (dead) dead[slot] = 1; }
            else                   counts[slot] += acc;
        }
    }
}

// ===========================================================================
// single-shot selftest kernel (1 thread) -- mirrors run_selftest()
// ===========================================================================
__global__ void selftest_kernel(const u64 *__restrict__ xof, const u64 *__restrict__ comb, u64 *out) {
    if (threadIdx.x || blockIdx.x) return;
    u32 tape[TAPE_WORDS];
    u64 k1[4] = { xof[0], xof[1], xof[2], xof[3] };
    u64 k2[4] = { xof[4], xof[5], xof[6], xof[7] };
    Jac a, b;
    comb_mul2(&a, &b, k1, k2, comb);
    u64 zi[4], zz[4], zzz[4], tx[4], ty[4], ox[4], oy[4];
    fe_inv(zi, a.z); fe_sqr(zz, zi); fe_mul(zzz, zz, zi);
    fe_mul(tx, a.x, zz); fe_mul(ty, a.y, zzz);
    fe_inv(zi, b.z); fe_sqr(zz, zi); fe_mul(zzz, zz, zi);
    fe_mul(ox, b.x, zz); fe_mul(oy, b.y, zzz);
    u64 d[4], di[4], lam[4], ex[4], ey[4], t[4];
    fe_sub(d, ox, tx); fe_inv(di, d); fe_sub(t, oy, ty); fe_mul(lam, t, di);
    fe_sqr(t, lam); fe_sub(t, t, tx); fe_sub(ex, t, ox);
    fe_sub(t, tx, ex); fe_mul(t, lam, t); fe_sub(ey, t, ty);
    u64 gx[4], gy[4];
    point_add_classical(gx, gy, tx, ty, ox, oy, tape);
    int o = 0;
#define EMIT(v) do { for (int i=0;i<4;++i) out[o+i] = (v)[i]; o += 4; } while (0)
    EMIT(k1); EMIT(k2); EMIT(tx); EMIT(ty); EMIT(ox); EMIT(oy);
    EMIT(ex); EMIT(ey); EMIT(gx); EMIT(gy);
#undef EMIT
}

// ===========================================================================
// ============================ HOST DRIVER ==================================
// ===========================================================================

// pingpong_filter.rs:366
static void h_batch_to_affine(const std::vector<Jac> &js, std::vector<u64> &out) {
    size_t n = js.size();
    std::vector<u64> prefix(n * 4);
    u64 acc[4] = {1,0,0,0};
    for (size_t i = 0; i < n; ++i) {
        for (int k = 0; k < 4; ++k) prefix[i*4+k] = acc[k];
        if (!u4_is_zero(js[i].z)) fe_mul(acc, acc, js[i].z);
    }
    u64 inv[4]; fe_inv(inv, acc);
    out.assign(n * 8, 0);
    for (size_t ii = n; ii-- > 0; ) {
        if (u4_is_zero(js[ii].z)) continue;                 // stays (0,0)
        u64 zinv[4]; fe_mul(zinv, inv, &prefix[ii*4]);
        fe_mul(inv, inv, js[ii].z);
        u64 z2[4], z3[4];
        fe_sqr(z2, zinv); fe_mul(z3, z2, zinv);
        fe_mul(&out[ii*8],     js[ii].x, z2);
        fe_mul(&out[ii*8 + 4], js[ii].y, z3);
    }
}

// CombTable::build                                  (pingpong_filter.rs:393)
static void build_comb(std::vector<u64> &pts) {
    std::vector<Jac> jacs; jacs.reserve(32 * 255);
    u64 bx[4], by[4];
    u4_copy(bx, H_GX); u4_copy(by, H_GY);
    for (int w = 0; w < 32; ++w) {
        Jac acc; u4_copy(acc.x, bx); u4_copy(acc.y, by);
        acc.z[0]=1; acc.z[1]=0; acc.z[2]=0; acc.z[3]=0;
        jacs.push_back(acc);
        for (int d = 2; d <= 255; ++d) { Jac t; jac_add_affine(&t, &acc, bx, by); acc = t; jacs.push_back(acc); }
        Jac t2; u4_copy(t2.x, bx); u4_copy(t2.y, by); t2.z[0]=1;t2.z[1]=0;t2.z[2]=0;t2.z[3]=0;
        for (int i = 0; i < 8; ++i) { Jac o; jac_double(&o, &t2); t2 = o; }
        std::vector<Jac> one(1, t2);
        std::vector<u64> a; h_batch_to_affine(one, a);
        u4_copy(bx, &a[0]); u4_copy(by, &a[4]);
    }
    h_batch_to_affine(jacs, pts);
}

// Model::new                                        (pingpong_filter.rs:604)
struct HModel {
    int rounds_div, rounds_mul, fold_w, endpoint_w, endpoint_m, seed_m;
    std::vector<unsigned short> wid_div, wid_mul;
};
static long env_usize(const char *n, long dflt) {
    const char *v = getenv(n);
    if (!v || !*v) return dflt;
    char *e = 0; long r = strtol(v, &e, 10);
    return (e && *e == 0) ? r : dflt;
}
static int satsub(int a, int b) { return (a > b) ? (a - b) : 0; }
static int value_width(int round) {
    const int BREAK_1=24, BREAK_2=304, SLOPE_1=17, SLOPE_2=34, SLOPE_3=40, MARGIN=4;
    int start = N_BITS + MARGIN, width;
    if (round < BREAK_1) width = satsub(start, SLOPE_1 * round / 100);
    else {
        int at_first = satsub(start, SLOPE_1 * BREAK_1 / 100);
        if (round < BREAK_2) width = satsub(at_first, SLOPE_2 * (round - BREAK_1) / 100);
        else {
            int at_second = satsub(at_first, SLOPE_2 * (BREAK_2 - BREAK_1) / 100);
            width = satsub(at_second, SLOPE_3 * (round - BREAK_2) / 100);
        }
    }
    if (width < 8) width = 8;
    if (width > VALUE_WIDTH) width = VALUE_WIDTH;
    return width;
}
static HModel build_model(int verbose) {
    if (getenv("SUB4_PINGPONG_SEPARATE_LIFT")) {
        fprintf(stderr, "pingpong_gpu: SUB4_PINGPONG_SEPARATE_LIFT is not modelled; refusing to guess.\n"); exit(2);
    }
    if (getenv("SUB4_LEGACY_POINT_ADD")) {
        fprintf(stderr, "pingpong_gpu: SUB4_LEGACY_POINT_ADD selects the trailmix circuit, not pingpong.\n"); exit(2);
    }
    HModel m;
    m.rounds_div = (int)env_usize("SUB4_PP_ROUNDS", 700);
    m.rounds_mul = (int)env_usize("SUB4_PP_ROUNDS_MUL", m.rounds_div - 4);
    m.fold_w     = (int)env_usize("SUB4_PP_REPLAY_FOLD_WINDOW", 53);
    m.endpoint_w = (int)env_usize("SUB4_PP_ENDPOINT_FOLD_WINDOW", 20);
    if (m.fold_w < 36 || m.fold_w > 64) {
        fprintf(stderr, "pingpong_gpu: REPLAY_FOLD_WINDOW %d outside the modelled range\n", m.fold_w); exit(2);
    }
    if (m.rounds_div > MAX_ROUNDS || m.rounds_mul > MAX_ROUNDS || m.rounds_div < 3 || m.rounds_mul < 3) {
        fprintf(stderr, "pingpong_gpu: round count outside the compiled range (max %d)\n", MAX_ROUNDS); exit(2);
    }
    const int hsb_f = 32;
    m.endpoint_m = ((hsb_f + m.endpoint_w) > (N_BITS - 2) ? (N_BITS - 2) : (hsb_f + m.endpoint_w)) + 2;
    m.seed_m     = ((hsb_f + 32)           > (N_BITS - 2) ? (N_BITS - 2) : (hsb_f + 32))           + 2;
    int rescale = getenv("SUB4_PP_WIDTH_RESCALE") ? 1 : 0;
    m.wid_div.resize(m.rounds_div);
    for (int r = 0; r < m.rounds_div; ++r) {
        int idx = (!rescale || m.rounds_div <= 1) ? r : (r * (704 - 1) / (m.rounds_div - 1));
        m.wid_div[r] = (unsigned short)value_width(idx);
    }
    m.wid_mul.resize(m.rounds_mul);
    for (int r = 0; r < m.rounds_mul; ++r) {
        int idx = (!rescale || m.rounds_div <= 1) ? r : (r * (704 - 1) / (m.rounds_div - 1));
        m.wid_mul[r] = (unsigned short)value_width(idx);
    }
    if (verbose)
        fprintf(stderr, "model windows: rounds_div=%d rounds_mul=%d replay_fold=%d endpoint_fold=%d "
                        "(must match pingpong_div.rs)\n",
                m.rounds_div, m.rounds_mul, m.fold_w, m.endpoint_m - 34);
    return m;
}

static void usage() {
    fprintf(stderr,
      "usage: pingpong_gpu --checkpoint <blob> --ops <count> --from <n> --to <n>\n"
      "       [--device N] [--batch N] [--window N] [--screen] [--selftest] [--verbose]\n"
      "       [--allow-op-mismatch]\n"
      "stdout: one \"<nonce> <classical_mismatch_count>\" line per nonce, ascending.\n"
      "Default is EXACT mode (full count; diffable against pingpong_filter).\n"
      "--screen enables first-mismatch early exit; count is then 0 (clean) or 1 (dirty).\n"
      "THIS IS A SCREEN, NOT A VALIDATOR: phase-channel failures are invisible here, so\n"
      "every clean nonce still needs a CPU eval_circuit confirm.\n");
    exit(2);
}
static void hexbe(char *dst, const u64 a[4]) {
    sprintf(dst, "%016llx%016llx%016llx%016llx", a[3], a[2], a[1], a[0]);
}
static double now_s() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}

int main(int argc, char **argv) {
#ifdef _WIN32
    // stdout must be BINARY: text mode would emit CRLF and break a byte-for-byte
    // `diff` against the CPU filter, which writes bare LF.
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    const char *ckpath = 0;
    long long want_ops = -1, from = -1, to = -1;
    int device = 0, batch = 1024, window = 1024, screen = 0, selftest = 0, verbose = 0, allow_mm = 0;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        #define NEXT() (((i + 1) < argc) ? argv[++i] : (usage(), (char*)0))
        if      (a == "--checkpoint") ckpath = NEXT();
        else if (a == "--ops")     want_ops = atoll(NEXT());
        else if (a == "--from")    from = atoll(NEXT());
        else if (a == "--to")      to = atoll(NEXT());
        else if (a == "--device")  device = atoi(NEXT());
        else if (a == "--batch")   batch = atoi(NEXT());
        else if (a == "--window")  window = atoi(NEXT());
        else if (a == "--screen")  screen = 1;
        else if (a == "--selftest") selftest = 1;
        else if (a == "--verbose" || a == "-v") verbose = 1;
        else if (a == "--allow-op-mismatch") allow_mm = 1;
        else usage();
        #undef NEXT
    }
    if (!ckpath) usage();
    if (!selftest && (from < 0 || to < 0 || to < from)) usage();
    if (want_ops < 0) {
        fprintf(stderr, "pingpong_gpu: --ops <count> is REQUIRED (it is the circuit fingerprint).\n");
        exit(2);
    }

    // ---- checkpoint ----
    FILE *f = fopen(ckpath, "rb");
    if (!f) { fprintf(stderr, "pingpong_gpu: cannot open %s\n", ckpath); exit(2); }
    std::vector<u8> blob(CKP_SIZE + 1);
    size_t got = fread(blob.data(), 1, CKP_SIZE + 1, f);
    fclose(f);
    if (got != (size_t)CKP_SIZE) {
        fprintf(stderr, "pingpong_gpu: %s is %zu bytes, expected %d\n", ckpath, got, CKP_SIZE); exit(2);
    }
    if (memcmp(blob.data(), "PPFSCKP1", 8) != 0) {
        fprintf(stderr, "pingpong_gpu: bad magic in %s (expected PPFSCKP1)\n", ckpath); exit(2);
    }
    u64 n_ops = 0, residual_len = 0;
    memcpy(&n_ops, blob.data() + 8, 8);
    memcpy(&residual_len, blob.data() + 16, 8);
    u64 h_state[25];
    memcpy(h_state, blob.data() + 24, 200);
    const u8 *residual = blob.data() + 224;
    const u8 *tail     = blob.data() + 360;
    if (residual_len >= RATE) {
        fprintf(stderr, "pingpong_gpu: residual_len %llu out of range\n", (unsigned long long)residual_len); exit(2);
    }
    if (n_ops != EXPECTED_OPS_B1_24) {
        fprintf(stderr,
            "pingpong_gpu: REFUSING TO RUN -- checkpoint ops %llu do not match "
            "the source-bound B1=24 identity %llu.\n",
            (unsigned long long)n_ops,
            (unsigned long long)EXPECTED_OPS_B1_24);
        return 4;
    }
    if ((long long)n_ops != want_ops) {
        fprintf(stderr,
            "pingpong_gpu: REFUSING TO RUN -- the checkpoint was produced by a circuit with %llu ops "
            "but --ops says %lld.  Screening a circuit other than the one you grind silently discards "
            "valid islands.  Regenerate the checkpoint from the circuit you are grinding.\n",
            (unsigned long long)n_ops, want_ops);
        if (!allow_mm) return 4;
        fprintf(stderr, "pingpong_gpu: --allow-op-mismatch given; continuing. RESULTS ARE UNTRUSTED.\n");
    }
    if (verbose) fprintf(stderr, "checkpoint: %llu ops, residual_len=%llu\n",
                         (unsigned long long)n_ops, (unsigned long long)residual_len);

    // ---- padded absorb stream + per-nonce patch table ----
    size_t L = (size_t)residual_len + (size_t)TAIL_OPS * ABSORB_BPO;
    size_t full = L / RATE;
    size_t nblk = full + 1;
    if (nblk > MAX_BLK) { fprintf(stderr, "pingpong_gpu: absorb stream too long (%zu blocks)\n", nblk); exit(2); }
    std::vector<u8> S(nblk * RATE, 0);
    memcpy(S.data(), residual, (size_t)residual_len);
    memcpy(S.data() + residual_len, tail, (size_t)TAIL_OPS * ABSORB_BPO);
    std::vector<u32> patch(TAIL_OPS);
    for (int k = 0; k < TAIL_OPS; ++k) {
        size_t off = (size_t)residual_len + (size_t)k * ABSORB_BPO + 17;
        for (int b = 0; b < 8; ++b) S[off + b] = 0;    // q_target is rewritten per nonce
        u32 blk = (u32)(off / RATE), ln = (u32)((off % RATE) / 8),
            sh = (u32)(8 * (off % 8)), nb = (u32)(k / 2);
        if (blk > 0xff || ln > 31 || sh > 63 || nb > 63) {
            fprintf(stderr, "pingpong_gpu: patch encode overflow\n"); exit(2);
        }
        patch[k] = blk | (ln << 8) | (sh << 13) | (nb << 19);
    }
    S[L] ^= 0x1f;                                 // SHAKE256 pad
    S[full * RATE + RATE - 1] ^= 0x80;
    std::vector<u64> stream(nblk * 17);
    for (size_t b = 0; b < nblk; ++b)
        for (int k = 0; k < 17; ++k) memcpy(&stream[b*17 + k], &S[b*RATE + k*8], 8);

    // ---- device setup ----
    CUCHK(cudaSetDevice(device));
    cudaDeviceProp prop; CUCHK(cudaGetDeviceProperties(&prop, device));
    if (verbose) fprintf(stderr, "device %d: %s, %d SMs, sm_%d%d\n",
                         device, prop.name, prop.multiProcessorCount, prop.major, prop.minor);

    HModel M = build_model(verbose);
    std::vector<u64> masks((VALUE_WIDTH + 1) * 5, 0);
    for (int w = 0; w <= VALUE_WIDTH; ++w)
        for (int i = 0; i < 5; ++i) {
            int lo = 64 * i;
            masks[w*5 + i] = (w >= lo + 64) ? ~0ULL : ((w > lo) ? ((1ULL << (w - lo)) - 1ULL) : 0ULL);
        }
    std::vector<unsigned short> wd(MAX_ROUNDS, 0), wm(MAX_ROUNDS, 0);
    for (int r = 0; r < M.rounds_div; ++r) wd[r] = M.wid_div[r];
    for (int r = 0; r < M.rounds_mul; ++r) wm[r] = M.wid_mul[r];

    CUCHK(cudaMemcpyToSymbol(c_RC,   H_RC,   sizeof(H_RC)));
    CUCHK(cudaMemcpyToSymbol(c_PMOD, H_PMOD, sizeof(H_PMOD)));
    CUCHK(cudaMemcpyToSymbol(c_masks, masks.data(), masks.size() * 8));
    CUCHK(cudaMemcpyToSymbol(c_wid_div, wd.data(), wd.size() * 2));
    CUCHK(cudaMemcpyToSymbol(c_wid_mul, wm.data(), wm.size() * 2));
    CUCHK(cudaMemcpyToSymbol(c_rounds_div, &M.rounds_div, 4));
    CUCHK(cudaMemcpyToSymbol(c_rounds_mul, &M.rounds_mul, 4));
    CUCHK(cudaMemcpyToSymbol(c_fold_w, &M.fold_w, 4));
    CUCHK(cudaMemcpyToSymbol(c_endpoint_m, &M.endpoint_m, 4));
    CUCHK(cudaMemcpyToSymbol(c_seed_m, &M.seed_m, 4));
    CUCHK(cudaMemcpyToSymbol(c_state0, h_state, sizeof(h_state)));
    CUCHK(cudaMemcpyToSymbol(c_stream, stream.data(), stream.size() * 8));
    CUCHK(cudaMemcpyToSymbol(c_patch, patch.data(), patch.size() * 4));
    { int nb = (int)nblk; CUCHK(cudaMemcpyToSymbol(c_nblk, &nb, 4)); }

    double tc0 = now_s();
    std::vector<u64> comb;
    build_comb(comb);
    if (verbose) fprintf(stderr, "comb table: %zu points built on the host in %.2fs\n",
                         comb.size()/8, now_s() - tc0);
    u64 *d_comb = 0;
    CUCHK(cudaMalloc(&d_comb, comb.size() * 8));
    CUCHK(cudaMemcpy(d_comb, comb.data(), comb.size() * 8, cudaMemcpyHostToDevice));

    // ---- selftest ----
    if (selftest) {
        const u64 kats[4] = { 3004060ULL, 7ULL, 1ULL, 7ULL + (1ULL << 48) };
        u64 *d_nonces = 0, *d_xof = 0, *d_out = 0;
        SqState *d_sq = 0;
        CUCHK(cudaMalloc(&d_nonces, 4 * 8));
        CUCHK(cudaMalloc(&d_sq, 4 * sizeof(SqState)));
        CUCHK(cudaMalloc(&d_xof, 4 * 8 * 8));
        CUCHK(cudaMalloc(&d_out, 40 * 8));
        CUCHK(cudaMemcpy(d_nonces, kats, 4 * 8, cudaMemcpyHostToDevice));
        fs_init_kernel<<<1, 32>>>(d_nonces, 4, d_sq);
        CUCHK(cudaGetLastError());
        fs_squeeze_kernel<<<1, 32>>>(d_sq, d_xof, 4, 8, 8, (const int*)0);
        CUCHK(cudaDeviceSynchronize());
        CUCHK(cudaGetLastError());
        std::vector<u64> hx(32);
        CUCHK(cudaMemcpy(hx.data(), d_xof, 4 * 8 * 8, cudaMemcpyDeviceToHost));
        for (int i = 0; i < 4; ++i) {
            u8 bb[32]; memcpy(bb, &hx[i*8], 32);
            char s[80]; for (int j = 0; j < 32; ++j) sprintf(s + 2*j, "%02x", bb[j]);
            fprintf(stderr, "xof[0..32] nonce %-20llu = %s\n", (unsigned long long)kats[i], s);
        }
        selftest_kernel<<<1, 32>>>(d_xof, d_comb, d_out);
        CUCHK(cudaDeviceSynchronize());
        CUCHK(cudaGetLastError());
        std::vector<u64> ho(40);
        CUCHK(cudaMemcpy(ho.data(), d_out, 40 * 8, cudaMemcpyDeviceToHost));
        const char *nm[10] = { "k1","k2","tx","ty","ox","oy","ex","ey","gx","gy" };
        char h[80];
        for (int i = 0; i < 10; ++i) { hexbe(h, &ho[i*4]); fprintf(stderr, "%s = %s\n", nm[i], h); }
        int okx = memcmp(&ho[6*4], &ho[8*4], 32) == 0;
        int oky = memcmp(&ho[7*4], &ho[9*4], 32) == 0;
        fprintf(stderr, "gx %s\ngy %s\n", okx ? "OK" : "MISMATCH", oky ? "OK" : "MISMATCH");
        return (okx && oky) ? 0 : 1;
    }

    if ((unsigned long long)to >= (1ULL << 48))
        fprintf(stderr, "pingpong_gpu: WARNING -- the nonce tail absorbs only bits 0..47; "
                        "nonces >= 2^48 alias to nonce mod 2^48.\n");
    if (window <= 0 || (window & 31) || window > NUM_TESTS) {
        fprintf(stderr, "pingpong_gpu: --window must be a positive multiple of 32, <= %d\n", NUM_TESTS); exit(2);
    }
    if (batch <= 0) usage();

    long long total = to - from + 1;
    if ((long long)batch > total) batch = (int)total;

    size_t win_words = (size_t)window * 8;
    u64 *d_nonces = 0, *d_xof = 0;
    unsigned long long *d_counts = 0;
    int *d_dead = 0;
    SqState *d_sq = 0;
    CUCHK(cudaMalloc(&d_nonces, (size_t)batch * 8));
    CUCHK(cudaMalloc(&d_sq, (size_t)batch * sizeof(SqState)));
    CUCHK(cudaMalloc(&d_xof, (size_t)batch * win_words * 8));
    CUCHK(cudaMalloc(&d_counts, (size_t)batch * 8));
    CUCHK(cudaMalloc(&d_dead, (size_t)batch * 4));
    if (verbose) fprintf(stderr, "xof buffer: %.1f MB (batch=%d window=%d) mode=%s\n",
                         (double)batch * win_words * 8 / 1048576.0, batch, window,
                         screen ? "screen" : "exact");

    const int TPB = 128;
    int max_blocks = prop.multiProcessorCount * 8;         // 8 blocks/SM of 4 warps
    std::vector<u64> hn(batch);
    std::vector<unsigned long long> hc(batch);
    double t0 = now_s();

    for (long long b0 = from; b0 <= to; b0 += batch) {
        int nb = (int)(((to - b0 + 1) < (long long)batch) ? (to - b0 + 1) : (long long)batch);
        for (int i = 0; i < nb; ++i) hn[i] = (u64)(b0 + i);
        CUCHK(cudaMemcpy(d_nonces, hn.data(), (size_t)nb * 8, cudaMemcpyHostToDevice));
        CUCHK(cudaMemset(d_counts, 0, (size_t)nb * 8));
        CUCHK(cudaMemset(d_dead, 0, (size_t)nb * 4));
        fs_init_kernel<<<(nb + 127) / 128, 128>>>(d_nonces, nb, d_sq);
        CUCHK(cudaGetLastError());
        for (int lo = 0; lo < NUM_TESTS; lo += window) {
            int hi = lo + window; if (hi > NUM_TESTS) hi = NUM_TESTS;
            fs_squeeze_kernel<<<(nb + 127) / 128, 128>>>(d_sq, d_xof, nb, (hi - lo) * 8,
                                                         (int)win_words, d_dead);
            CUCHK(cudaGetLastError());
            int blocks = (nb + (TPB / 32) - 1) / (TPB / 32);
            if (blocks > max_blocks) blocks = max_blocks;
            if (blocks < 1) blocks = 1;
            model_kernel<<<blocks, TPB>>>(d_xof, d_comb, nb, lo, hi, (int)win_words,
                                          d_counts, d_dead, screen);
            CUCHK(cudaGetLastError());
            CUCHK(cudaDeviceSynchronize());
        }
        CUCHK(cudaMemcpy(hc.data(), d_counts, (size_t)nb * 8, cudaMemcpyDeviceToHost));
        for (int i = 0; i < nb; ++i) printf("%llu %llu\n", (unsigned long long)(b0 + i), hc[i]);
        fflush(stdout);
    }
    double dt = now_s() - t0;
    if (verbose) fprintf(stderr, "screened %lld nonces in %.2fs = %.3f nonces/s\n",
                         total, dt, (double)total / (dt > 0 ? dt : 1e-9));
    return 0;
}
